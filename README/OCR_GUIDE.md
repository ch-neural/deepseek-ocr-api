# OCR 使用指南

本文檔整合了 OCR 配置參數、影像尺寸限制和 Prompt 使用說明。

## 目錄

1. [配置參數說明](#1-配置參數說明)
2. [影像尺寸限制](#2-影像尺寸限制)
3. [Prompt 處理機制](#3-prompt-處理機制)
4. [常見問題排除](#4-常見問題排除)

---

## 1. 配置參數說明

### 主要參數

所有參數都在 `config.py` 中設定，也可透過環境變數覆蓋。

| 參數 | 預設值 | 環境變數 | 說明 |
|------|-------|---------|------|
| `OCR_BASE_SIZE` | 1024 | `OCR_BASE_SIZE` | 圖片預處理基準尺寸 |
| `OCR_IMAGE_SIZE` | 640 | `OCR_IMAGE_SIZE` | 模型輸入尺寸 |
| `OCR_CROP_MODE` | True | `OCR_CROP_MODE` | 是否啟用裁切模式 |

### 參數詳解

#### OCR_BASE_SIZE

圖片會先被縮放到此尺寸（保持長寬比）。

- **1024**：適合 1280x720 或更小的圖片（處理快，約 10-30 秒）
- **2048**：適合 1920x1080 或更大的圖片（處理慢，約 30-60 秒）

#### OCR_IMAGE_SIZE

經過 base_size 處理後，圖片會進一步處理為此尺寸。

- **640**：適合快速處理（可能降低準確度）
- **1024**：推薦設定（平衡準確度與速度）

#### OCR_CROP_MODE

- **True**：將圖片裁切為多個區塊分別處理（適合大圖或多欄文字）
- **False**：將整張圖片作為一個區塊處理（適合單欄或小圖）

### 效能模式建議

| 模式 | BASE_SIZE | IMAGE_SIZE | 處理時間 | 準確度 | 適用場景 |
|------|-----------|------------|----------|--------|---------|
| 快速 | 1024 | 640 | ~10-30 秒 | 中等 | 即時處理、小圖 |
| 平衡 | 2048 | 1024 | ~30-60 秒 | 高 | 一般使用（推薦） |
| 高品質 | 2048 | 1280 | ~60-120 秒 | 極高 | 專業用途、大圖 |

### 設定方式

#### 方式 1：環境變數

```bash
export OCR_BASE_SIZE=2048
export OCR_IMAGE_SIZE=1024
./start_server.sh
```

#### 方式 2：修改 config.py

```python
class Config:
    OCR_BASE_SIZE = 2048
    OCR_IMAGE_SIZE = 1024
    OCR_CROP_MODE = True
```

---

## 2. 影像尺寸限制

### 支援的尺寸範圍

| 項目 | 最小 | 最大 | 建議 |
|------|-----|-----|------|
| 寬度 | 32 px | 4096 px | 1024-2048 px |
| 高度 | 32 px | 4096 px | 1024-2048 px |
| 檔案大小 | - | 16 MB | < 5 MB |

### 支援的格式

- PNG（推薦）
- JPEG / JPG
- GIF
- BMP
- WebP

### 圖片處理流程

```
原始圖片 → 縮放到 BASE_SIZE → 裁切/處理 → 輸入模型 → OCR 結果
```

### 最佳實踐

1. **解析度**：300 DPI 掃描品質最佳
2. **對比度**：確保文字與背景有足夠對比
3. **傾斜校正**：傾斜的文字可能影響辨識率
4. **壓縮**：避免過度壓縮的 JPEG

---

## 3. Prompt 處理機制

### 基本概念

DeepSeek-OCR 是一個視覺語言模型（VLM），可以透過文字 prompt 引導 OCR 行為。

### 預設 Prompt

```
<image>
Free OCR.
```

### 自訂 Prompt 範例

#### 基本 OCR

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@image.png"
```

#### 指定語言

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@image.png" \
  -F "prompt=這是一本繁體中文書的內頁，請用繁體中文輸出 OCR 結果。"
```

#### 表格辨識

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@table.png" \
  -F "prompt=請將表格轉換為 Markdown 格式。"
```

#### 只提取特定內容

```bash
curl -X POST http://localhost:5000/ocr \
  -F "file=@invoice.png" \
  -F "prompt=請只提取發票上的金額和日期。"
```

### Prompt 格式說明

- Prompt 會自動加上 `<image>` 標記（如果沒有）
- 可以使用中文或英文
- 建議明確指定輸出格式和語言

### ⚠️ 注意事項

1. **Prompt 不是指令**：模型會「參考」prompt，但不保證完全遵循
2. **保持簡潔**：過長的 prompt 可能影響效能
3. **測試調整**：不同圖片可能需要不同的 prompt

---

## 4. 常見問題排除

### 問題 1：OCR 結果重複或亂碼

**症狀**：輸出大量重複的文字，如 "xxx xxx xxx..."

**原因**：
- 圖片品質太差
- 參數設定不當
- 模型產生幻覺

**解決方案**：
1. 提高圖片品質
2. 調整參數：增加 `OCR_BASE_SIZE`
3. 使用更明確的 prompt
4. 程式碼已內建重複內容過濾機制

### 問題 2：OCR 速度太慢

**原因**：
- 使用標準版本（非 Unsloth）
- 圖片太大
- 參數設定太高

**解決方案**：
1. 安裝 Unsloth 加速
2. 縮小圖片尺寸
3. 降低 `OCR_BASE_SIZE` 和 `OCR_IMAGE_SIZE`

### 問題 3：中文辨識不準確

**解決方案**：
1. 使用包含「繁體中文」或「簡體中文」的 prompt
2. 確保圖片清晰度足夠
3. 使用 `OCR_CROP_MODE=True`

### 問題 4：表格辨識不完整

**解決方案**：
1. 使用明確的 prompt：「請將表格轉換為 Markdown 格式」
2. 增加 `OCR_BASE_SIZE` 到 2048
3. 確保表格邊界清晰

---

## Python 使用範例

```python
import requests

# 基本 OCR
def ocr_image(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:5000/ocr',
            files={'file': f}
        )
    return response.json()

# 自訂 Prompt
def ocr_with_prompt(image_path, prompt):
    with open(image_path, 'rb') as f:
        response = requests.post(
            'http://localhost:5000/ocr',
            files={'file': f},
            data={'prompt': prompt}
        )
    return response.json()

# 使用範例
result = ocr_image('document.png')
print(result['text'])

result = ocr_with_prompt('table.png', '請將表格轉換為 Markdown 格式')
print(result['text'])
```

---

**最後更新**：2025-12-01
