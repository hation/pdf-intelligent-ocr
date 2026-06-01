#!/usr/bin/env python3
from liteparse import LiteParse

def test_liteparse_with_ocr():
    print("Testing LiteParse with OCR enabled...")
    
    # 创建解析器实例，启用 OCR
    parser = LiteParse(ocr_enabled=True, quiet=True)
    
    # 测试解析有问题的文件
    filename = "files/【大佬持仓跟踪】HVDC+华为+AIDC，客户包括华为、维谛、台达等企业，熔断器已形成最高1500VDC平台，这家公司高压直流继电器已布局1000V产品.pdf"
    
    try:
        print(f"Parsing file: {filename}")
        result = parser.parse(filename)
        
        print(f"Parsing successful!")
        print(f"Number of pages: {len(result.pages)}")
        print(f"Total text length: {len(result.text)} characters")
        
        if len(result.text) > 0:
            print(f"\nFirst 300 characters of text:")
            print(result.text[:300])
        else:
            print("Warning: No text was extracted!")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_liteparse_with_ocr()
