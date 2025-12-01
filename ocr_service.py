"""
DeepSeek-OCR 服務類別
封裝 OCR 辨識功能
"""

# 延遲導入 unsloth，避免在模組載入時觸發 vllm 的 C++ ABI 錯誤
# from unsloth import FastVisionModel  # 移到 __init__ 中延遲導入
from transformers import AutoModel
from PIL import Image
import os
import torch
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError


class TimeoutError(Exception):
    """超時錯誤例外類別"""
    pass


def with_timeout(timeout_seconds):
    """
    超時裝飾器（線程安全版本）
    使用 ThreadPoolExecutor 實現超時控制，適用於 Flask 多線程環境
    
    Args:
        timeout_seconds: 超時秒數
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用 ThreadPoolExecutor 實現超時
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                
                result = None
                error = None
                
                # 等待結果或超時
                result = future.result(timeout=timeout_seconds)
                
                return result
        
        return wrapper
    return decorator


def check_gpu_memory():
    """
    檢查 GPU 記憶體狀態
    
    Returns:
        dict: GPU 記憶體資訊
            {
                'available': bool,
                'total_mb': float,
                'used_mb': float,
                'free_mb': float,
                'usage_percent': float
            }
    """
    if not torch.cuda.is_available():
        return {
            'available': False,
            'total_mb': 0,
            'used_mb': 0,
            'free_mb': 0,
            'usage_percent': 0
        }
    
    # 獲取 GPU 記憶體資訊
    total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)  # 轉換為 MB
    allocated = torch.cuda.memory_allocated(0) / (1024 ** 2)
    reserved = torch.cuda.memory_reserved(0) / (1024 ** 2)
    free = total - reserved
    
    return {
        'available': True,
        'total_mb': round(total, 2),
        'used_mb': round(reserved, 2),
        'free_mb': round(free, 2),
        'usage_percent': round((reserved / total) * 100, 2)
    }


class DeepSeekOCRService:
    """
    DeepSeek-OCR 服務類別
    
    提供單張和批次圖片的 OCR 辨識功能
    """
    
    def __init__(self, model_name="unsloth/DeepSeek-OCR", model_dir="./deepseek_ocr", 
                 ocr_timeout=300, base_size=2048, image_size=1024, 
                 crop_mode=True, test_compress=False, save_results=False):
        """
        初始化 DeepSeek-OCR 服務
        
        Args:
            model_name: 模型名稱，預設為 "unsloth/DeepSeek-OCR"
            model_dir: 模型本地目錄
            ocr_timeout: OCR 處理超時秒數，預設為 300 秒（5 分鐘）
            base_size: 圖片預處理基準尺寸，預設 2048（適合 1920x1080）
            image_size: 模型輸入圖片尺寸，預設 1024（平衡準確度與速度）
            crop_mode: 是否啟用裁切模式，預設 True
            test_compress: 是否測試壓縮，預設 False
            save_results: 是否保存結果，預設 False
        """
        self.model_name = model_name
        self.model_dir = model_dir
        self.default_prompt = "<image>\nFree OCR."
        self.ocr_timeout = ocr_timeout
        
        # OCR 圖片處理參數
        self.base_size = base_size
        self.image_size = image_size
        self.crop_mode = crop_mode
        self.test_compress = test_compress
        self.save_results = save_results
        
        print(f"OCR 處理超時設定: {ocr_timeout} 秒")
        print(f"OCR 圖片處理參數: base_size={base_size}, image_size={image_size}, crop_mode={crop_mode}")
        
        print(f"正在載入模型: {model_name}")
        
        # 下載模型（如果本地不存在）
        if not os.path.exists(model_dir):
            print(f"正在下載模型到 {model_dir}...")
            print("提示: 如果下載失敗，請執行以下步驟：")
            print("  1. 登入 Hugging Face: huggingface-cli login")
            print("  2. 或設定環境變數: export HF_TOKEN=your_token")
            
            from huggingface_hub import snapshot_download
            
            # 嘗試下載模型
            downloaded = False
            error_msg = None
            
            # 方法 1: 嘗試從 unsloth 下載
            if not downloaded:
                print(f"\n嘗試從 {model_name} 下載...")
                try:
                    snapshot_download(model_name, local_dir=model_dir)
                    downloaded = True
                    print("✅ 模型下載完成！")
                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ 從 {model_name} 下載失敗: {e}")
            
            # 方法 2: 嘗試從 deepseek-ai 官方倉庫下載
            if not downloaded:
                alternative_name = "deepseek-ai/deepseek-ocr"
                print(f"\n嘗試從官方倉庫 {alternative_name} 下載...")
                try:
                    snapshot_download(alternative_name, local_dir=model_dir)
                    downloaded = True
                    print("✅ 模型下載完成！")
                except Exception as e:
                    print(f"❌ 從 {alternative_name} 下載失敗: {e}")
            
            if not downloaded:
                error_message = f"""
