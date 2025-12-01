# Hugging Face 認證問題解決指南

## 錯誤訊息

```
huggingface_hub.errors.HfHubHTTPError: 401 Client Error: Unauthorized
Invalid credentials in Authorization header
```

## 錯誤原因

1. **需要登入 Hugging Face**: DeepSeek-OCR 模型可能需要 Hugging Face 帳號授權
2. **未提供認證 Token**: 系統找不到有效的 Hugging Face 認證資訊
3. **Token 已過期**: 您的 Hugging Face token 可能已經過期

## 解決方法

### 方法 1: 使用 Hugging Face CLI 登入（推薦）

這是最簡單和最安全的方法：

```bash
# 1. 安裝 huggingface_hub（如果還沒安裝）
pip install huggingface_hub

# 2. 執行登入指令
huggingface-cli login
```

執行後會提示您輸入 token：

```
Token: 
```

貼上您的 token 並按 Enter。

### 方法 2: 使用環境變數

如果您已經有 Hugging Face token：

```bash
# 設定環境變數
export HF_TOKEN=your_huggingface_token_here

# 然後啟動服務
python app.py
```

或在 `.bashrc` / `.zshrc` 中永久設定：

```bash
echo 'export HF_TOKEN=your_huggingface_token_here' >> ~/.bashrc
source ~/.bashrc
```

### 方法 3: 手動下載模型

如果上述方法都不行，可以手動下載模型：

#### 使用 Git LFS

```bash
# 1. 安裝 Git LFS
sudo apt-get install git-lfs
git lfs install

# 2. 克隆模型倉庫
git clone https://huggingface.co/unsloth/DeepSeek-OCR ./deepseek_ocr
```

如果需要認證，會提示您輸入：
- Username: 您的 Hugging Face 用戶名
- Password: 您的 Hugging Face token（不是密碼！）

#### 使用 Python 腳本

```python
from huggingface_hub import snapshot_download
import os

# 設定 token
os.environ['HF_TOKEN'] = 'your_token_here'

# 下載模型
snapshot_download(
    "unsloth/DeepSeek-OCR",
    local_dir="./deepseek_ocr",
    use_auth_token=True
)
```

## 如何獲取 Hugging Face Token

### 步驟 1: 註冊/登入 Hugging Face

訪問 [https://huggingface.co/](https://huggingface.co/) 並註冊或登入帳號。

### 步驟 2: 創建 Access Token

1. 訪問 [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. 點擊 "New token"
3. 填寫資訊：
   - **Name**: 例如 "DeepSeek-OCR-API"
   - **Type**: 選擇 "Read" (讀取權限即可)
4. 點擊 "Generate a token"
5. **重要**: 複製生成的 token（只會顯示一次！）

您的 token 格式類似：`hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 步驟 3: 使用 Token

使用上述任一方法設定 token。

## 驗證認證

驗證是否已正確登入：

```bash
# 檢查登入狀態
huggingface-cli whoami

# 如果成功，會顯示您的用戶名
```

或使用 Python：

```python
from huggingface_hub import whoami

try:
    user_info = whoami()
    print(f"✅ 已登入為: {user_info['name']}")
except Exception as e:
    print(f"❌ 未登入: {e}")
```

## 測試模型下載

登入後，測試是否能下載模型：

```python
from huggingface_hub import snapshot_download

try:
    snapshot_download("unsloth/DeepSeek-OCR", local_dir="./test_download")
    print("✅ 模型下載成功！")
except Exception as e:
    print(f"❌ 下載失敗: {e}")
```

## 完整啟動流程

```bash
# 1. 登入 Hugging Face
huggingface-cli login

# 2. 驗證登入
huggingface-cli whoami

# 3. 啟動服務
python app.py
```

## 常見問題

### Q1: Token 在哪裡存儲？

Token 存儲在 `~/.cache/huggingface/token` 檔案中。

### Q2: 如何更換 Token？

```bash
# 重新登入會覆蓋舊的 token
huggingface-cli login --token new_token_here
```

### Q3: Token 會過期嗎？

Token 不會自動過期，但您可以在 Hugging Face 設定頁面手動撤銷。

### Q4: 使用環境變數 vs CLI 登入？

- **CLI 登入**: Token 持久存儲，不需要每次設定
- **環境變數**: 臨時使用，每次啟動都需要設定

推薦使用 CLI 登入。

### Q5: 模型真的需要授權嗎？

某些模型可能需要：
1. 接受模型的使用條款
2. 提供認證 token

訪問模型頁面確認是否需要額外步驟。

## 替代方案

如果您無法訪問 `unsloth/DeepSeek-OCR`，可以嘗試：

1. **官方 DeepSeek 倉庫**: 
   ```bash
   # 嘗試從 deepseek-ai 下載
   # 修改 ocr_service.py 中的 model_name
   model_name = "deepseek-ai/deepseek-ocr"
   ```

2. **本地模型**: 如果您已經下載了模型，直接指定本地路徑：
   ```python
   ocr_service = DeepSeekOCRService(model_dir="/path/to/local/model")
   ```

## 安全性注意事項

⚠️ **重要**: 
- 不要在公開的代碼中硬編碼 token
- 不要將 token 提交到 Git
- 定期輪換 token
- 只給予必要的權限（Read 權限通常就夠了）

## 取得協助

如果仍然遇到問題：

1. 確認模型是否真的存在：訪問 https://huggingface.co/unsloth/DeepSeek-OCR
2. 檢查是否需要接受特殊條款
3. 聯繫 Unsloth 或 Hugging Face 支援

## 相關文檔

- [Hugging Face Token 文檔](https://huggingface.co/docs/hub/security-tokens)
- [huggingface_hub Python 文檔](https://huggingface.co/docs/huggingface_hub/index)
- [專案錯誤訊息說明](ERROR_MESSAGES.md)
- [快速啟動指南](QUICK_START.md)

