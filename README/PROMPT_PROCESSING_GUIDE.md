# DeepSeek-OCR Prompt 處理機制說明

## 概述

本文件說明 DeepSeek-OCR 模型如何處理使用者提供的文字 prompt，以及如何有效地使用 prompt 來引導 OCR 行為。

---

## 模型架構

DeepSeek-OCR 是一個 **Vision-Language Model (VLM)**，結合了視覺編碼器和語言模型：

```
輸入圖像 (H×W×3)
    ↓
┌─────────────────────────────┐
│    Vision Encoder           │  ← 視覺編碼器
│    - ViT-based              │  
│    - Patch Embedding        │
│    - 2D 佈局保持            │
└─────────────────────────────┘
    ↓
視覺 Tokens (N×D)
    ↓
┌─────────────────────────────┐
│   Optical Compression       │  ← 光學壓縮層
│   - Context Aware           │
│   - 10× Token 壓縮          │
└─────────────────────────────┘
    ↓
壓縮 Tokens + 文字 Prompt
    ↓
┌─────────────────────────────┐
│   Language Backbone         │  ← 語言模型 (DeepSeek-V2)
│   - 理解 prompt 指示        │
│   - 結合視覺特徵            │
│   - 生成 OCR 結果           │
└─────────────────────────────┘
    ↓
文字輸出
```

---

## Prompt 處理機制

### 1. 模型如何處理 Prompt？

DeepSeek-OCR 會將您的 **圖片** 和 **文字 prompt** 同時送入模型：

1. **視覺編碼器** 先處理圖片，提取視覺特徵並保持 2D 空間佈局
2. **語言模型** 接收視覺 tokens 和文字 prompt
3. **模型根據 prompt 指示**，理解您期望的 OCR 行為
4. **生成對應的 OCR 輸出**

### 2. 預設 Prompt

系統預設的 prompt 是：

```python
default_prompt = "<image>\nFree OCR."
```

這個簡單的 prompt 會讓模型自由地識別圖片中的所有文字。

### 3. 是的，模型會依照 Prompt 指示

模型會參考您 prompt 中的指示來調整 OCR 行為，包括：

- **文字排列方向**（直排/橫排）
- **閱讀順序**（由右往左/由左往右）
- **語言指定**（繁體中文/簡體中文/英文等）
- **輸出格式**（保持表格格式/純文字等）

---

## Prompt 使用範例

### 範例 1: 繁體中文直排書本

```python
prompt = """<image>
這是一本繁體中文書的內頁，文字排列是直排，由右往左閱讀。
請進行 OCR 並用繁體中文輸出結果。
"""
```

**說明**：告訴模型文字是直排排列，閱讀順序是由右往左。

### 範例 2: 繁體中文橫排書本

```python
prompt = """<image>
這是一本繁體中文書的內頁，文字排列是橫式，由左往右閱讀。
請 OCR 並用繁體中文輸出結果。
"""
```

### 範例 3: 表格數據提取

```python
prompt = """<image>
請提取這個表格的所有數據，保持格式。
輸出格式：每行用換行符分隔，每個單元格用 | 符號分隔。
"""
```

### 範例 4: 手寫文字識別

```python
prompt = """<image>
請識別這張圖片中的手寫文字。
"""
```

### 範例 5: 多語言文檔

```python
prompt = """<image>
這是一份包含中文和英文的文檔。
請 OCR 並保持原文語言輸出。
"""
```

---

## API 使用方式

### 使用 curl 發送自訂 prompt

```bash
curl -X POST \
  -F "file=@book_page.jpg" \
  -F "prompt=<image>\n這是繁體中文直排書本，由右往左閱讀。請 OCR。" \
  http://localhost:5000/ocr
```

### 使用 Python requests

```python
import requests

def ocr_with_custom_prompt(image_path, prompt):
    url = "http://localhost:5000/ocr"
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'prompt': prompt}
        response = requests.post(url, files=files, data=data)
    
    return response.json()

# 使用範例
result = ocr_with_custom_prompt(
    "book_page.jpg",
    "<image>\n這是繁體中文直排書本，文字由右往左、由上往下排列。請 OCR 並輸出結果。"
)
print(result['text'])
```

