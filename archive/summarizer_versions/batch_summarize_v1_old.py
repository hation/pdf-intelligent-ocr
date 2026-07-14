#!/usr/bin/env python3
"""批量AI总结脚本 - 分批处理避免超时"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_ocr_tool.summarizers.financial_summarizer import AIContentSummarizer

def get_one_sentence_summary(summarizer, text, filename):
    """生成一句话总结"""
    
    # 清洁文本
    text = summarizer.clean_text(text)
    
    # 提取句子和关键词
    summarizer.extract_sentences(text)
    summarizer.extract_keywords(text)
    
    if not summarizer.sentences:
        return f"该文件《{filename}》内容无法有效提取"
    
    # 计算句子重要性
    summarizer.calculate_sentence_importance(text)
    
    # 取最重要的1-2个句子
    if summarizer.important_sentences:
        # 找包含最多关键词的句子
        best_sentence = summarizer.important_sentences[0]
        # 确保不太长
        if len(best_sentence) > 200:
            best_sentence = best_sentence[:197] + "..."
        return best_sentence
    
    return f"《{filename}》的内容摘要"

def get_key_points(summarizer, text, count=5):
    """提取核心看点"""
    
    summarizer.extract_sentences(text)
    summarizer.extract_keywords(text)
    
    if not summarizer.sentences:
        return ["无法提取有效内容"]
    
    summarizer.calculate_sentence_importance(text)
    
    points = []
    for sent in summarizer.important_sentences[:count]:
        if len(sent) > 50:  # 只保留有信息量的句子
            points.append(sent[:150] + "..." if len(sent) > 150 else sent)
    
    return points if points else ["内容较简洁，无额外核心看点"]

def process_batch(start_idx, end_idx, md_files, processed_dir, summaries_dir):
    """处理一批文件"""
    
    summarizer = AIContentSummarizer()
    results = []
    
    for i in range(start_idx, min(end_idx, len(md_files))):
        filename = md_files[i]
        
        if not filename.endswith('.md'):
            continue
        
        md_path = os.path.join(processed_dir, filename)
        
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # 生成总结
            one_sentence = get_one_sentence_summary(summarizer, text, filename)
            key_points = get_key_points(summarizer, text)
            
            # 保存单文件总结
            summary_name = filename.replace('_hybrid.md', '_summary.md').replace('.md', '_summary.md')
            summary_path = os.path.join(summaries_dir, summary_name)
            
            summary_content = f"# {filename}\n\n"
            summary_content += f"## 一句话总结\n\n{one_sentence}\n\n"
            summary_content += f"## 核心看点\n\n"
            for j, point in enumerate(key_points, 1):
                summary_content += f"{j}. {point}\n"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            results.append({
                'filename': filename,
                'one_sentence': one_sentence
            })
            
            print(f"  ✓ [{i+1}] {filename[:50]}...")
            
        except Exception as e:
            print(f"  ✗ [{i+1}] {filename[:50]}... 错误: {e}")
    
    return results

def main():
    processed_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/processed"
    summaries_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/summaries"
    reports_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/reports"
    
    os.makedirs(summaries_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 获取所有 markdown 文件
    md_files = [f for f in os.listdir(processed_dir) if f.endswith('.md') and not f.startswith('processing_report_')]
    md_files.sort()
    
    print(f"找到 {len(md_files)} 个文件需要总结")
    
    # 分批处理（每批 30 个）
    batch_size = 30
    all_results = []
    
    for batch_start in range(0, len(md_files), batch_size):
        batch_end = min(batch_start + batch_size, len(md_files))
        print(f"\n=== 处理第 {batch_start//batch_size + 1} 批 ({batch_start+1}-{batch_end}) ===")
        
        batch_results = process_batch(batch_start, batch_end, md_files, processed_dir, summaries_dir)
        all_results.extend(batch_results)
    
    # 生成汇总清单
    print(f"\n=== 生成汇总清单 ===")
    summary_list_path = os.path.join(reports_dir, "summary_list_20260714.md")
    
    with open(summary_list_path, 'w', encoding='utf-8') as f:
        f.write("# 总结清单 2026-07-14\n\n")
        f.write("| 文档名称 | 一句话总结 |\n")
        f.write("|---|---|\n")
        
        for result in all_results:
            # 清理文件名显示
            display_name = result['filename'].replace('_hybrid.md', '')
            # 清理总结中的特殊字符
            summary = result['one_sentence'].replace('|', ' ').replace('\n', ' ')
            f.write(f"| {display_name} | {summary} |\n")
    
    print(f"✓ 汇总清单已保存: {summary_list_path}")
    print(f"\n{'='*50}")
    print(f"全部完成！共总结 {len(all_results)} 个文件")
    print(f"单文件总结目录: {summaries_dir}")
    print(f"汇总报告目录: {reports_dir}")

if __name__ == "__main__":
    main()
