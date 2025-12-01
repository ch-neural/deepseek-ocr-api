# DeepSeek-OCR API 詳細文檔

## 概述

DeepSeek-OCR API 提供了強大的圖片文字辨識（OCR）功能。本文檔詳細說明了所有 API 端點的使用方式、參數、回應格式和範例。

## 基本資訊

- **基礎 URL**: `http://localhost:5000`
- **API 版本**: 1.0.0
- **支援的請求格式**: `multipart/form-data`
- **回應格式**: `application/json`
- **字元編碼**: UTF-8

## 認證

目前版本不需要認證。未來版本可能會加入 API Key 認證機制。

## 速率限制

目前沒有速率限制。建議在生產環境中加入適當的速率限制機制。

---

## API 端點

### 1. 健康檢查

檢查 API 服務是否正常運行。

#### 端點資訊

- **URL**: `/health`
- **方法**: `GET`
- **認證**: 不需要

#### 請求參數

無

#### 回應格式

**成功回應** (HTTP 200)

```json
{
  "status": "healthy",
  "service": "DeepSeek-OCR API",
  "timestamp": "2025-11-10T12:34:56.789012"
}
```

#### 回應欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| status | string | 服務狀態，值為 "healthy" |
| service | string | 服務名稱 |
| timestamp | string | ISO 8601 格式的時間戳記 |

#### 使用範例

**cURL**:
```bash
curl http://localhost:5000/health
```

**Python**:
```python
import requests

response = requests.get('http://localhost:5000/health')
print(response.json())
```

**JavaScript**:
```javascript
fetch('http://localhost:5000/health')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

### 2. 單張圖片 OCR

對單張圖片執行 OCR 文字辨識。

#### 端點資訊

- **URL**: `/ocr`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`
- **認證**: 不需要

#### 請求參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| file | file | 是 | 要辨識的圖片檔案 |
| prompt | string | 否 | 自訂提示詞，預設為 `<image>\nFree OCR.` |

#### 支援的圖片格式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

#### 檔案大小限制

- 最大: 16 MB

#### 回應格式

**成功回應** (HTTP 200)

```json
{
  "text": "辨識出的完整文字內容...",
  "image_path": "uploads/20251110_123456_image.png",
  "prompt": "<image>\nFree OCR."
}
```

**錯誤回應** (HTTP 400)

```json
{
  "error": "請求中沒有檔案部分"
}
```

```json
{
  "error": "未選擇檔案"
}
```

```json
{
  "error": "不支援的檔案類型。允許的類型: png, jpg, jpeg, gif, bmp, webp"
}
```

**錯誤回應** (HTTP 413)

```json
{
  "error": "上傳的檔案過大，最大允許 16MB"
}
```

**錯誤回應** (HTTP 500)

```json
{
  "error": "圖片檔案不存在: /path/to/image.png",
  "image_path": "/path/to/image.png"
}
```

```json
{
  "error": "模型未返回任何結果",
  "image_path": "/path/to/image.png"
}
```

#### 回應欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| text | string | OCR 辨識的文字結果 |
| image_path | string | 暫存圖片的路徑（僅供參考，處理完會刪除） |
| prompt | string | 使用的提示詞 |
| error | string | 錯誤訊息（僅在錯誤時出現） |

#### 使用範例

**cURL - 基本使用**:
```bash
curl -X POST \
  -F "file=@/path/to/image.png" \
  http://localhost:5000/ocr
```

**cURL - 使用自訂提示詞**:
```bash
curl -X POST \
  -F "file=@/path/to/image.png" \
  -F "prompt=<image>\n請辨識圖片中的所有文字，包含中文和英文。" \
  http://localhost:5000/ocr
```

**Python - 基本使用**:
```python
import requests

with open('image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    
if response.status_code == 200:
    result = response.json()
    print(f"辨識結果: {result['text']}")
else:
    print(f"錯誤: {response.json()['error']}")
```

**Python - 使用自訂提示詞**:
```python
import requests

with open('document.jpg', 'rb') as f:
    files = {'file': f}
    data = {'prompt': '<image>\n請辨識這份文件中的所有文字，保持原有的格式和結構。'}
    response = requests.post('http://localhost:5000/ocr', files=files, data=data)
    
result = response.json()
print(result['text'])
```

