#!/usr/bin/env python3
"""
重跑指定日期的 AI 总结（临时工具）

解决什么问题：
  某个日期的 summaries/ 总结缺失或质量不合格时，从已解析的 processed/ 目录
  重新调用大模型生成总结。使用 only_new=False 强制覆盖重跑（默认只处理新文件）。

用法: python3 scripts/rerun_summaries.py <YYYYMMDD> [workers]
示例: python3 scripts/rerun_summaries.py 20260810 6
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/pdf_ocr_tool'))

from summarizers.financial_summarizer import MarkdownFileSummarizer

def rerun(date_str, workers=6):
    processed_dir = f"output/daily/{date_str}/processed"
    summaries_dir = f"output/daily/{date_str}/summaries"
    list_file = f"output/daily/{date_str}/reports/summary_list_{date_str}.md"
    
    if not os.path.isdir(processed_dir):
        print(f"❌ {processed_dir} 不存在")
        return
    
    os.makedirs(summaries_dir, exist_ok=True)
    
    summarizer = MarkdownFileSummarizer()
    print(f"🚀 开始重跑 {date_str} 的总结（{workers} 个 worker）...")
    
    analyses = summarizer.batch_process_markdown_files(
        processed_dir,
        summaries_dir=summaries_dir,
        workers=workers,
        only_new=False
    )
    
    print(f"✅ 完成：{len(analyses)} 份总结")
    print(f"📂 summaries: {summaries_dir}")
    
    # 生成 summary_list
    if analyses:
        os.makedirs(os.path.dirname(list_file), exist_ok=True)
        summarizer.generate_summary_list_report(analyses, list_file, summaries_dir)
        print(f"📄 summary_list: {list_file}")

if __name__ == '__main__':
    date = sys.argv[1] if len(sys.argv) > 1 else None
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    if not date:
        print("用法: python3 scripts/rerun_summaries.py <YYYYMMDD> [workers]")
        sys.exit(1)
    rerun(date, workers)
