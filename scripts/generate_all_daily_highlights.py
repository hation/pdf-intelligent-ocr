#!/usr/bin/env python3
"""
批量生成历史日期的每日重点汇总（临时工具）

解决什么问题：
  历史日期只有 summaries/ 单文件总结，缺少"每日重点汇总"文档。
  本脚本遍历 output/daily/ 下所有日期目录，对每个有 summaries 的日期
  调用大模型二次提炼生成 reports/每日重点汇总_YYYYMMDD.md，并推送飞书。

用法:
  python3 scripts/generate_all_daily_highlights.py
  可选参数: --start YYYYMMDD --end YYYYMMDD（只处理日期区间）
"""

import os
import sys
import re
import argparse

# 无缓冲输出：让进度实时可见，避免看起来像卡住
sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

# 手动读取 .env（避免 dotenv 在 stdin 模式下报错）
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

from pdf_ocr_tool.summarizers.financial_research_summarizer import FinancialResearchSummarizer


def main():
    parser = argparse.ArgumentParser(description='批量生成历史日期的每日重点汇总')
    parser.add_argument('--start', help='起始日期 YYYYMMDD（可选）')
    parser.add_argument('--end', help='结束日期 YYYYMMDD（可选）')
    args = parser.parse_args()

    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'daily')
    if not os.path.isdir(base_dir):
        print(f"❌ 目录不存在: {base_dir}")
        return

    summarizer = FinancialResearchSummarizer(use_llm=True)

    dates = sorted(d for d in os.listdir(base_dir) if re.match(r'^\d{8}$', d))
    if args.start:
        dates = [d for d in dates if d >= args.start]
    if args.end:
        dates = [d for d in dates if d <= args.end]

    print(f"共 {len(dates)} 个日期目录待检查")

    success, skipped_empty, skipped_exists, failed = [], [], [], []
    for date_str in dates:
        date_dir = os.path.join(base_dir, date_str)
        summary_dir = os.path.join(date_dir, 'summaries')
        reports_dir = os.path.join(date_dir, 'reports')
        output_file = os.path.join(reports_dir, f'每日重点汇总_{date_str}.md')

        if not os.path.isdir(summary_dir):
            skipped_empty.append(date_str)
            continue

        summary_files = [f for f in os.listdir(summary_dir) if f.endswith('_summary.md')]
        if not summary_files:
            skipped_empty.append(date_str)
            continue

        if os.path.exists(output_file):
            skipped_exists.append(date_str)
            print(f"⏭️  {date_str}: 每日重点汇总已存在，跳过")
            continue

        print(f"\n🔄 {date_str}: 开始生成（{len(summary_files)} 份总结）...")
        ok = summarizer.generate_daily_highlight_report(
            summary_dir, output_file, date_str=date_str
        )
        if ok:
            success.append(date_str)
            print(f"✅ {date_str}: 生成成功")
        else:
            failed.append(date_str)
            print(f"❌ {date_str}: 生成失败")

    print("\n" + "=" * 60)
    print(f"✅ 成功 {len(success)} 个: {success}")
    print(f"⏭️  已存在跳过 {len(skipped_exists)} 个: {skipped_exists}")
    print(f"⚠️  无总结跳过 {len(skipped_empty)} 个: {skipped_empty}")
    print(f"❌ 失败 {len(failed)} 个: {failed}")


if __name__ == '__main__':
    main()
