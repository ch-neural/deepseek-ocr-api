"""
DeepSeek-OCR 服務類別（標準 Transformers 版本，不使用 Unsloth）
封裝 OCR 辨識功能
"""

from transformers import AutoModel, AutoTokenizer, AutoImageProcessor
from PIL import Image
import os
import torch
import time
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
import io
import sys

# 禁用 SDPA (Scaled Dot Product Attention) 以避免 CUDA 錯誤
# 這個問題出現在 transformers 4.55+ 版本的 create_causal_mask 函數中
if hasattr(torch.backends.cuda, 'enable_flash_sdp'):
    torch.backends.cuda.enable_flash_sdp(False)
if hasattr(torch.backends.cuda, 'enable_mem_efficient_sdp'):
    torch.backends.cuda.enable_mem_efficient_sdp(False)
if hasattr(torch.backends.cuda, 'enable_math_sdp'):
    torch.backends.cuda.enable_math_sdp(True)  # 使用標準數學實現


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
    DeepSeek-OCR 服務類別（標準 Transformers 版本）
    
    提供單張和批次圖片的 OCR 辨識功能
    """
    
    def __init__(self, model_name="unsloth/DeepSeek-OCR", model_dir="./deepseek_ocr", 
                 ocr_timeout=300, base_size=2048, image_size=1024, 
                 crop_mode=True, test_compress=False, save_results=False):
        """
        初始化 DeepSeek-OCR 服務
        
        Args:
            model_name: 模型名稱
            model_dir: 模型本地目錄
            ocr_timeout: OCR 辨識超時秒數
            base_size: 圖片預處理的基準尺寸
            image_size: 模型輸入的圖片尺寸
            crop_mode: 是否啟用裁切模式
            test_compress: 是否測試壓縮
            save_results: 是否保存結果
        """
        self.model_name = model_name
        self.model_dir = model_dir
        self.ocr_timeout = ocr_timeout
        self.base_size = base_size
        self.image_size = image_size
        self.crop_mode = crop_mode
        self.test_compress = test_compress
        self.save_results = save_results
        
        print(f"正在載入模型: {model_name}")
        print(f"模型目錄: {model_dir}")
        print(f"超時設定: {ocr_timeout} 秒")
        
        # 檢查 GPU 可用性並設定使用的設備
        self.device = "cpu"
        if torch.cuda.is_available():
            # 強制使用單一 GPU (cuda:0) 避免多 GPU 導致的 tensor 設備不一致問題
            self.device = "cuda:0"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_count = torch.cuda.device_count()
            print(f"✅ GPU 可用: {gpu_name} ({gpu_memory:.1f} GB)")
            if gpu_count > 1:
                print(f"   偵測到 {gpu_count} 個 GPU，將只使用 cuda:0 避免多設備問題")
        else:
            print("⚠️  警告: GPU 不可用，將使用 CPU（速度會很慢）")
        
        # 決定從哪裡載入模型（本地目錄或 Hugging Face Hub）
        # 檢查本地目錄是否存在且包含必要文件
        model_source = model_dir
        if os.path.exists(model_dir) and os.path.isfile(os.path.join(model_dir, "config.json")):
            print(f"✅ 使用本地模型目錄: {model_dir}")
            model_source = model_dir
        else:
            print(f"⚠️  本地目錄 {model_dir} 不存在或不完整")
            print(f"   將從 Hugging Face Hub 下載模型: {model_name}")
            model_source = model_name
            
            # 自動下載模型到本地目錄
            print(f"   正在下載模型到 {model_dir}...")
            from huggingface_hub import snapshot_download
            try:
                snapshot_download(model_name, local_dir=model_dir)
                model_source = model_dir
                print(f"✅ 模型下載完成: {model_dir}")
            except Exception as e:
                print(f"❌ 模型下載失敗: {e}")
                print(f"   將嘗試直接從 Hugging Face Hub 載入")
                model_source = model_name
        
        # 載入 tokenizer
        print("載入 tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_source,
            trust_remote_code=True
        )
        
        # 載入模型（使用標準 AutoModel）
        print("載入模型...")
        
        # 設定載入參數 - 使用最保守的設定避免 CUDA 問題
        load_kwargs = {
            "trust_remote_code": True,
            "low_cpu_mem_usage": True,
        }
        
        # 設定 dtype
        if torch.cuda.is_available():
            load_kwargs["torch_dtype"] = torch.float16  # 使用 float16 而非 bfloat16，相容性更好
        else:
            load_kwargs["torch_dtype"] = torch.float32
        
        # 先載入模型到 CPU，再手動移動到 GPU（避免 device_map 的問題）
        self.model = AutoModel.from_pretrained(model_source, **load_kwargs)
        
        # 手動移動到指定設備
        if torch.cuda.is_available():
            print(f"將模型移動到 {self.device}...")
            self.model = self.model.to(self.device)
        
        # 確保模型在評估模式
        self.model.eval()
        
        print("✅ 模型載入完成！")
        
        # 檢查 GPU 記憶體
        gpu_mem = check_gpu_memory()
        if gpu_mem['available']:
            print(f"GPU 記憶體: {gpu_mem['used_mb']:.0f}MB / {gpu_mem['total_mb']:.0f}MB ({gpu_mem['usage_percent']:.1f}%)")
    
    def _perform_ocr_inference(self, image_path, prompt):
        """
        執行 OCR 推理
        
        Args:
            image_path: 圖片路徑
            prompt: 提示詞
            
        Returns:
            str: OCR 辨識結果文字
        """
        print(f"開始模型推理 (超時: {self.ocr_timeout} 秒)...")
        
        start_time = time.time()
        
        # 建立輸出目錄（模型需要這個路徑）
        import tempfile
        output_dir = tempfile.mkdtemp(prefix="ocr_output_")
        os.makedirs(output_dir, exist_ok=True)
        
        # 使用模型的 infer 方法
        try:
            # 執行推理 - 設定 eval_mode=True 以獲取返回值
            result = self.model.infer(
                self.tokenizer,
                prompt=prompt,
                image_file=image_path,
                output_path=output_dir,
                base_size=self.base_size,
                image_size=self.image_size,
                crop_mode=self.crop_mode,
                save_results=False,
                test_compress=self.test_compress,
                eval_mode=True  # 使用 eval 模式返回結果
            )
            
        except Exception as e:
            # 清理臨時目錄
            import shutil
            shutil.rmtree(output_dir, ignore_errors=True)
            raise e
        
        # 從輸出目錄讀取結果
        ocr_output = ""
        try:
            # 查找輸出的文字檔案
            for filename in os.listdir(output_dir):
                if filename.endswith('.txt') or filename.endswith('.md'):
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content:
                            ocr_output = content
                            print(f"從檔案 {filename} 讀取 OCR 結果，長度: {len(content)}")
                            break
        except Exception as e:
            print(f"讀取輸出檔案時發生錯誤: {e}")
        
        # 清理臨時目錄
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
        
        elapsed_time = time.time() - start_time
        print(f"模型推理完成")
        
        # 詳細日誌：記錄推理結果
        print(f"推理返回值類型: {type(result)}")
        print(f"推理返回值內容: {result}")
        print(f"從檔案讀取的輸出長度: {len(ocr_output) if ocr_output else 0}")
        
        # 提取 OCR 文字
        ocr_text = None
        
        # 方法 1: 從輸出檔案讀取（最可靠）
        if ocr_output and len(ocr_output) > 0:
            print(f"使用方法 1: 從輸出檔案讀取 OCR 文字，長度: {len(ocr_output)}")
            ocr_text = ocr_output
        # 方法 2: 檢查返回值是否為字串
        elif result and isinstance(result, str) and len(result) > 0:
            print(f"使用方法 2: 從返回值提取 OCR 文字，長度: {len(result)}")
            ocr_text = result
        # 方法 3: 檢查返回值是否有 text 屬性
        elif hasattr(result, 'text') and result.text:
            ocr_text = result.text
            print(f"使用方法 3: 從 result.text 提取，長度: {len(ocr_text)}")
        # 方法 4: 檢查返回值是否為 dict
        elif isinstance(result, dict) and 'text' in result:
            ocr_text = result['text']
            print(f"使用方法 4: 從 dict 提取，長度: {len(ocr_text) if ocr_text else 0}")
        
        return ocr_text if ocr_text else ""
    
    @with_timeout(300)  # 使用裝飾器設定超時
    def perform_ocr(self, image_path, custom_prompt=None):
        """
        執行 OCR 辨識
        
        Args:
            image_path: 圖片路徑
            custom_prompt: 自訂提示詞
            
        Returns:
            dict: OCR 辨識結果
        """
        print(f"開始執行 OCR 辨識: {image_path}")
        
        # 檢查圖片是否存在
        if not os.path.exists(image_path):
            error_msg = f"圖片檔案不存在: {image_path}"
            print(f"錯誤: {error_msg}")
            return {'error': error_msg, 'image_path': image_path}
        
        # 載入圖片以驗證
        try:
            img = Image.open(image_path)
            print(f"已載入圖片: {image_path}")
            print(f"圖片尺寸: {img.size}, 格式: {img.format}, 模式: {img.mode}")
        except Exception as e:
            error_msg = f"無法載入圖片: {str(e)}"
            print(f"錯誤: {error_msg}")
            return {'error': error_msg, 'image_path': image_path}
        
        # 檢查 GPU 記憶體
        gpu_mem = check_gpu_memory()
        print(f"GPU 記憶體狀態: {gpu_mem}")
        
        # 設定提示詞（必須以 <image> 開頭）
        if custom_prompt:
            # 確保自訂 prompt 包含 <image> 標記
            if '<image>' not in custom_prompt:
                prompt = f"<image>\n{custom_prompt}"
            else:
                prompt = custom_prompt
        else:
            prompt = "<image>\nFree OCR."
        print(f"使用提示詞: {prompt}")
        
        start_time = time.time()
        
        # 執行 OCR 推理
        try:
            print(f"正在執行 OCR 辨識... 超時設定: {self.ocr_timeout} 秒")
            
            # 使用帶超時的推理方法
            ocr_text = self._perform_ocr_inference(image_path, prompt)
            
            elapsed_time = time.time() - start_time
            print(f"OCR 處理耗時: {elapsed_time:.2f} 秒")
            
            # 檢查是否為 "幻覺" 輸出
            ocr_text_clean = ocr_text.strip()
            if len(ocr_text_clean) < 50:  # 文字太短
                prompt_overlap = sum(1 for a, b in zip(ocr_text_clean.lower(), prompt.lower()) if a == b)
                overlap_ratio = prompt_overlap / max(len(ocr_text_clean), 1)
                
                if overlap_ratio > 0.7:  # 超過 70% 重疊
                    error_msg = f"OCR 結果疑似模型幻覺（文字過短且與提示詞高度重疊）。請嘗試拍攝更清晰的照片。"
                    print(f"⚠️  {error_msg}")
                    print(f"   文字長度: {len(ocr_text_clean)}, 重疊率: {overlap_ratio:.1%}")
                    return {
                        'error': error_msg,
                        'text': ocr_text,
                        'image_path': image_path,
                        'processing_time': elapsed_time
                    }
            
            print(f"OCR 辨識完成，文字長度: {len(ocr_text)}")
            
            # 檢查 OCR 後的 GPU 記憶體
            gpu_mem_after = check_gpu_memory()
            print(f"OCR 後 GPU 記憶體狀態: {gpu_mem_after}")
            
            # 自動清理 GPU 快取（如果使用率超過 80%）
            if gpu_mem_after['available'] and gpu_mem_after['usage_percent'] > 80:
                print(f"⚠️  GPU 記憶體使用率過高 ({gpu_mem_after['usage_percent']:.1f}%)，正在清理快取...")
                torch.cuda.empty_cache()
                gpu_mem_cleaned = check_gpu_memory()
                print(f"✅ GPU 快取已清理，記憶體使用率: {gpu_mem_cleaned['usage_percent']:.1f}%")
            
            return {
                'text': ocr_text,
                'image_path': image_path,
                'processing_time': elapsed_time,
                'gpu_memory': gpu_mem_after
            }
            
        except FuturesTimeoutError:
            error_msg = f"OCR 推理超時 (超過 {self.ocr_timeout} 秒)"
            print(f"錯誤: {error_msg}")
            return {'error': error_msg, 'image_path': image_path}
        except Exception as e:
            error_msg = f"OCR 推理執行失敗: {str(e)}"
            print(f"錯誤: {error_msg}")
            import traceback
            print(f"錯誤詳情:\n{traceback.format_exc()}")
            return {'error': error_msg, 'image_path': image_path}
    
    def perform_batch_ocr(self, image_paths, custom_prompt=None):
        """
        批次執行 OCR 辨識
        
        Args:
            image_paths: 圖片路徑列表
            custom_prompt: 自訂提示詞
            
        Returns:
            list: OCR 辨識結果列表
        """
        results = []
        for idx, image_path in enumerate(image_paths):
            print(f"處理第 {idx+1}/{len(image_paths)} 個圖片: {image_path}")
            result = self.perform_ocr(image_path, custom_prompt)
            results.append(result)
        
        return results