**Python - 完整錯誤處理**:
```python
import requests

def perform_ocr(image_path, custom_prompt=None):
    """
    執行 OCR 辨識
    
    Args:
        image_path: 圖片檔案路徑
        custom_prompt: 自訂提示詞（選填）
    
    Returns:
        辨識的文字或 None（如果失敗）
    """
    url = 'http://localhost:5000/ocr'
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'prompt': custom_prompt} if custom_prompt else {}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            return result['text']
        elif response.status_code == 400:
            print(f"請求錯誤: {response.json()['error']}")
            return None
        elif response.status_code == 413:
            print(f"檔案過大: {response.json()['error']}")
            return None
        elif response.status_code == 500:
            print(f"伺服器錯誤: {response.json()['error']}")
            return None
        else:
            print(f"未知錯誤: HTTP {response.status_code}")
            return None

# 使用範例
text = perform_ocr('document.png')
if text:
    print(f"辨識成功: {text}")
```

**JavaScript (Node.js) - 使用 FormData**:
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function performOCR(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  
  try {
    const response = await axios.post('http://localhost:5000/ocr', form, {
      headers: form.getHeaders()
    });
    
    console.log('辨識結果:', response.data.text);
    return response.data.text;
  } catch (error) {
    if (error.response) {
      console.error('錯誤:', error.response.data.error);
    } else {
      console.error('請求失敗:', error.message);
    }
    return null;
  }
}

// 使用範例
performOCR('document.png');
```

**JavaScript (Browser) - 使用 fetch**:
```javascript
async function uploadAndOCR(fileInput) {
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  
  try {
    const response = await fetch('http://localhost:5000/ocr', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok) {
      console.log('辨識結果:', result.text);
      return result.text;
    } else {
      console.error('錯誤:', result.error);
      return null;
    }
  } catch (error) {
    console.error('請求失敗:', error);
    return null;
  }
}

// HTML 使用範例
// <input type="file" id="imageInput" accept="image/*">
// <button onclick="uploadAndOCR(document.getElementById('imageInput'))">辨識</button>
```

---

### 3. 批次圖片 OCR

對多張圖片執行批次 OCR 文字辨識。

#### 端點資訊

- **URL**: `/ocr/batch`
- **方法**: `POST`
- **Content-Type**: `multipart/form-data`
- **認證**: 不需要

#### 請求參數

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| files | file[] | 是 | 要辨識的多個圖片檔案 |
| prompt | string | 否 | 自訂提示詞，預設為 `<image>\nFree OCR.` |

#### 限制

- 每個檔案最大: 16 MB
- 建議一次最多 10 張圖片（視伺服器效能而定）

#### 回應格式

**成功回應** (HTTP 200)

```json
{
  "results": [
    {
      "text": "第一張圖片的文字內容...",
      "image_path": "uploads/20251110_123456_0_image1.png",
      "prompt": "<image>\nFree OCR."
    },
    {
      "text": "第二張圖片的文字內容...",
      "image_path": "uploads/20251110_123456_1_image2.png",
      "prompt": "<image>\nFree OCR."
    },
    {
      "text": "第三張圖片的文字內容...",
      "image_path": "uploads/20251110_123456_2_image3.png",
      "prompt": "<image>\nFree OCR."
    }
  ],
  "total": 3
}
```

**錯誤回應** (HTTP 400)

```json
{
  "error": "請求中沒有檔案部分"
}
```

```json
{
  "error": "未選擇任何檔案"
}
```

```json
{
  "error": "沒有有效的圖片檔案"
}
```

#### 回應欄位說明

| 欄位 | 類型 | 說明 |
|------|------|------|
| results | array | OCR 結果陣列 |
| results[].text | string | 該圖片的 OCR 辨識文字 |
| results[].image_path | string | 該圖片的暫存路徑 |
| results[].prompt | string | 使用的提示詞 |
| total | integer | 成功處理的圖片數量 |
| error | string | 錯誤訊息（僅在錯誤時出現） |

#### 使用範例

**cURL**:
```bash
curl -X POST \
  -F "files=@/path/to/image1.png" \
  -F "files=@/path/to/image2.jpg" \
  -F "files=@/path/to/image3.png" \
  http://localhost:5000/ocr/batch
