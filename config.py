"""
DeepSeek-OCR API 配置檔案
"""

import os


class Config:
    """基礎配置類別"""
    
    # Flask 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'deepseek-ocr-secret-key-2024'
    
    # 檔案上傳配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    
    # DeepSeek-OCR 模型配置
    MODEL_NAME = os.environ.get('DEEPSEEK_MODEL_NAME') or 'unsloth/DeepSeek-OCR'
    
    # OCR 參數配置（根據 DeepSeek 官方建議）
    OCR_TEMPERATURE = 0.0
    OCR_MAX_TOKENS = 8192
    OCR_NGRAM_SIZE = 30
    OCR_WINDOW_SIZE = 90
    OCR_DEFAULT_PROMPT = "<image>\nFree OCR."
    
    # ==================== OCR 圖片處理參數 ====================
    # 這些參數控制 DeepSeek-VL2 模型如何處理輸入圖片
    # 較大的值可以提高辨識準確度，但會增加處理時間和記憶體使用
    
    # base_size: 圖片預處理的基準尺寸（像素）
    # - 圖片會先被縮放到此尺寸（保持長寬比）
    # - 建議值範圍：1024-2048
    # - 1024: 適合 1280x720 或更小的圖片（處理速度快，約 10 秒）
    # - 2048: 適合 1920x1080 或更大的圖片（處理較慢，約 20-30 秒）
    # - 影響：值越大，文字越清晰，但處理時間越長，GPU 記憶體使用越多
    # - 注意：RTX 3090 (24GB) 使用 2048 可能導致 OOM，建議使用 1024
    OCR_BASE_SIZE = int(os.environ.get('OCR_BASE_SIZE', '1024'))
    
    # image_size: 模型輸入的圖片尺寸（像素）
    # - 經過 base_size 處理後，圖片會進一步處理為此尺寸
    # - 建議值範圍：640-1024
    # - 640: 適合小圖片或快速處理（可能降低準確度）
    # - 1024: 適合高解析度圖片（推薦設定，平衡準確度與速度）
    # - 影響：值越大，模型能看到更多細節，OCR 更準確
    # - 注意：較大的值需要更多 GPU 記憶體
    OCR_IMAGE_SIZE = int(os.environ.get('OCR_IMAGE_SIZE', '640'))
    
    # crop_mode: 是否啟用裁切模式
    # - True: 將圖片裁切為多個區塊分別處理（適合大圖或多欄文字）
    # - False: 將整張圖片作為一個區塊處理（適合單欄或小圖）
    # - 建議：True（預設），大多數情況下效果更好
    OCR_CROP_MODE = os.environ.get('OCR_CROP_MODE', 'true').lower() == 'true'
    
    # test_compress: 是否測試壓縮（用於調試）
    # - True: 測試不同壓縮率的效果（用於開發和調試）
    # - False: 不測試壓縮（正常使用，推薦）
    # - 建議：False（預設）
    OCR_TEST_COMPRESS = os.environ.get('OCR_TEST_COMPRESS', 'false').lower() == 'true'
    
    # save_results: 是否保存 OCR 結果到檔案
    # - True: 保存結果到 output 目錄
    # - False: 不保存（節省磁碟空間）
    # - 建議：False（預設）
    OCR_SAVE_RESULTS = os.environ.get('OCR_SAVE_RESULTS', 'false').lower() == 'true'
    
    # ==================== 效能建議 ====================
    # 根據不同的使用場景，推薦以下設定組合：
    #
    # 【快速模式】（適合即時處理、小圖片）
    #   OCR_BASE_SIZE = 1024
    #   OCR_IMAGE_SIZE = 640
    #   處理時間: ~10 秒
    #   準確度: 中等
    #   適用: 1280x720 或更小的圖片
    #
    # 【平衡模式】（推薦，適合大多數情況）
    #   OCR_BASE_SIZE = 2048
    #   OCR_IMAGE_SIZE = 1024
    #   處理時間: ~20-30 秒
    #   準確度: 高
    #   適用: 1920x1080 或更大的圖片
    #
    # 【高品質模式】（適合專業用途、需要最高準確度）
    #   OCR_BASE_SIZE = 2048
    #   OCR_IMAGE_SIZE = 1280
    #   處理時間: ~40-60 秒
    #   準確度: 極高
    #   適用: 2K 或 4K 圖片
    #   注意: 需要更多 GPU 記憶體（建議 12GB 以上）
    # ====================================================
    
    # 日誌配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = 'deepseek_ocr.log'


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """正式環境配置"""
    DEBUG = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

