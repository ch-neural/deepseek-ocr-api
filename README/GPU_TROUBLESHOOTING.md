# GPU 問題排除指南

本文檔整合了所有 GPU 相關的問題和解決方案。

## 目錄

1. [GPU 無法偵測](#1-gpu-無法偵測)
2. [NVIDIA 驅動和 CUDA 安裝](#2-nvidia-驅動和-cuda-安裝)
3. [GPU 記憶體管理](#3-gpu-記憶體管理)
4. [多 GPU 設備問題](#4-多-gpu-設備問題)

---

## 1. GPU 無法偵測

### 錯誤訊息

```
UserWarning: Can't initialize NVML
⚠️  警告: GPU 不可用，將使用 CPU（速度會很慢）
```

或

```
NotImplementedError: Unsloth cannot find any torch accelerator? You need a GPU.
```

### 診斷步驟

```bash
# 1. 檢查 GPU 硬體
lspci | grep -i nvidia

# 2. 檢查驅動是否載入
nvidia-smi

# 3. 檢查 PyTorch CUDA 狀態
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 解決方案

如果 `nvidia-smi` 失敗，請參考下一節安裝驅動。

---

## 2. NVIDIA 驅動和 CUDA 安裝

### 步驟 1：安裝 NVIDIA 驅動

#### Ubuntu 系統（推薦方法）

```bash
# 更新套件清單
sudo apt update

# 安裝驅動工具
sudo apt install ubuntu-drivers-common

# 檢測推薦驅動
ubuntu-drivers devices

# 自動安裝推薦驅動
sudo ubuntu-drivers autoinstall

# 重新啟動
sudo reboot
```

#### 手動安裝特定版本

```bash
# 安裝特定版本驅動（例如 550）
sudo apt install nvidia-driver-550
sudo reboot
```

### 步驟 2：驗證驅動安裝

```bash
nvidia-smi
```

預期輸出：
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 550.xxx    Driver Version: 550.xxx    CUDA Version: 12.x        |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:02:00.0 Off |                  N/A |
| 30%   45C    P8    15W / 350W |      0MiB / 24576MiB |      0%      Default |
+-------------------------------+----------------------+----------------------+
```

### 步驟 3：安裝 PyTorch（CUDA 版本）

```bash
# CUDA 11.8 版本
pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1 版本
pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu121
```

### 步驟 4：驗證 PyTorch CUDA

```bash
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
"
```

---

## 3. GPU 記憶體管理

### DeepSeek-OCR 記憶體使用

| 階段 | 記憶體使用 | 說明 |
|------|-----------|------|
| 模型載入 | ~6-7 GB | 固定佔用 |
| 單次推理 | +2-4 GB | 依圖片大小而定 |
| 推理完成 | 自動釋放 | 回到基礎使用量 |

### 記憶體不足 (OOM) 解決方案

#### 方法 1：調整圖片處理參數

```bash
# 使用較小的參數值
export OCR_BASE_SIZE=1024
export OCR_IMAGE_SIZE=640
```

#### 方法 2：手動清理快取

```python
import torch
torch.cuda.empty_cache()
```

#### 方法 3：使用較小的批次

一次只處理一張圖片，而非批次處理。

### 記憶體監控

```bash
# 即時監控 GPU 記憶體
watch -n 1 nvidia-smi
```

---

## 4. 多 GPU 設備問題

### 錯誤訊息

```
RuntimeError: Expected all tensors to be on the same device, 
but found at least two devices, cuda:1 and cuda:0!
```

### 原因

當使用 `device_map="auto"` 載入模型時，`accelerate` 會將模型分散到多個 GPU，
但 DeepSeek-OCR 模型的推理需要所有 tensor 在同一設備上。

### 解決方案

強制使用單一 GPU（`ocr_service_standard.py` 已自動處理）：

```python
# 正確做法
self.device = "cuda:0"
self.model = AutoModel.from_pretrained(
    model_dir,
    device_map={"": self.device}  # 強制使用 cuda:0
)
```

### 指定特定 GPU

如果有多個 GPU，可以指定使用哪一個：

```bash
# 只使用 GPU 0
export CUDA_VISIBLE_DEVICES=0
python app_standard.py

# 只使用 GPU 1
export CUDA_VISIBLE_DEVICES=1
python app_standard.py
```

---

## 常見問題 FAQ

### Q1：為什麼 GPU 使用率很低？

OCR 任務是「短暫高強度」的，GPU 使用率會在推理時飆升，然後迅速下降。

### Q2：可以用 CPU 運行嗎？

可以，但會非常慢（約 10-20 分鐘一張圖片）。強烈建議使用 GPU。

### Q3：需要多大的 GPU 記憶體？

- 最小：8 GB（可能需要調小參數）
- 推薦：12 GB 以上
- 理想：24 GB（如 RTX 3090）

---

**最後更新**：2025-12-01
