# DeepSeek-OCR API 服務

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Framework](https://img.shields.io/badge/framework-Flask-lightgrey)
![Model](https://img.shields.io/badge/model-DeepSeek--OCR-orange)

一個基於 **DeepSeek-OCR** 和 **Unsloth** 的高效能 OCR API 服務

[功能特色](#功能特色) • [快速開始](#快速開始) • [文檔](#文檔) • [API 使用](#api-使用) • [常見問題](#常見問題)

</div>

---

## 📖 簡介

DeepSeek-OCR API 是一個基於 Flask 框架開發的 RESTful API 服務，整合了 DeepSeek 公司開發的 **DeepSeek-OCR** 視覺語言模型（3B 參數），並透過 **Unsloth** 框架進行加速推理。本專案提供了簡單易用的 API 介面和友善的 Web UI，讓您可以輕鬆地將圖片轉換為文字。

### 💡 什麼是 DeepSeek-OCR？

DeepSeek-OCR 是一個專為光學字符識別（OCR）和文件理解任務設計的視覺語言模型，採用了創新的 **上下文光學壓縮（Context Optical Compression）** 技術，能夠：

- 🎯 高精度識別文字（印刷體、手寫體）
- 📊 理解複雜的文件結構（表格、圖表）
- 🌏 支援多語言（中文、英文等）
- ⚡ 高效推理（僅 3B 參數）

### 🚀 為什麼選擇 Unsloth？

Unsloth 是一個專為 LLM 和視覺語言模型優化的推理加速框架，提供：

- 💨 **更快的推理速度**（比標準實現快 2-5 倍）
- 💾 **更低的記憶體佔用**（節省 30-60% GPU 記憶體）
- 🔧 **簡單的 API**（無縫替換 Hugging Face Transformers）
- 🎓 **原生支援** DeepSeek-OCR

---

## ✨ 功能特色

### 核心功能

- ✅ **單圖 OCR**：上傳圖片，快速獲取文字結果
- ✅ **批次 OCR**：一次處理多張圖片
- ✅ **自訂提示詞**：客製化 OCR 行為（例如：只提取表格、只識別數字等）
- ✅ **Web UI**：直觀的網頁介面，無需編寫程式碼
- ✅ **RESTful API**：標準化的 API 設計，易於整合

### 技術特點

- 🔥 基於 **Unsloth** 加速推理引擎
- 🎯 支援 **DeepSeek-OCR** 最新模型
- 🐍 **Flask** 輕量級框架，易於部署
- 📦 **模組化設計**，易於維護和擴展
- 🛡️ 完善的錯誤處理和日誌記錄
- 📖 詳盡的文檔和範例

---

## 🚀 快速開始

### 系統需求

- **作業系統**：Linux (推薦 Ubuntu 20.04+)
- **Python**：3.8 或更高版本
- **GPU**：NVIDIA GPU（支援 CUDA）
  - 最小：8GB VRAM（例如 RTX 2080）
  - 推薦：12GB+ VRAM（例如 RTX 3090, A100）
- **CUDA**：11.8 或更高版本
- **磁碟空間**：至少 20GB（用於模型和依賴）

### 快速安裝

#### 1️⃣ 克隆專案

```bash
git clone https://github.com/ch-neural/deepseek-ocr-api
cd deepseek-ocr-api
```

#### 2️⃣ 設定 Hugging Face 認證（必要）

DeepSeek-OCR 模型託管在 Hugging Face Hub，您需要先登入：

```bash
pip install huggingface_hub
huggingface-cli login
```

輸入您的 Hugging Face Token（在 https://huggingface.co/settings/tokens 獲取）

#### 3️⃣ 建立虛擬環境並安裝依賴

```bash
# 建立虛擬環境
python -m venv .venv
source .venv/bin/activate

# 安裝 PyTorch（CUDA 11.8 版本）
pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu118

# 安裝其他依賴
pip install -r requirements.txt
```

#### 4️⃣ 啟動服務

```bash
chmod +x start_server.sh
./start_server.sh
```

腳本會自動：
- ✅ 偵測 Unsloth 是否可用
- ✅ 若 Unsloth 可用，使用加速版本（`app.py`）
- ✅ 若 Unsloth 不可用，使用標準版本（`app_standard.py`）
- ✅ 首次執行時自動下載 DeepSeek-OCR 模型
- ✅ 啟動 Flask 開發伺服器

#### 5️⃣ 存取服務

- **Web UI**：http://localhost:5000
- **API 端點**：http://localhost:5000/ocr

---

## 📚 文檔

我們提供了完整的文檔來幫助您快速上手和深入使用：

### 📖 主要文檔

| 文檔 | 說明 |
|------|------|
| [INSTALL.md](INSTALL.md) | 詳細安裝指南 |
| [docs/DEEPSEEK_OCR_TECHNICAL_GUIDE.md](docs/DEEPSEEK_OCR_TECHNICAL_GUIDE.md) | 深入淺出的技術文件 |
| [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | 快速參考指南 |
| [README/API_DOCUMENTATION.md](README/API_DOCUMENTATION.md) | API 完整文檔 |
| [README/QUICK_START.md](README/QUICK_START.md) | 快速開始指南 |

### 🔧 故障排除

| 文檔 | 說明 |
|------|------|
| [README/ERROR_MESSAGES.md](README/ERROR_MESSAGES.md) | 常見錯誤訊息及解決方法 |
| [README/GPU_SETUP.md](README/GPU_SETUP.md) | GPU 驅動和 CUDA 設定 |
| [README/HUGGINGFACE_AUTH.md](README/HUGGINGFACE_AUTH.md) | Hugging Face 認證問題 |
| [README/MODULE_ERROR.md](README/MODULE_ERROR.md) | 模組匯入錯誤解決 |

---

## 🔌 API 使用

### 健康檢查

```bash
curl http://localhost:5000/health
```

**回應範例**：
```json
{
  "status": "healthy",
  "service": "DeepSeek-OCR API (Standard Transformers)",
  "timestamp": "2025-11-10T15:30:45.123456"
}
```

### 單圖 OCR

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@image.png"
```

**回應範例**：
```json
{
  "text": "這是圖片中的文字內容",
  "image_path": "uploads/20251201_130224_image.png",
  "processing_time": 45.67,
  "gpu_memory": {
    "available": true,
    "total_mb": 24122.19,
    "used_mb": 6490.0,
    "free_mb": 17632.19,
    "usage_percent": 26.9
  }
}
```

### 自訂提示詞

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@invoice.png" \
  -F "prompt=請只提取發票上的金額"
```

### 批次 OCR

```bash
curl -X POST http://localhost:5000/ocr/batch \
  -F "files=@image1.png" \
  -F "files=@image2.png" \
  -F "files=@image3.png"
```

**回應範例**：
```json
{
  "results": [
    {
      "text": "第一張圖片的文字",
      "image_path": "uploads/20251201_130224_0_image1.png",
      "processing_time": 45.67
    },
    {
      "text": "第二張圖片的文字",
      "image_path": "uploads/20251201_130224_1_image2.png",
      "processing_time": 38.21
    },
    {
      "error": "OCR 處理失敗",
      "image_path": "uploads/20251201_130224_2_image3.png"
    }
  ],
  "total": 3
}
```

### Python 範例

```python
import requests

# 單圖 OCR
with open('image.png', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/ocr',
        files={'file': f}
    )
    result = response.json()
    print(result['text'])

# 自訂提示詞
with open('table.png', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/ocr',
        files={'file': f},
        data={'prompt': '請將表格轉換為 Markdown 格式'}
    )
    print(response.json()['text'])
```

詳細的 API 文檔請參考：[README/API_DOCUMENTATION.md](README/API_DOCUMENTATION.md)

---

## 🎯 應用場景

DeepSeek-OCR API 可以應用在多種場景：

- 📄 **文件數位化**：將紙本文件轉換為可編輯的電子檔
- 🧾 **發票處理**：自動提取發票資訊
- 📊 **表格識別**：將圖片中的表格轉換為結構化數據
- 🔍 **圖片搜尋**：為圖片建立可搜尋的文字索引
- 🌐 **多語言翻譯**：先 OCR 再翻譯
- 📱 **移動應用**：為手機 App 提供 OCR 後端服務
- 🤖 **自動化流程**：整合到 RPA 工作流程

---

## ⚙️ 進階配置

### 生產環境部署

使用 Gunicorn 部署到生產環境：

```bash
chmod +x start_production.sh
./start_production.sh
```

預設配置：
- 4 個 worker 程序
- 監聽 0.0.0.0:5000
- 自動記錄日誌

### 環境變數

您可以透過環境變數來配置服務：

```bash
export DEEPSEEK_MODEL_NAME="unsloth/DeepSeek-OCR"
export DEEPSEEK_MODEL_DIR="./deepseek_ocr"
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export MAX_CONTENT_LENGTH="16777216"  # 16MB
```

### 效能調校

修改 `config.py` 或透過環境變數來調整推理參數：

```python
class Config:
    # 上傳檔案大小限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # OCR 設定（可透過環境變數覆蓋）
    OCR_BASE_SIZE = int(os.environ.get('OCR_BASE_SIZE', '1024'))   # 圖片處理基準大小
    OCR_IMAGE_SIZE = int(os.environ.get('OCR_IMAGE_SIZE', '640'))  # 實際推理大小
    OCR_CROP_MODE = True   # 是否啟用裁切模式
    
    # 預設提示詞
    OCR_DEFAULT_PROMPT = "<image>\nFree OCR."
```

**效能模式建議**：

| 模式 | OCR_BASE_SIZE | OCR_IMAGE_SIZE | 處理時間 | 準確度 |
|------|---------------|----------------|----------|--------|
| 快速 | 1024 | 640 | ~10-30 秒 | 中等 |
| 平衡（推薦） | 2048 | 1024 | ~30-60 秒 | 高 |
| 高品質 | 2048 | 1280 | ~60-120 秒 | 極高 |

---

## 🐛 常見問題

### ❓ 模型下載失敗

**問題**：`401 Client Error: Unauthorized`

**解決方法**：
1. 確認已執行 `huggingface-cli login`
2. 檢查 Token 權限
3. 參考 [README/HUGGINGFACE_AUTH.md](README/HUGGINGFACE_AUTH.md)

### ❓ GPU 無法偵測

**問題**：`NotImplementedError: Unsloth cannot find any torch accelerator`

**解決方法**：
1. 安裝 NVIDIA 驅動
2. 安裝 CUDA Toolkit
3. 重新安裝 PyTorch（CUDA 版本）
4. 參考 [README/GPU_SETUP.md](README/GPU_SETUP.md)

### ❓ OCR 結果不正確

**建議**：
- 確保圖片清晰度足夠
- 嘗試使用自訂提示詞引導模型
- 調整 `OCR_BASE_SIZE` 和 `OCR_IMAGE_SIZE`
- 啟用 `OCR_CROP_MODE`（針對大型文件）

更多問題請參考：[README/ERROR_MESSAGES.md](README/ERROR_MESSAGES.md)

---

## 🧪 測試

執行測試腳本：

```bash
python test_api.py
```

測試包含：
- ✅ 健康檢查
- ✅ 單圖 OCR
- ✅ 自訂提示詞
- ✅ 批次 OCR
- ✅ 錯誤處理

---

## 📁 專案結構

```
deepseek-ocr-api/
├── app.py                      # Flask 主應用程式（Unsloth 版本）
├── app_standard.py             # Flask 主應用程式（標準 Transformers 版本）
├── ocr_service.py              # DeepSeek-OCR 服務封裝（Unsloth 版本）
├── ocr_service_standard.py     # DeepSeek-OCR 服務封裝（標準版本）
├── config.py                   # 配置設定
├── requirements.txt            # Python 依賴
├── start_server.sh             # 開發伺服器啟動腳本（自動偵測 Unsloth）
├── start_production.sh         # 生產伺服器啟動腳本
├── test_api.py                 # API 測試腳本
├── INSTALL.md                  # 安裝指南
├── templates/
│   └── index.html              # Web UI 介面
├── docs/                       # 技術文檔
│   ├── DEEPSEEK_OCR_TECHNICAL_GUIDE.md
│   ├── QUICK_REFERENCE.md
│   └── README.md
├── README/                     # 參考文檔
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   ├── ERROR_MESSAGES.md
│   ├── GPU_SETUP.md
│   ├── HUGGINGFACE_AUTH.md
│   ├── MODULE_ERROR.md
│   ├── QUICK_START.md
│   └── UNSLOTH_INSTALL_ISSUE.md
├── uploads/                    # 上傳檔案暫存
├── logs/                       # 應用程式日誌
└── deepseek_ocr/              # DeepSeek-OCR 模型 (自動下載)
```

### 版本說明

| 文件 | 說明 |
|------|------|
| `app.py` + `ocr_service.py` | **Unsloth 版本**：推理速度快（10-30 秒），但需要安裝 Unsloth |
| `app_standard.py` + `ocr_service_standard.py` | **標準版本**：推理較慢（60-120 秒），但穩定性高，無需額外依賴 |

`start_server.sh` 會自動偵測 Unsloth 是否可用，並選擇合適的版本啟動。

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

1. Fork 本專案
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

---

## 📄 授權

本專案採用 MIT 授權。詳見 [LICENSE](LICENSE) 檔案。

---

## 🙏 致謝

- **DeepSeek**：感謝開發 DeepSeek-OCR 模型
- **Unsloth**：感謝提供高效的推理框架
- **Hugging Face**：感謝提供模型託管服務
- **Flask**：感謝提供優秀的 Web 框架

---

## 📧 聯絡方式

如有任何問題或建議，歡迎：

- 📮 提交 [Issue](https://github.com/你的帳號/Deepseek-OCR/issues)
- 💬 發起 [Discussion](https://github.com/你的帳號/Deepseek-OCR/discussions)

---

## 🔗 相關連結

- [DeepSeek-OCR 模型](https://huggingface.co/unsloth/DeepSeek-OCR)
- [Unsloth 官方網站](https://unsloth.ai/)
- [Flask 文檔](https://flask.palletsprojects.com/)
- [Hugging Face Hub](https://huggingface.co/)

---

<div align="center">

**⭐ 如果這個專案對您有幫助，請給我們一個 Star！⭐**

Made with ❤️ by [您的名字]

</div>













