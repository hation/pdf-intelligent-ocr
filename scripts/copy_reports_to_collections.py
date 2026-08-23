#!/usr/bin/env python3
"""
批量复制历史日期的汇总文档到集合文件夹（临时工具）

解决什么问题：
  新增了"每日重点汇总 -> 重点汇总/、summary_list -> 一句话总结/"的复制功能后，
  历史日期目录中的文件尚未复制。本脚本遍历 output/daily/ 下所有日期目录，
  调用 daily_processor.copy_reports_to_collections 补齐复制。

用法:
  python3 scripts/copy_reports_to_collections.py
  可选参数: --start YYYYMMDD --end YYYYMMDD（只处理日期区间）
"""

import os
import sys
import re
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from pdf_ocr_tool.scripts.daily_processor import copy_reports_to_collections


def main():
    parser = argparse.ArgumentParser(description='批量复制历史日期的汇总文档到集合文件夹')
    parser.add_argument('--start', help='起始日期 YYYYMMDD（可选）')
    parser.add_argument('--end', help='结束日期 YYYYMMDD（可选）')
    args = parser.parse_args()

    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output', 'daily')
    if not os.path.isdir(base_dir):
        print(f"❌ 目录不存在: {base_dir}")
        return

    dates = sorted(d for d in os.listdir(base_dir) if re.match(r'^\d{8}$', d))
    if args.start:
        dates = [d for d in dates if d >= args.start]
    if args.end:
        dates = [d for d in dates if d <= args.end]

    print(f"共 {len(dates)} 个日期目录待检查")

    total_copied = 0
    for date_str in dates:
        date_dir = os.path.join(base_dir, date_str)
        copied = copy_reports_to_collections(date_dir)
        if copied:
            for src, dst in copied:
                print(f"✅ {os.path.basename(src)} -> {os.path.relpath(dst, base_dir)}")
                total_copied += 1
        else:
            print(f"⏭️  {date_str}: 无可复制的汇总文件")

    print("\n" + "=" * 60)
    print(f"共处理 {len(dates)} 个日期，成功复制 {total_copied} 个文件")


if __name__ == '__main__':
    main()
