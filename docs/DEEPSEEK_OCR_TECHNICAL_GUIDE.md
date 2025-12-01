# DeepSeek-OCR 技術文件：深入淺出指南

**版本**: 1.0.0  
**更新日期**: 2025-11-10  
**作者**: DeepSeek-OCR API Team

---

## 目錄

1. [DeepSeek-OCR 介紹](#1-deepseek-ocr-介紹)
2. [Unsloth 與 DeepSeek-OCR](#2-unsloth-與-deepseek-ocr)
3. [系統安裝與環境設定](#3-系統安裝與環境設定)
4. [API 使用指南與應用領域](#4-api-使用指南與應用領域)
5. [進階主題](#5-進階主題)
6. [常見問題](#6-常見問題)

---

## 1. DeepSeek-OCR 介紹

### 1.1 開發背景

**DeepSeek-OCR** 是由 **DeepSeek AI** 開發的專業級光學字符識別（OCR）模型，於 2025 年發布。DeepSeek AI 是一家專注於大型語言模型和視覺語言模型研究的人工智慧公司，其開發的 DeepSeek 系列模型在多個領域都展現出卓越性能。

### 1.2 核心特點

#### 🎯 技術規格

- **模型大小**: 3B 參數（30億參數）
- **模型架構**: Vision-Language Model (VLM)
- **基礎架構**: DeepSeek V2 架構
- **視覺編碼器**: 自定義的視覺 Transformer
- **語言模型**: DeepSeek-V2 語言骨幹網路
- **訓練數據**: 大規模多語言文檔數據集

#### ⚡ 性能優勢

1. **高精確度**: 達到 97% 的字符識別精確度
2. **高效率**: 視覺 token 使用量僅為文字 token 的 1/10
3. **效能提升**: 比純文字 LLM 快 10 倍
4. **低資源**: 3B 參數模型在保持高性能的同時降低計算需求

#### 🌟 關鍵創新

##### Context Optical Compression（上下文光學壓縮）

DeepSeek-OCR 的核心創新是 **Context Optical Compression** 技術：

```
傳統 OCR 流程:
圖像 → 特徵提取 → 字符識別 → 文字輸出

DeepSeek-OCR 流程:
圖像 → 2D 佈局保持 → 視覺 Token 壓縮 → 上下文理解 → 文字輸出
```

**工作原理**:
1. 將 2D 圖像佈局轉換為視覺 tokens
2. 保持文檔的空間關係和結構信息
3. 通過壓縮算法減少 token 數量
4. 結合語言模型進行上下文理解

這種方法使得模型能夠：
- 理解表格結構
- 保持段落格式
- 識別手寫文字
- 處理多欄位佈局

### 1.3 功能特性

#### 📄 支援的文檔類型

1. **印刷文檔**
   - 書籍、雜誌
   - 報紙、論文
   - 商業文件

2. **手寫文檔**
   - 手寫筆記
   - 簽名
   - 手繪圖表

3. **結構化文檔**
   - 表格數據
   - 發票、收據
   - 表單

4. **複雜佈局**
   - 多欄位文檔
   - 混合圖文
   - 技術圖表

#### 🌍 語言支援

- **中文**: 簡體中文、繁體中文
- **英文**: 美式英語、英式英語
- **日文**: 平假名、片假名、漢字
- **韓文**: 諺文
- **其他**: 法文、德文、西班牙文等

### 1.4 使用技術

#### 模型架構層

```
DeepSeek-OCR 架構:

輸入圖像 (H×W×3)
    ↓
┌─────────────────────┐
│  Vision Encoder     │  ← 視覺編碼器
│  - ViT-based        │  
│  - Patch Embedding  │
└─────────────────────┘
    ↓
視覺 Tokens (N×D)
    ↓
┌─────────────────────┐
│ Optical Compression │  ← 光學壓縮層
│  - Context Aware    │
│  - 10× Reduction    │
└─────────────────────┘
    ↓
壓縮 Tokens (N/10×D)
    ↓
┌─────────────────────┐
│ Language Backbone   │  ← 語言模型
│  - DeepSeek-V2      │
│  - Causal LM        │
└─────────────────────┘
    ↓
文字輸出
```

#### 深度學習框架

- **PyTorch**: 2.0+
- **Transformers**: 4.57.1
- **CUDA**: 11.8+ / 12.x
- **Flash Attention**: 支援加速推理
- **BFloat16**: 混合精度訓練

#### 最佳化技術

1. **模型量化**
   - 支援 4-bit 量化 (降低 75% 記憶體)
   - 支援 8-bit 量化 (降低 50% 記憶體)
   - LoRA 微調

2. **推理加速**
   - Xformers 優化
   - Flash Attention 2
   - KV Cache 優化

3. **記憶體優化**
   - Gradient Checkpointing
   - CPU Offloading
   - 模型並行

### 1.5 開發目的與願景

#### 主要目標

1. **文檔數字化**: 加速紙質文檔轉換為數字格式
2. **無障礙訪問**: 協助視覺障礙人士閱讀文檔
3. **跨語言理解**: 實現多語言文檔的自動翻譯與理解
4. **知識提取**: 從大量文檔中快速提取關鍵資訊

#### 應用願景

DeepSeek-OCR 旨在成為：
- 企業文檔管理的基礎設施
- 教育領域的輔助工具
- 歷史文獻數字化的利器
- AI 應用的視覺理解引擎

---

## 2. Unsloth 與 DeepSeek-OCR

### 2.1 Unsloth 簡介

**Unsloth** 是由 Unsloth AI 開發的深度學習優化框架，專門用於加速大型語言模型（LLM）和視覺語言模型（VLM）的訓練與推理。

#### 核心優勢

- **速度提升**: 2-5x 更快的訓練速度
- **記憶體優化**: 40-70% 更少的記憶體使用
- **易用性**: 與 Hugging Face Transformers 完美整合
- **成本效益**: 降低 GPU 成本，支援更長的上下文

### 2.2 Unsloth 支援 DeepSeek-OCR 的原理

#### 2.2.1 模型封裝與優化

Unsloth 為 DeepSeek-OCR 提供了專門的封裝類 `FastVisionModel`：

```python
from unsloth import FastVisionModel

# Unsloth 封裝的 DeepSeek-OCR
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/DeepSeek-OCR",
    load_in_4bit=False,
    trust_remote_code=True,
)
```

**封裝優勢**:

1. **自動優化**: 自動應用各種優化技術
2. **統一接口**: 提供一致的 API
3. **記憶體管理**: 智能管理 GPU 記憶體
4. **錯誤處理**: 完善的錯誤檢測與處理

#### 2.2.2 Kernel 層級優化

Unsloth 在 CUDA kernel 層級進行了深度優化：

```
標準 PyTorch 流程:
Python API → PyTorch C++ → CUDA Kernels → GPU

Unsloth 優化流程:
Python API → Unsloth Optimized Kernels → GPU
              ↑
         (跳過中間層，直接優化)
```

**優化技術**:

1. **Fused Kernels**: 融合多個操作為單一 kernel
   ```
   標準: Attention → Add → LayerNorm (3 個 kernel)
   Unsloth: FusedAttentionNorm (1 個 kernel)
   ```

2. **Memory Access Pattern 優化**
   - 減少全局記憶體訪問
   - 最大化共享記憶體使用
   - 優化記憶體對齊

3. **Flash Attention 整合**
   ```python
   # Unsloth 自動啟用 Flash Attention
   # O(N²) → O(N) 記憶體複雜度
   ```

#### 2.2.3 視覺模型特定優化

DeepSeek-OCR 作為視覺語言模型，Unsloth 提供了特殊優化：

##### Image Preprocessing 加速

```python
# 標準方式
image = Image.open("document.png")
inputs = processor(images=image, return_tensors="pt")

# Unsloth 優化
# 自動應用：
# - GPU 加速的圖像變換
# - 批次處理優化
# - 記憶體池管理
```

##### Vision Encoder 優化

```python
class OptimizedVisionEncoder:
    def __init__(self):
        # Patch Embedding 優化
        self.patch_embed = FusedPatchEmbedding()
        
        # Attention 層優化
        self.attention_layers = [
            FlashAttention() for _ in range(num_layers)
        ]
        
        # Compression 層優化
        self.compression = OptimizedCompression()
```

### 2.3 Unsloth 的優化方法

#### 2.3.1 自動混合精度 (AMP)

Unsloth 智能管理混合精度計算：

```python
# 自動選擇最佳精度
FP32: 高精度計算（如 LayerNorm）
BF16: 主要計算（如 Attention）
FP16: 快速計算（如 Activation）
INT8: 推理優化（可選）
```

**BFloat16 優勢**:
- 與 FP32 相同的動態範圍
- 訓練穩定性更好
- RTX 30/40 系列原生支援

#### 2.3.2 Gradient Checkpointing 增強

```python
# 標準 Gradient Checkpointing
model.gradient_checkpointing_enable()
# 記憶體: ↓50%, 速度: ↓30%

# Unsloth Gradient Checkpointing
use_gradient_checkpointing = "unsloth"
# 記憶體: ↓50%, 速度: ↓10% (優化後)
```

**優化原理**:
- 選擇性重計算（只重計算昂貴的層）
- 智能 checkpoint 點選擇
- 並行化重計算

#### 2.3.3 LoRA (Low-Rank Adaptation) 優化

Unsloth 對 LoRA 微調提供特別優化：

```python
from unsloth import FastVisionModel

# 自動應用 LoRA
model = FastVisionModel.from_pretrained(
    "unsloth/DeepSeek-OCR",
    load_in_4bit=True,  # 4-bit 量化
)

# Unsloth 自動優化的 LoRA
model = FastVisionModel.get_peft_model(
    model,
    r=16,              # LoRA rank
    lora_alpha=16,
    target_modules=[   # 自動選擇最佳目標模組
        "q_proj", "k_proj", "v_proj",
        "o_proj", "gate_proj", "up_proj"
    ],
)
```

**LoRA 優化效果**:
- 訓練參數: ↓99% (只訓練 1% 的參數)
- 記憶體: ↓70%
- 速度: ↑2x
- 準確度: 保持 > 95%

### 2.4 性能對比

#### 推理性能

| 方法 | 速度 (it/s) | 記憶體 (GB) | Token/s |
|------|-------------|-------------|---------|
| 標準 Transformers | 1.0 | 24.0 | 15 |
| + Flash Attention | 1.4 | 24.0 | 21 |
| + Unsloth | **2.1** | **16.8** | **32** |

#### 訓練性能

| 方法 | 訓練時間 | 記憶體 | 準確度 |
|------|----------|--------|--------|
| 標準全量微調 | 100 小時 | 48 GB | 100% |
| LoRA | 24 小時 | 16 GB | 98% |
| Unsloth LoRA | **17 小時** | **10 GB** | **98%** |

### 2.5 Unsloth 技術架構

```
Unsloth 架構層次:

┌──────────────────────────────────────┐
│         User Application             │
│    (DeepSeek-OCR Flask API)          │
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│      Unsloth Python API              │
│  - FastVisionModel                   │
│  - FastLanguageModel                 │
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│    Unsloth Optimization Layer        │
│  - Kernel Fusion                     │
│  - Memory Management                 │
│  - Precision Control                 │
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│     Transformers Integration         │
│  - Model Loading                     │
│  - Tokenization                      │
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│       PyTorch Backend                │
│  - CUDA Operations                   │
│  - Tensor Operations                 │
└──────────────────────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│           GPU Hardware               │
│  (NVIDIA RTX 3090, A100, etc.)       │
└──────────────────────────────────────┘
```

---

## 3. 系統安裝與環境設定

### 3.1 系統需求

#### 硬體需求

##### 最低配置
- **GPU**: NVIDIA GPU (8GB VRAM)
  - GTX 1080 Ti
  - RTX 2080
  - Tesla P40
- **RAM**: 16GB 系統記憶體
- **儲存**: 20GB 可用空間
- **CPU**: 4 核心以上

##### 推薦配置
- **GPU**: NVIDIA GPU (16GB+ VRAM)
  - RTX 3090 (24GB)
  - RTX 4090 (24GB)
  - A100 (40GB/80GB)
- **RAM**: 32GB+ 系統記憶體
- **儲存**: 50GB+ SSD
- **CPU**: 8 核心以上

##### 支援的 GPU 架構
- **Ampere**: RTX 30 系列, A100
- **Ada Lovelace**: RTX 40 系列
- **Turing**: RTX 20 系列
- **Pascal**: GTX 10 系列 (有限支援)

#### 軟體需求

- **作業系統**: Linux (Ubuntu 20.04/22.04/24.04 推薦)
- **Python**: 3.8, 3.9, 3.10, 3.11
- **CUDA**: 11.8, 12.1, 12.2, 12.8
- **NVIDIA Driver**: 驅動版本 >= 525

### 3.2 環境安裝步驟

#### 步驟 1: 系統準備

```bash
# 更新系統套件
sudo apt update && sudo apt upgrade -y

# 安裝基礎工具
sudo apt install -y build-essential git wget curl

# 安裝 Python 開發套件
sudo apt install -y python3-dev python3-pip python3-venv
```

#### 步驟 2: 安裝 NVIDIA 驅動和 CUDA

##### 方法 A: 使用 Ubuntu 套件管理器（推薦）

```bash
# 安裝 NVIDIA 驅動工具
sudo apt install ubuntu-drivers-common

# 自動安裝推薦驅動
sudo ubuntu-drivers autoinstall

# 重新啟動
sudo reboot
```

重啟後驗證：

```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 應該看到類似輸出：
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.2   |
# +-----------------------------------------------------------------------------+
```

##### 方法 B: 手動安裝特定版本

```bash
# 安裝 NVIDIA 驅動 535
sudo apt install -y nvidia-driver-535

# 安裝 CUDA Toolkit
sudo apt install -y nvidia-cuda-toolkit

# 重新啟動
sudo reboot
```

#### 步驟 3: 創建 Python 虛擬環境

```bash
# 進入專案目錄
cd /GPUData/working/Deepseek-OCR

# 創建虛擬環境
python3 -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate

# 升級 pip
pip install --upgrade pip setuptools wheel
```

#### 步驟 4: 安裝 PyTorch (CUDA 版本)

```bash
# For CUDA 12.1 (推薦)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 驗證安裝
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

預期輸出：
```
PyTorch: 2.8.0+cu121
CUDA: True
```

#### 步驟 5: 安裝 Unsloth

```bash
# 安裝 Unsloth
pip install --upgrade unsloth

# 或強制重新安裝
pip install --upgrade --force-reinstall --no-deps --no-cache-dir unsloth unsloth_zoo
```

#### 步驟 6: 安裝其他依賴

```bash
# 安裝 Flask 和相關套件
pip install Flask Pillow Werkzeug

# 安裝 Transformers 和 HuggingFace 套件
pip install transformers accelerate huggingface_hub

# 安裝額外工具
pip install datasets peft bitsandbytes
```

#### 步驟 7: 下載 DeepSeek-OCR 模型

```bash
# 方法 1: 使用 Git LFS (推薦)
git lfs install
git clone https://huggingface.co/unsloth/DeepSeek-OCR ./deepseek_ocr

# 方法 2: 使用 Python
python -c "from huggingface_hub import snapshot_download; snapshot_download('unsloth/DeepSeek-OCR', local_dir='./deepseek_ocr')"
```

模型大小：約 6.3 GB

#### 步驟 8: 驗證安裝

創建測試腳本 `verify_installation.py`:

```python
#!/usr/bin/env python
"""驗證 DeepSeek-OCR 環境安裝"""

import sys

def check_cuda():
    """檢查 CUDA"""
    import torch
    print("=" * 60)
    print("CUDA 檢查")
    print("=" * 60)
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA 版本: {torch.version.cuda}")
        print(f"GPU 數量: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
            print(f"  記憶體: {torch.cuda.get_device_properties(i).total_memory / 1e9:.2f} GB")
    return torch.cuda.is_available()

def check_unsloth():
    """檢查 Unsloth"""
    print("\n" + "=" * 60)
    print("Unsloth 檢查")
    print("=" * 60)
    try:
        import unsloth
        print(f"✅ Unsloth 已安裝")
        print(f"版本: {unsloth.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Unsloth 未安裝: {e}")
        return False

def check_transformers():
    """檢查 Transformers"""
    print("\n" + "=" * 60)
    print("Transformers 檢查")
    print("=" * 60)
    try:
        import transformers
        print(f"✅ Transformers 已安裝")
        print(f"版本: {transformers.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Transformers 未安裝: {e}")
        return False

def check_model():
    """檢查模型檔案"""
    print("\n" + "=" * 60)
    print("模型檔案檢查")
    print("=" * 60)
    import os
    model_path = "./deepseek_ocr"
    if os.path.exists(model_path):
        print(f"✅ 模型目錄存在: {model_path}")
        # 檢查關鍵檔案
        files = ["config.json", "model-00001-of-000001.safetensors"]
        for f in files:
            file_path = os.path.join(model_path, f)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path) / 1e9
                print(f"  ✅ {f}: {size:.2f} GB")
            else:
                print(f"  ❌ {f}: 不存在")
                return False
        return True
    else:
        print(f"❌ 模型目錄不存在: {model_path}")
        return False

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("DeepSeek-OCR 環境驗證")
    print("=" * 60 + "\n")
    
    checks = {
        "CUDA": check_cuda(),
        "Unsloth": check_unsloth(),
        "Transformers": check_transformers(),
        "Model": check_model(),
    }
    
    print("\n" + "=" * 60)
    print("驗證結果")
    print("=" * 60)
    
    all_passed = True
    for name, passed in checks.items():
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{name:15s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 所有檢查通過！系統已準備就緒。")
        return 0
    else:
        print("⚠️  部分檢查失敗，請檢查上述錯誤訊息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

執行驗證：

```bash
python verify_installation.py
```

### 3.3 環境配置

#### 配置文件

創建 `.env` 檔案進行環境配置：

```bash
# .env - 環境變數配置

# Flask 配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# 模型配置
MODEL_NAME=unsloth/DeepSeek-OCR
MODEL_DIR=./deepseek_ocr
LOAD_IN_4BIT=False

# Unsloth 配置
UNSLOTH_WARN_UNINITIALIZED=0
HF_HUB_OFFLINE=1
TRANSFORMERS_TRUST_REMOTE_CODE=1

# OCR 參數
OCR_BASE_SIZE=1024
OCR_IMAGE_SIZE=640
OCR_CROP_MODE=True

# 檔案配置
MAX_UPLOAD_SIZE=16777216  # 16MB
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,bmp,webp
```

#### 系統服務配置（Systemd）

創建系統服務 `/etc/systemd/system/deepseek-ocr.service`:

```ini
[Unit]
Description=DeepSeek-OCR API Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/GPUData/working/Deepseek-OCR
Environment="PATH=/GPUData/working/Deepseek-OCR/.venv/bin"
EnvironmentFile=/GPUData/working/Deepseek-OCR/.env
ExecStart=/GPUData/working/Deepseek-OCR/.venv/bin/python app.py
Restart=always
RestartSec=10

# 資源限制
MemoryLimit=32G
CPUQuota=400%

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟用服務
sudo systemctl enable deepseek-ocr

# 啟動服務
sudo systemctl start deepseek-ocr

# 檢查狀態
sudo systemctl status deepseek-ocr

# 查看日誌
sudo journalctl -u deepseek-ocr -f
```

### 3.4 疑難排解

#### 問題 1: GPU 偵測失敗

```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 如果失敗，重新安裝驅動
sudo apt purge nvidia-*
sudo apt autoremove
sudo ubuntu-drivers autoinstall
sudo reboot
```

#### 問題 2: CUDA 版本不匹配

```bash
# 檢查 CUDA 版本
nvcc --version

# 安裝對應的 PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu<version>
```

#### 問題 3: 記憶體不足

```python
# 使用 4-bit 量化
model = FastVisionModel.from_pretrained(
    model_dir,
    load_in_4bit=True,  # 降低記憶體使用
)
```

---

## 4. API 使用指南與應用領域

### 4.1 快速開始

#### 4.1.1 啟動服務

```bash
# 進入專案目錄
cd /GPUData/working/Deepseek-OCR

# 啟動虛擬環境
source .venv/bin/activate

# 啟動服務
python app.py
```

服務將在 `http://0.0.0.0:5000` 上運行。

#### 4.1.2 第一個 API 請求

```bash
# 健康檢查
curl http://localhost:5000/health

# OCR 辨識
curl -X POST \
  -F "file=@document.png" \
  http://localhost:5000/ocr
```

### 4.2 API 端點詳解

#### 4.2.1 健康檢查 API

**端點**: `GET /health`

**用途**: 檢查服務是否正常運行

**請求範例**:
```bash
curl http://localhost:5000/health
```

**回應範例**:
```json
{
  "status": "healthy",
  "service": "DeepSeek-OCR API",
  "timestamp": "2025-11-10T15:30:00.123456"
}
```

#### 4.2.2 單張圖片 OCR API

**端點**: `POST /ocr`

**用途**: 對單張圖片執行 OCR 辨識

**請求參數**:
- `file` (必填): 圖片檔案
- `prompt` (選填): 自訂提示詞

**請求範例**:
```bash
# 基本使用
curl -X POST \
  -F "file=@invoice.png" \
  http://localhost:5000/ocr

# 使用自訂提示詞
curl -X POST \
  -F "file=@table.png" \
  -F "prompt=<image>\n請提取這個表格的所有數據，保持格式。" \
  http://localhost:5000/ocr
```

**回應範例**:
```json
{
  "text": "發票\n公司名稱：XXX有限公司\n統一編號：12345678\n...",
  "image_path": "uploads/20251110_153000_invoice.png",
  "prompt": "<image>\nFree OCR."
}
```

**錯誤回應**:
```json
{
  "error": "不支援的檔案類型。允許的類型: png, jpg, jpeg, gif, bmp, webp"
}
```

#### 4.2.3 批次圖片 OCR API

**端點**: `POST /ocr/batch`

**用途**: 對多張圖片執行批次 OCR 辨識

**請求參數**:
- `files` (必填): 多個圖片檔案
- `prompt` (選填): 自訂提示詞（應用於所有圖片）

**請求範例**:
```bash
curl -X POST \
  -F "files=@page1.png" \
  -F "files=@page2.png" \
  -F "files=@page3.png" \
  http://localhost:5000/ocr/batch
```

**回應範例**:
```json
{
  "results": [
    {
      "text": "第一頁內容...",
      "image_path": "uploads/20251110_153000_0_page1.png",
      "prompt": "<image>\nFree OCR."
    },
    {
      "text": "第二頁內容...",
      "image_path": "uploads/20251110_153000_1_page2.png",
      "prompt": "<image>\nFree OCR."
    }
  ],
  "total": 2
}
```

### 4.3 編程語言範例

#### 4.3.1 Python 範例

##### 基本使用

```python
import requests

def ocr_image(image_path, host="http://localhost:5000"):
    """執行 OCR 辨識"""
    url = f"{host}/ocr"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        return result['text']
    else:
        error = response.json()
        raise Exception(f"OCR 失敗: {error.get('error')}")

# 使用範例
text = ocr_image("document.png")
print(text)
```

##### 批次處理

```python
import requests
from pathlib import Path

def batch_ocr(image_paths, host="http://localhost:5000"):
    """批次 OCR 辨識"""
    url = f"{host}/ocr/batch"
    
    files = []
    for path in image_paths:
        files.append(('files', open(path, 'rb')))
    
    try:
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()['results']
        else:
            raise Exception(f"批次 OCR 失敗: {response.json().get('error')}")
    finally:
        # 關閉所有檔案
        for _, f in files:
            f.close()

# 批次處理目錄中的所有圖片
image_dir = Path("documents")
image_files = list(image_dir.glob("*.png"))

results = batch_ocr(image_files)
for i, result in enumerate(results):
    print(f"文件 {i+1}:\n{result['text']}\n")
```

##### 完整的類別封裝

```python
import requests
from typing import List, Dict, Optional
from pathlib import Path

class DeepSeekOCRClient:
    """DeepSeek-OCR API 客戶端"""
    
    def __init__(self, host: str = "http://localhost:5000"):
        self.host = host
        self.session = requests.Session()
    
    def health_check(self) -> bool:
        """檢查服務健康狀態"""
        try:
            response = self.session.get(f"{self.host}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    def ocr(
        self, 
        image_path: str, 
        prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """單張圖片 OCR"""
        url = f"{self.host}/ocr"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'prompt': prompt} if prompt else {}
            
            response = self.session.post(url, files=files, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OCR 失敗: {response.json().get('error')}")
    
    def batch_ocr(
        self, 
        image_paths: List[str], 
        prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """批次圖片 OCR"""
        url = f"{self.host}/ocr/batch"
        
        files = [('files', open(path, 'rb')) for path in image_paths]
        data = {'prompt': prompt} if prompt else {}
        
        try:
            response = self.session.post(url, files=files, data=data)
            
            if response.status_code == 200:
                return response.json()['results']
            else:
                raise Exception(f"批次 OCR 失敗: {response.json().get('error')}")
        finally:
            for _, f in files:
                f.close()
    
    def ocr_directory(
        self, 
        directory: str, 
        pattern: str = "*.png",
        prompt: Optional[str] = None
    ) -> Dict[str, str]:
        """處理目錄中的所有圖片"""
        dir_path = Path(directory)
        image_files = sorted(dir_path.glob(pattern))
        
        if not image_files:
            raise ValueError(f"目錄 {directory} 中沒有找到匹配 {pattern} 的檔案")
        
        results = self.batch_ocr([str(f) for f in image_files], prompt)
        
        # 建立檔案名到結果的映射
        return {
            image_files[i].name: results[i]['text']
            for i in range(len(results))
        }

# 使用範例
if __name__ == "__main__":
    client = DeepSeekOCRClient()
    
    # 健康檢查
    if not client.health_check():
        print("服務未運行！")
        exit(1)
    
    # 單張圖片
    result = client.ocr("document.png")
    print(f"OCR 結果:\n{result['text']}\n")
    
    # 批次處理
    results = client.batch_ocr([
        "page1.png", 
        "page2.png", 
        "page3.png"
    ])
    
    for i, result in enumerate(results, 1):
        print(f"頁面 {i}:\n{result['text']}\n")
    
    # 處理整個目錄
    dir_results = client.ocr_directory("documents", "*.jpg")
    for filename, text in dir_results.items():
        print(f"{filename}:\n{text}\n")
```

#### 4.3.2 JavaScript/TypeScript 範例

##### Node.js 範例

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

class DeepSeekOCRClient {
    constructor(host = 'http://localhost:5000') {
        this.host = host;
    }

    async healthCheck() {
        try {
            const response = await axios.get(`${this.host}/health`);
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    async ocr(imagePath, prompt = null) {
        const form = new FormData();
        form.append('file', fs.createReadStream(imagePath));
        if (prompt) {
            form.append('prompt', prompt);
        }

        const response = await axios.post(
            `${this.host}/ocr`,
            form,
            { headers: form.getHeaders() }
        );

        return response.data;
    }

    async batchOcr(imagePaths, prompt = null) {
        const form = new FormData();
        
        imagePaths.forEach(path => {
            form.append('files', fs.createReadStream(path));
        });
        
        if (prompt) {
            form.append('prompt', prompt);
        }

        const response = await axios.post(
            `${this.host}/ocr/batch`,
            form,
            { headers: form.getHeaders() }
        );

        return response.data.results;
    }
}

// 使用範例
async function main() {
    const client = new DeepSeekOCRClient();

    // 健康檢查
    if (!await client.healthCheck()) {
        console.log('服務未運行！');
        return;
    }

    // 單張圖片
    const result = await client.ocr('document.png');
    console.log('OCR 結果:');
    console.log(result.text);

    // 批次處理
    const results = await client.batchOcr([
        'page1.png',
        'page2.png',
        'page3.png'
    ]);

    results.forEach((result, index) => {
        console.log(`\n頁面 ${index + 1}:`);
        console.log(result.text);
    });
}

main().catch(console.error);
```

##### 瀏覽器範例 (React)

```typescript
import React, { useState } from 'react';
import axios from 'axios';

interface OCRResult {
    text: string;
    image_path: string;
    prompt: string;
}

const OCRComponent: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    const API_HOST = 'http://localhost:5000';

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError('');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (!file) {
            setError('請選擇圖片檔案');
            return;
        }

        setLoading(true);
        setError('');
        setResult('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post<OCRResult>(
                `${API_HOST}/ocr`,
                formData,
                {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                }
            );

            setResult(response.data.text);
        } catch (err: any) {
            setError(
                err.response?.data?.error || 
                'OCR 辨識失敗，請重試'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="ocr-container">
            <h2>DeepSeek-OCR 文字辨識</h2>
            
            <form onSubmit={handleSubmit}>
                <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    disabled={loading}
                />
                
                <button 
                    type="submit" 
                    disabled={!file || loading}
                >
                    {loading ? '辨識中...' : '開始辨識'}
                </button>
            </form>

            {error && (
                <div className="error">
                    錯誤: {error}
                </div>
            )}

            {result && (
                <div className="result">
                    <h3>辨識結果:</h3>
                    <pre>{result}</pre>
                </div>
            )}
        </div>
    );
};

export default OCRComponent;
```

#### 4.3.3 其他語言範例

##### cURL (Shell 腳本)

```bash
#!/bin/bash
# ocr.sh - DeepSeek-OCR Shell 腳本

API_HOST="http://localhost:5000"

# 健康檢查
health_check() {
    echo "檢查服務健康狀態..."
    curl -s "${API_HOST}/health" | jq '.'
}

# 單張圖片 OCR
ocr_single() {
    local image_file="$1"
    local prompt="$2"
    
    echo "辨識圖片: ${image_file}"
    
    if [ -z "$prompt" ]; then
        curl -X POST \
            -F "file=@${image_file}" \
            "${API_HOST}/ocr" | jq -r '.text'
    else
        curl -X POST \
            -F "file=@${image_file}" \
            -F "prompt=${prompt}" \
            "${API_HOST}/ocr" | jq -r '.text'
    fi
}

# 批次 OCR
ocr_batch() {
    local files=("$@")
    local curl_args=()
    
    echo "批次辨識 ${#files[@]} 張圖片..."
    
    for file in "${files[@]}"; do
        curl_args+=(-F "files=@${file}")
    done
    
    curl -X POST \
        "${curl_args[@]}" \
        "${API_HOST}/ocr/batch" | jq '.results[].text'
}

# 主函數
main() {
    case "$1" in
        health)
            health_check
            ;;
        single)
            ocr_single "$2" "$3"
            ;;
        batch)
            shift
            ocr_batch "$@"
            ;;
        *)
            echo "用法:"
            echo "  $0 health                    - 健康檢查"
            echo "  $0 single <圖片>             - 單張 OCR"
            echo "  $0 single <圖片> <提示詞>    - 單張 OCR (自訂提示)"
            echo "  $0 batch <圖片1> <圖片2> ... - 批次 OCR"
            exit 1
            ;;
    esac
}

main "$@"
```

使用範例:
```bash
chmod +x ocr.sh

# 健康檢查
./ocr.sh health

# 單張 OCR
./ocr.sh single document.png

# 批次 OCR
./ocr.sh batch page1.png page2.png page3.png
```

### 4.4 應用領域與實際案例

#### 4.4.1 文檔數字化

##### 應用場景
- 歷史文獻數字化
- 圖書館檔案管理
- 企業文檔管理
- 紙質合約電子化

##### 實施方案

```python
"""文檔數字化系統"""
import os
from pathlib import Path
from deepseek_ocr_client import DeepSeekOCRClient

class DocumentDigitizer:
    """文檔數字化工具"""
    
    def __init__(self, ocr_host="http://localhost:5000"):
        self.client = DeepSeekOCRClient(ocr_host)
    
    def digitize_document(
        self, 
        input_dir: str, 
        output_dir: str,
        file_pattern: str = "*.jpg"
    ):
        """數字化整個文檔目錄"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 獲取所有圖片檔案
        image_files = sorted(input_path.glob(file_pattern))
        
        print(f"找到 {len(image_files)} 個圖片檔案")
        
        # 批次處理
        batch_size = 10
        all_results = []
        
        for i in range(0, len(image_files), batch_size):
            batch = image_files[i:i+batch_size]
            print(f"處理批次 {i//batch_size + 1}/{(len(image_files)-1)//batch_size + 1}")
            
            results = self.client.batch_ocr([str(f) for f in batch])
            all_results.extend(zip(batch, results))
        
        # 儲存結果
        for image_file, result in all_results:
            # 建立對應的文字檔
            txt_file = output_path / f"{image_file.stem}.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            print(f"已處理: {image_file.name} -> {txt_file.name}")
        
        # 合併所有文字為單一檔案
        merged_file = output_path / "merged_document.txt"
        with open(merged_file, 'w', encoding='utf-8') as f:
            for _, result in all_results:
                f.write(result['text'])
                f.write("\n\n" + "="*80 + "\n\n")
        
        print(f"\n完成！共處理 {len(all_results)} 個檔案")
        print(f"合併檔案: {merged_file}")

# 使用範例
digitizer = DocumentDigitizer()
digitizer.digitize_document(
    input_dir="scanned_documents",
    output_dir="digitized_output",
    file_pattern="*.png"
)
```

##### ROI 分析
- **效率提升**: 比人工輸入快 100-200 倍
- **成本節省**: 降低 80% 數據輸入成本
- **準確度**: 97% 準確率，減少人為錯誤
- **可搜尋性**: 所有文檔變為可搜尋的數字格式

#### 4.4.2 發票與收據處理

##### 應用場景
- 財務報銷系統
- 電子商務訂單管理
- 會計自動化
- 費用追蹤

##### 實施方案

```python
"""發票處理系統"""
import re
from datetime import datetime
from typing import Dict, List

class InvoiceProcessor:
    """發票處理器"""
    
    def __init__(self, ocr_host="http://localhost:5000"):
        self.client = DeepSeekOCRClient(ocr_host)
    
    def process_invoice(self, image_path: str) -> Dict:
        """處理單張發票"""
        # 使用專門的提示詞
        prompt = """<image>
請提取這張發票的以下資訊：
- 發票號碼
- 日期
- 公司名稱
- 統一編號
- 項目明細
- 總金額
"""
        
        result = self.client.ocr(image_path, prompt)
        text = result['text']
        
        # 解析發票資訊
        invoice_data = {
            'raw_text': text,
            'invoice_number': self._extract_invoice_number(text),
            'date': self._extract_date(text),
            'company_name': self._extract_company(text),
            'tax_id': self._extract_tax_id(text),
            'total_amount': self._extract_amount(text),
            'items': self._extract_items(text),
        }
        
        return invoice_data
    
    def _extract_invoice_number(self, text: str) -> str:
        """提取發票號碼"""
        pattern = r'發票號碼[:：]\s*([A-Z]{2}\d{8})'
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def _extract_date(self, text: str) -> str:
        """提取日期"""
        patterns = [
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
            r'(\d{3})年(\d{1,2})月(\d{1,2})日',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""
    
    def _extract_company(self, text: str) -> str:
        """提取公司名稱"""
        pattern = r'([^，。\n]+(?:有限公司|股份有限公司|企業社))'
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def _extract_tax_id(self, text: str) -> str:
        """提取統一編號"""
        pattern = r'統一編號[:：]\s*(\d{8})'
        match = re.search(pattern, text)
        return match.group(1) if match else ""
    
    def _extract_amount(self, text: str) -> float:
        """提取總金額"""
        patterns = [
            r'總[計金]額[:：]\s*[\$NT]*\s*([\d,]+)',
            r'合計[:：]\s*[\$NT]*\s*([\d,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '')
                return float(amount_str)
        return 0.0
    
    def _extract_items(self, text: str) -> List[Dict]:
        """提取項目明細"""
        # 簡化版本，實際應用需要更複雜的解析
        items = []
        lines = text.split('\n')
        
        for line in lines:
            # 匹配項目格式：名稱 數量 單價 金額
            pattern = r'(.+?)\s+(\d+)\s+([\d,]+)\s+([\d,]+)'
            match = re.search(pattern, line)
            if match:
                items.append({
                    'name': match.group(1).strip(),
                    'quantity': int(match.group(2)),
                    'unit_price': float(match.group(3).replace(',', '')),
                    'amount': float(match.group(4).replace(',', '')),
                })
        
        return items
    
    def batch_process_invoices(
        self, 
        invoice_dir: str,
        output_csv: str = "invoices.csv"
    ):
        """批次處理發票並輸出 CSV"""
        import csv
        from pathlib import Path
        
        invoice_path = Path(invoice_dir)
        image_files = list(invoice_path.glob("*.png")) + \
                      list(invoice_path.glob("*.jpg"))
        
        processed_invoices = []
        
        for image_file in image_files:
            print(f"處理: {image_file.name}")
            try:
                invoice_data = self.process_invoice(str(image_file))
                invoice_data['filename'] = image_file.name
                processed_invoices.append(invoice_data)
            except Exception as e:
                print(f"  錯誤: {e}")
        
        # 輸出 CSV
        if processed_invoices:
            with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
                fieldnames = [
                    'filename', 'invoice_number', 'date',
                    'company_name', 'tax_id', 'total_amount'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for invoice in processed_invoices:
                    row = {k: invoice.get(k, '') for k in fieldnames}
                    writer.writerow(row)
            
            print(f"\n完成！已處理 {len(processed_invoices)} 張發票")
            print(f"結果已儲存至: {output_csv}")

# 使用範例
processor = InvoiceProcessor()

# 單張發票
invoice_data = processor.process_invoice("invoice.png")
print(f"發票號碼: {invoice_data['invoice_number']}")
print(f"總金額: ${invoice_data['total_amount']:,.2f}")

# 批次處理
processor.batch_process_invoices("invoices", "processed_invoices.csv")
```

##### 效益
- **自動化**: 減少 90% 手動輸入時間
- **整合**: 直接輸出為 CSV/Excel 格式
- **追蹤**: 建立完整的費用記錄
- **合規**: 確保財務文檔的數字化存檔

#### 4.4.3 表格數據提取

##### 應用場景
- 財務報表分析
- 問卷調查數據整理
- 科學實驗數據記錄
- 統計報告處理

##### 實施方案

```python
"""表格數據提取系統"""
import pandas as pd
from typing import List

class TableExtractor:
    """表格提取器"""
    
    def __init__(self, ocr_host="http://localhost:5000"):
        self.client = DeepSeekOCRClient(ocr_host)
    
    def extract_table(
        self, 
        image_path: str,
        save_to_excel: bool = True
    ) -> pd.DataFrame:
        """提取表格數據"""
        # 使用表格專用提示詞
        prompt = """<image>
請提取這個表格的所有數據。
輸出格式：每行用換行符分隔，每個單元格用 | 符號分隔。
保持表頭和數據的對應關係。
"""
        
        result = self.client.ocr(image_path, prompt)
        text = result['text']
        
        # 解析表格
        df = self._parse_table_text(text)
        
        # 儲存為 Excel
        if save_to_excel:
            output_file = image_path.replace('.png', '.xlsx').replace('.jpg', '.xlsx')
            df.to_excel(output_file, index=False)
            print(f"表格已儲存至: {output_file}")
        
        return df
    
    def _parse_table_text(self, text: str) -> pd.DataFrame:
        """解析表格文字為 DataFrame"""
        lines = text.strip().split('\n')
        
        # 嘗試不同的分隔符
        separators = ['|', '\t', '  ', ',']
        
        for sep in separators:
            if sep in lines[0]:
                # 解析每一行
                rows = []
                for line in lines:
                    if line.strip():
                        cells = [cell.strip() for cell in line.split(sep)]
                        rows.append(cells)
                
                if rows:
                    # 第一行作為表頭
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                    return df
        
        # 如果無法解析，返回原始文字
        return pd.DataFrame({'text': [text]})
    
    def batch_extract_tables(
        self,
        table_dir: str,
        output_dir: str = "extracted_tables"
    ):
        """批次提取表格"""
        from pathlib import Path
        
        input_path = Path(table_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        image_files = list(input_path.glob("*.png")) + \
                      list(input_path.glob("*.jpg"))
        
        all_dataframes = {}
        
        for image_file in image_files:
            print(f"提取表格: {image_file.name}")
            try:
                df = self.extract_table(str(image_file), save_to_excel=False)
                
                # 儲存為 Excel
                excel_file = output_path / f"{image_file.stem}.xlsx"
                df.to_excel(excel_file, index=False)
                
                all_dataframes[image_file.name] = df
                print(f"  成功! 表格大小: {df.shape}")
            except Exception as e:
                print(f"  錯誤: {e}")
        
        # 如果所有表格結構相同，合併為單一檔案
        if all_dataframes:
            try:
                combined_df = pd.concat(all_dataframes.values(), ignore_index=True)
                combined_file = output_path / "all_tables_combined.xlsx"
                combined_df.to_excel(combined_file, index=False)
                print(f"\n合併檔案: {combined_file}")
            except Exception as e:
                print(f"\n無法合併表格: {e}")

# 使用範例
extractor = TableExtractor()

# 單個表格
df = extractor.extract_table("financial_report.png")
print(df.head())

# 批次處理
extractor.batch_extract_tables("tables")
```

#### 4.4.4 教育與輔助工具

##### 應用場景
- 作業批改輔助
- 學生筆記數字化
- 考試答案掃描
- 視覺障礙學生輔助閱讀

##### 實施方案

```python
"""教育輔助工具"""

class EducationAssistant:
    """教育輔助工具"""
    
    def __init__(self, ocr_host="http://localhost:5000"):
        self.client = DeepSeekOCRClient(ocr_host)
    
    def read_aloud_for_visually_impaired(
        self, 
        image_path: str,
        voice_output: bool = True
    ) -> str:
        """為視覺障礙者朗讀文字"""
        # OCR 辨識
        result = self.client.ocr(image_path)
        text = result['text']
        
        if voice_output:
            # 使用 TTS (Text-to-Speech)
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        
        return text
    
    def digitize_student_notes(
        self,
        notes_dir: str,
        output_dir: str = "digitized_notes"
    ):
        """數字化學生筆記"""
        from pathlib import Path
        import datetime
        
        notes_path = Path(notes_dir)
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 按日期組織筆記
        image_files = sorted(
            list(notes_path.glob("*.png")) + 
            list(notes_path.glob("*.jpg"))
        )
        
        all_notes = []
        
        for image_file in image_files:
            print(f"處理筆記: {image_file.name}")
            
            result = self.client.ocr(str(image_file))
            
            # 添加元數據
            note = {
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'filename': image_file.name,
                'content': result['text']
            }
            all_notes.append(note)
        
        # 生成 Markdown 格式的筆記本
        notebook_file = output_path / "notebook.md"
        with open(notebook_file, 'w', encoding='utf-8') as f:
            f.write("# 數字化筆記\n\n")
            
            for note in all_notes:
                f.write(f"## {note['date']} - {note['filename']}\n\n")
                f.write(note['content'])
                f.write("\n\n---\n\n")
        
        print(f"\n完成！筆記已儲存至: {notebook_file}")
        return all_notes

# 使用範例
assistant = EducationAssistant()

# 輔助閱讀
text = assistant.read_aloud_for_visually_impaired("textbook_page.png")

# 筆記數字化
notes = assistant.digitize_student_notes("student_notes")
```

#### 4.4.5 其他應用領域

##### 1. 醫療健康
- **應用**: 病歷數字化、處方簽識別、醫療報告整理
- **價值**: 提高醫療記錄效率，減少錯誤

##### 2. 法律服務
- **應用**: 合約文件整理、法庭記錄數字化、法律文件搜尋
- **價值**: 加速案件處理，提高檢索效率

##### 3. 物流運輸
- **應用**: 快遞單掃描、貨運標籤識別、倉儲單據處理
- **價值**: 自動化物流流程，減少人工輸入

##### 4. 零售電商
- **應用**: 商品標籤識別、價格標籤提取、庫存單據處理
- **價值**: 提高庫存管理效率，減少定價錯誤

##### 5. 政府部門
- **應用**: 公文數字化、歷史檔案整理、證件識別
- **價值**: 提升政務效率，便民服務

### 4.5 進階配置

#### 4.5.1 性能優化

##### GPU 記憶體優化

```python
# 使用 4-bit 量化降低記憶體
model = FastVisionModel.from_pretrained(
    "./deepseek_ocr",
    load_in_4bit=True,  # 記憶體降低 75%
)

# 使用 8-bit 量化
model = FastVisionModel.from_pretrained(
    "./deepseek_ocr",
    load_in_8bit=True,  # 記憶體降低 50%
)
```

##### 批次大小調整

```python
# config.py
BATCH_SIZE = 4  # 根據 GPU 記憶體調整

# 在處理時分批
def process_large_batch(image_paths, batch_size=BATCH_SIZE):
    results = []
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i+batch_size]
        batch_results = client.batch_ocr(batch)
        results.extend(batch_results)
    return results
```

#### 4.5.2 錯誤處理與重試

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """重試裝飾器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"錯誤: {e}, 重試 {attempt + 1}/{max_retries}")
                    time.sleep(delay)
        return wrapper
    return decorator

class RobustOCRClient(DeepSeekOCRClient):
    """帶重試機制的 OCR 客戶端"""
    
    @retry_on_failure(max_retries=3, delay=2)
    def ocr(self, image_path, prompt=None):
        """帶重試的 OCR"""
        return super().ocr(image_path, prompt)
```

---

## 5. 進階主題

### 5.1 模型微調

DeepSeek-OCR 支援針對特定領域進行微調：

```python
from unsloth import FastVisionModel
from datasets import load_dataset

# 載入模型
model, tokenizer = FastVisionModel.from_pretrained(
    "./deepseek_ocr",
    load_in_4bit=True,
)

# 準備 LoRA 微調
model = FastVisionModel.get_peft_model(
    model,
    r=16,
    lora_alpha=16,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj"
    ],
)

# 載入訓練數據
dataset = load_dataset("your_ocr_dataset")

# 訓練（簡化示例）
from transformers import Trainer

trainer = Trainer(
    model=model,
    train_dataset=dataset['train'],
    # ... 其他訓練參數
)

trainer.train()
```

### 5.2 多 GPU 部署

```python
# 使用 Ray Serve 進行多 GPU 部署
from ray import serve
import ray

ray.init()
serve.start()

@serve.deployment(num_replicas=2, ray_actor_options={"num_gpus": 1})
class DeepSeekOCRService:
    def __init__(self):
        self.model, self.tokenizer = FastVisionModel.from_pretrained(
            "./deepseek_ocr"
        )
    
    def ocr(self, image_bytes):
        # OCR 處理邏輯
        pass

serve.run(DeepSeekOCRService.bind())
```

### 5.3 監控與日誌

```python
import logging
from prometheus_client import Counter, Histogram

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_service.log'),
        logging.StreamHandler()
    ]
)

# Prometheus 指標
ocr_requests = Counter('ocr_requests_total', 'Total OCR requests')
ocr_duration = Histogram('ocr_duration_seconds', 'OCR processing duration')

@ocr_duration.time()
def perform_ocr(image_path):
    ocr_requests.inc()
    # OCR 處理
    pass
```

---

## 6. 常見問題

### Q1: 如何處理大型文檔？

**A**: 將文檔分頁掃描，使用批次 API 處理，然後合併結果。

```python
# 分頁處理大型文檔
def process_large_document(pages_dir):
    pages = sorted(Path(pages_dir).glob("page_*.png"))
    results = client.batch_ocr([str(p) for p in pages])
    
    # 合併所有頁面
    full_text = "\n\n".join([r['text'] for r in results])
    return full_text
```

### Q2: 如何提高識別準確度？

**A**: 
1. 提供高質量的圖片（清晰、對比度高）
2. 使用適當的提示詞
3. 針對特定領域進行微調

### Q3: 支援哪些圖片格式？

**A**: PNG, JPG, JPEG, GIF, BMP, WEBP

### Q4: 如何處理手寫文字？

**A**: DeepSeek-OCR 原生支援手寫文字，可以使用特定提示詞：

```python
prompt = "<image>\n請識別這張圖片中的手寫文字。"
result = client.ocr("handwriting.png", prompt)
```

### Q5: 可以離線使用嗎？

**A**: 可以！模型下載後即可完全離線運行。

### Q6: 記憶體需求如何優化？

**A**: 使用 4-bit 量化可降低 75% 記憶體使用：

```python
model = FastVisionModel.from_pretrained(
    "./deepseek_ocr",
    load_in_4bit=True
)
```

---

## 7. 結論

DeepSeek-OCR 結合 Unsloth 優化框架，提供了業界領先的 OCR 解決方案。通過本文檔，您應該能夠：

1. ✅ 理解 DeepSeek-OCR 的技術原理和優勢
2. ✅ 掌握 Unsloth 的優化機制
3. ✅ 完成系統的安裝和配置
4. ✅ 使用 API 進行各種應用開發
5. ✅ 將 OCR 技術應用到實際業務場景

希望本文檔能幫助您充分發揮 DeepSeek-OCR 的潛力！

---

## 8. 參考資源

### 官方文檔
- [DeepSeek-OCR 官方文檔](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)
- [Unsloth 官方網站](https://unsloth.ai/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

### 社群資源
- [Unsloth GitHub](https://github.com/unslothai/unsloth)
- [DeepSeek AI](https://www.deepseek.com/)

### 相關論文
- DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model
- Context Optical Compression for Vision-Language Models

---

**文檔版本**: 1.0.0  
**最後更新**: 2025-11-10  
**維護者**: DeepSeek-OCR API Team  
**授權**: MIT License

