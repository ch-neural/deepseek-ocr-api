# DeepSeek-OCR API 使用說明

## 專案簡介

這是一個基於 Flask 框架開發的 DeepSeek-OCR API 服務，提供強大的圖片文字辨識（OCR）功能。DeepSeek-OCR 是一個 3B 參數的視覺模型，專門用於 OCR 和文件理解，能夠處理表格、論文和手寫文字，達到 97% 的精確度。

## 主要特點

- ✨ **高精確度**: 使用 DeepSeek-OCR 3B 模型，達到 97% 辨識精確度
- 🚀 **高效率**: 視覺 token 使用量是文字 token 的 1/10，效率提升 10 倍
- 📄 **多格式支援**: 支援 PNG、JPG、JPEG、GIF、BMP、WEBP 等常見圖片格式
- 🔄 **批次處理**: 支援單張和批次圖片 OCR 辨識
- 🎯 **自訂提示詞**: 可以自訂提示詞以適應不同的 OCR 需求
- 🛡️ **錯誤處理**: 完整的錯誤處理和訊息提示

## 系統需求

### 硬體需求

- GPU: 建議使用 NVIDIA GPU（至少 8GB VRAM）
- RAM: 建議至少 16GB
- 儲存空間: 至少 10GB（用於模型和暫存檔案）

### 軟體需求

- Python 3.8 或以上版本
- CUDA 11.8 或以上版本（用於 GPU 加速）
- Linux 作業系統（建議使用 Ubuntu 20.04 或以上版本）

## 安裝步驟

### 1. 克隆專案

```bash
cd /GPUData/working/Deepseek-OCR
```

### 2. 安裝依賴套件

#### 使用 UV 工具（推薦）

```bash
# 安裝 UV 工具
pip install uv

# 建立虛擬環境
uv venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝 vLLM（從 nightly build）
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 安裝其他依賴
pip install Flask Pillow Werkzeug
```

#### 使用傳統 pip

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝 vLLM（從 nightly build）
pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 安裝其他依賴
pip install Flask Pillow Werkzeug
```

### 3. 下載模型

模型會在第一次啟動服務時自動下載，或者您可以手動預先下載：

```bash
python -c "from huggingface_hub import snapshot_download; snapshot_download('unsloth/DeepSeek-OCR', local_dir='models/deepseek_ocr')"
```

## 使用方式

### 啟動服務

#### 開發模式

```bash
# 使用提供的啟動腳本
chmod +x start_server.sh
./start_server.sh

# 或直接執行
python app.py
```

#### 正式環境

```bash
# 使用 Gunicorn（推薦用於正式環境）
chmod +x start_production.sh
./start_production.sh
```

服務將在 `http://0.0.0.0:5000` 上運行。

### API 端點

#### 1. 健康檢查

**端點**: `GET /health`

**說明**: 檢查服務是否正常運行

**回應範例**:

```json
{
  "status": "healthy",
  "service": "DeepSeek-OCR API",
  "timestamp": "2025-11-10T12:00:00.000000"
}
```

#### 2. 單張圖片 OCR

**端點**: `POST /ocr`

**說明**: 對單張圖片執行 OCR 辨識

**請求參數**:
- `file` (必填): 圖片檔案（multipart/form-data）
- `prompt` (選填): 自訂提示詞，預設為 `<image>\nFree OCR.`

**回應範例**:

```json
{
  "text": "辨識出的文字內容...",
  "image_path": "uploads/20251110_120000_image.png",
  "prompt": "<image>\nFree OCR."
}
```

**使用範例**:

```bash
# 基本使用
curl -X POST -F "file=@/path/to/image.png" http://localhost:5000/ocr

# 使用自訂提示詞
curl -X POST -F "file=@/path/to/image.png" -F "prompt=<image>\n請辨識圖片中的所有文字" http://localhost:5000/ocr
```

**Python 範例**:

```python
import requests

# 基本使用
with open('image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    result = response.json()
    print(result['text'])

# 使用自訂提示詞
with open('image.png', 'rb') as f:
    files = {'file': f}
    data = {'prompt': '<image>\n請辨識圖片中的所有中文文字'}
    response = requests.post('http://localhost:5000/ocr', files=files, data=data)
    result = response.json()
    print(result['text'])
```

#### 3. 批次圖片 OCR

**端點**: `POST /ocr/batch`

**說明**: 對多張圖片執行批次 OCR 辨識

