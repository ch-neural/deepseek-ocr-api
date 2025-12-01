# OCR 輸出路徑錯誤修復

## 問題描述

執行 OCR 辨識時出現以下錯誤：

```
錯誤: OCR 推理執行失敗: expected str, bytes or os.PathLike object, not NoneType

Traceback (most recent call last):
  File "/GPUData/working/Deepseek-OCR/ocr_service_standard.py", line 253, in perform_ocr
    ocr_text = self._perform_ocr_inference(image_path, prompt)
  File "/GPUData/working/Deepseek-OCR/ocr_service_standard.py", line 169, in _perform_ocr_inference
    result = self.model.infer(
  File ".../modeling_deepseekocr.py", line 715, in infer
    os.makedirs(output_path, exist_ok=True)
TypeError: expected str, bytes or os.PathLike object, not NoneType
```

## 原因分析

DeepSeek-OCR 模型的 `infer()` 方法內部會呼叫 `os.makedirs(output_path, exist_ok=True)`，
即使設定 `save_results=False`，模型仍然需要一個有效的 `output_path` 參數。

原本程式碼傳遞 `output_path=None`，導致 `os.makedirs()` 失敗。

## 解決方法

修改 `ocr_service_standard.py`，將 `output_path=None` 改為有效的目錄路徑：

```python
# 修改前
result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=None,  # ❌ 這會導致錯誤
    ...
)

# 修改後
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

result = self.model.infer(
    self.tokenizer,
    prompt=prompt,
    image_file=image_path,
    output_path=output_dir,  # ✅ 使用有效的輸出目錄
    ...
)
```

## 修改的檔案

| 檔案 | 修改內容 |
|------|---------|
| `ocr_service_standard.py` | 在 `_perform_ocr_inference()` 方法中，建立 `./output` 目錄並傳遞給 `model.infer()` |

## 驗證修復

重新啟動服務後，OCR 應該能正常執行：

```bash
# 重新啟動服務
python app_standard.py

# 測試 OCR
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/ocr
```

---

**最後更新**：2025-11-30

