# DeepSeek-OCR 快速參考指南

## 📚 快速鏈接

- [完整技術文件](DEEPSEEK_OCR_TECHNICAL_GUIDE.md)
- [API 文檔](../README/API_DOCUMENTATION.md)
- [錯誤訊息說明](../README/ERROR_MESSAGES.md)
- [安裝指南](../INSTALL.md)

---

## ⚡ 5 分鐘快速開始

### 1. 安裝依賴

```bash
pip install unsloth transformers Flask Pillow
```

### 2. 下載模型

```bash
git clone https://huggingface.co/unsloth/DeepSeek-OCR ./deepseek_ocr
```

### 3. 啟動服務

```bash
python app.py
```

### 4. 測試 API

```bash
curl -X POST -F "file=@image.png" http://localhost:5000/ocr
```

---

## 🔑 核心概念速查

### DeepSeek-OCR 特點

| 特性 | 數值 |
|------|------|
| 模型大小 | 3B 參數 |
| 準確率 | 97% |
| 效率提升 | 10x |
| Token 壓縮 | 10:1 |

### 系統需求

- **最低**: GTX 1080 Ti (8GB VRAM)
- **推薦**: RTX 3090 (24GB VRAM)
- **CUDA**: 11.8+
- **RAM**: 16GB+

---

## 📖 API 速查表

### 健康檢查

```bash
curl http://localhost:5000/health
```

### 單張 OCR

```bash
curl -X POST -F "file=@image.png" http://localhost:5000/ocr
```

### 批次 OCR

```bash
curl -X POST \
  -F "files=@img1.png" \
  -F "files=@img2.png" \
  http://localhost:5000/ocr/batch
```

### 自訂提示詞

```bash
curl -X POST \
  -F "file=@table.png" \
  -F "prompt=<image>\n請提取表格數據" \
  http://localhost:5000/ocr
```

---

## 🐍 Python 代碼片段

### 基本使用

```python
import requests

with open('image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    result = response.json()
    print(result['text'])
```

### 批次處理

```python
files = [
    ('files', open('page1.png', 'rb')),
    ('files', open('page2.png', 'rb'))
]
response = requests.post('http://localhost:5000/ocr/batch', files=files)
```

---

## 🛠️ 常用命令

### 環境管理

```bash
# 創建虛擬環境
python -m venv .venv

# 啟動環境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 服務管理

```bash
# 開發模式
python app.py

# 生產模式
./start_production.sh

# 後台運行
nohup python app.py > logs/app.log 2>&1 &
```

### 驗證安裝

```bash
# 檢查 GPU
nvidia-smi

# 檢查 PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# 檢查 Unsloth
python -c "import unsloth; print(unsloth.__version__)"
```

---

## 🔍 疑難排解

### 常見錯誤

| 錯誤 | 解決方法 |
|------|----------|
| CUDA out of memory | 使用 `load_in_4bit=True` |
| Model not found | 檢查 `./deepseek_ocr` 目錄 |
| Port already in use | 修改 `app.py` 中的 port |
| Trust remote code | 設定環境變數 `TRANSFORMERS_TRUST_REMOTE_CODE=1` |

### 性能優化

```python
# 降低記憶體使用
load_in_4bit=True  # 降低 75%

# 批次大小調整
BATCH_SIZE = 4     # 根據 GPU 調整

# 圖片預處理
image_size = 640   # 降低解析度
```

---

## 📊 效能基準

### 推理速度

| GPU | 速度 (it/s) | 記憶體 (GB) |
|-----|-------------|-------------|
| RTX 3090 | 2.1 | 16.8 |
| A100 | 3.5 | 14.2 |
| RTX 4090 | 2.8 | 15.6 |

### 準確度

| 類型 | 準確率 |
|------|--------|
| 印刷文字 | 97% |
| 手寫文字 | 92% |
| 表格 | 95% |

---

## 🌟 應用場景

### 文檔處理
```python
# 批次數字化文檔
digitizer.digitize_document("scanned_docs", "output")
```

### 發票處理
```python
# 自動提取發票資訊
invoice_data = processor.process_invoice("invoice.png")
```

### 表格提取
```python
# 轉換表格為 Excel
df = extractor.extract_table("table.png")
```

---

## 📞 取得協助

- **完整文檔**: [技術指南](DEEPSEEK_OCR_TECHNICAL_GUIDE.md)
- **API 文檔**: [API 說明](../README/API_DOCUMENTATION.md)
- **錯誤排查**: [錯誤訊息](../README/ERROR_MESSAGES.md)

---

**快速參考版本**: 1.0.0  
**更新日期**: 2025-11-10

