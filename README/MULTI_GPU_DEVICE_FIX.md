# 多 GPU 設備不一致錯誤修復

## 問題描述

在有多個 GPU 的主機上執行 OCR 時出現以下錯誤：

```
RuntimeError: Expected all tensors to be on the same device, but found at least two devices, cuda:1 and cuda:0! 
(when checking argument for argument tensors in method wrapper_CUDA_cat)
```

## 原因分析

當使用 `device_map="auto"` 載入模型時，`accelerate` 會自動將模型的不同層分配到不同的 GPU 上。
這在某些模型上運作正常，但 DeepSeek-OCR 模型在推理時需要將來自不同層的 tensor 進行 concatenation，
導致「設備不一致」錯誤。

```python
# 問題代碼
self.model = AutoModel.from_pretrained(
    model_dir,
    device_map="auto"  # ❌ 會將模型分散到多個 GPU
)
```

## 解決方法

強制將整個模型載入到單一 GPU（cuda:0）：

```python
# 修復代碼
self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

self.model = AutoModel.from_pretrained(
    model_dir,
    device_map={"": self.device}  # ✅ 強制使用單一設備
)
```

## 修改的檔案

| 檔案 | 修改內容 |
|------|---------|
| `ocr_service_standard.py` | 將 `device_map="auto"` 改為 `device_map={"": self.device}`，強制使用 cuda:0 |

## 適用情境

此修復適用於：
- 有多個 GPU 的伺服器
- 使用 `accelerate` 載入模型
- 模型推理時發生 tensor 設備不一致錯誤

## 如果需要使用多 GPU

如果模型太大需要分散到多個 GPU，可能需要：
1. 使用模型的官方多 GPU 支援（如果有）
2. 使用 `tensor_parallel` 或 `pipeline_parallel` 方式載入
3. 確保模型代碼支援多設備操作

對於 DeepSeek-OCR 這個模型（約 2.6GB），單一 RTX 3090（24GB）足夠載入整個模型。

---

**最後更新**：2025-11-30

