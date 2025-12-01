# Unsloth 安裝依賴衝突問題

## 問題描述

執行 `./start_server.sh` 時，可能遇到以下問題：

### 錯誤訊息 1：Core Dumped

```
🦥 Unsloth: Will patch your computer to enable 2x faster free finetuning.
./start_server.sh: line 38: 26698 Aborted (core dumped) python -c "import unsloth" 2> /dev/null
```

### 錯誤訊息 2：依賴解析過深

```
ERROR: Exception:
pip._vendor.resolvelib.resolvers.ResolutionTooDeep: 2000000
```

### 錯誤訊息 3：長時間回溯

```
INFO: pip is looking at multiple versions of torch to determine which version is compatible
INFO: This is taking longer than usual. You might need to provide the dependency resolver...
```

### 原因分析

1. **依賴複雜度**：`unsloth` 依賴於 `torch`, `xformers`, `transformers`, `trl` 等套件
2. **版本衝突**：這些套件之間有嚴格的版本依賴關係，pip 難以找到相容組合
3. **編譯問題**：Unsloth 使用 JIT 編譯，可能因 CUDA/PyTorch 版本不匹配導致 Core Dump
4. **回溯解析**：pip 的依賴解析器嘗試找到兼容的版本組合，導致無限回溯

```
unsloth → torch (多個版本)
       → xformers (多個版本)
       → transformers (多個版本)
       → trl (多個版本)
       (彼此之間有複雜的版本約束)
```

---

## 解決方案

### ✅ 方案 1：使用智能啟動腳本（推薦）

**優點**：自動偵測 Unsloth，不可用時自動切換到標準版本

```bash
# 直接執行主啟動腳本
./start_server.sh
```

**新版腳本特點**：
- ✅ 自動偵測 Unsloth 是否可用
- ✅ 若 Unsloth 不可用，自動使用標準 Transformers 版本
- ✅ 功能完全相同，只是推理速度略慢
- ✅ 不會卡在依賴安裝

---

### ✅ 方案 2：直接使用標準版本

**優點**：完全不需要 Unsloth

```bash
# 使用不需要 Unsloth 的版本
./start_server_no_unsloth.sh
```

**或手動啟動**：

```bash
# 1. 啟動虛擬環境
source /home/chtseng/envs/DP-OCR/bin/activate

# 2. 直接執行標準版本
python app_standard.py
```

---

### ✅ 方案 3：手動啟動（最安全）

**適用**：所有情況

```bash
# 1. 中斷當前安裝（按 Ctrl+C）

# 2. 啟動虛擬環境
source /home/chtseng/envs/DP-OCR/bin/activate

# 3. 檢查必要套件
python -c "import flask, torch, transformers; print('✅ 基本套件正常')"

# 4. 建立必要目錄
mkdir -p uploads logs output

# 5. 直接啟動服務（標準版本）
python app_standard.py
```

---

## Unsloth vs 標準版本比較

| 功能 | Unsloth 版本 | 標準版本 |
|------|-------------|---------|
| OCR 辨識 | ✅ | ✅ |
| 批次處理 | ✅ | ✅ |
| Web 介面 | ✅ | ✅ |
| API 端點 | ✅ | ✅ |
| 推理速度 | ⚡ 較快 | 🐢 略慢 |
| 記憶體使用 | 📉 較低 | 📈 較高 |
| 安裝難度 | 😣 困難 | 😊 簡單 |

**結論**：如果不是特別需要性能優化，建議使用標準版本。

---

## 環境驗證

### 使用檢查腳本

```bash
python check_env.py
```

### 手動檢查

```bash
# 測試 1：Python 套件
python -c "import flask, torch, transformers; print('OK')"

# 測試 2：CUDA（如果有 GPU）
python -c "import torch; print('CUDA:', torch.cuda.is_available())"

# 測試 3：健康檢查
curl http://localhost:5000/health
```

---

## 如果需要安裝 Unsloth

### 方法 1：使用 --no-deps 避免依賴解析

```bash
# 清理快取
pip cache purge

# 安裝（跳過依賴解析）
pip install unsloth --no-deps

# 如果缺少依賴，手動安裝
pip install xformers accelerate bitsandbytes
```

### 方法 2：分階段安裝

```bash
# 階段 1：安裝 PyTorch（指定版本）
pip install torch==2.4.0 torchvision --index-url https://download.pytorch.org/whl/cu121

# 階段 2：安裝 Transformers
pip install transformers==4.51.3 accelerate

# 階段 3：安裝 xformers（與 PyTorch 版本匹配）
pip install xformers==0.0.27.post2

# 階段 4：安裝 Unsloth
pip install unsloth --no-deps
```

### 方法 3：使用舊版本

```bash
pip install "unsloth<2025.11.0" --no-deps
```

---

## 常見問題

### Q1：Unsloth 是否必需？

**A**：不需要！DeepSeek-OCR 有兩個版本：
- `app.py` + `ocr_service.py`：使用 Unsloth（可選）
- `app_standard.py` + `ocr_service_standard.py`：使用標準 Transformers

兩者功能完全相同，只有性能差異。

### Q2：Core Dumped 錯誤怎麼辦？

這通常是 Unsloth 的 JIT 編譯與 CUDA 版本不匹配導致的。解決方案：
1. 使用標準版本（推薦）
2. 或重新安裝匹配的 PyTorch/CUDA 版本

### Q3：如何完全重裝環境？

```bash
# 1. 停用虛擬環境
deactivate

# 2. 刪除舊環境
rm -rf /home/chtseng/envs/DP-OCR

# 3. 建立新環境
python -m venv /home/chtseng/envs/DP-OCR

# 4. 啟動新環境
source /home/chtseng/envs/DP-OCR/bin/activate

# 5. 安裝基本套件
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers accelerate huggingface_hub
pip install flask pillow werkzeug
```

---

## 總結

### 推薦流程

```bash
# 立即解決
Ctrl+C  # 中斷當前安裝

# 最簡單的方法（推薦）
./start_server.sh  # 新版腳本會自動處理

# 或直接使用標準版本
./start_server_no_unsloth.sh
```

### 關鍵要點

1. ✅ **Unsloth 是可選的**：標準版本功能完全相同
2. ✅ **使用智能腳本**：新版 `start_server.sh` 會自動處理
3. ✅ **避免強制升級**：不要使用 `pip install --upgrade unsloth`
4. ✅ **依賴解析失敗時**：直接使用標準版本

---

---

## 已驗證的工作環境（2025-11-30）

以下版本組合已測試可正常運作：

```
Python                  3.10
torch                   2.7.1+cu118
transformers            4.56.2
tokenizers              0.22.1
accelerate              1.11.0
Flask                   3.1.2
```

**關鍵發現**：
1. `transformers >= 4.57` 會導致 CUDA mask 錯誤
2. `transformers == 4.56.2` 可正常運作
3. 使用 `app_standard.py` 可避免所有 Unsloth 相關問題

---

**最後更新**：2025-11-30  
**相關文件**：
- `start_server.sh` - 智能啟動腳本（自動偵測）
- `start_server_no_unsloth.sh` - 標準版本啟動腳本
- `start_server_simple.sh` - 簡化啟動腳本
- `app_standard.py` - 標準版本主程式
- `ocr_service_standard.py` - 標準版本 OCR 服務
- `check_env.py` - 環境檢查腳本
- `INSTALL.md` - 完整安裝指南
