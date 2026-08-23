#!/usr/bin/env python3
"""
单日 LLM 总结脚本（临时工具）

解决什么问题：
  某个日期的 processed/ 目录已有解析好的 Markdown 文档，但没有生成 summaries/ 总结，
  本脚本对指定日期批量调用大模型生成总结，并输出 summary_list。

注意：
  脚本内硬编码了日期目录（output/daily/20260810），如需处理其他日期请修改下方
  processed_dir / summary_dir 两个路径。

用法:
  python3 run_llm_summary.py
"""
import sys
import os
sys.path.insert(0, 'src')
from pdf_ocr_tool.summarizers.financial_summarizer import MarkdownFileSummarizer

processed_dir = 'output/daily/20260810/processed'
summary_dir = 'output/daily/20260810/summaries'

md_files = [f for f in os.listdir(processed_dir) if f.endswith('.md')]
print(f'开始LLM总结，共 {len(md_files)} 份文档...')

summarizer = MarkdownFileSummarizer()
analyses = summarizer.batch_process_markdown_files(processed_dir, summaries_dir=summary_dir, only_new=True, workers=6)

if analyses:
    summarizer.generate_summary_outputs(analyses, 'output/daily/20260810/summary_list.md', summary_dir)
    print(f'✓ 总结完成，共 {len(analyses)} 份')
else:
    print('✗ 没有生成任何总结')
