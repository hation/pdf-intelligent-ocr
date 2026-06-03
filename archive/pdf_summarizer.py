#!/usr/bin/env python3
"""
PDF 内容提取与简单总结工具
使用 PyPDF2 库提取文本内容，并提供简单的统计和总结功能
"""

import sys
import argparse
from PyPDF2 import PdfReader
from collections import Counter
import re


def extract_text_from_pdf(pdf_path):
    """
    从 PDF 文件中提取文本内容
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = []
            
            for page_num, page in enumerate(reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text.append(f"=== 第 {page_num} 页 ===\n{page_text}")
            
            return '\n\n'.join(text), len(reader.pages)
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None, 0


def clean_and_tokenize(text):
    """
    清洁文本并分词
    """
    # 移除非字母数字字符，保留中文和英文
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]+', ' ', text)
    # 转换为小写
    cleaned = cleaned.lower()
    # 分词
    tokens = cleaned.split()
    return tokens


def analyze_text(text):
    """
    分析文本内容，生成基本统计信息
    """
    # 分词
    tokens = clean_and_tokenize(text)
    
    # 计算统计数据
    word_count = len(tokens)
    unique_word_count = len(set(tokens))
    char_count = len(text)
    
    # 计算词频
    word_freq = Counter(tokens)
    top_words = word_freq.most_common(20)
    
    return {
        'word_count': word_count,
        'unique_word_count': unique_word_count,
        'char_count': char_count,
        'top_words': top_words
    }


def print_summary(text, stats, num_pages):
    """
    打印文本内容和统计信息
    """
    print(f"PDF 文件处理完成！")
    print(f"总页数: {num_pages}")
    print(f"字符总数: {stats['char_count']}")
    print(f"总词数: {stats['word_count']}")
    print(f"不重复词数: {stats['unique_word_count']}")
    print(f"\n词频最高的 20 个词汇:")
    for word, count in stats['top_words']:
        print(f"  {word}: {count}")
    print(f"\n=== 内容预览 ===\n")
    # 打印前 500 个字符作为预览
    print(text[:500] + "..." if len(text) > 500 else text)


def main():
    parser = argparse.ArgumentParser(description='PDF 内容提取与简单总结工具')
    parser.add_argument('pdf_file', help='要处理的 PDF 文件路径')
    parser.add_argument('-o', '--output', help='输出文本文件路径')
    parser.add_argument('-p', '--print', action='store_true', 
                       help='直接打印提取的文本到控制台')
    parser.add_argument('-s', '--stats', action='store_true', 
                       help='只显示统计信息')
    
    args = parser.parse_args()
    
    print(f"正在处理 PDF 文件: {args.pdf_file}")
    
    # 提取文本
    text, num_pages = extract_text_from_pdf(args.pdf_file)
    
    if text:
        # 分析文本
        stats = analyze_text(text)
        
        if args.stats:
            print_summary(text, stats, num_pages)
        elif args.print:
            print(text)
        else:
            print_summary(text, stats, num_pages)
        
        # 保存到输出文件
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as file:
                    file.write(text)
                print(f"\n文本已保存到: {args.output}")
            except Exception as e:
                print(f"\nError saving to file: {e}")
    else:
        print("未能提取到文本内容")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
