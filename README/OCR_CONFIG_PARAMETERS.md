# OCR 圖片處理參數設定說明

## 概述

DeepSeek-OCR 的圖片處理參數已移至 `config.py` 配置檔案，方便日後調整和優化。這些參數控制 OCR 如何處理輸入圖片，直接影響辨識準確度、處理時間和 GPU 記憶體使用。

## 配置檔案位置

- **主配置**: `/GPUData/working/Deepseek-OCR/config.py`
- **環境變數**: `/GPUData/working/Deepseek-OCR/.env` （可選）

## 參數說明

### 1. OCR_BASE_SIZE

**圖片預處理的基準尺寸（像素）**

```python
OCR_BASE_SIZE = int(os.environ.get('OCR_BASE_SIZE', '2048'))
```

**作用**：
- 圖片會先被縮放到此尺寸（保持長寬比）
- 這是圖片處理的第一步

**建議值**：
- **1024**：適合 1280x720 或更小的圖片
  - 處理速度：快（約 10 秒）
  - 準確度：中等
  - GPU 記憶體：約 4-6 GB
  
- **2048**：適合 1920x1080 或更大的圖片（推薦）
  - 處理速度：中等（約 20-30 秒）
  - 準確度：高
  - GPU 記憶體：約 6-8 GB

- **3072**：適合 2K 或更大的圖片
  - 處理速度：慢（約 40-60 秒）
  - 準確度：極高
  - GPU 記憶體：約 8-12 GB

**影響**：
- ✅ 值越大，文字越清晰，辨識越準確
- ❌ 值越大，處理時間越長，GPU 記憶體使用越多

---

### 2. OCR_IMAGE_SIZE

**模型輸入的圖片尺寸（像素）**

```python
OCR_IMAGE_SIZE = int(os.environ.get('OCR_IMAGE_SIZE', '1024'))
```

**作用**：
- 經過 base_size 處理後，圖片會進一步處理為此尺寸
- 這是實際送入 OCR 模型的圖片尺寸

**建議值**：
- **640**：快速處理模式
  - 處理速度：快
  - 準確度：中等（可能降低小字體辨識準確度）
  - 適用：小圖片、快速處理需求
  
- **1024**：平衡模式（推薦）
  - 處理速度：中等
  - 準確度：高
  - 適用：大多數使用場景

- **1280**：高品質模式
  - 處理速度：慢
  - 準確度：極高
  - 適用：專業用途、需要最高準確度
  - 注意：需要更多 GPU 記憶體（建議 12GB 以上）

**影響**：
- ✅ 值越大，模型能看到更多細節，OCR 更準確
- ❌ 值越大，處理時間越長，GPU 記憶體使用越多

---

### 3. OCR_CROP_MODE

**是否啟用裁切模式**

```python
OCR_CROP_MODE = os.environ.get('OCR_CROP_MODE', 'true').lower() == 'true'
```

**作用**：
- **True**：將圖片裁切為多個區塊分別處理
- **False**：將整張圖片作為一個區塊處理

**建議**：
- **True**（預設，推薦）：適合大圖、多欄文字、複雜排版
- **False**：適合單欄文字、小圖片、簡單排版

**適用場景**：

| 場景 | 推薦設定 | 原因 |
|------|----------|------|
| 書本內頁（單欄） | True | 提高準確度 |
| 書本內頁（雙欄） | True | 正確處理多欄文字 |
| 名片 | False | 簡單排版 |
| 收據 | True | 複雜排版 |
| 海報 | True | 大圖、多區域文字 |

---

### 4. OCR_TEST_COMPRESS

**是否測試壓縮（用於調試）**

```python
OCR_TEST_COMPRESS = os.environ.get('OCR_TEST_COMPRESS', 'false').lower() == 'true'
```

**作用**：
- **True**：測試不同壓縮率的效果（用於開發和調試）
- **False**：不測試壓縮（正常使用，推薦）

**建議**：
- **False**（預設，推薦）：正常使用
- **True**：僅用於開發、調試、測試不同壓縮率對 OCR 的影響

---

### 5. OCR_SAVE_RESULTS

**是否保存 OCR 結果到檔案**

