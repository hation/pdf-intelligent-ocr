#!/usr/bin/env python3
"""
专题提取工具 - 支持多专题配置（AI/新能源/医药/消费/科技/汽车/有色/煤炭/地产/银行）

使用方式:
    # 默认提取AI专题
    python3 extract_topic_summary.py

    # 提取指定专题（支持多个）
    python3 extract_topic_summary.py --topic 新能源
    python3 extract_topic_summary.py --topic AI --topic 医药

    # 从指定目录提取
    python3 extract_topic_summary.py --input output/daily/20260724/summaries --topic 消费
"""

import argparse
import sys
import os
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from pdf_ocr_tool.topics.config import TOPIC_CONFIGS
from pdf_ocr_tool.topics.utils import find_latest_summaries_dir
from pdf_ocr_tool.topics.extractor import extract_topic_by_keywords

# 聚合导出（保持向后兼容：from extract_topic_summary import X）
from pdf_ocr_tool.topics.config import TOPIC_CONFIGS as _TOPIC_CONFIGS
from pdf_ocr_tool.topics.extractor import extract_topic_by_keywords as _extract_topic_by_keywords


def infer_date_and_batch(input_dir):
    """从输入 summaries 目录推断日期字符串与批次输出根。

    输入形如 output/daily/2026090615/summaries 或 output/daily_media/2026090615/summaries：
      - 日期取父目录名（2026090615，支持 8 位或 10 位）
      - 批次根：daily_media -> output/topic_summaries_media，否则 -> output/topic_summaries
    """
    abs_dir = os.path.abspath(input_dir)
    parent = os.path.basename(os.path.dirname(abs_dir))
    if re.fullmatch(r'\d{8}|\d{10}', parent):
        date_str = parent
    else:
        # 兼容直接传日期目录（如 output/daily/2026090615）
        base = os.path.basename(abs_dir)
        date_str = base if re.fullmatch(r'\d{8}|\d{10}', base) else None

    grand = os.path.basename(os.path.dirname(os.path.dirname(abs_dir)))
    if 'daily_media' in grand:
        output_root = os.path.join('output', 'topic_summaries_media')
    else:
        output_root = os.path.join('output', 'topic_summaries')
    return date_str, output_root


def main():
    parser = argparse.ArgumentParser(
        description='专题提取工具 - 支持多专题配置（AI/新能源/医药/消费/科技/汽车/有色/煤炭/地产/银行）'
    )
    parser.add_argument('--input', '-i', help='输入summaries目录（默认自动找最新的）')
    parser.add_argument('--topic', '-t', action='append',
                        help=f'提取的专题（可重复指定），支持：{", ".join(TOPIC_CONFIGS.keys())}（默认提取AI）')
    parser.add_argument('--list-topics', action='store_true', help='列出所有支持的专题')

    args = parser.parse_args()

    if args.list_topics:
        print("支持的专题列表:")
        for name, config in TOPIC_CONFIGS.items():
            print(f"  - {name}: {config['description']}")
            print(f"    关键词示例: {', '.join(config['keywords'][:5])}...")
        return

    input_dir = args.input if args.input else find_latest_summaries_dir()
    if not input_dir:
        print("❌ 未找到summaries目录，请指定--input参数")
        return

    topics = args.topic if args.topic else ['AI']

    date_str, output_root = infer_date_and_batch(input_dir)

    for topic in topics:
        if topic not in TOPIC_CONFIGS:
            print(f"❌ 不支持的专题: {topic}")
            print(f"支持的专题: {', '.join(TOPIC_CONFIGS.keys())}")
            continue

        extract_topic_by_keywords(
            input_dir,
            TOPIC_CONFIGS[topic],
            output_dir=os.path.join(output_root, topic),
            date_str=date_str,
        )

    print(f"\n✅ 共提取 {len(topics)} 个专题报告")


if __name__ == "__main__":
    main()
