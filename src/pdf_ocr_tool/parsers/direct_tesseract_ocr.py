#!/usr/bin/env python3
"""
直接使用Tesseract OCR进行识别，避免中间转换层可能带来的质量损失
接受命令行参数
"""

from pdf2image import convert_from_path
import pytesseract
import PIL.ImageOps
import io
import os
import sys

def tesseract_ocr_on_pdf(filename):
    print(f"正在使用Tesseract OCR识别PDF文件: {filename}")
    
    # 将PDF转换为图像
    try:
        print("正在将PDF转换为图像...")
        images = convert_from_path(filename, dpi=400, grayscale=True)
        print(f"成功转换为 {len(images)} 页图像")
    except Exception as e:
        print(f"转换失败: {e}")
        return None
    
    full_text = []
    
    for i, img in enumerate(images, 1):
        print(f"正在识别第 {i} 页...")
        
        # 优化图像
        enhanced_img = img
        
        # 提高对比度
        enhanced_img = PIL.ImageOps.autocontrast(enhanced_img, cutoff=2)
        
        # 二值化处理
        enhanced_img = enhanced_img.convert('L').point(lambda x: 0 if x < 150 else 255, '1')
        
        # 进行OCR识别
        try:
            text = pytesseract.image_to_string(enhanced_img, lang='chi_sim+eng')
            
            if text.strip():
                full_text.append(f"=== 第 {i} 页 ===\n{text.strip()}")
                print(f"识别到 {len(text.strip())} 个字符")
            else:
                print("警告: 未识别到任何文本")
                
        except Exception as e:
            print(f"OCR识别失败: {e}")
            continue
    
    return '\n\n'.join(full_text)

def save_to_markdown(text, filename, output_dir="outputs_liteparse_ocr"):
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/{os.path.splitext(os.path.basename(filename))[0]}_tesseract.md"
    
    md_content = f"# {os.path.splitext(os.path.basename(filename))[0]}\n\n"
    md_content += f"## 文件统计\n"
    md_content += f"页数: 1\n"
    md_content += f"字符数: {len(text)}\n"
    md_content += f"单词数: {len(text.split())}\n"
    md_content += f"解析方法: 直接Tesseract OCR识别\n"
    md_content += f"配置: 400DPI，对比度增强，二值化\n\n"
    
    md_content += f"## 内容\n"
    md_content += text
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_file

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf"
    
    output_dir = "outputs_liteparse_ocr"
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    ocr_result = tesseract_ocr_on_pdf(filename)
    
    if ocr_result:
        output_path = save_to_markdown(ocr_result, filename, output_dir)
        print(f"结果已保存到: {output_path}")
        
        # 检查结果质量
        char_count = len(ocr_result)
        word_count = len(ocr_result.split())
        
        print(f"\n=== 识别质量分析 ===")
        print(f"字符数: {char_count}")
        print(f"单词数: {word_count}")
        
        if char_count > 1000 and word_count > 50:
            print("✓ 识别质量良好")
        elif char_count > 500 and word_count > 20:
            print("⚠️  识别质量一般，可能需要进一步优化")
        else:
            print("❌ 识别质量差，可能是图像质量问题")
    else:
        print("OCR识别失败")

if __name__ == "__main__":
    main()
