"""
DeepSeek-OCR Flask API 主應用程式（標準 Transformers 版本）
提供圖片 OCR 辨識服務
"""

from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ocr_service_standard import DeepSeekOCRService
from config import Config

app = Flask(__name__)

# 設定 JSON 輸出為 UTF-8，不轉義 ASCII
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# 配置設定
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上傳檔案大小為 16MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}

# 確保上傳目錄存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 讀取 OCR 設定（從 config.py）
ocr_timeout = int(os.environ.get('OCR_TIMEOUT', 300))
ocr_base_size = Config.OCR_BASE_SIZE
ocr_image_size = Config.OCR_IMAGE_SIZE
ocr_crop_mode = Config.OCR_CROP_MODE
ocr_test_compress = Config.OCR_TEST_COMPRESS
ocr_save_results = Config.OCR_SAVE_RESULTS

print(f"OCR 超時設定: {ocr_timeout} 秒")
print(f"OCR 圖片處理參數:")
print(f"  - base_size: {ocr_base_size}")
print(f"  - image_size: {ocr_image_size}")
print(f"  - crop_mode: {ocr_crop_mode}")
print(f"  - test_compress: {ocr_test_compress}")
print(f"  - save_results: {ocr_save_results}")

# 初始化 OCR 服務（使用標準 Transformers 版本）
print("正在初始化 DeepSeek-OCR 服務（標準 Transformers 版本）...")
ocr_service = DeepSeekOCRService(
    ocr_timeout=ocr_timeout,
    base_size=ocr_base_size,
    image_size=ocr_image_size,
    crop_mode=ocr_crop_mode,
    test_compress=ocr_test_compress,
    save_results=ocr_save_results
)
print("DeepSeek-OCR 服務初始化完成！")


def allowed_file(filename):
    """檢查檔案副檔名是否允許"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """首頁 - Web 介面"""
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'DeepSeek-OCR API (Standard Transformers)',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/ocr', methods=['POST'])
def perform_ocr():
    """執行 OCR 辨識"""
    # 檢查是否有上傳檔案
    if 'file' not in request.files:
        error_msg = "請求中沒有檔案部分"
        print(f"錯誤: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    file = request.files['file']
    
    # 檢查檔案名稱
    if file.filename == '':
        error_msg = "未選擇檔案"
        print(f"錯誤: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 檢查檔案類型
    if not allowed_file(file.filename):
        error_msg = f"不支援的檔案類型。允許的類型: {', '.join(app.config['ALLOWED_EXTENSIONS'])}"
        print(f"錯誤: {error_msg}, 收到檔案: {file.filename}")
        return jsonify({'error': error_msg}), 400
    
    # 取得自訂提示詞（如果有）
    custom_prompt = request.form.get('prompt', None)
    
    # 儲存上傳的檔案
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    print(f"正在儲存上傳的檔案: {filepath}")
    file.save(filepath)
    
    # 執行 OCR
    print(f"開始執行 OCR 辨識: {filepath}")
    
    # 執行 OCR 並捕獲可能的錯誤（包括超時錯誤）
    result = None
    error_info = None
    from concurrent.futures import TimeoutError as FuturesTimeoutError
    
    try:
        result = ocr_service.perform_ocr(filepath, custom_prompt)
    except FuturesTimeoutError as timeout_err:
        error_info = f"OCR 處理超時 (超過 {ocr_service.ocr_timeout} 秒)，請嘗試使用更小的圖片或增加超時設定"
        print(f"======== OCR 超時錯誤 ========")
        print(f"錯誤類型: TimeoutError")
        print(f"錯誤訊息: {error_info}")
        print(f"圖片路徑: {filepath}")
        print(f"超時設定: {ocr_service.ocr_timeout} 秒")
        print(f"============================")
    except Exception as general_err:
        error_info = f"OCR 處理發生錯誤: {str(general_err)}"
        print(f"======== OCR 執行錯誤 ========")
        print(f"錯誤類型: {type(general_err).__name__}")
        print(f"錯誤訊息: {str(general_err)}")
        print(f"圖片路徑: {filepath}")
        print(f"============================")
        import traceback
        print(f"錯誤詳情:\n{traceback.format_exc()}")
    
    # 刪除暫存檔案
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"已刪除暫存檔案: {filepath}")
    
    # 檢查是否有錯誤
    if error_info:
        print(f"返回錯誤響應: {error_info}")
        return jsonify({'error': error_info, 'image_path': filepath}), 500
    elif result and 'error' in result:
        error_msg = result['error']
        print(f"OCR 執行錯誤: {error_msg}")
        return jsonify(result), 500
    
    print(f"OCR 辨識完成，文字長度: {len(result.get('text', ''))}")
    return jsonify(result), 200


@app.route('/ocr/batch', methods=['POST'])
def perform_batch_ocr():
    """批次執行 OCR 辨識"""
    # 檢查是否有上傳檔案
    if 'files' not in request.files:
        error_msg = "請求中沒有檔案部分"
        print(f"錯誤: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    files = request.files.getlist('files')
    
    if len(files) == 0:
        error_msg = "未選擇任何檔案"
        print(f"錯誤: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 取得自訂提示詞（如果有）
    custom_prompt = request.form.get('prompt', None)
    
    # 儲存所有上傳的檔案
    filepaths = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for idx, file in enumerate(files):
        if file.filename == '':
            continue
            
        if not allowed_file(file.filename):
            error_msg = f"檔案 {file.filename} 類型不支援"
            print(f"錯誤: {error_msg}")
            continue
        
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{idx}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        print(f"正在儲存上傳的檔案 {idx+1}: {filepath}")
        file.save(filepath)
        filepaths.append(filepath)
    
    if len(filepaths) == 0:
        error_msg = "沒有有效的圖片檔案"
        print(f"錯誤: {error_msg}")
        return jsonify({'error': error_msg}), 400
    
    # 執行批次 OCR
    print(f"開始執行批次 OCR 辨識，共 {len(filepaths)} 個檔案")
    results = ocr_service.perform_batch_ocr(filepaths, custom_prompt)
    
    # 刪除暫存檔案
    for filepath in filepaths:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"已刪除暫存檔案: {filepath}")
    
    print(f"批次 OCR 辨識完成，共處理 {len(results)} 個檔案")
    return jsonify({'results': results, 'total': len(results)}), 200


@app.errorhandler(413)
def request_entity_too_large(error):
    """處理檔案過大錯誤"""
    error_msg = "上傳的檔案過大，最大允許 16MB"
    print(f"錯誤: {error_msg}")
    return jsonify({'error': error_msg}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """處理內部伺服器錯誤"""
    error_msg = f"內部伺服器錯誤: {str(error)}"
    print(f"錯誤: {error_msg}")
    return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    # 開發模式運行
    print("=" * 60)
    print("DeepSeek-OCR API 服務啟動中（標準 Transformers 版本）...")
    print("=" * 60)
    # 關閉 debug 模式以避免模型重複載入
    app.run(host='0.0.0.0', port=5000, debug=False)

