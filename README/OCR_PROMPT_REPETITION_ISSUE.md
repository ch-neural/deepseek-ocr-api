# OCR 返回 Prompt 重複內容問題

## 問題描述

**發生日期**: 2025-11-13

### 問題現象

在使用 1920x1080 解析度拍攝照片後，有時 OCR 辨識結果只返回 Prompt 的重複內容，而沒有實際辨識書本上的文字。

**測試案例**：

| 時間 | 解析度 | 處理時間 | 文字長度 | 結果 |
|------|--------|----------|----------|------|
| 17:41:08 | 1920x1080 | 13 秒 | 415 字元 | ✅ 正確（實際書本文字） |
| 17:42:16 | 1920x1080 | 2 秒 | 100 字元 | ❌ 錯誤（只有 Prompt） |
| 17:43:07 | 1920x1080 | 2 秒 | 100 字元 | ❌ 錯誤（只有 Prompt） |

### 錯誤範例

**輸入 Prompt**：
```
這是一本繁體中文書的內頁screen, 文字排列是橫式，由左往右。請OCR 並用繁體中文輸出結果。
```

**期望 OCR 結果**：
```
江逸航的家中冷氣嗡嗡大作，只有他一人在，正戴著耳機...
（書本上的實際文字）
```

**實際 OCR 結果**（錯誤）：
```
開始模型推理 (超時: 300 秒)...
這是一本繁體中文書的內頁screen, 文字排列是橫式，由右往左。請OCR 並用繁體中文輸出結果。這是一本繁體中文書的內
模型推理完成
OCR 推理執行成功
```

---

## 問題分析

### 1. 圖片檢查

檢查有問題的圖片：

```bash
$ file capture_20251113_174216.jpg
capture_20251113_174216.jpg: JPEG image data, ..., 1920x1080, components 3

$ python -c "
from PIL import Image
img = Image.open('capture_20251113_174216.jpg')
print('尺寸:', img.size)
print('亮度範圍:', img.convert('L').getextrema())
"
尺寸: (1920, 1080)
亮度範圍: (78, 117)  # 不是空白或純色
```

**結論**：圖片本身正常，不是空白或損壞。

### 2. 處理時間分析

| 案例 | 處理時間 | 狀態 |
|------|----------|------|
| 正常 OCR | 10-15 秒 | 正確辨識 |
| 異常 OCR | 2 秒 | 只返回 Prompt |

**問題**：處理時間過短（2 秒）表示模型可能沒有正確執行完整的推理過程。

### 3. 可能原因

#### 原因 1: 圖片內容問題

- **可能性**：圖片模糊、光線不足、文字不清晰
- **表現**：模型無法辨識文字，返回 Prompt 作為"幻覺"輸出
- **驗證**：需要人工檢查拍攝的圖片是否清晰

#### 原因 2: 圖片尺寸處理問題

**代碼位置**：`ocr_service.py` - `_perform_ocr_inference()` 函數

```python
inference_result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=temp_output,
    base_size=1024,      # ← 圖片會被縮小到 1024
    image_size=640,      # ← 進一步處理為 640
    crop_mode=True,      # ← 啟用裁切模式
    save_results=False,
    test_compress=False
)
```

**問題**：
- 原始圖片：1920x1080
- base_size：1024（縮小到 1024）
- image_size：640（進一步縮小到 640）
- 最終處理尺寸：**640x360**（大幅縮小）

**影響**：
- 文字可能變得太小，模型無法辨識
- 圖片品質下降，影響 OCR 準確度

#### 原因 3: OCR 模型幻覺

**現象**：DeepSeek OCR 模型在某些情況下會產生"幻覺"（Hallucination），即生成與輸入 Prompt 相關但與圖片內容無關的文字。

**觸發條件**：
- 圖片文字不清晰或無法辨識
- 圖片尺寸處理不當
- 光線不足或對比度低
- 模型處理異常（超時、記憶體不足等）

**表現**：
- 返回 Prompt 的部分或全部內容
- 返回與 Prompt 語義相關但與圖片無關的文字
- 處理時間異常短（2-3 秒 vs 正常 10-15 秒）

#### 原因 4: 系統訊息過濾問題

從日誌可以看到，後端返回的文字已經包含系統訊息：

