#!/usr/bin/env python3
"""
将文本内容转换为 Markdown 格式的工具
"""

import os
import sys
import re


def convert_to_markdown(text, filename):
    """
    将提取的文本内容转换为 Markdown 格式
    """
    md_content = []
    
    # 添加标题
    md_content.append(f"# {filename}")
    md_content.append("")
    
    # 提取统计信息部分
    lines = text.split('\n')
    stats_section = []
    content_section = []
    in_content = False
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("=== 第") and line.endswith("页 ==="):
            in_content = True
        
        if not in_content and line:
            stats_section.append(line)
        elif in_content and line:
            content_section.append(line)
    
    # 处理统计信息
    if stats_section:
        md_content.append("## 文档统计")
        md_content.append("")
        
        for line in stats_section:
            if line.startswith("总页数:") or \
               line.startswith("字符总数:") or \
               line.startswith("总词数:") or \
               line.startswith("不重复词数:"):
                # 格式化统计信息为列表
                md_content.append(f"- {line}")
        
        md_content.append("")
    
    # 提取词频信息
    word_freq_match = False
    word_freq = []
    
    for line in lines:
        line = line.strip()
        
        if line == "词频最高的 20 个词汇:":
            word_freq_match = True
        elif word_freq_match and line and not line.startswith("=== "):
            # 去除前缀空格并格式化
            if line.startswith("  "):
                word_freq.append(line.strip())
        elif word_freq_match and line.startswith("=== "):
            break
    
    if word_freq:
        md_content.append("## 词频分析")
        md_content.append("")
        
        md_content.append("| 词汇 | 出现次数 |")
        md_content.append("|------|----------|")
        
        for item in word_freq:
            parts = item.split(": ")
            if len(parts) == 2:
                word = parts[0]
                count = parts[1]
                md_content.append(f"| {word} | {count} |")
        
        md_content.append("")
    
    # 处理内容部分
    if content_section:
        md_content.append("## 内容预览")
        md_content.append("")
        
        current_page = None
        page_content = []
        
        for line in content_section:
            if line.startswith("=== 第") and line.endswith("页 ==="):
                # 新的页码开始
                if current_page and page_content:
                    md_content.append(f"### {current_page}")
                    md_content.append("")
                    for p_line in page_content:
                        if p_line.strip():
                            md_content.append(p_line.strip())
                    md_content.append("")
                
                current_page = line
                page_content = []
            else:
                if line.strip():
                    page_content.append(line.strip())
        
        # 添加最后一页内容
        if current_page and page_content:
            md_content.append(f"### {current_page}")
            md_content.append("")
            for p_line in page_content:
                if p_line.strip():
                    md_content.append(p_line.strip())
            md_content.append("")
    
    return '\n'.join(md_content)


def process_directory(input_dir, output_dir):
    """
    处理目录下的所有文本文件
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + ".md"
            output_path = os.path.join(output_dir, output_filename)
            
            print(f"正在转换: {filename} -> {output_filename}")
            
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                md_content = convert_to_markdown(text, os.path.splitext(filename)[0])
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                print(f"转换成功: {output_path}")
            except Exception as e:
                print(f"转换失败: {filename} - {e}")


def main():
    if len(sys.argv) < 3:
        print("用法: python text_to_markdown.py <输入目录> <输出目录>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_directory(input_dir, output_dir)


if __name__ == '__main__':
    main()
