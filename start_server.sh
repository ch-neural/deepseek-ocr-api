#!/bin/bash

# DeepSeek-OCR API 啟動腳本（智能版本）
# 會自動偵測 Unsloth 是否可用，若不可用則使用標準 Transformers 版本

# 載入環境變數
source .env 2>/dev/null || true

# 設定預設的 OCR 參數（如未設定）
export OCR_BASE_SIZE=${OCR_BASE_SIZE:-1024}
export OCR_IMAGE_SIZE=${OCR_IMAGE_SIZE:-640}
echo "====================================="
echo "DeepSeek-OCR API 伺服器啟動腳本"
echo "====================================="

# 檢查是否已在虛擬環境中
if [ -z "$VIRTUAL_ENV" ]; then
    # 嘗試使用預設的虛擬環境
    if [ -d "/home/chtseng/envs/DEEPSEEK-OCR" ]; then
        echo "正在啟動虛擬環境..."
        source /home/chtseng/envs/DEEPSEEK-OCR/bin/activate
    elif [ -d "/home/chtseng/envs/DP-OCR" ]; then
        echo "正在啟動虛擬環境..."
        source /home/chtseng/envs/DP-OCR/bin/activate
    elif [ -d ".venv" ]; then
        echo "正在啟動本地虛擬環境..."
        source .venv/bin/activate
    else
        echo "⚠️  警告: 未偵測到虛擬環境"
        echo "請先建立或啟動虛擬環境，例如："
        echo "  source /home/chtseng/envs/DEEPSEEK-OCR/bin/activate"
        exit 1
    fi
fi

echo "✅ 已在虛擬環境中: $VIRTUAL_ENV"
echo ""

# 檢查必要套件
echo "正在檢查必要套件..."
MISSING_PACKAGES=0

python -c "import flask; print('✅ Flask:', flask.__version__)" 2>/dev/null || { echo "❌ Flask 未安裝"; MISSING_PACKAGES=1; }
python -c "import torch; print('✅ PyTorch:', torch.__version__)" 2>/dev/null || { echo "❌ PyTorch 未安裝"; MISSING_PACKAGES=1; }
python -c "import transformers; print('✅ Transformers:', transformers.__version__)" 2>/dev/null || { echo "❌ Transformers 未安裝"; MISSING_PACKAGES=1; }
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>/dev/null || { echo "❌ Pillow 未安裝"; MISSING_PACKAGES=1; }

if [ $MISSING_PACKAGES -eq 1 ]; then
    echo ""
    echo "❌ 缺少必要套件，請先安裝："
    echo "   pip install flask torch transformers pillow"
    exit 1
fi

# 建立必要的目錄
echo ""
echo "正在建立必要的目錄..."
mkdir -p uploads
mkdir -p logs
mkdir -p output

# 檢測 Unsloth 是否可用
echo ""
echo "正在檢測 Unsloth 狀態..."

# 使用 timeout 命令限制檢測時間（5 秒）
UNSLOTH_AVAILABLE=0
timeout 5 python -c "import unsloth; print('✅ Unsloth 可用')" 2>/dev/null && UNSLOTH_AVAILABLE=1

if [ $UNSLOTH_AVAILABLE -eq 1 ]; then
    echo "✅ Unsloth 可用，使用 Unsloth 優化版本"
    APP_FILE="app.py"
else
    echo "⚠️  Unsloth 不可用或載入失敗"
    echo "   將使用標準 Transformers 版本（功能相同）"
    APP_FILE="app_standard.py"
fi

# 啟動 Flask 應用
echo ""
echo "====================================="
echo "正在啟動 DeepSeek-OCR API 伺服器..."
echo "使用: $APP_FILE"
echo "伺服器將監聽 http://0.0.0.0:5000"
echo "====================================="
echo ""

python $APP_FILE
