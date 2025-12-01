# Server 卡住問題修復說明

## 問題描述

Server 端有時會在執行 OCR 辨識時卡住不動，沒有回覆給客戶端。從日誌可以看到：

```
[werkzeug|INFO]172.30.17.72 - - [11/Nov/2025 10:32:53] "POST /ocr HTTP/1.1" 200 -
正在儲存上傳的檔案: uploads/20251111_103451_image.jpg
開始執行 OCR 辨識: uploads/20251111_103451_image.jpg
已載入圖片: uploads/20251111_103451_image.jpg
正在執行 OCR 辨識...
[之後就沒有任何回應]
```

## 問題原因

1. **缺少超時機制** - `model.infer()` 方法可能因為各種原因長時間執行，但沒有超時保護
2. **GPU 記憶體問題** - 沒有檢查 GPU 記憶體狀態，可能因記憶體不足而卡住
3. **缺乏錯誤處理** - 當模型推理出現問題時，沒有機制捕獲並回報錯誤
4. **記憶體洩漏** - 長時間運行可能導致 GPU 記憶體累積

## 修復方案

### 1. 添加超時保護機制

使用 Python 的 `signal` 模組實現超時機制：

```python
def timeout_handler(signum, frame):
    """超時處理函數"""
    raise TimeoutError("OCR 處理超時")

# 在執行 OCR 前設定超時
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(timeout_seconds)

try:
    # 執行 OCR
    result = self.model.infer(...)
except TimeoutError:
    # 處理超時錯誤
    return {'error': 'OCR 處理超時'}
finally:
    # 取消超時信號
    signal.alarm(0)
```

**特點**:
- 預設超時時間：300 秒（5 分鐘）
- 可透過環境變數 `OCR_TIMEOUT` 調整
- 超時後自動中止處理並返回錯誤訊息

### 2. GPU 記憶體監控

在執行 OCR 前檢查 GPU 記憶體狀態：

```python
def check_gpu_memory():
    """檢查 GPU 記憶體狀態"""
    if not torch.cuda.is_available():
        return {'available': False, ...}
    
    total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
    reserved = torch.cuda.memory_reserved(0) / (1024 ** 2)
    free = total - reserved
    
    return {
        'available': True,
        'total_mb': total,
        'used_mb': reserved,
        'free_mb': free,
        'usage_percent': (reserved / total) * 100
    }
```

**檢查項目**:
- GPU 是否可用
- 記憶體使用率是否超過 95%
- 可用記憶體是否少於 500MB
- 記憶體不足時拒絕請求

### 3. GPU 記憶體自動清理

批次處理時自動清理 GPU 快取：

```python
def clear_gpu_cache(self):
    """清理 GPU 快取記憶體"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
```

**清理時機**:
- 批次處理每 5 張圖片清理一次
- 批次處理完成後清理一次

### 4. 詳細的錯誤處理和日誌

```python
try:
    # 執行 OCR
    result = self.model.infer(...)
except TimeoutError as e:
    error_msg = f"OCR 處理超時 ({timeout} 秒)"
    print(f"超時錯誤: {error_msg}")
    return {'error': error_msg, ...}
except Exception as e:
    error_msg = f"OCR 處理發生錯誤: {str(e)}"
    print(f"處理錯誤: {error_msg}")
    print(f"錯誤詳情: {traceback.format_exc()}")
    return {'error': error_msg, ...}
```

**日誌內容**:
- GPU 記憶體狀態（處理前後）
- 處理時間
- 錯誤詳情和堆疊追蹤
- 批次處理進度

### 5. 處理時間統計

返回結果中包含處理時間資訊：

```python
{
    'text': '辨識結果',
    'processing_time': 12.34,  # 秒
    'gpu_info_before': {...},
    'gpu_info_after': {...}
}
```

## 使用方法

### 基本使用

服務會自動使用預設超時設定（300 秒）：

```bash
# 啟動服務
./start_server.sh

# 或直接運行
python app.py
```

### 自訂超時時間

#### 方法 1: 環境變數

```bash
# 設定 10 分鐘超時
export OCR_TIMEOUT=600
python app.py
```

#### 方法 2: 修改程式碼

在 `app.py` 中：

```python
# 初始化時指定超時時間（秒）
ocr_service = DeepSeekOCRService(ocr_timeout=600)
```

### 監控 GPU 狀態

```bash
# 即時監控 GPU
watch -n 1 nvidia-smi

# 查看特定程序的 GPU 使用
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
```

## 錯誤訊息說明

### 1. 超時錯誤

```json
{
  "error": "OCR 處理超時 (300 秒)，請嘗試使用更小的圖片或增加超時設定",
  "image_path": "uploads/image.jpg",
  "processing_time": 300.00,
  "gpu_info": {...}
}
```

**原因**: 處理時間超過設定的超時時間

**解決方法**:
1. 增加超時時間設定
2. 壓縮圖片大小
3. 檢查 GPU 是否正常運作

### 2. GPU 記憶體不足

```json
{
  "error": "GPU 記憶體不足，可用記憶體: 256 MB，建議至少有 500 MB 可用記憶體",
  "image_path": "uploads/image.jpg",
  "gpu_info": {
    "available": true,
    "total_mb": 8192,
    "used_mb": 7936,
    "free_mb": 256,
    "usage_percent": 96.88
  }
}
```

**原因**: GPU 可用記憶體不足

**解決方法**:
1. 關閉其他使用 GPU 的程序
2. 重啟 OCR 服務
3. 清理 GPU 快取記憶體

### 3. OCR 處理錯誤

```json
{
  "error": "OCR 處理發生錯誤: CUDA error: out of memory",
  "image_path": "uploads/image.jpg",
  "processing_time": 45.67,
  "gpu_info": {...}
}
```