```
- 文字前 100 字元: 開始模型推理 (超時: 300 秒)...
這是一本繁體中文書的內頁screen, 文字排列是橫式，由右往左。請OCR 並用繁體中文輸出結果。這是一本繁體中文書的內
- 文字後 100 字元: 開始模型推理 (超時: 300 秒)...
這是一本繁體中文書的內頁screen, 文字排列是橫式，由右往左。請OCR 並用繁體中文輸出結果。這是一本繁體中文書的內
模型推理完成
OCR 推理執行成功
```

**問題**：過濾邏輯沒有正確工作，系統訊息和 Prompt 重複內容都被返回。

---

## 解決方案

### 方案 1: 改進圖片尺寸處理

**問題**：當前 `base_size=1024` 和 `image_size=640` 會將 1920x1080 的圖片大幅縮小，導致文字不清晰。

**建議**：增加處理尺寸

```python
# 原始設定
inference_result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=temp_output,
    base_size=1024,     # ← 改為 2048
    image_size=640,     # ← 改為 1024
    crop_mode=True,
    save_results=False,
    test_compress=False
)

# 建議設定
inference_result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=temp_output,
    base_size=2048,     # ✅ 增加到 2048
    image_size=1024,    # ✅ 增加到 1024
    crop_mode=True,
    save_results=False,
    test_compress=False
)
```

**權衡**：
- ✅ 優點：更清晰的文字，更高的辨識準確度
- ❌ 缺點：處理時間增加（可能從 10 秒增加到 20-30 秒），GPU 記憶體使用增加

### 方案 2: 強化系統訊息過濾

**檔案**：`ocr_service.py` - `perform_ocr()` 方法

當前過濾邏輯：

```python
system_messages = [
    '開始模型推理',
    '模型推理完成',
    'OCR 推理執行成功',
    'BASE:',
    'PATCHES:'
]

for line in lines:
    line_stripped = line.strip()
    if not line_stripped:
        continue
    if line_stripped.startswith('==='):
        continue
    # 檢查是否包含系統訊息關鍵字
    is_system_message = any(keyword in line_stripped for keyword in system_messages)
    if not is_system_message:
        text_lines.append(line)
```

**問題**：Prompt 重複內容沒有被過濾。

**建議**：添加 Prompt 去重邏輯

```python
# 方案 A: 過濾與 Prompt 相似的行
def is_similar_to_prompt(line, prompt, threshold=0.5):
    """檢查行是否與 Prompt 相似"""
    if not prompt or not line:
        return False
    
    # 簡單的相似度檢查：檢查 Prompt 的關鍵字是否在行中
    prompt_keywords = set(prompt.split())
    line_keywords = set(line.split())
    
    if not line_keywords:
        return False
    
    # 計算重疊率
    overlap = len(prompt_keywords & line_keywords) / len(line_keywords)
    return overlap > threshold

# 在過濾邏輯中使用
for line in lines:
    line_stripped = line.strip()
    if not line_stripped:
        continue
    if line_stripped.startswith('==='):
        continue
    
    # 檢查系統訊息
    is_system_message = any(keyword in line_stripped for keyword in system_messages)
    if is_system_message:
        continue
    
    # ✅ 檢查是否與 Prompt 相似
    if is_similar_to_prompt(line_stripped, prompt, threshold=0.6):
        continue
    
    text_lines.append(line)
```

**方案 B: 檢測異常短的 OCR 結果**

```python
ocr_text = '\n'.join(text_lines).strip()

# ✅ 檢查 OCR 結果是否異常短
if len(ocr_text) < 50:  # 少於 50 字元視為異常
    print(f"⚠️ 警告：OCR 結果異常短（{len(ocr_text)} 字元），可能是辨識失敗")
    print(f"OCR 結果內容: {ocr_text}")
    
    # 檢查是否主要是 Prompt 內容
    if prompt and len(ocr_text) > 0:
        prompt_overlap = len(set(prompt.split()) & set(ocr_text.split())) / len(set(ocr_text.split()))
        if prompt_overlap > 0.7:  # 70% 以上重疊
            print(f"❌ OCR 結果疑似為 Prompt 重複，將返回空結果")
            return {
                'error': 'OCR 辨識失敗：模型返回 Prompt 重複內容，請重新拍攝更清晰的照片',
                'image_path': image_path,
                'processing_time': round(elapsed_time, 2),
                'gpu_info': gpu_info
            }
```

### 方案 3: 改進拍攝品質提示

**檔案**：`example_bookReader/templates/book_reader.html`

在界面上添加拍攝提示：