```

**cURL - 使用自訂提示詞**:
```bash
curl -X POST \
  -F "files=@/path/to/doc1.png" \
  -F "files=@/path/to/doc2.png" \
  -F "prompt=<image>\n請辨識這些文件的所有文字。" \
  http://localhost:5000/ocr/batch
```

**Python - 基本使用**:
```python
import requests

# 準備多個檔案
files = [
    ('files', open('image1.png', 'rb')),
    ('files', open('image2.jpg', 'rb')),
    ('files', open('image3.png', 'rb'))
]

response = requests.post('http://localhost:5000/ocr/batch', files=files)

# 記得關閉所有檔案
for _, f in files:
    f.close()

if response.status_code == 200:
    result = response.json()
    print(f"處理了 {result['total']} 張圖片")
    
    for idx, item in enumerate(result['results']):
        print(f"\n圖片 {idx + 1}:")
        print(item['text'])
else:
    print(f"錯誤: {response.json()['error']}")
```

**Python - 使用 with 語句**:
```python
import requests

image_paths = ['doc1.png', 'doc2.png', 'doc3.png']

# 使用 with 語句自動管理檔案
with requests.Session() as session:
    files = [('files', (path, open(path, 'rb'))) for path in image_paths]
    
    response = session.post('http://localhost:5000/ocr/batch', files=files)
    
    # 關閉所有檔案
    for _, (_, f) in files:
        f.close()
    
    result = response.json()
    
    # 處理結果
    for idx, item in enumerate(result['results'], 1):
        print(f"\n=== 文件 {idx} ({image_paths[idx-1]}) ===")
        print(item['text'])
        print("=" * 50)
```

**Python - 批次處理函數**:
```python
import requests
import os

def batch_ocr(image_paths, custom_prompt=None):
    """
    批次執行 OCR 辨識
    
    Args:
        image_paths: 圖片檔案路徑列表
        custom_prompt: 自訂提示詞（選填）
    
    Returns:
        包含所有辨識結果的字典，或 None（如果失敗）
    """
    url = 'http://localhost:5000/ocr/batch'
    
    # 檢查所有檔案是否存在
    valid_paths = [path for path in image_paths if os.path.exists(path)]
    
    if not valid_paths:
        print("錯誤: 沒有有效的圖片檔案")
        return None
    
    # 準備檔案
    files = [('files', open(path, 'rb')) for path in valid_paths]
    data = {'prompt': custom_prompt} if custom_prompt else {}
    
    response = requests.post(url, files=files, data=data)
    
    # 關閉所有檔案
    for _, f in files:
        f.close()
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"錯誤: {response.json()['error']}")
        return None

# 使用範例
images = ['page1.png', 'page2.png', 'page3.png', 'page4.png']
result = batch_ocr(images)

if result:
    print(f"成功處理 {result['total']} 張圖片")
    
    # 將所有文字合併
    full_text = '\n\n--- 新頁面 ---\n\n'.join(
        item['text'] for item in result['results']
    )
    
    # 儲存到檔案
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    print("結果已儲存到 output.txt")
```

**JavaScript (Node.js)**:
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function batchOCR(imagePaths) {
  const form = new FormData();
  
  // 添加所有圖片檔案
  imagePaths.forEach(path => {
    form.append('files', fs.createReadStream(path));
  });
  
  try {
    const response = await axios.post('http://localhost:5000/ocr/batch', form, {
      headers: form.getHeaders()
    });
    
    console.log(`成功處理 ${response.data.total} 張圖片`);
    
    response.data.results.forEach((item, index) => {
      console.log(`\n圖片 ${index + 1}:`);
      console.log(item.text);
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('錯誤:', error.response.data.error);
    } else {
      console.error('請求失敗:', error.message);
    }
    return null;
  }
}

// 使用範例
const images = ['page1.png', 'page2.png', 'page3.png'];
batchOCR(images);
```

---

