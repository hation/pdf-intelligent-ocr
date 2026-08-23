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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from pdf_ocr_tool.topics.config import TOPIC_CONFIGS
from pdf_ocr_tool.topics.utils import find_latest_summaries_dir
from pdf_ocr_tool.topics.extractor import extract_topic_by_keywords

# 聚合导出（保持向后兼容：from extract_topic_summary import X）
from pdf_ocr_tool.topics.config import TOPIC_CONFIGS as _TOPIC_CONFIGS
from pdf_ocr_tool.topics.extractor import extract_topic_by_keywords as _extract_topic_by_keywords


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

    for topic in topics:
        if topic not in TOPIC_CONFIGS:
            print(f"❌ 不支持的专题: {topic}")
            print(f"支持的专题: {', '.join(TOPIC_CONFIGS.keys())}")
            continue

        extract_topic_by_keywords(input_dir, TOPIC_CONFIGS[topic])

    print(f"\n✅ 共提取 {len(topics)} 个专题报告")


if __name__ == "__main__":
    main()
