# 📁 檔案清單

本文件列出 DeepSeek-OCR API 專案的完整檔案結構和說明。

## 📊 專案結構

```
Deepseek-OCR/
│
├── 📄 核心程式檔案
│   ├── app.py                      # Flask 主應用程式（API 路由、請求處理）
│   ├── ocr_service.py              # DeepSeek-OCR 服務封裝（模型載入、推理）
│   └── config.py                   # 應用程式配置設定
│
├── ⚙️ 配置與部署
│   ├── requirements.txt            # Python 依賴套件清單
│   ├── start_server.sh             # 開發伺服器啟動腳本
│   ├── start_production.sh         # 生產伺服器啟動腳本（Gunicorn）
│   └── .gitignore                  # Git 忽略檔案清單
│
├── 🧪 測試
│   └── test_api.py                 # API 功能測試腳本
│
├── 🌐 網頁介面
│   └── templates/
│       └── index.html              # Web UI 使用者介面
│
├── 📚 文檔（主要）
│   ├── README.md                   # 專案主要說明文件（您正在看的）
│   ├── INSTALL.md                  # 快速安裝指南
│   ├── LICENSE                     # MIT 開源授權
│   ├── CONTRIBUTING.md             # 貢獻指南
│   └── FILE_LIST.md                # 本檔案（檔案清單）
│
├── 📖 文檔（參考手冊）
│   └── README/
│       ├── README.md               # README 目錄索引
│       ├── API_DOCUMENTATION.md    # API 完整參考文件
│       ├── QUICK_START.md          # 快速開始指南
│       ├── ERROR_MESSAGES.md       # 常見錯誤及解決方法
│       ├── GPU_SETUP.md            # GPU 驅動和 CUDA 設定指南
│       ├── HUGGINGFACE_AUTH.md     # Hugging Face 認證設定
│       └── MODULE_ERROR.md         # Python 模組錯誤排除
│
├── 📘 文檔（深入技術）
│   └── docs/
│       ├── README.md               # 技術文檔索引
│       ├── DEEPSEEK_OCR_TECHNICAL_GUIDE.md  # 深入技術指南（2000+ 行）
│       └── QUICK_REFERENCE.md      # 快速參考手冊
│
├── 🤖 模型檔案（自動下載）
│   └── deepseek_ocr/
│       └── .gitkeep                # 模型下載說明（實際模型約 6GB）
│
├── 📂 資料目錄
│   ├── uploads/                    # 上傳檔案暫存目錄
│   │   └── .gitkeep
│   └── logs/                       # 應用程式日誌目錄
│       └── .gitkeep
│
└── 🔧 其他
    └── unsloth_compiled_cache/     # Unsloth 編譯快取（自動生成）
```

## 📄 檔案詳細說明

### 核心程式檔案

#### `app.py`
- **用途**：Flask Web 應用程式主檔案
- **功能**：
  - 定義 API 路由（`/health`, `/ocr`, `/ocr/batch`）
  - 處理檔案上傳
  - 錯誤處理和日誌記錄
  - 提供 Web UI
- **程式碼行數**：約 200 行

#### `ocr_service.py`
- **用途**：DeepSeek-OCR 服務封裝
- **功能**：
  - 模型下載和載入
  - OCR 推理執行
  - 結果解析和處理
  - stdout 重導向（擷取模型輸出）
- **程式碼行數**：約 150 行

#### `config.py`
- **用途**：應用程式配置管理
- **功能**：
  - 定義配置參數（上傳大小、OCR 設定等）
  - 環境變數讀取
  - 目錄路徑設定
- **程式碼行數**：約 50 行

### 配置與部署檔案

#### `requirements.txt`
- **用途**：Python 依賴套件清單
- **主要套件**：
  - `flask`：Web 框架
  - `unsloth`：模型推理加速
  - `transformers`：模型載入
  - `torch`：深度學習框架
  - `pillow`：圖片處理
  - `gunicorn`：生產伺服器

#### `start_server.sh`
- **用途**：開發環境一鍵啟動腳本
- **功能**：
  - 建立/啟用虛擬環境
  - 安裝依賴套件
  - 下載模型（如果不存在）
  - 啟動 Flask 開發伺服器

#### `start_production.sh`
- **用途**：生產環境部署腳本
- **功能**：
  - 使用 Gunicorn 啟動（4 workers）
  - 綁定到 0.0.0.0:5000
  - 日誌記錄

#### `.gitignore`
- **用途**：Git 版本控制忽略清單
- **排除**：
  - Python 快取（`__pycache__/`, `*.pyc`）
  - 虛擬環境（`venv/`）
  - 模型檔案（`deepseek_ocr/`）
  - 日誌和上傳檔案
  - IDE 設定檔

### 測試檔案