## 提示詞（Prompt）使用指南

### 預設提示詞

```
<image>\nFree OCR.
```

這是 DeepSeek-OCR 的標準提示詞，適用於大多數一般 OCR 需求。

### 自訂提示詞範例

#### 1. 中文文件辨識

```
<image>\n請辨識圖片中的所有中文文字，保持原有的格式和結構。
```

#### 2. 表格辨識

```
<image>\n請辨識這個表格的所有內容，包含表頭和所有資料列。
```

#### 3. 手寫文字辨識

```
<image>\n請辨識這張圖片中的手寫文字。
```

#### 4. 多語言文件

```
<image>\n請辨識圖片中的所有文字，包含中文、英文和數字。
```

#### 5. 名片辨識

```
<image>\n請辨識這張名片的所有資訊，包含姓名、職稱、公司、電話和電子郵件。
```

### 提示詞最佳實踐

1. **明確指定語言**: 如果文件包含特定語言，在提示詞中明確說明
2. **說明格式**: 如果需要保持特定格式（如表格、清單），在提示詞中說明
3. **指定重點**: 如果只需要辨識特定部分，在提示詞中說明
4. **簡潔明確**: 提示詞應該簡潔但明確，避免過於複雜

---

## HTTP 狀態碼

| 狀態碼 | 說明 |
|--------|------|
| 200 | 請求成功 |
| 400 | 請求參數錯誤 |
| 413 | 上傳檔案過大 |
| 500 | 伺服器內部錯誤 |

---

## 效能考量

### 處理時間

- 單張圖片: 1-5 秒（取決於圖片大小和內容複雜度）
- 批次處理: 效率比多次呼叫單張 API 高約 30-50%

### 最佳化建議

1. **圖片大小**: 建議將圖片調整到適當大小（最大 2048x2048）以加快處理速度
2. **批次處理**: 對於多張圖片，使用批次 API 而非多次呼叫單張 API
3. **並行請求**: 在客戶端可以使用多執行緒或非同步請求來提高吞吐量
4. **圖片格式**: PNG 和 JPEG 格式處理速度較快

---

## 錯誤處理最佳實踐

### 客戶端錯誤處理

```python
import requests
import time

def ocr_with_retry(image_path, max_retries=3, delay=1):
    """
    帶有重試機制的 OCR 請求
    
    Args:
        image_path: 圖片路徑
        max_retries: 最大重試次數
        delay: 重試延遲（秒）
    
    Returns:
        OCR 結果或 None
    """
    url = 'http://localhost:5000/ocr'
    
    for attempt in range(max_retries):
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                # 客戶端錯誤，不重試
                print(f"請求錯誤: {response.json()['error']}")
                return None
            elif response.status_code == 500:
                # 伺服器錯誤，可以重試
                if attempt < max_retries - 1:
                    print(f"伺服器錯誤，{delay} 秒後重試...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"達到最大重試次數: {response.json()['error']}")
                    return None
    
    return None

# 使用範例
result = ocr_with_retry('document.png')
if result:
    print(result['text'])
```

---

## 整合範例

### Flask Web 應用整合

```python
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': '沒有檔案'}), 400
    
    file = request.files['file']
    
    # 轉發到 DeepSeek-OCR API
    files = {'file': file}
    response = requests.post('http://localhost:5000/ocr', files=files)
    
    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(port=8000)
```

### Django 整合

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def ocr_view(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        
        # 轉發到 DeepSeek-OCR API
        files = {'file': file}
        response = requests.post('http://localhost:5000/ocr', files=files)
        
        return JsonResponse(response.json(), status=response.status_code)
    
    return JsonResponse({'error': '無效的請求'}, status=400)
```

---

## 版本歷史

### v1.0.0 (2025-11-10)

- 初始版本發布
- 支援單張和批次圖片 OCR
- 支援自訂提示詞
- 完整的錯誤處理機制

---

## 相關文檔

- [使用說明](README.md)
- [錯誤訊息說明](ERROR_MESSAGES.md)
- [DeepSeek-OCR 官方文檔](https://docs.unsloth.ai/new/deepseek-ocr-how-to-run-and-fine-tune)

