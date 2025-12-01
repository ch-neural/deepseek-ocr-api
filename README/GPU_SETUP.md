# GPU 驅動和 CUDA 安裝指南

## 問題：Unsloth cannot find any torch accelerator? You need a GPU.

### 錯誤訊息

```
NotImplementedError: Unsloth cannot find any torch accelerator? You need a GPU.
```

### 原因分析

系統偵測到 NVIDIA GPU 硬體：
```
NVIDIA Corporation GM200 [GeForce GTX TITAN X]
```

但是：
1. ❌ NVIDIA 驅動程式未安裝
2. ❌ CUDA 未安裝
3. ❌ PyTorch 無法存取 GPU

## 🔧 解決方案：安裝 NVIDIA 驅動和 CUDA

### 步驟 1: 檢查您的 GPU

```bash
lspci | grep -i nvidia
```

輸出應該顯示您的 GPU 型號。

### 步驟 2: 安裝 NVIDIA 驅動

#### 方法 A: 使用 Ubuntu 推薦驅動（推薦）

```bash
# 1. 更新套件清單
sudo apt update

# 2. 安裝 ubuntu-drivers-common
sudo apt install ubuntu-drivers-common

# 3. 檢測推薦的驅動
ubuntu-drivers devices

# 4. 自動安裝推薦的驅動
sudo ubuntu-drivers autoinstall

# 5. 重新啟動系統
sudo reboot
```

#### 方法 B: 手動選擇驅動版本

根據您的 GPU（GTX TITAN X），建議使用以下驅動：

```bash
# 安裝 NVIDIA 驅動 535（穩定版）
sudo apt install nvidia-driver-535

# 重新啟動系統
sudo reboot
```

### 步驟 3: 驗證驅動安裝

重新啟動後，執行：

```bash
nvidia-smi
```

應該看到類似輸出：

```
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx              Driver Version: 535.xx.xx      CUDA Version: 12.2     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce GTX TITAN X   Off   | 00000000:02:00.0  Off |                  N/A |
| 22%   40C    P8              15W / 250W |      0MiB / 12288MiB   |      0%      Default |
+-----------------------------------------+------------------------+----------------------+
```

### 步驟 4: 安裝 CUDA Toolkit（可選但推薦）

```bash
# 安裝 CUDA Toolkit 12.x
sudo apt install nvidia-cuda-toolkit

# 或從 NVIDIA 官方下載
# https://developer.nvidia.com/cuda-downloads
```

### 步驟 5: 重新安裝 PyTorch（正確的 CUDA 版本）

```bash
# 進入您的虛擬環境
source /home/chtseng/envs/DP-OCR/bin/activate

# 解除安裝現有的 PyTorch
pip uninstall torch torchvision torchaudio

# 安裝支援 CUDA 的 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 步驟 6: 驗證 PyTorch GPU 支援

```bash
python -c "import torch; print('CUDA 可用:', torch.cuda.is_available()); print('GPU 數量:', torch.cuda.device_count()); print('GPU 名稱:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

應該輸出：

```
CUDA 可用: True
GPU 數量: 1
GPU 名稱: NVIDIA GeForce GTX TITAN X
```

### 步驟 7: 重新啟動 DeepSeek-OCR 服務

```bash
cd /GPUData/working/Deepseek-OCR
python app.py
```

## ⚡ 快速安裝腳本

將所有步驟合併成一個腳本：

```bash
#!/bin/bash

echo "====================================="
echo "NVIDIA 驅動和 CUDA 安裝腳本"
echo "====================================="

# 1. 更新系統
echo "正在更新系統..."
sudo apt update

# 2. 安裝推薦驅動
echo "正在安裝 NVIDIA 驅動..."
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

# 3. 安裝 CUDA Toolkit
echo "正在安裝 CUDA Toolkit..."
sudo apt install -y nvidia-cuda-toolkit

echo "====================================="
echo "安裝完成！"
echo "請重新啟動系統："
echo "  sudo reboot"
echo ""
echo "重新啟動後，執行以下指令驗證："
echo "  nvidia-smi"
echo "====================================="
```

