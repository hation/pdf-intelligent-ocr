#!/usr/bin/env python3
"""
使用 LiteParse 解析所有 PDF 文件并保存为 Markdown 格式
"""

import os
import sys
import argparse
from liteparse import LiteParse

def ensure_directory_exists(directory):
    """确保目录存在，不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")
    else:
        print(f"目录已存在: {directory}")

def parse_pdf_with_liteparse(input_dir, output_dir):
    """使用 LiteParse 解析 input_dir 中的所有 PDF 文件"""
    ensure_directory_exists(output_dir)
    
    # 创建解析器实例，禁用 OCR 以避免网络依赖
    parser = LiteParse(ocr_enabled=False, quiet=True)
    
    # 获取 input_dir 中的所有 PDF 文件
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件需要解析")
    
    for filename in pdf_files:
        input_path = os.path.join(input_dir, filename)
        output_filename = os.path.splitext(filename)[0] + '.md'
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            print(f"正在解析: {filename}")
            
            # 解析 PDF 文件
            result = parser.parse(input_path)
            
            # 创建 Markdown 内容
            md_content = []
            md_content.append(f"# {os.path.splitext(filename)[0]}")
            md_content.append("")
            
            # 添加文件统计信息
            md_content.append(f"## 文件统计")
            md_content.append(f"页数: {len(result.pages)}")
            md_content.append(f"文本长度: {len(result.text)} 字符")
            md_content.append("")
            
            # 添加内容
            md_content.append(f"## 内容")
            md_content.append(result.text)
            
            # 保存到 Markdown 文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            
            print(f"解析成功，保存到: {output_filename}")
            
        except Exception as e:
            print(f"解析失败 '{filename}': {e}")
            import traceback
            print(traceback.format_exc())
    
    print(f"\n所有文件解析完成！结果已保存到: {output_dir}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='使用 LiteParse 解析 PDF 文件并保存为 Markdown')
    
    parser.add_argument('input_dir', nargs='?', default='files', 
                      help='输入目录（默认: files）')
    parser.add_argument('output_dir', nargs='?', default='outputs_liteparse',
                      help='输出目录（默认: outputs_liteparse）')
    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.input_dir):
        print(f"错误: 输入目录 '{args.input_dir}' 不存在")
        sys.exit(1)
    
    parse_pdf_with_liteparse(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()
