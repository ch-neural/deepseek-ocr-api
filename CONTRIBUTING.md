# 貢獻指南

感謝您考慮為 DeepSeek-OCR API 專案做出貢獻！

## 🤝 如何貢獻

### 報告 Bug

如果您發現了 Bug，請：

1. 確認該 Bug 尚未被報告（搜尋現有的 Issues）
2. 創建一個新的 Issue，並包含：
   - 清晰的標題
   - 詳細的描述
   - 重現步驟
   - 預期行為 vs 實際行為
   - 系統環境資訊（OS、Python 版本、GPU 型號等）
   - 相關的錯誤訊息和日誌

### 提出新功能

如果您有新功能的想法：

1. 先創建一個 Issue 討論該功能
2. 說明該功能的用途和價值
3. 等待維護者的反饋

### 提交 Pull Request

1. **Fork 專案**
   ```bash
   # 在 GitHub 上點擊 Fork 按鈕
   ```

2. **克隆您的 Fork**
   ```bash
   git clone https://github.com/你的帳號/Deepseek-OCR.git
   cd Deepseek-OCR
   ```

3. **創建特性分支**
   ```bash
   git checkout -b feature/你的功能名稱
   # 或
   git checkout -b fix/你的修復名稱
   ```

4. **進行修改**
   - 保持程式碼風格一致
   - 添加必要的註解
   - 更新相關文檔

5. **測試您的修改**
   ```bash
   # 執行測試
   python test_api.py
   
   # 手動測試
   ./start_server.sh
   # 測試各項功能
   ```

6. **提交變更**
   ```bash
   git add .
   git commit -m "feat: 添加某某功能"
   # 或
   git commit -m "fix: 修復某某問題"
   ```

7. **推送到您的 Fork**
   ```bash
   git push origin feature/你的功能名稱
   ```

8. **創建 Pull Request**
   - 在 GitHub 上打開您的 Fork
   - 點擊 "New Pull Request"
   - 填寫 PR 描述，說明您的變更

## 📝 程式碼風格

### Python 程式碼

- 遵循 PEP 8 風格指南
- 使用 4 個空格縮排（不使用 Tab）
- 函數和方法使用 snake_case
- 類別使用 PascalCase
- 常數使用 UPPER_CASE

範例：
```python
class DeepSeekOCRService:
    """DeepSeek-OCR 服務類別"""
    
    def __init__(self, model_name, model_dir):
        self.model_name = model_name
        self.model_dir = model_dir
    
    def perform_ocr(self, image_path):
        """執行 OCR"""
        # 實作邏輯
        pass
```

### 註解規範

- 使用繁體中文撰寫註解
- 為複雜邏輯添加說明
- 為每個函數添加 docstring

範例：
```python
def perform_ocr(self, image_path, custom_prompt=None):
    """
    執行 OCR 識別
    
    Args:
        image_path (str): 圖片檔案路徑
        custom_prompt (str, optional): 自訂提示詞. Defaults to None.
    
    Returns:
        str: OCR 識別結果文字
    
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
    """
    pass
```

### 錯誤處理

- 避免使用空的 try-except
- 明確處理特定的異常類型
- 在 except 區塊中提供清晰的錯誤訊息

範例：
```python
# ❌ 不好的做法
try:
    result = risky_operation()
except:
    pass

# ✅ 好的做法
try:
    result = risky_operation()
except FileNotFoundError as e:
    print(f"錯誤：找不到檔案 - {e}")
    raise
except Exception as e:
    print(f"發生未預期的錯誤：{e}")
    raise
```

## 📚 文檔

如果您的變更影響到使用方式，請更新相關文檔：

- `README.md`：主要說明文件
- `INSTALL.md`：安裝指南
- `README/API_DOCUMENTATION.md`：API 文檔
- `README/ERROR_MESSAGES.md`：錯誤訊息說明
- `docs/`：技術文檔

## 🧪 測試

在提交 PR 前，請確保：

- ✅ 所有現有測試通過
- ✅ 新功能有對應的測試
- ✅ 手動測試過主要功能
- ✅ 檢查過不同的錯誤情況

## 📋 Commit 訊息格式

使用語意化的 commit 訊息：

- `feat:` 新功能
- `fix:` Bug 修復
- `docs:` 文檔更新
- `style:` 程式碼格式調整（不影響功能）
- `refactor:` 重構（不是新功能也不是 Bug 修復）
- `test:` 測試相關
- `chore:` 建置流程或輔助工具變動

範例：
```
feat: 添加批次 OCR 功能
fix: 修復 GPU 記憶體洩漏問題
docs: 更新 API 文檔
refactor: 重構 OCR 服務類別
```

## 🔍 Pull Request 檢查清單

提交 PR 前，請確認：

- [ ] 程式碼符合專案風格
- [ ] 添加了必要的註解和文檔
- [ ] 所有測試通過
- [ ] 更新了相關文檔
- [ ] Commit 訊息清晰明確
- [ ] PR 描述說明了變更內容

## 💬 社群準則

- 尊重所有貢獻者
- 歡迎建設性的批評
- 專注於對專案最有利的事情
- 表現出同理心和善意

## 📧 聯絡方式

如有任何問題，歡迎：

- 創建 [Issue](https://github.com/你的帳號/Deepseek-OCR/issues)
- 參與 [Discussions](https://github.com/你的帳號/Deepseek-OCR/discussions)

## 🙏 致謝

感謝所有為這個專案做出貢獻的人！

---

再次感謝您的貢獻！❤️