❌ 模型下載失敗！

錯誤原因: {error_msg}

解決方法：

方法 1: 登入 Hugging Face
  執行以下指令登入：
  $ huggingface-cli login
  然後輸入您的 Hugging Face token

方法 2: 設定環境變數
  $ export HF_TOKEN=your_huggingface_token
  
方法 3: 手動下載模型
  1. 訪問 https://huggingface.co/unsloth/DeepSeek-OCR
  2. 點擊 "Files and versions"
  3. 下載所有檔案到 {model_dir}/ 目錄

方法 4: 使用 Git LFS 手動克隆
  $ git lfs install
  $ git clone https://huggingface.co/unsloth/DeepSeek-OCR {model_dir}

獲取 Hugging Face Token:
  1. 訪問 https://huggingface.co/settings/tokens
  2. 創建一個新的 token (需要 read 權限)
  3. 使用該 token 登入或設定環境變數
"""
                print(error_message)
                raise Exception(error_message)
        
        # 設定環境變數以避免警告和跳過統計收集
        os.environ["UNSLOTH_WARN_UNINITIALIZED"] = '0'
        os.environ["HF_HUB_OFFLINE"] = '1'  # 強制離線模式，跳過統計收集
        os.environ["TRANSFORMERS_TRUST_REMOTE_CODE"] = '1'  # 自動信任遠程代碼，不詢問
        
        # 延遲導入 unsloth，避免在模組載入時觸發 vllm 的 C++ ABI 錯誤
        # 只有在實際需要載入模型時才導入
        # 嘗試設置環境變數來避免 vllm 相關問題
        os.environ.setdefault("VLLM_USE_PRECOMPILED", "0")
        
        try:
            from unsloth import FastVisionModel
        except ImportError as e:
            error_msg = f"""
無法導入 unsloth 模組！

錯誤訊息: {e}

這通常是因為 vllm 和 PyTorch 版本不匹配導致的 C++ ABI 錯誤。

解決方案：

1. 重新安裝 unsloth（推薦）：
   pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo

2. 確認 PyTorch 版本兼容性：
   python -c "import torch; print(f'PyTorch: {{torch.__version__}}')"
   python -c "import torch; print(f'CUDA Available: {{torch.cuda.is_available()}}')"

3. 如果問題持續，嘗試重新安裝 PyTorch：
   pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

4. 清理並重新安裝：
   pip uninstall -y vllm unsloth unsloth_zoo
   pip install --upgrade unsloth
"""
            print(error_msg)
            raise ImportError(error_msg)
        except Exception as e:
            # 捕獲其他可能的錯誤（如 C++ ABI 錯誤）
            error_msg = f"""
導入 unsloth 時發生錯誤！

錯誤訊息: {e}

這可能是由於 vllm 和 PyTorch 版本不匹配導致的 C++ ABI 錯誤。

解決方案：

1. 重新安裝 unsloth（推薦）：
   pip install --upgrade --force-reinstall --no-cache-dir unsloth unsloth_zoo

2. 確認 PyTorch 版本兼容性：
   python -c "import torch; print(f'PyTorch: {{torch.__version__}}')"
   python -c "import torch; print(f'CUDA Available: {{torch.cuda.is_available()}}')"

3. 如果問題持續，嘗試重新安裝 PyTorch：
   pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

4. 清理並重新安裝：
   pip uninstall -y vllm unsloth unsloth_zoo
   pip install --upgrade unsloth