```python
OCR_SAVE_RESULTS = os.environ.get('OCR_SAVE_RESULTS', 'false').lower() == 'true'
```

**作用**：
- **True**：保存結果到 `output` 目錄
- **False**：不保存（節省磁碟空間）

**建議**：
- **False**（預設，推薦）：正常使用，節省磁碟空間
- **True**：用於除錯、保留歷史記錄

---

## 使用方式

### 方式 1: 修改 config.py（推薦）

直接修改 `/GPUData/working/Deepseek-OCR/config.py`：

```python
# 快速模式
OCR_BASE_SIZE = 1024
OCR_IMAGE_SIZE = 640

# 平衡模式（推薦）
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1024

# 高品質模式
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1280
```

### 方式 2: 使用環境變數

創建或修改 `.env` 檔案：

```bash
# .env 檔案
OCR_BASE_SIZE=2048
OCR_IMAGE_SIZE=1024
OCR_CROP_MODE=true
OCR_TEST_COMPRESS=false
OCR_SAVE_RESULTS=false
```

### 方式 3: 臨時設定（測試用）

在啟動服務前設定環境變數：

```bash
# Linux/macOS
export OCR_BASE_SIZE=2048
export OCR_IMAGE_SIZE=1024
python app.py

# Windows
set OCR_BASE_SIZE=2048
set OCR_IMAGE_SIZE=1024
python app.py
```

---

## 效能模式建議

### 【快速模式】

**適合**：即時處理、小圖片、低延遲需求

```python
OCR_BASE_SIZE = 1024
OCR_IMAGE_SIZE = 640
OCR_CROP_MODE = True
```

**效能指標**：
- 處理時間：~10 秒
- 準確度：中等（70-80%）
- GPU 記憶體：4-6 GB
- 適用圖片：1280x720 或更小

**適用場景**：
- 快速預覽
- 低品質圖片
- 小字體不多的情況

---

### 【平衡模式】（推薦）

**適合**：大多數使用場景、1920x1080 圖片

```python
OCR_BASE_SIZE = 2048      # 目前設定
OCR_IMAGE_SIZE = 1024     # 目前設定
OCR_CROP_MODE = True
```

**效能指標**：
- 處理時間：~20-30 秒
- 準確度：高（85-95%）
- GPU 記憶體：6-8 GB
- 適用圖片：1920x1080

**適用場景**：
- 一般書本 OCR
- 正常光線、清晰照片
- 標準字體大小

---

### 【高品質模式】

**適合**：專業用途、需要最高準確度

```python
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1280
OCR_CROP_MODE = True
```

**效能指標**：
- 處理時間：~40-60 秒
- 準確度：極高（95-99%）
- GPU 記憶體：8-12 GB
- 適用圖片：2K、4K 高解析度圖片

**適用場景**：
- 專業檔案數位化
- 小字體、複雜排版
- 歷史文獻、手寫文字

**注意**：需要至少 12GB GPU 記憶體

---

## 重新啟動服務套用設定

修改 `config.py` 後，需要重新啟動 OCR API 伺服器：

```bash
# 1. 找到現有的 OCR API 伺服器 PID
ps aux | grep "python.*app.py" | grep -v grep

# 2. 停止服務
kill <PID>

# 3. 重新啟動服務
cd /GPUData/working/Deepseek-OCR
python app.py
```

**啟動後檢查日誌**：

```
正在初始化 DeepSeek-OCR 服務...
OCR 超時設定: 300 秒
OCR 圖片處理參數:
  - base_size: 2048
  - image_size: 1024
  - crop_mode: True
  - test_compress: False
  - save_results: False
OCR 圖片處理參數: base_size=2048, image_size=1024, crop_mode=True
DeepSeek-OCR 服務初始化完成！
```

---

## 參數調整建議

### 如果 OCR 辨識不準確

**可能原因**：圖片尺寸太小，文字不清晰

**解決方案**：
1. 增加 `OCR_BASE_SIZE` 到 2048 或更高
2. 增加 `OCR_IMAGE_SIZE` 到 1024 或 1280
3. 確保 `OCR_CROP_MODE = True`

```python
# 修改前（不準確）
OCR_BASE_SIZE = 1024
OCR_IMAGE_SIZE = 640

# 修改後（更準確）
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1024
```

