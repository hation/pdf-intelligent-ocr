# 项目规则 - PDF 识别方案

## 识别困难PDF的处理方案

### 问题特征
如果PDF文件具有以下特征，则可能属于难以识别的类型：
- 文件大小较小但内容复杂
- 使用常规OCR方法识别到的内容极少或只有水印
- 文件可能是扫描件或图像形式
- 文本与背景对比度低

### 推荐处理流程

1. 首先尝试使用PyPDF2等基本工具检查文件是否包含可选择的文本：
```python
from PyPDF2 import PdfReader

def has_selectable_text(filename):
    reader = PdfReader(filename)
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and len(text.strip()) > 100:
            print(f"第{page_num}页包含可选文本")
            return True
    print("该文件可能是扫描件或无可选文本的PDF")
    return False
```

2. 如果确认是难以识别的PDF，则立即使用我们的Tesseract OCR方案：
```bash
cd /Users/xingan/Documents/software/workspace/summary
./direct_tesseract_ocr.py <PDF文件路径>
```

3. 或者直接使用Python代码：
```python
from direct_tesseract_ocr import tesseract_ocr_on_pdf
tesseract_ocr_on_pdf("/path/to/your/difficult.pdf")
```

### 方案优势
- 直接使用Tesseract OCR引擎，识别率更高
- 包含图像预处理（对比度增强和二值化）
- 支持中文+英文双语言识别
- 可以处理各种复杂布局和低对比度的PDF文件

### 参考文件
详细方案文档: `/Users/xingan/Documents/software/workspace/summary/PDF_OCR_SOLUTION.md`
快速访问配置: `/Users/xingan/Documents/software/workspace/summary/pdf_ocr_recipe.txt`
主执行脚本: `/Users/xingan/Documents/software/workspace/summary/direct_tesseract_ocr.py`

### 成功案例
已成功处理文件: 【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf
识别结果: /Users/xingan/Documents/software/workspace/summary/outputs_liteparse_ocr/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.md
