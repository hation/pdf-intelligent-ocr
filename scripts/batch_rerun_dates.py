#!/usr/bin/env python3
"""
批量重跑多个日期的总结（临时工具）

解决什么问题：
  历史某些日期的 summaries/ 总结存在质量问题（内容缺失、格式错误等），需要
  从已解析的 processed/ 目录重新调用大模型生成总结。本脚本支持一次指定多个
  日期批量重跑，并重新生成对应的 summary_list。

与 rerun_summaries.py 的区别：
  rerun_summaries.py 只重跑单个日期；本脚本支持批量多日期。

用法: python3 scripts/batch_rerun_dates.py <date1> <date2> ... [workers]
示例: python3 scripts/batch_rerun_dates.py 20260602 20260603 8
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../src/pdf_ocr_tool'))

from summarizers.financial_summarizer import MarkdownFileSummarizer

def main():
    args = sys.argv[1:]
    workers = 8
    dates = []
    
    for a in args:
        if a.isdigit() and len(a) == 1:
            workers = int(a)
        else:
            dates.append(a)
    
    if not dates:
        print("用法: python3 scripts/batch_rerun_dates.py <date1> <date2> ... [workers]")
        sys.exit(1)
    
    summarizer = MarkdownFileSummarizer()
    
    print("=" * 60)
    print(f"批量重跑 {len(dates)} 个日期的总结")
    print(f"日期: {', '.join(dates)}")
    print(f"workers: {workers}")
    print("=" * 60)
    print()
    
    total_all = 0
    success_dates = []
    fail_dates = []
    
    for i, date in enumerate(dates):
        processed_dir = f"output/daily/{date}/processed"
        summaries_dir = f"output/daily/{date}/summaries"
        list_file = f"output/daily/{date}/reports/summary_list_{date}.md"
        
        if not os.path.isdir(processed_dir):
            print(f"[{i+1}/{len(dates)}] ❌ {date}: processed 目录不存在，跳过")
            fail_dates.append(date)
            continue
        
        os.makedirs(summaries_dir, exist_ok=True)
        
        print(f"[{i+1}/{len(dates)}] 🚀 开始重跑 {date} ...")
        
        analyses = summarizer.batch_process_markdown_files(
            processed_dir,
            summaries_dir=summaries_dir,
            workers=workers,
            only_new=False
        )
        
        if analyses:
            os.makedirs(os.path.dirname(list_file), exist_ok=True)
            summarizer.generate_summary_list_report(analyses, list_file, summaries_dir)
            print(f"  ✅ 完成：{len(analyses)} 份总结")
            print(f"  📄 summary_list: {list_file}")
            success_dates.append((date, len(analyses)))
            total_all += len(analyses)
        else:
            print(f"  ⚠️  没有生成总结")
            fail_dates.append(date)
        
        print()
    
    print("=" * 60)
    print(f"全部完成！成功 {len(success_dates)} 个日期，失败 {len(fail_dates)} 个日期")
    print(f"总计生成 {total_all} 份总结")
    if success_dates:
        print("成功日期:")
        for d, n in success_dates:
            print(f"  {d}: {n} 份")
    if fail_dates:
        print(f"失败/跳过日期: {', '.join(fail_dates)}")
    print("=" * 60)

if __name__ == '__main__':
    main()