---

## 重要提醒

### 1. Prompt 效果取決於圖片品質

| 圖片品質 | 處理時間 | OCR 結果 |
|---------|---------|---------|
| 清晰、光線充足 | 10-20 秒 | ✅ 正確遵循 prompt 指示 |
| 模糊、光線不足 | 2-3 秒 | ⚠️ 可能產生幻覺，返回 prompt 重複內容 |

### 2. 避免模型幻覺

當模型無法正確識別圖片文字時，可能會產生「幻覺」（Hallucination），表現為：
- 返回 prompt 的部分或全部內容
- 處理時間異常短（2-3 秒而非正常的 10-20 秒）

**解決方法**：
1. 確保圖片清晰、光線充足
2. 使用適當的 `OCR_BASE_SIZE` 和 `OCR_IMAGE_SIZE` 設定
3. 避免圖片過度壓縮

### 3. 建議的圖片處理參數

在 `config.py` 中設定：

```python
# 平衡模式（推薦）
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1024
OCR_CROP_MODE = True
```

---

## Prompt 設計建議

### ✅ 好的 Prompt

```
<image>
這是一本繁體中文書的內頁，文字排列是直排，由右往左閱讀。
請 OCR 並用繁體中文輸出結果。
```

**特點**：
- 明確說明文字排列方向
- 指定語言
- 說明閱讀順序

### ❌ 不好的 Prompt

```
OCR
```

**問題**：
- 太簡短，沒有提供有用的上下文
- 沒有說明文字特性

---

## 技術原理

### Context Optical Compression（上下文光學壓縮）

DeepSeek-OCR 的核心創新是「光學壓縮」技術：

1. **保持 2D 佈局**：視覺編碼器會保持文檔的空間關係和結構信息
2. **壓縮視覺 tokens**：將視覺特徵壓縮為更少的 tokens（約 10 倍壓縮）
3. **結合 prompt 指示**：語言模型結合視覺特徵和 prompt 來生成輸出

這意味著當您在 prompt 中提到「直排文字」時：
- 視覺編碼器已經捕捉到文字的 2D 佈局
- 語言模型會參考您的指示來理解佈局含義
- 輸出會按照您期望的順序組織

---

## 常見問題

### Q1: 模型會完全按照我的 prompt 指示嗎？

**A**: 模型會盡量遵循您的指示，但結果取決於：
- 圖片品質（最重要）
- prompt 的清晰程度
- 模型的理解能力

### Q2: 直排/橫排文字需要特別設定嗎？

**A**: 建議在 prompt 中明確說明文字排列方向，這可以幫助模型更準確地理解圖片內容。

### Q3: 如果模型沒有正確理解我的 prompt 怎麼辦？

**A**: 嘗試：
1. 提供更清晰的圖片
2. 使用更明確的 prompt 描述
3. 調整圖片處理參數（增加 `OCR_BASE_SIZE` 和 `OCR_IMAGE_SIZE`）

### Q4: prompt 中可以使用什麼語言？

**A**: 建議使用與期望輸出相同的語言。例如，期望繁體中文輸出時，prompt 也使用繁體中文。

---

## 相關文件

- [OCR 參數設定說明](./OCR_CONFIG_PARAMETERS.md)
- [OCR Prompt 重複問題](./OCR_PROMPT_REPETITION_ISSUE.md)
- [DeepSeek-VL2 與 OCR 的關係](./DEEPSEEK_VL2_OCR_RELATIONSHIP.md)
- [技術指南](../docs/DEEPSEEK_OCR_TECHNICAL_GUIDE.md)

---

## 總結

| 問題 | 答案 |
|------|------|
| 模型會處理 prompt 嗎？ | ✅ 是的，會作為語言模型的輸入 |
| 模型會遵循 prompt 指示嗎？ | ✅ 是的，會盡量遵循 |
| 可以指定文字排列方向嗎？ | ✅ 是的，建議明確說明 |
| 效果保證嗎？ | ⚠️ 取決於圖片品質 |

**最佳實踐**：提供清晰的圖片 + 明確的 prompt = 最佳 OCR 結果


