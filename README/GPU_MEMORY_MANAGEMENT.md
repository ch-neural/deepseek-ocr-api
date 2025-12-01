# DeepSeek-OCR GPU 記憶體管理分析

## 問題概述

用戶詢問：DeepSeek-OCR API 在使用時，會隨著傳入的檔案以及處理，增加 GPU 的使用嗎？最後會不會因記憶體不夠而 crash？

## 現況分析

### 1. 模型載入方式

**單例模式**：模型在服務啟動時載入一次，之後重複使用

```python
# app.py 第 32 行
ocr_service = DeepSeekOCRService(ocr_timeout=ocr_timeout)
```

**優點**：
- 避免每次請求都重新載入模型（載入模型需要數秒到數十秒）
- 減少初始化開銷

**缺點**：
- 模型常駐 GPU 記憶體（約 3-6 GB）
- 無法動態釋放模型記憶體

### 2. 記憶體管理機制

#### ✅ 已實作的功能

1. **GPU 記憶體檢查**（`ocr_service.py` 第 230-246 行）
   - 處理前檢查 GPU 記憶體狀態
   - 如果使用率 > 95% 或可用記憶體 < 500MB，拒絕請求
   - 處理前後記錄 GPU 記憶體狀態

2. **批次處理自動清理**（`ocr_service.py` 第 416-418 行）
   - 每處理 5 張圖片清理一次 GPU 快取
   - 批次處理完成後清理一次

3. **GPU 快取清理方法**（`ocr_service.py` 第 375-387 行）
   ```python
   def clear_gpu_cache(self):
       torch.cuda.empty_cache()
       torch.cuda.synchronize()
   ```

#### ❌ 缺失的功能

1. **單張圖片處理時沒有自動清理**
   - 每次處理單張圖片後，GPU 快取不會自動清理
   - 連續處理多張大圖片時，記憶體可能累積

2. **沒有主動釋放中間結果**
   - 處理過程中的臨時張量（tensors）可能沒有及時釋放
   - 依賴 Python 的垃圾回收機制

3. **沒有記憶體使用上限保護**
   - 只檢查處理前記憶體，不檢查處理中記憶體增長
   - 如果單次處理需要大量記憶體，可能導致 OOM

### 3. 記憶體使用模式

#### 模型基礎記憶體（常駐）

- **模型權重**：約 3-6 GB（取決於精度）
- **模型緩存**：約 0.5-1 GB
- **總計**：約 4-7 GB 常駐記憶體

#### 處理時動態記憶體

- **輸入圖片張量**：取決於圖片尺寸
  - 640x640：約 0.5 MB
  - 1024x1024：約 1.2 MB
  - 2048x2048：約 4.8 MB
- **中間計算結果**：約為輸入的 2-5 倍
- **輸出張量**：取決於文字長度

#### 記憶體累積風險

**單張圖片處理**：
- 處理完成後，中間結果應該被釋放
- 但 GPU 快取可能保留未使用的記憶體塊
- 連續處理時可能累積

**批次處理**：
- 每 5 張清理一次，風險較低
- 但單張處理時沒有清理機制

## 潛在問題

### 1. 記憶體累積

**場景**：連續處理多張大圖片（如 2048x2048）

```
處理第 1 張：記憶體使用 7.5 GB
處理第 2 張：記憶體使用 8.0 GB（累積）
處理第 3 張：記憶體使用 8.5 GB（累積）
...
處理第 10 張：記憶體使用 11 GB（可能 OOM）
```

**原因**：
- `torch.cuda.empty_cache()` 只清理未使用的快取
- 如果中間結果沒有及時釋放，記憶體會累積
- 單張處理時沒有清理機制

### 2. 單次處理記憶體峰值

**場景**：處理超大圖片（如 4000x3000）

```
模型基礎：7 GB
輸入張量：約 20 MB
中間計算：約 100-200 MB（多個區塊）
峰值記憶體：可能達到 8-9 GB
```

**風險**：
- 如果 GPU 只有 8 GB，可能導致 OOM
- 沒有在處理中監控記憶體增長

