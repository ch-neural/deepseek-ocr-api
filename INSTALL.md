# DeepSeek-OCR API 快速安裝指南

## 系統需求

- **作業系統**: Linux (Ubuntu 20.04 或以上)
- **Python**: 3.8 或以上
- **GPU**: NVIDIA GPU (至少 8GB VRAM)
- **CUDA**: 11.8 或以上
- **RAM**: 建議至少 16GB
- **儲存空間**: 至少 10GB

## 快速安裝步驟

### 步驟 1: 檢查系統環境

```bash
# 檢查 Python 版本
python --version

# 檢查 CUDA 版本
nvidia-smi

# 檢查磁碟空間
df -h
```

### 步驟 2: 安裝 UV 工具（推薦）

```bash
pip install uv
```

### 步驟 3: 建立虛擬環境並安裝依賴

```bash
# 進入專案目錄
cd /GPUData/working/Deepseek-OCR

# 建立虛擬環境
uv venv

# 啟動虛擬環境
source .venv/bin/activate

# 安裝 vLLM（從 nightly build）
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 安裝其他依賴
pip install Flask Pillow Werkzeug
```

### 步驟 4: 啟動服務

#### 使用啟動腳本（推薦）

```bash
# 給予執行權限（如果還沒有）
chmod +x start_server.sh

# 啟動服務
./start_server.sh
```

#### 手動啟動

```bash
# 確保在虛擬環境中
source .venv/bin/activate

# 啟動 Flask 應用
python app.py
```

### 步驟 5: 訪問服務

- **Web 介面**: 在瀏覽器中打開 `http://localhost:5000`
- **API 端點**: `http://localhost:5000/ocr`
- **健康檢查**: `http://localhost:5000/health`

## 測試服務

### 使用 Web 介面

1. 在瀏覽器打開 `http://localhost:5000`
2. 上傳圖片
3. 點擊「開始辨識」
4. 查看結果

### 使用 API

```bash
# 健康檢查
curl http://localhost:5000/health

# OCR 辨識（替換為您的圖片路徑）
curl -X POST -F "file=@/path/to/image.png" http://localhost:5000/ocr
```

### 使用測試腳本

```bash
# 執行測試腳本
python test_api.py
```

## 正式環境部署

### 使用 Gunicorn（推薦）

```bash
# 安裝 Gunicorn
pip install gunicorn

# 使用正式環境啟動腳本
chmod +x start_production.sh
./start_production.sh
```

### 使用 Systemd 服務

建立服務檔案 `/etc/systemd/system/deepseek-ocr.service`:

```ini
[Unit]
Description=DeepSeek-OCR API Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/GPUData/working/Deepseek-OCR
Environment="PATH=/GPUData/working/Deepseek-OCR/.venv/bin"
ExecStart=/GPUData/working/Deepseek-OCR/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 300 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務:

```bash
sudo systemctl daemon-reload
sudo systemctl enable deepseek-ocr
sudo systemctl start deepseek-ocr
sudo systemctl status deepseek-ocr
```

## 常見問題排除

### 問題 1: vLLM 安裝失敗

**解決方法**:
```bash
# 確認使用正確的安裝來源
pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly
```

### 問題 2: CUDA 版本不符

**解決方法**:
```bash
# 檢查 CUDA 版本
nvidia-smi

# 如果版本低於 11.8，需要升級 CUDA
# 參考 NVIDIA 官方文檔
```

### 問題 3: GPU 記憶體不足

**解決方法**:
- 確保沒有其他程式佔用 GPU
- 關閉不必要的 GPU 程式
- 考慮升級 GPU（至少需要 8GB VRAM）

### 問題 4: Port 5000 已被佔用

**解決方法**:
```bash
# 查找佔用 Port 的程式
lsof -i :5000

# 關閉該程式或使用其他 Port
# 修改 app.py 中的 port 參數
```

### 問題 5: 模型下載過慢

**解決方法**:
```bash
# 設定 Hugging Face 鏡像（中國地區）
export HF_ENDPOINT=https://hf-mirror.com

# 然後重新啟動服務
python app.py
```

## 更新服務

```bash
# 進入專案目錄
cd /GPUData/working/Deepseek-OCR

# 啟動虛擬環境
source .venv/bin/activate

# 更新 vLLM
uv pip install -U vllm --pre --extra-index-url https://wheels.vllm.ai/nightly

# 更新其他套件
pip install --upgrade Flask Pillow Werkzeug

# 重新啟動服務
./start_server.sh
```

## 卸載服務

```bash
# 停止服務
# 如果使用 systemd
sudo systemctl stop deepseek-ocr
sudo systemctl disable deepseek-ocr

# 刪除虛擬環境
rm -rf .venv

# 刪除暫存檔案
rm -rf uploads/* logs/*
```

## 取得協助

如果遇到問題，請查看：

- [README 文檔](README/README.md)
- [錯誤訊息說明](README/ERROR_MESSAGES.md)
- [API 詳細文檔](README/API_DOCUMENTATION.md)

或參考官方文檔：
- [DeepSeek-OCR 官方文檔](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)

