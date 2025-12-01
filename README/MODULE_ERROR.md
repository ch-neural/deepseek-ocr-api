# DeepSeek-OCR 模組錯誤說明

## 錯誤：ModuleNotFoundError: No module named 'vllm.model_executor.models.deepseek_ocr'

### 錯誤訊息

```
Traceback (most recent call last):
  File "/GPUData/working/Deepseek-OCR/app.py", line 10, in <module>
    from ocr_service import DeepSeekOCRService
  File "/GPUData/working/Deepseek-OCR/ocr_service.py", line 7, in <module>
    from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
ModuleNotFoundError: No module named 'vllm.model_executor.models.deepseek_ocr'
```

### 發生原因

1. **vLLM 版本問題**：當前 vLLM 版本可能還沒有完整支援 DeepSeek-OCR
2. **模組不存在**：`NGramPerReqLogitsProcessor` 在當前 vLLM 版本中不存在
3. **需要使用 Unsloth**：根據官方文檔，DeepSeek-OCR 在 Unsloth 中有完整支援

### 解決方法

專案已經更新為使用 **Unsloth** 而非 vLLM，因為 Unsloth 對 DeepSeek-OCR 有更好的支援。

#### 方法 1: 安裝 Unsloth（推薦）

```bash
# 1. 安裝 Unsloth
pip install --upgrade unsloth

# 2. 安裝相關依賴
pip install transformers torch accelerate huggingface_hub

# 3. 安裝 Flask 相關套件
pip install Flask Pillow Werkzeug

# 4. 啟動服務
python app.py
```

#### 方法 2: 使用啟動腳本

```bash
./start_server.sh
```

腳本會自動安裝 Unsloth 和所有依賴套件。

### Unsloth vs vLLM

| 特性 | Unsloth | vLLM |
|------|---------|------|
| DeepSeek-OCR 支援 | ✅ 完整支援 | ❌ 部分支援或不支援 |
| 安裝難度 | 簡單 | 需要 nightly build |
| 記憶體使用 | 優化良好（支援 4bit） | 較高 |
| 效能 | 1.4x 更快 | 標準 |
| 文檔完整度 | 完整 | DeepSeek-OCR 部分缺少 |

### 驗證安裝

安裝完成後，可以驗證：

```bash
# 驗證 Unsloth 已安裝
python -c "import unsloth; print('Unsloth 版本:', unsloth.__version__)"

# 驗證 Transformers 已安裝
python -c "import transformers; print('Transformers 版本:', transformers.__version__)"

# 驗證 PyTorch 已安裝
python -c "import torch; print('PyTorch 版本:', torch.__version__); print('CUDA 可用:', torch.cuda.is_available())"
```

### 首次啟動注意事項

第一次啟動服務時，會自動下載 DeepSeek-OCR 模型（約 3GB）：

```bash
python app.py
```

您會看到類似的輸出：

```
正在初始化 DeepSeek-OCR 服務...
正在載入模型: unsloth/DeepSeek-OCR
正在下載模型到 ./deepseek_ocr...
Downloading (…)lve/main/config.json: 100%|████████| 1.23k/1.23k [00:00<00:00, 123kB/s]
...
模型下載完成！
模型載入完成: unsloth/DeepSeek-OCR
```

這個過程可能需要 5-15 分鐘，取決於您的網路速度。

### 如果仍然遇到問題

#### 問題 1: Unsloth 安裝失敗

```bash
# 確保 PyTorch 已正確安裝
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 強制重新安裝 Unsloth
pip install --upgrade --force-reinstall --no-deps --no-cache-dir unsloth unsloth_zoo
```

#### 問題 2: CUDA 不可用

```bash
# 檢查 CUDA
nvidia-smi

# 如果沒有 GPU，DeepSeek-OCR 無法運行
# 建議使用有 GPU 的伺服器
```

#### 問題 3: 記憶體不足

```bash
# 修改 ocr_service.py 使用 4bit 模式（更省記憶體）
# 在 ocr_service.py 的 __init__ 方法中：
load_in_4bit=True,  # 改為 True
```

#### 問題 4: 模型下載失敗

```bash
# 設定 Hugging Face 鏡像（中國地區）
export HF_ENDPOINT=https://hf-mirror.com

# 或手動下載模型
python -c "from huggingface_hub import snapshot_download; snapshot_download('unsloth/DeepSeek-OCR', local_dir='deepseek_ocr')"
```

### 更多資訊

- [Unsloth 官方文檔](https://docs.unsloth.ai/)
- [DeepSeek-OCR 使用指南](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)
- [專案 README](../README.md)
- [完整錯誤訊息說明](ERROR_MESSAGES.md)