"""
            print(error_msg)
            raise RuntimeError(error_msg)
        
        # 初始化模型
        self.model, self.tokenizer = FastVisionModel.from_pretrained(
            model_dir,
            load_in_4bit=False,  # 使用 16bit 以獲得更好的精確度
            auto_model=AutoModel,
            trust_remote_code=True,
            unsloth_force_compile=True,
            use_gradient_checkpointing="unsloth",
            local_files_only=True,  # 只使用本地檔案，不嘗試連線
            revision=None,  # 避免版本檢查
        )
        
        print(f"模型載入完成: {model_name}")
    
    def perform_ocr(self, image_path, custom_prompt=None):
        """
        對單張圖片執行 OCR 辨識
        
        Args:
            image_path: 圖片檔案路徑
            custom_prompt: 自訂提示詞，若為 None 則使用預設提示詞
            
        Returns:
            dict: 包含辨識結果的字典
                {
                    'text': OCR 辨識的文字,
                    'image_path': 圖片路徑,
                    'prompt': 使用的提示詞
                }
                或錯誤時返回
                {
                    'error': 錯誤訊息,
                    'image_path': 圖片路徑
                }
        """
        # 檢查圖片是否存在
        if not os.path.exists(image_path):
            error_msg = f"圖片檔案不存在: {image_path}"
            print(f"錯誤: {error_msg}")
            return {
                'error': error_msg,
                'image_path': image_path
            }
        
        print(f"已載入圖片: {image_path}")
        
        # 檢查 GPU 記憶體狀態
        gpu_info = check_gpu_memory()
        print(f"GPU 記憶體狀態: {gpu_info}")
        
        if gpu_info['available']:
            if gpu_info['usage_percent'] > 95:
                print(f"警告: GPU 記憶體使用率過高 ({gpu_info['usage_percent']}%)")
                print(f"可用記憶體: {gpu_info['free_mb']} MB / {gpu_info['total_mb']} MB")
            
            if gpu_info['free_mb'] < 500:  # 少於 500MB 可用記憶體
                error_msg = f"GPU 記憶體不足，可用記憶體: {gpu_info['free_mb']} MB，建議至少有 500 MB 可用記憶體"
                print(f"錯誤: {error_msg}")
                return {
                    'error': error_msg,
                    'image_path': image_path,
                    'gpu_info': gpu_info
                }
        
        # 使用自訂提示詞或預設提示詞
        prompt = custom_prompt if custom_prompt else self.default_prompt
        
        # 執行 OCR
        print(f"正在執行 OCR 辨識...")
        print(f"超時設定: {self.ocr_timeout} 秒")
        
        start_time = time.time()
        
        # 創建臨時輸出目錄
        import tempfile
        import sys
        from io import StringIO
        import shutil
        
        temp_output = tempfile.mkdtemp(prefix="ocr_output_")
        
        result = None
        ocr_output = None
        error_occurred = None
        
        # 捕獲 stdout 輸出（因為 model.infer 會將結果打印出來）
        captured_output = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_output
        
        # 使用線程池執行 OCR 推理（支援超時控制）
        def _perform_ocr_inference():
            """實際執行 OCR 推理的內部函數"""
            print(f"開始模型推理 (超時: {self.ocr_timeout} 秒)...")
            
            # 使用 Unsloth 的 infer 方法
            # 註：使用從 config.py 載入的參數來處理圖片
            inference_result = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=image_path,
                output_path=temp_output,  # 提供臨時輸出路徑
                base_size=self.base_size,      # 從 config.py 讀取
                image_size=self.image_size,    # 從 config.py 讀取
                crop_mode=self.crop_mode,      # 從 config.py 讀取
                save_results=self.save_results,  # 從 config.py 讀取
                test_compress=self.test_compress  # 從 config.py 讀取
            )
            
            print(f"模型推理完成")
            return inference_result
        
        # 執行 OCR 推理（使用線程池實現超時控制）
        from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
        
        # 在 Flask 工作線程中安全地執行帶有超時控制的 OCR 推理
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_perform_ocr_inference)
            
            # 等待結果或超時
            inference_result = future.result(timeout=self.ocr_timeout)
            
            result = inference_result
            
            print(f"OCR 推理執行成功")
        
        # 恢復 stdout
        sys.stdout = old_stdout
        
        # 獲取捕獲的輸出
        ocr_output = captured_output.getvalue()
        captured_output.close()
        
        # 清理臨時目錄
        if os.path.exists(temp_output):
            shutil.rmtree(temp_output, ignore_errors=True)
        
        # 計算處理時間
        elapsed_time = time.time() - start_time
        print(f"OCR 處理耗時: {elapsed_time:.2f} 秒")
        
        # 如果發生錯誤，返回錯誤訊息
        if error_occurred:
            return {
                'error': error_occurred,
                'image_path': image_path,
                'processing_time': round(elapsed_time, 2),
                'gpu_info': gpu_info
            }
        
        # 提取 OCR 文字（可能在 result 中，也可能在 captured_output 中）
        ocr_text = None
        
        # 詳細日誌：記錄推理結果
        print(f"推理返回值類型: {type(result)}")
        print(f"推理返回值內容: {result}")
        print(f"捕獲的輸出長度: {len(ocr_output) if ocr_output else 0}")
        if ocr_output:
            print(f"捕獲的輸出前 500 字元: {ocr_output[:500]}")
        
        # 方法 1: 檢查返回值
        if result and isinstance(result, str) and len(result) > 0:
            print(f"使用方法 1: 從返回值提取 OCR 文字，長度: {len(result)}")
            ocr_text = result
        # 方法 2: 從捕獲的輸出中提取（去除日誌和分隔線）
        elif ocr_output:
            print(f"使用方法 2: 從捕獲的輸出提取 OCR 文字")
            # 過濾掉日誌行和分隔線
            lines = ocr_output.split('\n')
            text_lines = []
            
            # 定義要過濾的系統訊息關鍵字
            system_messages = [
                '開始模型推理',
                '模型推理完成',
                'OCR 推理執行成功',
                'BASE:',
                'PATCHES:'
            ]
            
            for line in lines:
                line_stripped = line.strip()
                # 跳過空行、分隔線、系統訊息
                if not line_stripped:
                    continue
                if line_stripped.startswith('==='):
                    continue
                # 檢查是否包含系統訊息關鍵字
                is_system_message = any(keyword in line_stripped for keyword in system_messages)
                if not is_system_message:
                    text_lines.append(line)
            
            ocr_text = '\n'.join(text_lines).strip()
            print(f"過濾後 OCR 文字長度: {len(ocr_text) if ocr_text else 0}")
            if ocr_text:
                print(f"過濾後 OCR 文字前 200 字元: {ocr_text[:200]}")
        
        # 檢查 OCR 結果是否異常（可能是 Prompt 重複）
        if ocr_text and len(ocr_text) < 50:
            print(f"⚠️ 警告：OCR 結果異常短（{len(ocr_text)} 字元），可能是辨識失敗")
            
            # 檢查是否與 Prompt 高度重疊
            if prompt:
                prompt_words = set(prompt.split())
                ocr_words = set(ocr_text.split())
                if ocr_words:
                    overlap_ratio = len(prompt_words & ocr_words) / len(ocr_words)
                    print(f"Prompt 重疊率: {overlap_ratio:.2%}")
                    
                    if overlap_ratio > 0.7:  # 70% 以上重疊視為異常
                        print(f"❌ OCR 結果疑似為 Prompt 重複，將返回錯誤")
                        return {
                            'error': 'OCR 辨識失敗：照片可能模糊或光線不足，請重新拍攝更清晰的照片',
                            'image_path': image_path,
                            'processing_time': round(elapsed_time, 2),
                            'gpu_info': gpu_info,
                            'debug_info': {
                                'ocr_text_length': len(ocr_text),
                                'prompt_overlap_ratio': overlap_ratio
                            }
                        }
        
        if ocr_text and len(ocr_text) > 0:
            print(f"OCR 辨識完成，文字長度: {len(ocr_text)}")
            
            # 檢查 OCR 後的 GPU 記憶體狀態
            gpu_info_after = check_gpu_memory()
            print(f"OCR 後 GPU 記憶體狀態: {gpu_info_after}")
            
            # 如果記憶體使用率超過 80%，自動清理 GPU 快取以降低記憶體累積風險
            if gpu_info_after['available'] and gpu_info_after['usage_percent'] > 80:
                print(f"GPU 記憶體使用率較高 ({gpu_info_after['usage_percent']}%)，執行自動清理...")
                gpu_before_cleanup = gpu_info_after['used_mb']
                self.clear_gpu_cache()
                gpu_info_after_cleanup = check_gpu_memory()
                memory_freed = gpu_before_cleanup - gpu_info_after_cleanup['used_mb']
                print(f"自動清理完成，釋放記憶體: {memory_freed:.2f} MB")
                gpu_info_after = gpu_info_after_cleanup
            
            return {
                'text': ocr_text,
                'image_path': image_path,
                'prompt': prompt,
                'processing_time': round(elapsed_time, 2),
                'gpu_info_before': gpu_info,
                'gpu_info_after': gpu_info_after
            }
        else:
            error_msg = "模型未返回任何結果"
            print(f"錯誤: {error_msg}")
            
            # 即使處理失敗，也檢查並清理 GPU 記憶體（如果使用率過高）
            gpu_info_after = check_gpu_memory()
            if gpu_info_after['available'] and gpu_info_after['usage_percent'] > 80:
                print(f"處理失敗但 GPU 記憶體使用率較高 ({gpu_info_after['usage_percent']}%)，執行自動清理...")
                self.clear_gpu_cache()
            
            return {
                'error': error_msg,
                'image_path': image_path,
                'processing_time': round(elapsed_time, 2),
                'gpu_info': gpu_info
            }
    
    def clear_gpu_cache(self):
        """清理 GPU 快取記憶體"""
        if torch.cuda.is_available():
            print("正在清理 GPU 快取記憶體...")
            gpu_before = check_gpu_memory()
            print(f"清理前 GPU 記憶體: {gpu_before}")
            
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
            gpu_after = check_gpu_memory()
            print(f"清理後 GPU 記憶體: {gpu_after}")
            print(f"釋放記憶體: {gpu_before['used_mb'] - gpu_after['used_mb']:.2f} MB")
    
    def perform_batch_ocr(self, image_paths, custom_prompt=None):
        """
        對多張圖片執行批次 OCR 辨識
        
        Args:
            image_paths: 圖片檔案路徑列表
            custom_prompt: 自訂提示詞，若為 None 則使用預設提示詞
            
        Returns:
            list: 包含多個辨識結果的列表，每個元素為 dict
        """
        # 使用自訂提示詞或預設提示詞
        prompt = custom_prompt if custom_prompt else self.default_prompt
        
        results = []
        total_images = len(image_paths)
        
        print(f"開始批次處理 {total_images} 張圖片")
        
        for idx, image_path in enumerate(image_paths, 1):
            print(f"\n處理進度: {idx}/{total_images}")
            # 檢查圖片是否存在
            if not os.path.exists(image_path):
                error_msg = f"圖片檔案不存在: {image_path}"
                print(f"警告: {error_msg}")
                continue
            
            # 檢查 GPU 記憶體（每 5 張圖片清理一次）
            if idx % 5 == 0:
                self.clear_gpu_cache()
            
            # 呼叫單張圖片的 OCR 方法（已包含超時和錯誤處理）
            single_result = self.perform_ocr(image_path, custom_prompt)
            
            # 如果處理成功，加入結果列表
            if 'text' in single_result:
                results.append(single_result)
                print(f"✓ 圖片 {idx}/{total_images} 處理成功")
            else:
                # 即使失敗也加入結果，但包含錯誤訊息
                results.append(single_result)
                print(f"✗ 圖片 {idx}/{total_images} 處理失敗: {single_result.get('error', '未知錯誤')}")
        
        # 最後清理一次 GPU 記憶體
        self.clear_gpu_cache()
        
        success_count = sum(1 for r in results if 'text' in r)
        failed_count = len(results) - success_count
        
        print(f"\n批次 OCR 辨識完成")
        print(f"總計: {total_images} 張，成功: {success_count} 張，失敗: {failed_count} 張")
        
        return results