```html
<div class="photo-tips">
    <h4>📸 拍攝提示</h4>
    <ul>
        <li>✅ 確保光線充足</li>
        <li>✅ 文字清晰可讀</li>
        <li>✅ 避免反光和陰影</li>
        <li>✅ 相機與書本保持水平</li>
        <li>❌ 避免手震和模糊</li>
    </ul>
</div>
```

### 方案 4: 添加 OCR 結果驗證

**檔案**：`example_bookReader/static/js/book_reader.js`

在前端檢查 OCR 結果：

```javascript
// 顯示 OCR 結果前檢查
if (result.status === 'completed' && result.text) {
    const cleanText = filterSystemMessages(result.text);
    
    // ✅ 檢查結果是否太短
    if (cleanText.length < 20) {
        console.warn('OCR 結果過短，可能辨識失敗');
        content = `
            <div class="result-warning">⚠️ OCR 辨識結果過短</div>
            <p style="margin-top: 10px;">可能原因：</p>
            <ul>
                <li>圖片模糊或光線不足</li>
                <li>文字不清晰</li>
                <li>相機角度不佳</li>
            </ul>
            <p style="margin-top: 10px;">建議：重新拍攝更清晰的照片</p>
        `;
    } else {
        content = `
            <div class="result-success">✅ OCR 辨識成功！</div>
            <div class="result-item-text" style="margin-top: 15px; white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(cleanText)}</div>
        `;
    }
}
```

---

## 實施建議

### 優先級 1: 改進圖片尺寸處理（立即實施）

```python
# /GPUData/working/Deepseek-OCR/ocr_service.py
# 修改 base_size 和 image_size
inference_result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=temp_output,
    base_size=2048,     # 從 1024 增加到 2048
    image_size=1024,    # 從 640 增加到 1024
    crop_mode=True,
    save_results=False,
    test_compress=False
)
```

### 優先級 2: 強化異常檢測（建議實施）

在 `ocr_service.py` 的 `perform_ocr()` 方法中添加結果驗證：

```python
# 檢查 OCR 結果是否異常
if ocr_text and len(ocr_text) < 50:
    print(f"⚠️ 警告：OCR 結果異常短（{len(ocr_text)} 字元）")
    
    # 檢查是否與 Prompt 高度重疊
    if prompt:
        prompt_words = set(prompt.split())
        ocr_words = set(ocr_text.split())
        if ocr_words and len(prompt_words & ocr_words) / len(ocr_words) > 0.7:
            return {
                'error': 'OCR 辨識失敗：請確保照片清晰、光線充足',
                'image_path': image_path,
                'processing_time': round(elapsed_time, 2),
                'debug_info': {
                    'ocr_text_length': len(ocr_text),
                    'prompt_overlap': len(prompt_words & ocr_words) / len(ocr_words) if ocr_words else 0
                }
            }
```

### 優先級 3: 用戶界面改進（後續實施）

- 添加拍攝提示
- 改進錯誤訊息顯示
- 提供重新拍攝建議

---

## 測試驗證

### 測試案例 1: 清晰照片

1. 確保光線充足
2. 文字清晰可讀
3. 拍攝照片並執行 OCR
4. **預期結果**：正確辨識書本文字，無 Prompt 重複

### 測試案例 2: 模糊照片

1. 故意拍攝模糊照片
2. 執行 OCR
3. **預期結果**：系統檢測到結果異常，提示用戶重新拍攝

### 測試案例 3: 不同解析度

| 解析度 | base_size | image_size | 預期結果 |
|--------|-----------|------------|----------|
| 1280x720 | 1024 | 640 | 可能失敗 |
| 1920x1080 | 1024 | 640 | 可能失敗 |
| 1920x1080 | 2048 | 1024 | 應該成功 ✅ |

---

## 總結

**問題**：1920x1080 照片的 OCR 有時只返回 Prompt 重複內容。

**根本原因**：
1. 圖片在處理時被大幅縮小（1024→640），文字不清晰
2. OCR 模型產生"幻覺"，返回 Prompt 內容而非實際文字
3. 過濾邏輯沒有檢測和處理這種異常情況

**解決方案**：
1. ✅ **立即實施**：增加 `base_size` 和 `image_size`
2. ✅ **建議實施**：添加異常檢測和 Prompt 去重邏輯
3. ⏰ **後續實施**：改進用戶界面和錯誤提示

實施這些改進後，OCR 準確度應該會明顯提升，Prompt 重複問題應該會大幅減少。

