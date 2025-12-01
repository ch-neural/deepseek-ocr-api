#!/bin/bash

# DeepSeek-OCR API 正式環境啟動腳本（使用 Gunicorn）

echo "====================================="
echo "DeepSeek-OCR API 正式環境啟動"
echo "====================================="

# 載入環境變數
source .env 2>/dev/null || true

# 檢查是否已在虛擬環境中
if [ -z "$VIRTUAL_ENV" ]; then
    # 嘗試使用預設的虛擬環境
    if [ -d "/home/chtseng/envs/DP-OCR" ]; then
        source /home/chtseng/envs/DP-OCR/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "❌ 請先啟動虛擬環境"
        exit 1
    fi
fi

echo "✅ 虛擬環境: $VIRTUAL_ENV"

# 檢查是否已安裝 Gunicorn
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "正在安裝 Gunicorn..."
    pip install gunicorn -q
fi

# 建立必要的目錄
mkdir -p uploads logs output

# 設定預設的 OCR 參數（如未設定）
export OCR_BASE_SIZE=${OCR_BASE_SIZE:-1024}
export OCR_IMAGE_SIZE=${OCR_IMAGE_SIZE:-640}

echo ""
echo "OCR 參數設定:"
echo "  - OCR_BASE_SIZE: $OCR_BASE_SIZE"
echo "  - OCR_IMAGE_SIZE: $OCR_IMAGE_SIZE"

# 使用 Gunicorn 啟動應用（使用標準版本）
echo ""
echo "====================================="
echo "正在使用 Gunicorn 啟動伺服器..."
echo "Workers: 1 (OCR 模型需要大量 GPU 記憶體)"
echo "Port: 5000"
echo "Timeout: 300 秒"
echo "====================================="

gunicorn -w 1 -b 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    app_standard:app
