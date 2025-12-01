# NVIDIA GPU 驅動問題排除指南

## 問題描述

啟動 DeepSeek-OCR 時出現以下警告或錯誤：

```
UserWarning: Can't initialize NVML
⚠️  警告: GPU 不可用，將使用 CPU（速度會很慢）
```

或 Unsloth 報錯：

```
NotImplementedError: Unsloth cannot find any torch accelerator? You need a GPU.
```

---

## 診斷步驟

### 1. 檢查 GPU 硬體

```bash
# 使用 lspci 檢查是否有 NVIDIA 顯示卡
lspci | grep -i nvidia
```

預期輸出（有 GPU）：
```
02:00.0 VGA compatible controller: NVIDIA Corporation GM200 [GeForce GTX TITAN X]
```

### 2. 檢查驅動是否載入

```bash
# 檢查 nvidia 設備
ls -la /dev/nvidia*

# 檢查驅動版本
cat /proc/driver/nvidia/version

# 使用 nvidia-smi
nvidia-smi
```

如果這些命令都失敗，表示 **驅動未載入**。

### 3. 檢查 PyTorch CUDA 狀態

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

---

## 解決方案

### 方案 1：載入現有驅動

如果驅動已安裝但未載入：

```bash
# 嘗試載入 nvidia 模組
sudo modprobe nvidia
sudo modprobe nvidia-uvm

# 驗證
nvidia-smi
```

### 方案 2：安裝 NVIDIA 驅動

如果驅動未安裝：

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nvidia-driver-535  # 或其他版本

# 重新啟動
sudo reboot
```

### 方案 3：使用 NVIDIA Container Toolkit（Docker 環境）

如果在 Docker 容器中：

```bash
# 確保主機已安裝 nvidia-container-toolkit
sudo apt install nvidia-container-toolkit

# 重新啟動 Docker
sudo systemctl restart docker

# 使用 --gpus 參數啟動容器
docker run --gpus all ...
```

### 方案 4：遠端主機特殊情況

如果在遠端主機（如 SSH）上遇到問題：

1. **檢查是否有 GPU 訪問權限**
   ```bash
   groups  # 確認用戶在 video/render 群組中
   ```

2. **確認驅動已在主機上載入**
   - 聯繫系統管理員確認 GPU 驅動狀態
   - 可能需要重新啟動主機載入驅動

3. **如果使用 slurm/PBS 作業系統**
   ```bash
   # 可能需要申請 GPU 資源
   srun --gres=gpu:1 --pty bash
   ```

---

## 暫時解決方案（無 GPU 時使用 CPU）

如果無法修復 GPU 問題，可以使用 CPU 運行（會很慢）：

```bash
# 使用標準版本
./start_server_no_unsloth.sh

# 或直接執行
source /home/chtseng/envs/DEEPSEEK-OCR/bin/activate
python app_standard.py
```

**注意**：CPU 模式下，OCR 處理可能需要數分鐘，不建議用於生產環境。

---

## 驗證修復

修復後，運行以下命令驗證：

```bash
# 1. 檢查 nvidia-smi
nvidia-smi

# 2. 檢查 PyTorch CUDA
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

# 3. 啟動服務
./start_server.sh
```

預期輸出：
```
✅ GPU 可用: NVIDIA GeForce GTX TITAN X (12.0 GB)
```

---

## 相關文件

- `UNSLOTH_INSTALL_ISSUE.md` - Unsloth 安裝問題
- `GPU_SETUP.md` - GPU 設定指南
- `GPU_MEMORY_MANAGEMENT.md` - GPU 記憶體管理

---

**最後更新**：2025-11-30