#### `test_api.py`
- **用途**：API 功能測試
- **測試項目**：
  - 健康檢查 API
  - 單圖 OCR
  - 自訂提示詞
  - 批次 OCR
  - 錯誤處理

### 網頁介面

#### `templates/index.html`
- **用途**：Web UI 使用者介面
- **功能**：
  - 檔案上傳拖放
  - 自訂提示詞輸入
  - OCR 結果顯示
  - 批次處理介面
- **程式碼行數**：約 500 行（包含 CSS 和 JavaScript）

### 文檔檔案

#### 主要文檔

| 檔案 | 行數 | 用途 |
|------|------|------|
| `README.md` | ~600 | 專案主要說明文件 |
| `INSTALL.md` | ~200 | 快速安裝指南 |
| `LICENSE` | ~21 | MIT 開源授權 |
| `CONTRIBUTING.md` | ~300 | 貢獻指南 |
| `FILE_LIST.md` | ~300 | 本檔案 |

#### 參考手冊（README/）

| 檔案 | 行數 | 用途 |
|------|------|------|
| `API_DOCUMENTATION.md` | ~500 | API 完整參考 |
| `QUICK_START.md` | ~300 | 快速開始 |
| `ERROR_MESSAGES.md` | ~600 | 錯誤排除 |
| `GPU_SETUP.md` | ~400 | GPU 設定 |
| `HUGGINGFACE_AUTH.md` | ~200 | HF 認證 |
| `MODULE_ERROR.md` | ~300 | 模組錯誤 |

#### 技術文檔（docs/）

| 檔案 | 行數 | 用途 |
|------|------|------|
| `DEEPSEEK_OCR_TECHNICAL_GUIDE.md` | ~2161 | 深入技術指南 |
| `QUICK_REFERENCE.md` | ~243 | 快速參考 |
| `README.md` | ~100 | 文檔索引 |

## 📊 統計資訊

### 程式碼統計

- **Python 程式碼**：約 400 行
- **HTML/CSS/JavaScript**：約 500 行
- **Shell 腳本**：約 150 行
- **總計**：約 1050 行程式碼

### 文檔統計

- **Markdown 文檔**：約 6000 行
- **檔案數量**：20+ 個 Markdown 檔案
- **總大小**：約 500KB

### 模型統計

- **模型大小**：約 6GB（不包含在 Git）
- **模型格式**：SafeTensors
- **參數量**：3B（30 億參數）

## 🎯 文檔閱讀建議

### 新手使用者

1. 📖 先閱讀 `README.md`（主要說明）
2. 🚀 參考 `INSTALL.md`（安裝系統）
3. 🎯 查看 `README/QUICK_START.md`（快速開始）
4. 🔌 學習 `README/API_DOCUMENTATION.md`（API 使用）

### 進階使用者

1. 📘 閱讀 `docs/DEEPSEEK_OCR_TECHNICAL_GUIDE.md`（深入技術）
2. 📋 參考 `docs/QUICK_REFERENCE.md`（快速查詢）
3. 🐛 遇到問題查看 `README/ERROR_MESSAGES.md`

### 開發者

1. 🤝 先讀 `CONTRIBUTING.md`（貢獻指南）
2. 📁 了解 `FILE_LIST.md`（本檔案）
3. 🔍 研究原始碼（`app.py`, `ocr_service.py`）

## 🔍 快速查找

### 遇到錯誤？

- 模組匯入錯誤 → `README/MODULE_ERROR.md`
- GPU 相關問題 → `README/GPU_SETUP.md`
- 認證失敗 → `README/HUGGINGFACE_AUTH.md`
- 其他錯誤 → `README/ERROR_MESSAGES.md`

### 想了解功能？

- API 如何使用 → `README/API_DOCUMENTATION.md`
- 快速開始 → `README/QUICK_START.md`
- 深入原理 → `docs/DEEPSEEK_OCR_TECHNICAL_GUIDE.md`

### 想要貢獻？

- 如何貢獻 → `CONTRIBUTING.md`
- 程式碼在哪 → `app.py`, `ocr_service.py`
- 測試如何寫 → `test_api.py`

## 📝 維護資訊

### 自動生成的檔案（請勿手動修改）

- `deepseek_ocr/`：模型檔案（自動下載）
- `unsloth_compiled_cache/`：編譯快取（自動生成）
- `__pycache__/`：Python 快取（自動生成）
- `logs/*.log`：日誌檔案（自動記錄）
- `uploads/*`：上傳檔案（臨時）

### 需要手動維護的檔案

- 所有 `.md` 文檔檔案
- 所有 `.py` 程式檔案
- `requirements.txt`
- `.gitignore`

## 🔄 更新紀錄

- **2025-11-10**：初始版本，包含完整的程式碼和文檔

---

如有任何問題或建議，歡迎提交 Issue！













