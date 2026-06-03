#!/usr/bin/env python3
"""
专门解析有问题的PDF文件，使用更高级的OCR配置
"""

from liteparse import LiteParse

def parse_specific_file():
    filename = "files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf"
    output_file = "【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满_improved.md"
    
    print(f"开始解析文件: {filename}")
    
    # 尝试1: 使用默认配置（无OCR）
    parser1 = LiteParse(ocr_enabled=False, quiet=True)
    result1 = parser1.parse(filename)
    
    print(f"无OCR配置解析结果: {len(result1.text)}字符")
    
    # 尝试2: 使用OCR，提高DPI
    parser2 = LiteParse(
        ocr_enabled=True, 
        dpi=300,  # 提高DPI，默认150
        quiet=True
    )
    result2 = parser2.parse(filename)
    
    print(f"OCR + 300DPI解析结果: {len(result2.text)}字符")
    
    # 尝试3: 使用OCR，默认DPI
    parser3 = LiteParse(
        ocr_enabled=True, 
        dpi=150,  # 默认DPI
        quiet=True
    )
    result3 = parser3.parse(filename)
    
    print(f"OCR + 150DPI解析结果: {len(result3.text)}字符")
    
    # 保存最佳结果
    best_result = max([(len(result1.text), result1), (len(result2.text), result2), (len(result3.text), result3)])
    
    print(f"最佳结果: {best_result[0]}字符")
    
    # 保存到Markdown文件
    md_content = f"# 【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满\n\n"
    md_content += f"## 文件统计\n"
    md_content += f"页数: {len(best_result[1].pages)}\n"
    md_content += f"文本长度: {len(best_result[1].text)} 字符\n\n"
    md_content += f"## 内容\n"
    md_content += best_result[1].text
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"结果已保存到: {output_file}")
    
    # 打印前200字符进行预览
    if len(best_result[1].text) > 0:
        print(f"\n预览内容:\n{best_result[1].text[:200]}")
    else:
        print("警告: 未能提取到任何文本内容")

if __name__ == "__main__":
    parse_specific_file()