### 3. 長時間運行記憶體洩漏

**場景**：服務運行數小時，處理數百張圖片

**可能原因**：
- Python 垃圾回收可能不及時
- PyTorch 的記憶體管理可能有小量洩漏
- 模型內部緩存可能累積

## 改進建議

### 1. 單張處理後自動清理（建議實作）

**修改位置**：`ocr_service.py` 的 `perform_ocr` 方法

```python
def perform_ocr(self, image_path, custom_prompt=None):
    # ... 現有程式碼 ...
    
    if ocr_text and len(ocr_text) > 0:
        # 檢查 OCR 後的 GPU 記憶體狀態
        gpu_info_after = check_gpu_memory()
        print(f"OCR 後 GPU 記憶體狀態: {gpu_info_after}")
        
        # 如果記憶體使用率超過 80%，清理快取
        if gpu_info_after['usage_percent'] > 80:
            self.clear_gpu_cache()
        
        return {
            'text': ocr_text,
            # ... 其他欄位 ...
        }
```

### 2. 處理中記憶體監控（進階）

**實作方式**：在處理過程中定期檢查記憶體

```python
def _perform_ocr_inference(self):
    """實際執行 OCR 推理的內部函數"""
    # 設定記憶體監控
    import threading
    
    def monitor_memory():
        while not self._stop_monitoring:
            gpu_info = check_gpu_memory()
            if gpu_info['usage_percent'] > 95:
                print(f"警告：GPU 記憶體使用率過高 ({gpu_info['usage_percent']}%)")
            time.sleep(1)
    
    # 啟動監控線程
    monitor_thread = threading.Thread(target=monitor_memory, daemon=True)
    monitor_thread.start()
    
    # 執行推理
    result = self.model.infer(...)
    
    # 停止監控
    self._stop_monitoring = True
    return result
```

### 3. 主動釋放中間結果（進階）

**實作方式**：在處理完成後明確釋放變數

```python
def perform_ocr(self, image_path, custom_prompt=None):
    # ... 處理邏輯 ...
    
    try:
        result = self.model.infer(...)
    finally:
        # 明確釋放臨時變數
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    return result
```

### 4. 記憶體使用上限保護（建議實作）

**修改位置**：`ocr_service.py` 的 `perform_ocr` 方法

```python
def perform_ocr(self, image_path, custom_prompt=None):
    # 檢查 GPU 記憶體狀態
    gpu_info = check_gpu_memory()
    
    # 設定記憶體使用上限（例如：總記憶體的 90%）
    memory_limit = gpu_info['total_mb'] * 0.9
    
    if gpu_info['used_mb'] > memory_limit:
        error_msg = f"GPU 記憶體使用率過高 ({gpu_info['usage_percent']}%)，請稍後再試或清理記憶體"
        return {
            'error': error_msg,
            'gpu_info': gpu_info
        }
    
    # ... 繼續處理 ...
```

### 5. 定期清理機制（建議實作）

**實作方式**：在 Flask 應用中添加定期清理任務

```python
# app.py
import threading
import time

def periodic_cleanup():
    """定期清理 GPU 快取"""
    while True:
        time.sleep(300)  # 每 5 分鐘清理一次
        gpu_info = ocr_service.check_gpu_memory()
        if gpu_info['usage_percent'] > 70:
            ocr_service.clear_gpu_cache()
            print(f"定期清理 GPU 快取完成")

# 啟動清理線程
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()
```

## 實際測試建議

### 測試 1：連續處理多張圖片

```python
import requests

# 連續處理 20 張圖片
for i in range(20):
    with open(f'image_{i}.png', 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:5000/ocr', files=files)
        print(f"處理第 {i+1} 張，記憶體狀態：{response.json().get('gpu_info_after', {})}")
```

**觀察重點**：
- 記憶體使用是否持續增長
- 是否在處理某張圖片時 OOM

### 測試 2：處理超大圖片