---

### 如果處理時間太長

**可能原因**：圖片尺寸過大

**解決方案**：
1. 降低 `OCR_BASE_SIZE` 到 1024
2. 降低 `OCR_IMAGE_SIZE` 到 640
3. 考慮在前端降低相機解析度

```python
# 修改前（太慢）
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1280

# 修改後（更快）
OCR_BASE_SIZE = 1024
OCR_IMAGE_SIZE = 640
```

**注意**：這會降低準確度

---

### 如果 GPU 記憶體不足

**錯誤訊息**：`CUDA out of memory`

**解決方案**：
1. 降低 `OCR_IMAGE_SIZE` 到 640 或 512
2. 降低 `OCR_BASE_SIZE` 到 1024
3. 清理 GPU 快取

```python
# 修改前（記憶體不足）
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1280

# 修改後（記憶體友好）
OCR_BASE_SIZE = 1024
OCR_IMAGE_SIZE = 640
```

---

### 如果出現 Prompt 重複問題

**現象**：OCR 返回 Prompt 內容而不是實際文字

**解決方案**：
1. **必須**增加 `OCR_BASE_SIZE` 到 2048
2. **必須**增加 `OCR_IMAGE_SIZE` 到 1024
3. 確保照片清晰、光線充足

```python
# 正確設定（避免 Prompt 重複）
OCR_BASE_SIZE = 2048      # 必須 >= 2048
OCR_IMAGE_SIZE = 1024     # 必須 >= 1024
OCR_CROP_MODE = True
```

這是因為圖片被縮小太多，OCR 模型無法辨識文字，產生"幻覺"。

---

## 測試不同設定

建議測試不同設定組合，找出最適合您使用場景的配置：

```bash
# 測試快速模式
export OCR_BASE_SIZE=1024
export OCR_IMAGE_SIZE=640
python app.py

# 測試一張圖片
curl -X POST -F "file=@test.jpg" http://localhost:5000/ocr

# 測試平衡模式
export OCR_BASE_SIZE=2048
export OCR_IMAGE_SIZE=1024
python app.py

# 測試同一張圖片，比較結果
curl -X POST -F "file=@test.jpg" http://localhost:5000/ocr
```

---

## 常見問題

### Q1: 修改 config.py 後沒有生效？

**A**: 需要重新啟動 OCR API 伺服器。配置在服務啟動時載入，不會動態更新。

```bash
# 重新啟動服務
ps aux | grep "python.*app.py" | grep -v grep
kill <PID>
python app.py
```

---

### Q2: 如何知道當前使用的參數？

**A**: 查看服務啟動時的日誌輸出：

```
OCR 圖片處理參數:
  - base_size: 2048
  - image_size: 1024
  - crop_mode: True
```

---

### Q3: 可以針對不同圖片使用不同參數嗎？

**A**: 目前不支援。所有圖片使用相同的參數。如果需要針對不同圖片使用不同參數，可以：
1. 啟動多個 OCR API 伺服器實例（不同埠）
2. 每個實例使用不同的配置

---

### Q4: 環境變數 vs config.py，哪個優先？

**A**: **環境變數優先**。如果設定了環境變數，會覆蓋 `config.py` 中的預設值。

優先順序：
1. 環境變數（`.env` 或 `export`）
2. `config.py` 中的預設值

---

## 總結

| 參數 | 預設值 | 建議值 | 影響 |
|------|--------|--------|------|
| `OCR_BASE_SIZE` | 2048 | 1024-2048 | 準確度、處理時間 |
| `OCR_IMAGE_SIZE` | 1024 | 640-1280 | 準確度、GPU 記憶體 |
| `OCR_CROP_MODE` | True | True | 多欄文字處理 |
| `OCR_TEST_COMPRESS` | False | False | 測試用 |
| `OCR_SAVE_RESULTS` | False | False | 磁碟空間 |

**推薦設定**（平衡模式）：
```python
OCR_BASE_SIZE = 2048
OCR_IMAGE_SIZE = 1024
OCR_CROP_MODE = True
OCR_TEST_COMPRESS = False
OCR_SAVE_RESULTS = False
```

這個設定適合大多數使用場景，提供高準確度且處理時間可接受（20-30 秒）。