**請求參數**:
- `files` (必填): 多個圖片檔案（multipart/form-data）
- `prompt` (選填): 自訂提示詞

**回應範例**:

```json
{
  "results": [
    {
      "text": "第一張圖片的文字...",
      "image_path": "uploads/20251110_120000_0_image1.png",
      "prompt": "<image>\nFree OCR."
    },
    {
      "text": "第二張圖片的文字...",
      "image_path": "uploads/20251110_120000_1_image2.png",
      "prompt": "<image>\nFree OCR."
    }
  ],
  "total": 2
}
```

**使用範例**:

```bash
# 批次處理多張圖片
curl -X POST \
  -F "files=@/path/to/image1.png" \
  -F "files=@/path/to/image2.png" \
  -F "files=@/path/to/image3.png" \
  http://localhost:5000/ocr/batch
```

**Python 範例**:

```python
import requests

# 批次處理
files = [
    ('files', open('image1.png', 'rb')),
    ('files', open('image2.png', 'rb')),
    ('files', open('image3.png', 'rb'))
]

response = requests.post('http://localhost:5000/ocr/batch', files=files)

# 關閉所有檔案
for _, f in files:
    f.close()

result = response.json()
print(f"處理了 {result['total']} 張圖片")

for idx, item in enumerate(result['results']):
    print(f"\n圖片 {idx + 1}: {item['text']}")
```

## 測試

專案包含了完整的測試腳本 `test_api.py`，您可以使用它來測試 API 功能：

```bash
# 確保服務已啟動
python test_api.py
```

## 配置說明

### 環境變數

您可以通過環境變數來配置服務：

- `SECRET_KEY`: Flask 密鑰（預設: 'deepseek-ocr-secret-key-2024'）
- `DEEPSEEK_MODEL_NAME`: DeepSeek-OCR 模型名稱（預設: 'unsloth/DeepSeek-OCR'）
- `LOG_LEVEL`: 日誌級別（預設: 'INFO'）

### DeepSeek 建議參數

根據 DeepSeek 官方建議，系統使用以下參數：

- `temperature`: 0.0（確定性輸出）
- `max_tokens`: 8192（最大輸出長度）
- `ngram_size`: 30（N-gram 大小）
- `window_size`: 90（窗口大小）

## 專案結構

```
Deepseek-OCR/
├── app.py                      # Flask 主應用程式
├── ocr_service.py              # OCR 服務類別
├── config.py                   # 配置檔案
├── requirements.txt            # Python 依賴套件
├── start_server.sh             # 開發模式啟動腳本
├── start_production.sh         # 正式環境啟動腳本
├── test_api.py                 # API 測試腳本
├── uploads/                    # 暫存上傳檔案目錄
├── logs/                       # 日誌檔案目錄
└── README/                     # 文檔目錄
    ├── README.md              # 使用說明（本檔案）
    ├── ERROR_MESSAGES.md      # 錯誤訊息說明
    └── API_DOCUMENTATION.md   # API 詳細文檔
```

## 注意事項

1. **模型大小**: DeepSeek-OCR 模型約 3GB，第一次啟動會需要時間下載
2. **GPU 記憶體**: 確保有足夠的 GPU 記憶體來載入模型
3. **暫存檔案**: 上傳的圖片會暫存在 `uploads/` 目錄，處理完成後會自動刪除
4. **檔案大小限制**: 預設限制上傳檔案大小為 16MB
5. **支援格式**: 僅支援常見的圖片格式（PNG、JPG、JPEG、GIF、BMP、WEBP）

## 效能優化建議

1. **批次處理**: 對於多張圖片，使用批次 API 可以獲得更好的效能
2. **圖片大小**: 適當調整圖片大小可以加快處理速度
3. **GPU 加速**: 確保使用 GPU 來運行模型以獲得最佳效能
4. **並行處理**: 正式環境建議使用 Gunicorn 的多 worker 模式

## 常見問題

請參閱 [錯誤訊息說明](ERROR_MESSAGES.md) 文檔。

## 版本資訊

- **版本**: 1.0.0
- **發布日期**: 2025-11-10
- **DeepSeek-OCR 模型**: unsloth/DeepSeek-OCR
- **vLLM 版本**: nightly build

## 授權

本專案使用 MIT 授權。

## 參考資料

- [DeepSeek-OCR 官方文檔](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)
- [vLLM 官方網站](https://vllm.ai/)
- [Flask 官方文檔](https://flask.palletsprojects.com/)