儲存為 `install_nvidia.sh` 並執行：

```bash
chmod +x install_nvidia.sh
./install_nvidia.sh
```

## 🔍 疑難排解

### 問題 1: 驅動安裝後 nvidia-smi 仍然無法運行

```bash
# 檢查驅動是否載入
lsmod | grep nvidia

# 如果沒有輸出，手動載入驅動
sudo modprobe nvidia

# 檢查錯誤日誌
dmesg | grep -i nvidia
```

### 問題 2: Secure Boot 衝突

如果系統啟用了 Secure Boot，NVIDIA 驅動可能無法載入：

```bash
# 方法 1: 停用 Secure Boot（在 BIOS/UEFI 中）

# 方法 2: 簽署 NVIDIA 模組
sudo apt install mokutil
sudo mokutil --import /var/lib/shim-signed/mok/MOK.der
# 重新啟動並完成 MOK 註冊
```

### 問題 3: 舊驅動殘留

```bash
# 完全移除舊驅動
sudo apt purge nvidia-*
sudo apt autoremove
sudo apt autoclean

# 重新安裝
sudo ubuntu-drivers autoinstall
sudo reboot
```

### 問題 4: PyTorch 仍然偵測不到 CUDA

```bash
# 確認 CUDA 版本
nvcc --version

# 安裝對應版本的 PyTorch
# CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 📋 系統需求總結

### 硬體需求

- ✅ **GPU**: NVIDIA GeForce GTX TITAN X（已偵測到）
- ✅ **VRAM**: 12GB（符合 DeepSeek-OCR 的 8GB 最低需求）
- ✅ **計算能力**: Maxwell 架構（支援 CUDA）

### 軟體需求

- ⚠️ **NVIDIA 驅動**: 需要安裝（版本 >= 535）
- ⚠️ **CUDA**: 需要安裝（版本 >= 11.8）
- ⚠️ **PyTorch**: 需要重新安裝 CUDA 版本
- ✅ **Unsloth**: 已安裝
- ✅ **模型檔案**: 已下載（6.3GB）

## 🎯 預期時間

- **驅動安裝**: 5-10 分鐘
- **系統重新啟動**: 1-2 分鐘
- **驗證**: 1 分鐘
- **PyTorch 重新安裝**: 5-10 分鐘
- **總計**: 約 15-25 分鐘

## ✅ 完成後檢查清單

- [ ] `nvidia-smi` 能正常執行
- [ ] `torch.cuda.is_available()` 返回 True
- [ ] GPU 名稱正確顯示
- [ ] DeepSeek-OCR 服務能成功啟動
- [ ] API 能正確回應 OCR 請求

## 📚 相關資源

- [NVIDIA 驅動下載](https://www.nvidia.com/Download/index.aspx)
- [CUDA Toolkit 下載](https://developer.nvidia.com/cuda-downloads)
- [PyTorch 安裝指南](https://pytorch.org/get-started/locally/)
- [Unsloth 文檔](https://docs.unsloth.ai/)

## 💡 重要提示

1. **必須重新啟動**: 安裝 NVIDIA 驅動後必須重新啟動系統
2. **虛擬環境**: 確保在正確的虛擬環境中重新安裝 PyTorch
3. **CUDA 版本匹配**: PyTorch 版本必須與 CUDA 版本匹配
4. **Secure Boot**: 如果啟用，可能需要停用或簽署驅動模組

## 🆘 需要協助？

如果遇到問題，請收集以下資訊：

```bash
# 系統資訊
uname -a
lsb_release -a

# GPU 資訊
lspci | grep -i nvidia

# 驅動狀態
lsmod | grep nvidia
dmesg | grep -i nvidia | tail -20

# PyTorch 資訊
python -c "import torch; print('PyTorch 版本:', torch.__version__); print('CUDA 可用:', torch.cuda.is_available())"
```

將這些資訊提供給技術支援以獲得協助。

