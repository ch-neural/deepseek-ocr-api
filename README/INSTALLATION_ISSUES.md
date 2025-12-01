# 安裝問題排除指南

本文檔整合了所有安裝相關的問題和解決方案。

## 目錄

1. [Unsloth 安裝問題](#1-unsloth-安裝問題)
2. [std::bad_alloc 記憶體錯誤](#2-stdbad_alloc-記憶體錯誤)
3. [模組匯入錯誤](#3-模組匯入錯誤)

---

## 1. Unsloth 安裝問題

### 錯誤訊息

```
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
./start_server.sh: line 38: 26698 Aborted (core dumped) python -c "import unsloth" 2> /dev/null
```

### 原因

1. **依賴複雜度**：Unsloth 依賴於多個套件（torch, xformers, transformers, trl 等）
2. **版本衝突**：不同套件之間可能有版本衝突
3. **編譯問題**：Unsloth 使用 JIT 編譯，可能因 CUDA/PyTorch 版本不匹配導致 Core Dump

### 解決方案

#### 方案 A：使用標準版本（推薦）

不需要 Unsloth，使用標準 Transformers 版本：

```bash
# 啟動腳本會自動偵測並切換到標準版本
./start_server.sh
```

#### 方案 B：嘗試安裝 Unsloth

```bash
# 方法 1：標準安裝
pip install unsloth

# 方法 2：無依賴安裝（如果有衝突）
pip install unsloth --no-deps

# 方法 3：指定版本
pip install "unsloth<2025.11.0" --no-deps
```

### Unsloth vs 標準版本比較

| 特性 | Unsloth 版本 | 標準版本 |
|------|-------------|---------|
| 推理速度 | 10-30 秒 | 60-120 秒 |
| 穩定性 | 可能有依賴衝突 | 穩定 |
| 安裝難度 | 較複雜 | 簡單 |
| OCR 功能 | 完全相同 | 完全相同 |

---

## 2. std::bad_alloc 記憶體錯誤

### 錯誤訊息

```
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
terminate called after throwing an instance of 'std::bad_alloc'
  what():  std::bad_alloc
Aborted (core dumped)
```

### 原因

- Unsloth 的 `FastVisionModel` 在初始化時發生 C++ 記憶體分配失敗
- 即使系統有足夠記憶體，仍可能發生此錯誤
- 通常是 Unsloth 版本與 DeepSeek-OCR 模型不兼容造成

### 解決方案

**使用標準 Transformers 版本**（完全繞過 Unsloth）：

```bash
# 直接啟動標準版本
python app_standard.py
```

或修改 `start_server.sh`，強制使用標準版本。

---

## 3. 模組匯入錯誤

### 錯誤訊息 A：vLLM 模組

```
ModuleNotFoundError: No module named 'vllm.model_executor.models.deepseek_ocr'
```

**原因**：DeepSeek-OCR 不再使用 vLLM，已改用 Unsloth 或標準 Transformers。

**解決方案**：確保使用最新版本的程式碼，不需要安裝 vLLM。

### 錯誤訊息 B：Unsloth 模組

```
ModuleNotFoundError: No module named 'unsloth'
```

**解決方案**：

```bash
# 選項 1：安裝 Unsloth
pip install unsloth

# 選項 2：使用標準版本（推薦）
python app_standard.py
```

### 錯誤訊息 C：其他模組

```
ModuleNotFoundError: No module named 'xxx'
```

**解決方案**：

```bash
pip install -r requirements.txt
```

---

## 正確的安裝流程

### 完整安裝步驟

```bash
# 1. 克隆專案
git clone https://github.com/ch-neural/deepseek-ocr-api
cd deepseek-ocr-api

# 2. 建立虛擬環境
python -m venv .venv
source .venv/bin/activate

# 3. 安裝 PyTorch（CUDA 版本）
pip install torch==2.7.1 torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cu118

# 4. 安裝其他依賴
pip install -r requirements.txt

# 5. （可選）安裝 Unsloth 以獲得更快速度
pip install unsloth --no-deps

# 6. 啟動服務
./start_server.sh
```

### 驗證安裝

```bash
# 檢查 PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

# 檢查 Transformers
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"

# 檢查 Flask
python -c "import flask; print(f'Flask: {flask.__version__}')"

# （可選）檢查 Unsloth
python -c "import unsloth; print(f'Unsloth: {unsloth.__version__}')" 2>/dev/null || echo "Unsloth not installed (optional)"
```

---

## 常見問題 FAQ

### Q1：Unsloth 是必需的嗎？

**不是**。標準版本功能完全相同，只是推理速度較慢。

### Q2：如何強制使用標準版本？

```bash
python app_standard.py
```

### Q3：安裝後仍有問題怎麼辦？

1. 檢查 Python 版本（需要 3.8+）
2. 檢查 CUDA 是否正確安裝
3. 嘗試重新建立虛擬環境
4. 查看 [ERROR_MESSAGES.md](ERROR_MESSAGES.md) 尋找特定錯誤

---

**最後更新**：2025-12-01
