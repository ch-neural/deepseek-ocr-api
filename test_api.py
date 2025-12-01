"""
DeepSeek-OCR API 測試腳本
"""

import requests
import os


def test_health_check():
    """測試健康檢查端點"""
    print("=" * 60)
    print("測試健康檢查端點...")
    print("=" * 60)
    
    response = requests.get("http://localhost:5000/health")
    print(f"狀態碼: {response.status_code}")
    print(f"回應: {response.json()}")
    print()


def test_single_ocr(image_path):
    """測試單張圖片 OCR"""
    print("=" * 60)
    print("測試單張圖片 OCR...")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"錯誤: 圖片不存在 - {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post("http://localhost:5000/ocr", files=files)
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"辨識成功!")
        print(f"圖片路徑: {result.get('image_path')}")
        print(f"使用提示詞: {result.get('prompt')}")
        print(f"OCR 結果:")
        print("-" * 60)
        print(result.get('text'))
        print("-" * 60)
    else:
        print(f"錯誤: {response.json()}")
    
    print()


def test_single_ocr_with_custom_prompt(image_path, custom_prompt):
    """測試使用自訂提示詞的單張圖片 OCR"""
    print("=" * 60)
    print("測試使用自訂提示詞的單張圖片 OCR...")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"錯誤: 圖片不存在 - {image_path}")
        return
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        data = {'prompt': custom_prompt}
        response = requests.post("http://localhost:5000/ocr", files=files, data=data)
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"辨識成功!")
        print(f"圖片路徑: {result.get('image_path')}")
        print(f"使用提示詞: {result.get('prompt')}")
        print(f"OCR 結果:")
        print("-" * 60)
        print(result.get('text'))
        print("-" * 60)
    else:
        print(f"錯誤: {response.json()}")
    
    print()


def test_batch_ocr(image_paths):
    """測試批次圖片 OCR"""
    print("=" * 60)
    print("測試批次圖片 OCR...")
    print("=" * 60)
    
    files = []
    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"警告: 圖片不存在 - {image_path}")
            continue
        files.append(('files', open(image_path, 'rb')))
    
    if len(files) == 0:
        print("錯誤: 沒有有效的圖片")
        return
    
    response = requests.post("http://localhost:5000/ocr/batch", files=files)
    
    # 關閉所有檔案
    for _, f in files:
        f.close()
    
    print(f"狀態碼: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"批次辨識成功! 共處理 {result.get('total')} 張圖片")
        
        for idx, item in enumerate(result.get('results', [])):
            print(f"\n圖片 {idx + 1}:")
            print(f"  路徑: {item.get('image_path')}")
            print(f"  OCR 結果:")
            print("-" * 60)
            print(item.get('text'))
            print("-" * 60)
    else:
        print(f"錯誤: {response.json()}")
    
    print()


if __name__ == '__main__':
    # 測試健康檢查
    test_health_check()
    
    # 測試單張圖片 OCR（請替換為您的圖片路徑）
    test_image = "10-21-37.png"
    if os.path.exists(test_image):
        test_single_ocr(test_image)
        
        # 測試使用自訂提示詞
        custom_prompt = "<image>\n請辨識圖片中的所有文字，包含中文和英文。"
        test_single_ocr_with_custom_prompt(test_image, custom_prompt)
    else:
        print(f"測試圖片不存在: {test_image}")
        print("請將測試圖片放在專案根目錄，或修改 test_image 變數")
    
    # 測試批次 OCR（如果有多張圖片）
    # test_batch_ocr(['image1.png', 'image2.png', 'image3.png'])

