# 快速啟動指南

## 系統需求

- Python 3.10+
- NVIDIA GPU（建議 RTX 3090 或更高，24GB 顯存）
- CUDA 11.8 或 12.1
- 至少 16GB 系統記憶體

---

## 方法一：使用標準版本（推薦）

標準版本不需要 Unsloth，穩定性更高。

### 步驟 1: 建立虛擬環境

```bash
python -m venv ~/envs/DP-OCR
source ~/envs/DP-OCR/bin/activate
```

### 步驟 2: 安裝 PyTorch（根據 CUDA 版本選擇）

```bash
# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 或 CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 步驟 3: 安裝依賴

```bash
# 安裝 transformers（重要：使用特定版本避免 CUDA 錯誤）
pip install transformers==4.56.2

# 安裝其他依賴
pip install Flask Pillow Werkzeug accelerate huggingface_hub
pip install einops timm easydict addict matplotlib opencv-python
```

### 步驟 4: 建立必要目錄

```bash
mkdir -p uploads logs output
```

### 步驟 5: 啟動服務

```bash
python app_standard.py
```

---

## 方法二：使用啟動腳本

```bash
# 智能腳本（自動偵測環境）
./start_server.sh

# 或直接使用標準版本
./start_server_no_unsloth.sh
```

---

## 驗證安裝

啟動服務後，在另一個終端機測試：

```bash
# 健康檢查
curl http://localhost:5000/health

# 或在瀏覽器打開
# http://localhost:5000
```

---

## 測試 OCR

```bash
# 使用測試圖片
curl -X POST -F "file=@10-21-37.png" http://localhost:5000/ocr
```

或使用 Python：

```python
import requests

with open('test_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    result = response.json()
    print(result.get('text', result.get('error')))
```

---

## GPU 記憶體優化

如果遇到 GPU 記憶體不足（OOM）錯誤，可以調整參數：

```bash
# 使用較小的圖片處理參數
export OCR_BASE_SIZE=1024
export OCR_IMAGE_SIZE=640

python app_standard.py
```

或修改 `config.py` 中的預設值。

---

## 常見問題

### Q1: CUDA 錯誤 (device-side assert triggered)

**原因**：transformers 版本過新

**解決**：
```bash
pip install transformers==4.56.2
```

### Q2: Unsloth 無法導入

**原因**：vllm 和 PyTorch 版本不匹配

**解決**：使用標準版本
```bash
python app_standard.py
```

### Q3: GPU 記憶體不足

**解決**：
```bash
export OCR_BASE_SIZE=1024
export OCR_IMAGE_SIZE=640
python app_standard.py
```

### Q4: 多 GPU 導致的設備錯誤

**原因**：模型被分散到多個 GPU

**解決**：程式碼已自動處理，強制使用 cuda:0

---

## 推薦配置

| 項目 | 推薦版本 |
|------|---------|
| Python | 3.10 |
| PyTorch | 2.7.1+cu118 |
| transformers | 4.56.2 |
| CUDA | 11.8 |
| GPU | RTX 3090 (24GB) |

---

**相關文件**：
- `README/UNSLOTH_INSTALL_ISSUE.md` - Unsloth 安裝問題
- `README/MULTI_GPU_DEVICE_FIX.md` - 多 GPU 問題
- `README/GPU_DRIVER_ISSUE.md` - GPU 驅動問題

**最後更新**：2025-11-30