```python
# 處理 4000x3000 的大圖片
with open('large_image.png', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/ocr', files=files)
    print(f"記憶體狀態：{response.json().get('gpu_info_after', {})}")
```

**觀察重點**：
- 處理時的記憶體峰值
- 是否導致 OOM

### 測試 3：長時間運行

```python
# 運行服務數小時，處理數百張圖片
# 使用 nvidia-smi 監控記憶體
nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1
```

**觀察重點**：
- 記憶體是否持續增長
- 是否有記憶體洩漏跡象

## 結論

### 現況評估

1. **模型載入**：✅ 單例模式，避免重複載入
2. **記憶體檢查**：✅ 處理前檢查，有基本保護
3. **批次清理**：✅ 批次處理時有清理機制
4. **單張清理**：❌ 單張處理時沒有自動清理
5. **記憶體監控**：⚠️ 只有處理前後檢查，沒有處理中監控

### 風險評估

**低風險場景**：
- 處理小圖片（≤ 1024x1024）
- 處理頻率低（每分鐘 < 5 張）
- GPU 記憶體充足（≥ 12 GB）

**中風險場景**：
- 處理中等圖片（1024-2048）
- 處理頻率中等（每分鐘 5-20 張）
- GPU 記憶體中等（8-12 GB）

**高風險場景**：
- 處理大圖片（> 2048x2048）
- 處理頻率高（每分鐘 > 20 張）
- GPU 記憶體不足（< 8 GB）

### 建議行動

1. **立即實作**：單張處理後自動清理（如果記憶體使用率 > 80%）
2. **短期改進**：添加記憶體使用上限保護
3. **長期優化**：實作處理中記憶體監控和定期清理機制

### 監控建議

1. **使用 nvidia-smi 監控**
   ```bash
   watch -n 1 nvidia-smi
   ```

2. **記錄記憶體使用日誌**
   - 每次處理前後記錄記憶體狀態
   - 分析記憶體增長趨勢

3. **設定告警**
   - 記憶體使用率 > 90% 時告警
   - 記憶體使用率 > 95% 時拒絕請求（已實作）

## 相關檔案

- `ocr_service.py`：OCR 服務實作
- `app.py`：Flask 應用主程式
- `README/SERVER_TIMEOUT_FIX.md`：超時和記憶體管理相關文檔

## 實作記錄

### 2025-01-12：單張處理後自動清理機制

**實作內容**：
- 在 `perform_ocr` 方法中添加自動清理機制
- 處理完成後檢查 GPU 記憶體使用率
- 如果使用率超過 80%，自動清理 GPU 快取
- 記錄清理前後的記憶體狀態和釋放的記憶體量

**修改位置**：`ocr_service.py` 第 357-365 行、第 379-383 行

**實作邏輯**：
```python
# 如果記憶體使用率超過 80%，自動清理 GPU 快取
if gpu_info_after['available'] and gpu_info_after['usage_percent'] > 80:
    print(f"GPU 記憶體使用率較高 ({gpu_info_after['usage_percent']}%)，執行自動清理...")
    gpu_before_cleanup = gpu_info_after['used_mb']
    self.clear_gpu_cache()
    gpu_info_after_cleanup = check_gpu_memory()
    memory_freed = gpu_before_cleanup - gpu_info_after_cleanup['used_mb']
    print(f"自動清理完成，釋放記憶體: {memory_freed:.2f} MB")
    gpu_info_after = gpu_info_after_cleanup
```

**效果**：
- ✅ 單張處理後自動檢查記憶體使用率
- ✅ 超過閾值時自動清理 GPU 快取
- ✅ 降低記憶體累積風險
- ✅ 記錄清理效果（釋放的記憶體量）

**注意事項**：
- 清理閾值設定為 80%，可根據實際需求調整
- 清理只會釋放未使用的快取，不會影響正在使用的記憶體
- 處理失敗時也會檢查並清理記憶體（如果使用率過高）

## 更新記錄

- **2025-01-12**：初始版本，分析 GPU 記憶體管理機制和潛在問題
- **2025-01-12**：實作單張處理後自動清理機制

