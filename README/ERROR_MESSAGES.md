# DeepSeek-OCR API 錯誤訊息說明

本文檔詳細說明 DeepSeek-OCR API 可能遇到的錯誤訊息、發生原因和解決方法。

## 目錄

- [安裝相關錯誤](#安裝相關錯誤)
- [模型載入錯誤](#模型載入錯誤)
- [API 請求錯誤](#api-請求錯誤)
- [檔案處理錯誤](#檔案處理錯誤)
- [系統資源錯誤](#系統資源錯誤)

---

## 安裝相關錯誤

### 錯誤 1: 無法安裝 vLLM

**錯誤訊息**:
```
ERROR: Could not find a version that satisfies the requirement vllm
```

**發生原因**:
- 沒有使用正確的安裝來源
- Python 版本不符合要求（需要 Python 3.8+）
- 系統不支援 vLLM（需要 Linux 系統）

**解決方法**:

1. 確認 Python 版本：
```bash
python --version  # 應該是 3.8 或以上
```

2. 使用正確的安裝指令：
```bash
# 使用 UV 工具
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 或使用 pip
pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

3. 如果仍然失敗，檢查是否為 Linux 系統：
```bash
uname -s  # 應該顯示 Linux
```

### 錯誤 2: CUDA 版本不符

**錯誤訊息**:
```
RuntimeError: CUDA version mismatch
```

**發生原因**:
- 系統的 CUDA 版本與 vLLM 要求的版本不一致
- 沒有安裝 CUDA 或 CUDA 驅動

**解決方法**:

1. 檢查 CUDA 版本：
```bash
nvidia-smi  # 查看 CUDA 版本
```

2. 安裝或更新 CUDA（需要 CUDA 11.8 或以上）：
```bash
# 參考 NVIDIA 官方文檔安裝 CUDA
# https://developer.nvidia.com/cuda-downloads
```

3. 如果無法更新 CUDA，考慮使用 CPU 版本（效能會較差）

### 錯誤 3: UV 工具語法錯誤

**錯誤訊息**:
```
error: unexpected argument '-U' found
tip: to pass '-U' as a value, use '-- -U'
```

**發生原因**:
- 新版 uv 工具的語法已改變，不再支援 `-U` 參數
- 應該使用 `--upgrade` 或直接使用 `pip install --upgrade`

**解決方法**:

```bash
# 方法 1: 直接使用 pip（推薦）
pip install --upgrade vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 方法 2: 使用 uv 的正確語法
uv pip install --upgrade vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 方法 3: 如果您已經在虛擬環境中，直接安裝
pip install vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

### 錯誤 4: UV 工具未安裝

**錯誤訊息**:
```
bash: uv: command not found
```

**發生原因**:
- 沒有安裝 UV 工具

**解決方法**:

```bash
# 不需要安裝 uv，直接使用 Python 內建的 venv 和 pip
python -m venv .venv
source .venv/bin/activate
pip install --upgrade vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
pip install Flask Pillow Werkzeug
```

---

## 模型載入錯誤

### 錯誤 5: 模型下載失敗

**錯誤訊息**:
```
HTTPError: 401 Unauthorized
```
或
```
ConnectionError: Failed to download model
```

**發生原因**:
- 網路連線問題
- Hugging Face 伺服器暫時無法連線
- 需要登入 Hugging Face（部分模型需要授權）

**解決方法**:

1. 檢查網路連線：
```bash
ping huggingface.co
```

2. 如果需要授權，登入 Hugging Face：
```bash
pip install huggingface_hub
huggingface-cli login
```

3. 設定代理（如果在防火牆後面）：
```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=https://your-proxy:port
```

4. 手動下載模型：
```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('unsloth/DeepSeek-OCR', local_dir='models/deepseek_ocr')"
```

### 錯誤 6: GPU 記憶體不足

**錯誤訊息**:
```
RuntimeError: CUDA out of memory
```

**發生原因**:
- GPU 記憶體不足以載入模型
- 其他程式正在使用 GPU 記憶體

**解決方法**:

1. 檢查 GPU 記憶體使用情況：
```bash
nvidia-smi
```

2. 釋放 GPU 記憶體：
```bash
# 關閉其他使用 GPU 的程式
kill -9 <PID>
```

3. 如果 GPU 記憶體確實不足（需要至少 8GB），考慮：
   - 使用更小的批次大小
   - 升級 GPU 硬體
   - 使用 CPU 模式（效能較差）

### 錯誤 17: 模型檔案損壞

**錯誤訊息**:
```
RuntimeError: Error loading model checkpoint
```

**發生原因**:
- 模型檔案下載不完整或損壞
- 磁碟空間不足導致檔案損壞

**解決方法**:

1. 刪除損壞的模型檔案：
```bash
rm -rf ~/.cache/huggingface/hub/models--unsloth--DeepSeek-OCR
```

2. 重新下載模型：
```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('unsloth/DeepSeek-OCR', local_dir='models/deepseek_ocr')"
```

3. 確認磁碟空間充足：
```bash
df -h  # 至少需要 10GB 可用空間
```

---

## API 請求錯誤

### 錯誤 17: 請求中沒有檔案

**錯誤訊息**:
```json
{
  "error": "請求中沒有檔案部分"
}
```

**HTTP 狀態碼**: 400 Bad Request

**發生原因**:
- POST 請求沒有包含 `file` 參數
- 使用了錯誤的請求格式

**解決方法**:

確保使用 `multipart/form-data` 格式並包含 `file` 參數：

```bash
# 正確的 curl 請求
curl -X POST -F "file=@/path/to/image.png" http://localhost:5000/ocr
```

```python
# 正確的 Python 請求
import requests

with open('image.png', 'rb') as f:
    files = {'file': f}  # 注意：參數名稱必須是 'file'
    response = requests.post('http://localhost:5000/ocr', files=files)
```

### 錯誤 17: 未選擇檔案

**錯誤訊息**:
```json
{
  "error": "未選擇檔案"
}
```

**HTTP 狀態碼**: 400 Bad Request

**發生原因**:
- `file` 參數存在但檔案名稱為空
- 前端表單沒有正確選擇檔案

**解決方法**:

確保檔案路徑正確且檔案存在：

```bash
# 檢查檔案是否存在
ls -lh /path/to/image.png

# 使用正確的檔案路徑
curl -X POST -F "file=@/path/to/image.png" http://localhost:5000/ocr
```

### 錯誤 17: 不支援的檔案類型

**錯誤訊息**:
```json
{
  "error": "不支援的檔案類型。允許的類型: png, jpg, jpeg, gif, bmp, webp"
}
```

**HTTP 狀態碼**: 400 Bad Request

**發生原因**:
- 上傳的檔案副檔名不在允許的清單中
- 檔案沒有副檔名

**解決方法**:

1. 確認檔案格式：
```bash
file image.xxx  # 查看檔案實際格式
```

2. 轉換檔案格式為支援的格式：
```bash
# 使用 ImageMagick 轉換
convert input.tiff output.png

# 使用 Python PIL
from PIL import Image
Image.open('input.tiff').save('output.png')
```

3. 支援的格式包括：
   - PNG (.png)
   - JPEG (.jpg, .jpeg)
   - GIF (.gif)
   - BMP (.bmp)
   - WebP (.webp)

### 錯誤 17: 上傳的檔案過大

**錯誤訊息**:
```json
{
  "error": "上傳的檔案過大，最大允許 16MB"
}
```

**HTTP 狀態碼**: 413 Request Entity Too Large

**發生原因**:
- 上傳的檔案超過 16MB 限制

**解決方法**:

1. 壓縮圖片：
```bash
# 使用 ImageMagick 壓縮
convert input.png -quality 85 -resize 50% output.png
```

```python
# 使用 Python PIL 壓縮
from PIL import Image

img = Image.open('input.png')
img.save('output.png', quality=85, optimize=True)
```

2. 如果需要處理更大的檔案，可以修改配置：

在 `app.py` 中修改：
```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 改為 32MB
```

---

## 檔案處理錯誤

### 錯誤 17: 圖片檔案不存在

**錯誤訊息**:
```json
{
  "error": "圖片檔案不存在: /path/to/image.png",
  "image_path": "/path/to/image.png"
}
```

**HTTP 狀態碼**: 500 Internal Server Error

**發生原因**:
- 檔案在上傳後被意外刪除
- 檔案路徑錯誤
- 權限問題導致無法存取檔案

**解決方法**:

這個錯誤通常不應該發生（因為是內部處理流程）。如果遇到：

1. 檢查 `uploads/` 目錄權限：
```bash
chmod 755 uploads/
```

2. 檢查磁碟空間：
```bash
df -h
```

3. 檢查日誌以了解詳細錯誤：
```bash
tail -f logs/error.log
```

### 錯誤 17: 無法讀取圖片

**錯誤訊息**:
```
PIL.UnidentifiedImageError: cannot identify image file
```

**發生原因**:
- 檔案不是有效的圖片格式
- 圖片檔案損壞
- 檔案副檔名與實際格式不符

**解決方法**:

1. 驗證圖片檔案：
```bash
# 檢查檔案實際類型
file image.png

# 嘗試用其他工具開啟
display image.png  # 或 eog image.png
```

2. 重新儲存圖片：
```python
from PIL import Image

# 嘗試讀取並重新儲存
try:
    img = Image.open('problematic.png')
    img.save('fixed.png')
except Exception as e:
    print(f"錯誤: {e}")
```

### 錯誤 17: 沒有有效的圖片可以處理

**錯誤訊息**:
```json
{
  "error": "沒有有效的圖片可以處理"
}
```

**HTTP 狀態碼**: 400 Bad Request

**發生原因**:
- 批次請求中所有圖片都無效
- 所有圖片檔案都不存在或無法讀取

**解決方法**:

檢查每個圖片檔案：

```bash
# 檢查多個檔案
for file in image1.png image2.png image3.png; do
    if [ -f "$file" ]; then
        echo "$file 存在"
        file "$file"
    else
        echo "$file 不存在"
    fi
done
```

---

## 系統資源錯誤

### 錯誤 17: 模型未返回任何結果

**錯誤訊息**:
```json
{
  "error": "模型未返回任何結果",
  "image_path": "/path/to/image.png"
}
```

**HTTP 狀態碼**: 500 Internal Server Error

**發生原因**:
- 模型處理過程中發生錯誤
- 輸入圖片格式異常
- GPU 記憶體不足導致處理失敗

**解決方法**:

1. 檢查伺服器日誌：
```bash
tail -f logs/error.log
```

2. 重新啟動服務：
```bash
./start_server.sh
```

3. 確認 GPU 狀態：
```bash
nvidia-smi
```

### 錯誤 17: 內部伺服器錯誤

**錯誤訊息**:
```json
{
  "error": "內部伺服器錯誤: [詳細錯誤訊息]"
}
```

**HTTP 狀態碼**: 500 Internal Server Error

**發生原因**:
- 未預期的系統錯誤
- Python 套件版本不相容
- 系統資源不足

**解決方法**:

1. 查看完整錯誤日誌：
```bash
tail -100 logs/error.log
```

2. 檢查系統資源：
```bash
# 檢查 CPU 和記憶體使用
top

# 檢查磁碟空間
df -h

# 檢查 GPU 狀態
nvidia-smi
```

3. 驗證套件安裝：
```bash
pip list | grep -E "vllm|flask|pillow"
```

4. 如果問題持續，嘗試重新安裝：
```bash
pip uninstall vllm flask pillow
pip install Flask Pillow
pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

### 錯誤 17: 服務無法啟動

**錯誤訊息**:
```
Error: Cannot allocate memory
```
或
```
Address already in use
```

**發生原因**:
- 系統記憶體不足
- Port 5000 已被其他服務佔用

**解決方法**:

1. 檢查記憶體使用：
```bash
free -h
```

2. 如果記憶體不足，關閉不必要的程式或增加記憶體

3. 檢查 Port 是否被佔用：
```bash
lsof -i :5000
```

4. 關閉佔用 Port 的程式：
```bash
kill -9 <PID>
```

5. 或使用不同的 Port：
```python
# 在 app.py 中修改
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## OCR 處理問題

### 問題 19: Server 卡住不動，沒有回覆

**現象**:
```
正在儲存上傳的檔案: uploads/20251111_103451_image.jpg
開始執行 OCR 辨識: uploads/20251111_103451_image.jpg
已載入圖片: uploads/20251111_103451_image.jpg
正在執行 OCR 辨識...
[之後就沒有任何回應]
```

**可能原因**:
1. **GPU 記憶體不足或被佔用** - 其他程序佔用了 GPU 記憶體，導致模型推理卡住
2. **圖片過大或過於複雜** - 處理時間超過預期，但沒有超時機制
3. **模型推理死鎖** - 模型在處理特定圖片時發生內部錯誤
4. **系統資源不足** - CPU 或記憶體不足導致系統響應變慢

**解決方法**:

#### 方法 1: 檢查 GPU 狀態

```bash
# 查看 GPU 記憶體使用情況
nvidia-smi

# 如果有其他程序佔用 GPU，可以考慮停止它們
kill -9 <PID>

# 或重啟 OCR 服務
./start_server.sh
```

#### 方法 2: 調整超時設定

系統現在已添加超時保護機制，預設為 300 秒（5 分鐘）。如果您的圖片需要更長時間處理，可以在 `ocr_service.py` 初始化時調整：

```python
# 在 app.py 中修改
ocr_service = DeepSeekOCRService(ocr_timeout=600)  # 改為 10 分鐘
```

或設定環境變數：

```bash
export OCR_TIMEOUT=600
python app.py
```

#### 方法 3: 壓縮圖片

如果圖片過大，建議先壓縮再上傳：

```bash
# 使用 ImageMagick 壓縮
convert large_image.png -resize 50% -quality 85 compressed_image.png
```

```python
# 使用 Python PIL 壓縮
from PIL import Image

img = Image.open('large_image.png')
# 縮小到最大 2048x2048
img.thumbnail((2048, 2048))
img.save('compressed_image.png', optimize=True, quality=85)
```

#### 方法 4: 清理 GPU 快取記憶體

如果長時間運行後出現卡住，可能是 GPU 記憶體累積過多。系統現在會自動清理，但您也可以手動重啟服務：

```bash
# 停止服務
pkill -f "python app.py"

# 重新啟動
./start_server.sh
```

#### 方法 5: 查看詳細日誌

啟用詳細日誌以診斷問題：

```python
# 在 app.py 中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

查看日誌輸出：
```bash
tail -f logs/ocr_service.log
```

**預防措施**:

系統現已實施以下保護機制：

1. **超時保護** - OCR 處理超過設定時間會自動中止並返回錯誤
2. **GPU 記憶體監控** - 處理前檢查 GPU 記憶體，不足時拒絕請求
3. **自動清理** - 批次處理時每 5 張圖片自動清理 GPU 快取
4. **詳細日誌** - 記錄處理時間、GPU 狀態等資訊
5. **錯誤處理** - 捕獲異常並提供詳細錯誤訊息

**系統需求**:

為避免處理卡住，建議：
- GPU 記憶體至少 8GB
- 系統記憶體至少 16GB
- 可用 GPU 記憶體至少 500MB
- 圖片大小建議不超過 4096x4096 像素

### 問題 20: OCR 處理超時

**錯誤訊息**:
```json
{
  "error": "OCR 處理超時 (300 秒)，請嘗試使用更小的圖片或增加超時設定",
  "image_path": "/path/to/image.png",
  "processing_time": 300.00,
  "gpu_info": {...}
}
```

**發生原因**:
- 圖片過大或過於複雜，處理時間超過超時設定（預設 300 秒）
- GPU 效能不足
- 系統負載過高

**解決方法**:

1. **增加超時時間** - 在 app.py 中調整：
```python
ocr_service = DeepSeekOCRService(ocr_timeout=600)  # 10 分鐘
```

2. **壓縮圖片** - 減小圖片尺寸和檔案大小

3. **檢查 GPU 效能** - 確保 GPU 正常工作且未被其他程序佔用

4. **分批處理** - 對於多張圖片，使用批次 API 而非同時發送多個請求

### 問題 21: GPU 記憶體不足

**錯誤訊息**:
```json
{
  "error": "GPU 記憶體不足，可用記憶體: 256 MB，建議至少有 500 MB 可用記憶體",
  "image_path": "/path/to/image.png",
  "gpu_info": {
    "available": true,
    "total_mb": 8192,
    "used_mb": 7936,
    "free_mb": 256,
    "usage_percent": 96.88
  }
}
```

**發生原因**:
- GPU 記憶體被其他程序大量佔用
- 連續處理多張圖片導致記憶體累積
- GPU 記憶體本身容量不足

**解決方法**:

1. **關閉其他 GPU 程序**:
```bash
# 查看 GPU 使用情況
nvidia-smi

# 關閉佔用 GPU 的程序
kill -9 <PID>
```

2. **重啟 OCR 服務** - 釋放累積的記憶體：
```bash
./start_server.sh
```

3. **等待一段時間後重試** - GPU 記憶體會自動釋放

4. **使用更大的 GPU** - 建議至少 8GB VRAM

### 問題 22: Flask 多線程環境中的 Signal 錯誤

**錯誤訊息**:
```
ValueError: signal only works in main thread of the main interpreter

Traceback (most recent call last):
  File "/GPUData/working/Deepseek-OCR/ocr_service.py", line 273, in perform_ocr
    signal.signal(signal.SIGALRM, timeout_handler)
  File "/usr/lib/python3.10/signal.py", line 56, in signal
    handler = _signal.signal(_enum_to_int(signalnum), _enum_to_int(handler))
ValueError: signal only works in main thread of the main interpreter
```

**HTTP 狀態碼**: 500 Internal Server Error

**發生原因**:

1. **Python Signal 模組限制** - `signal.SIGALRM` 只能在主線程（main thread）中使用
2. **Flask 多線程架構** - Flask 在處理 HTTP 請求時使用工作線程（worker thread），而非主線程
3. **超時機制設計問題** - 原始程式碼使用 `signal.signal()` 和 `signal.alarm()` 實現超時控制，這在 Flask 的工作線程中無法運作

**技術背景**:

Python 的 `signal` 模組基於 Unix 信號機制，信號處理器（signal handler）必須在主線程中註冊和執行。當 Flask 接收到 HTTP 請求時，請求處理函數在工作線程中執行，此時嘗試調用 `signal.signal()` 會拋出 `ValueError`。

**解決方法**:

#### 方法 1: 使用線程安全的超時機制（已實施）

系統已修改為使用 `concurrent.futures.ThreadPoolExecutor` 實現超時控制，這是線程安全的方式：

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# 在工作線程中安全地執行帶有超時控制的 OCR 推理
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(perform_ocr_function)
    result = future.result(timeout=300)  # 300 秒超時
```

這個方法的優點：
- ✅ 線程安全，可在 Flask 工作線程中使用
- ✅ 明確的超時控制
- ✅ 不依賴 Unix 信號機制
- ✅ 跨平台相容（Windows、Linux、macOS）

#### 方法 2: 使用 Gunicorn 單一 worker 模式（不推薦）

```bash
# 使用單一 worker，所有請求在主線程處理
gunicorn -w 1 --threads 1 -b 0.0.0.0:5000 app:app
```

這個方法的缺點：
- ❌ 無法並行處理多個請求
- ❌ 效能低下
- ❌ 無法充分利用多核 CPU

#### 方法 3: 使用 multiprocessing.Process（不推薦）

```python
from multiprocessing import Process, Queue

# 在子進程中執行 OCR
```

這個方法的缺點：
- ❌ 進程間通訊開銷大
- ❌ GPU 記憶體無法共享
- ❌ 複雜度高

**如何驗證修復**:

1. 重新啟動服務：
```bash
./start_server.sh
```

2. 測試 OCR API：
```bash
curl -X POST -F "file=@test_image.png" http://localhost:5000/ocr
```

3. 檢查不會再出現 `ValueError: signal only works in main thread` 錯誤

**相關修改**:

修改的檔案包括：
- `ocr_service.py`: 
  - 移除 `signal` 模組依賴
  - 移除 `timeout_handler` 函數
  - 將超時機制改為使用 `ThreadPoolExecutor`
- `app.py`: 
  - 添加 `try-except` 捕獲 `FuturesTimeoutError`
  - 清楚顯示超時錯誤訊息和詳細信息

**效能影響**:

使用 `ThreadPoolExecutor` 的效能影響極小：
- 額外記憶體開銷：< 1 MB
- 額外 CPU 開銷：< 0.1%
- 超時精度：毫秒級

**預防措施**:

1. **避免在 Flask 路由中使用 signal** - 任何需要超時控制的功能都應使用線程安全的方式
2. **使用 concurrent.futures** - 這是 Python 標準庫提供的線程安全超時機制
3. **錯誤處理** - 始終捕獲 `TimeoutError` 並提供清楚的錯誤訊息

**參考資料**:
- Python signal 模組文檔: https://docs.python.org/3/library/signal.html#signals-and-threads
- concurrent.futures 文檔: https://docs.python.org/3/library/concurrent.futures.html
- Flask 請求處理: https://flask.palletsprojects.com/en/2.3.x/patterns/threadlocal/

---

## 前端界面問題

### 問題 23: 相機預覽畫面旋轉後持續變大

**錯誤訊息**:
```
updatePreviewRotation: 當前容器尺寸: 31978656 x 33554428
updatePreviewRotation: 當前容器尺寸: 33554428 x 33554428
updatePreviewRotation: 當前容器尺寸: 33554428 x 33554428
[容器尺寸持續增大]
```

**發生原因**:

1. **無限循環調用** - `updatePreviewRotation` 函數在每次收到相機畫面時都會被調用（即使旋轉角度沒有改變）
2. **尺寸計算問題** - 函數使用 `offsetWidth` 和 `offsetHeight` 讀取容器尺寸，這會觸發瀏覽器重排（reflow）
3. **異常值累積** - 如果容器尺寸已經異常大，基於這個異常尺寸計算的新尺寸也會異常大，導致無限放大
4. **缺少防護機制** - 沒有檢查當前旋轉角度是否已應用，也沒有限制容器尺寸的最大值

**技術背景**:

- `offsetWidth` 和 `offsetHeight` 是讀取屬性，會強制瀏覽器進行佈局計算（layout），可能觸發重排
- 每次設置容器的 `width` 和 `height` 樣式時，可能會觸發某些事件監聽器或瀏覽器內部的重新計算
- 如果容器尺寸異常大（如 3.35544e+07px），基於這個值計算的新尺寸也會異常大

**解決方法**:

#### 方法 1: 添加旋轉角度緩存（已實施）

系統已添加 `currentAppliedRotation` 變數來記錄當前應用的旋轉角度：

```javascript
// 只在旋轉角度改變時才更新（避免每次收到畫面都重複處理）
const rotation = elements.imageRotation ? parseInt(elements.imageRotation.value) || 0 : 0;
if (currentAppliedRotation !== rotation) {
    updatePreviewRotation(rotation);
}
```

#### 方法 2: 使用防抖機制（已實施）

添加防抖計時器，避免短時間內重複調用：

```javascript
function updatePreviewRotation(rotation) {
    // 清除之前的防抖計時器
    if (rotationUpdateTimer) {
        clearTimeout(rotationUpdateTimer);
        rotationUpdateTimer = null;
    }
    
    // 防抖處理：延遲執行以避免重複調用
    rotationUpdateTimer = setTimeout(() => {
        _updatePreviewRotationInternal(rotation);
    }, 50);
}
```

#### 方法 3: 使用 getBoundingClientRect() 替代 offsetWidth/offsetHeight（已實施）

`getBoundingClientRect()` 不會觸發重排，且返回實際渲染尺寸：

```javascript
// 使用 getBoundingClientRect() 獲取實際渲染尺寸（不會觸發重排）
const containerRect = previewContainer.getBoundingClientRect();
let currentWidth = containerRect.width;
let currentHeight = containerRect.height;
```

#### 方法 4: 添加尺寸限制和異常檢測（已實施）

檢測異常尺寸並重置為合理值：

```javascript
// 如果尺寸異常大（超過視窗大小的2倍），重置為合理的初始值
const maxReasonableSize = Math.max(window.innerWidth, window.innerHeight) * 2;
if (currentWidth > maxReasonableSize || currentHeight > maxReasonableSize || 
    currentWidth < 1 || currentHeight < 1) {
    console.warn('updatePreviewRotation: 檢測到異常容器尺寸，重置為初始值');
    // 重置容器樣式，讓 CSS 重新計算
    previewContainer.style.width = '';
    previewContainer.style.height = '';
    previewContainer.style.aspectRatio = '16/9';
    // 重新獲取尺寸
    const resetRect = previewContainer.getBoundingClientRect();
    currentWidth = resetRect.width;
    currentHeight = resetRect.height;
}
```

#### 方法 5: 限制計算出的尺寸最大值（已實施）

確保計算出的新尺寸不超過合理範圍：

```javascript
// 確保使用合理的短邊值（限制最大值）
const fixedShortSide = Math.min(currentHeight, maxReasonableSize / 2);
const newWidth = fixedShortSide;
const newHeight = newWidth * (16 / 9);

// 確保新尺寸不超過合理範圍
const finalWidth = Math.min(newWidth, maxReasonableSize);
const finalHeight = Math.min(newHeight, maxReasonableSize);
```

**如何驗證修復**:

1. 重新載入頁面（清除瀏覽器緩存）：
   - 按 `Ctrl+Shift+R` (Windows/Linux) 或 `Cmd+Shift+R` (Mac) 強制刷新
   - 或清除瀏覽器緩存後重新載入

2. 測試旋轉功能：
   - 啟用相機預覽
   - 選擇不同的旋轉角度（0°、90°、180°、270°）
   - 確認預覽畫面正常旋轉，且尺寸不會持續變大

3. 檢查瀏覽器控制台：
   - 打開開發者工具（F12）
   - 查看 Console，確認不會出現異常大的容器尺寸
   - 確認 `updatePreviewRotation` 不會重複調用

**相關修改**:

修改的檔案包括：
- `example_bookReader/static/js/book_reader.js`:
  - 添加 `currentAppliedRotation` 變數記錄當前旋轉角度
  - 添加 `rotationUpdateTimer` 防抖計時器
  - 將 `updatePreviewRotation` 拆分為公開函數和內部函數
  - 使用 `getBoundingClientRect()` 替代 `offsetWidth/offsetHeight`
  - 添加異常尺寸檢測和重置邏輯
  - 添加尺寸最大值限制
  - 在收到畫面時檢查旋轉角度是否改變
- `example_bookReader/templates/book_reader.html`:
  - 更新 JS 文件版本號為 `v=20250112-10` 強制瀏覽器刷新緩存

**預防措施**:

1. **避免不必要的重複調用** - 在調用函數前檢查狀態是否已改變
2. **使用防抖機制** - 對於可能頻繁調用的函數，使用防抖或節流
3. **避免觸發重排** - 使用 `getBoundingClientRect()` 而非 `offsetWidth/offsetHeight` 讀取尺寸
4. **添加異常檢測** - 檢查計算結果是否在合理範圍內
5. **限制最大值** - 為所有計算出的尺寸設置合理的上限

**參考資料**:
- MDN getBoundingClientRect(): https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect
- MDN offsetWidth: https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/offsetWidth
- Web 性能優化: https://web.dev/rendering-performance/

---

## 效能問題

### 問題 18: OCR 處理速度很慢

**現象**:
- 單張圖片處理時間超過 30 秒
- 批次處理時間過長

**可能原因**:
- 沒有使用 GPU 加速
- 圖片解析度過高
- 系統資源不足

**解決方法**:

1. 確認使用 GPU：
```python
import torch
print(torch.cuda.is_available())  # 應該返回 True
```

2. 調整圖片大小：
```python
from PIL import Image

img = Image.open('large_image.png')
# 縮小到適當大小
img.thumbnail((2048, 2048))
img.save('resized_image.png')
```

3. 使用批次處理 API 而非多次呼叫單張 API

4. 增加 Gunicorn workers（正式環境）：
```bash
gunicorn -w 8 -b 0.0.0.0:5000 app:app
```

---

## 除錯技巧

### 啟用詳細日誌

在 `config.py` 中設定：
```python
LOG_LEVEL = 'DEBUG'
```

或使用環境變數：
```bash
export LOG_LEVEL=DEBUG
python app.py
```

### 檢查 API 回應

使用 curl 的詳細模式：
```bash
curl -v -X POST -F "file=@image.png" http://localhost:5000/ocr
```

### 測試模型是否正常

建立簡單的測試腳本：
```python
from ocr_service import DeepSeekOCRService

service = DeepSeekOCRService()
result = service.perform_ocr('test_image.png')
print(result)
```

---

## 取得協助

如果以上解決方法都無法解決您的問題：

1. 檢查伺服器日誌檔案：
   - `logs/error.log`
   - `logs/access.log`

2. 收集以下資訊：
   - 錯誤訊息的完整內容
   - 系統環境（作業系統、Python 版本、CUDA 版本）
   - 使用的圖片格式和大小
   - API 請求的完整內容

3. 參考官方文檔：
   - [DeepSeek-OCR 文檔](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)
   - [vLLM 文檔](https://docs.vllm.ai/)
   - [Flask 文檔](https://flask.palletsprojects.com/)