**原因**: 處理過程中發生異常

**解決方法**:
1. 查看錯誤詳情
2. 重啟服務
3. 檢查系統資源

## 系統需求和建議

### 最低需求

- **GPU 記憶體**: 8GB VRAM
- **系統記憶體**: 16GB RAM
- **可用 GPU 記憶體**: 至少 500MB
- **CUDA**: 11.8 或更高版本

### 建議設定

- **圖片大小**: 不超過 4096x4096 像素
- **超時時間**: 
  - 一般圖片: 300 秒（預設）
  - 大型圖片: 600 秒
  - 複雜圖片: 900 秒
- **批次處理**: 每次不超過 10 張圖片

### 效能優化建議

1. **壓縮圖片**
```python
from PIL import Image

img = Image.open('large_image.png')
img.thumbnail((2048, 2048))
img.save('compressed.png', optimize=True, quality=85)
```

2. **定期重啟服務**
```bash
# 每處理 100 張圖片後重啟
./start_server.sh
```

3. **監控 GPU 使用率**
```bash
# 使用率超過 90% 時考慮清理或重啟
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv -l 1
```

## 測試驗證

### 測試超時機制

```bash
# 使用一張很大的圖片測試
curl -X POST -F "file=@very_large_image.png" http://localhost:5000/ocr

# 應該在設定的超時時間後返回錯誤
```

### 測試 GPU 記憶體檢查

```bash
# 先填滿 GPU 記憶體（使用其他程序）
# 然後嘗試 OCR
curl -X POST -F "file=@test.png" http://localhost:5000/ocr

# 應該返回 GPU 記憶體不足的錯誤
```

### 測試批次處理

```python
import requests

files = [
    ('files', open('image1.png', 'rb')),
    ('files', open('image2.png', 'rb')),
    # ... 更多圖片
]

response = requests.post('http://localhost:5000/ocr/batch', files=files)
print(response.json())
```

## 技術細節

### 超時機制實作

使用 UNIX 的 `SIGALRM` 信號實現超時：

1. 設定信號處理器：`signal.signal(signal.SIGALRM, timeout_handler)`
2. 設定超時時間：`signal.alarm(timeout_seconds)`
3. 執行任務
4. 超時時觸發 `SIGALRM`，執行處理器
5. 處理器拋出 `TimeoutError` 異常
6. 捕獲異常並處理
7. 清理：`signal.alarm(0)` 取消未觸發的鬧鐘

**注意事項**:
- 此機制僅在 UNIX/Linux 系統上有效
- Windows 系統需要使用其他方法（如 threading.Timer）
- 信號處理器會中斷所有阻塞操作

### GPU 記憶體管理

PyTorch 提供的 GPU 記憶體管理函數：

- `torch.cuda.memory_allocated()`: 已分配的記憶體
- `torch.cuda.memory_reserved()`: 已保留的記憶體
- `torch.cuda.empty_cache()`: 清空快取
- `torch.cuda.synchronize()`: 同步所有 CUDA 流

**記憶體狀態**:
- `allocated`: 實際使用的記憶體
- `reserved`: PyTorch 保留但未使用的記憶體
- `free`: 可用記憶體 = total - reserved

## 版本歷史

### v1.1.0 (2025-11-11)

**新增功能**:
- ✅ 超時保護機制（預設 300 秒）
- ✅ GPU 記憶體監控和檢查
- ✅ 自動 GPU 快取清理
- ✅ 詳細的錯誤處理和日誌
- ✅ 處理時間統計
- ✅ 環境變數配置支援

**改進**:
- 批次處理自動清理記憶體
- 返回結果包含 GPU 狀態資訊
- 完整的錯誤追蹤和回報

**文檔**:
- 更新 ERROR_MESSAGES.md
- 新增 SERVER_TIMEOUT_FIX.md

## 相關文檔

- [錯誤訊息說明](./ERROR_MESSAGES.md) - 完整的錯誤訊息和解決方法
- [快速開始](./QUICK_START.md) - 快速安裝和使用指南
- [API 文檔](./API_DOCUMENTATION.md) - 完整的 API 說明
- [GPU 設定](./GPU_SETUP.md) - GPU 環境設定指南

## 常見問題

### Q1: 為什麼需要超時機制？

**A**: 模型推理可能因為以下原因長時間執行或卡住：
- GPU 記憶體不足
- 圖片過大或過於複雜
- 模型內部錯誤
- 系統資源不足

超時機制確保服務不會無限期等待，並能及時回報錯誤。

### Q2: 300 秒超時夠用嗎？

**A**: 對於大多數圖片（4096x4096 以下），300 秒通常足夠。如果您經常處理更大或更複雜的圖片，建議增加超時時間。

### Q3: GPU 記憶體清理會影響效能嗎？

**A**: `torch.cuda.empty_cache()` 只清理未使用的快取，不會釋放正在使用的記憶體。對效能的影響很小，但可以防止記憶體累積。

### Q4: 如何判斷是否需要增加超時時間？

**A**: 如果您經常看到超時錯誤，但：
- GPU 使用率正常
- 系統資源充足
- 圖片大小合理

那麼可能需要增加超時時間。

### Q5: Windows 系統上超時機制會正常工作嗎？

**A**: 目前的實現使用 UNIX 信號，在 Windows 上不支援。如果需要在 Windows 上使用，需要改用 `threading.Timer` 或其他方法。

## 支援

如果遇到問題：

1. 查看 [ERROR_MESSAGES.md](./ERROR_MESSAGES.md) 尋找解決方案
2. 檢查日誌輸出
3. 確認系統需求
4. 嘗試壓縮圖片或增加超時時間

## 授權

本專案採用 MIT 授權條款。

