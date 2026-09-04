#!/usr/bin/env python3
"""
每日500个PDF处理系统 - 命令行入口
用法: python3 daily_500_pdf_processor.py files output/daily/ [--workers 6] [--topic AI]
"""

import os
import re
import argparse
from datetime import datetime

from pdf_ocr_tool.scripts.daily_processor import DailyPDFProcessor


def main():
    parser = argparse.ArgumentParser(
        description="每日500个PDF处理系统 - 完整解决方案"
    )
    
    parser.add_argument('input_dir', help='输入目录（包含PDF文件）')
    parser.add_argument('output_dir', help='输出目录（如 output/daily/，自动追加当天日期）')
    parser.add_argument('--workers', type=int, default=8, 
                       help='并行工作进程数（默认: 8）')
    parser.add_argument('--strategy', choices=['auto', 'tesseract', 'liteparse', 'optimized'], 
                       default='auto', help='处理策略（默认: 自动选择）')
    parser.add_argument('--no-ai', action='store_true', 
                       help='禁用AI内容分析和专题提取')
    parser.add_argument('--topic', '-t', action='append', 
                       help='要提取的专题（可多次指定，默认: AI），支持：AI/新能源/医药/消费/科技/汽车/有色/煤炭/地产/银行')
    parser.add_argument('--min-score', type=int, default=60,
                       help='进入总结的最低解析质量评分（默认: 60）')
    parser.add_argument('--force', action='store_true',
                       help='忽略缓存，强制重新解析PDF')
    
    args = parser.parse_args()
    
    # 自动追加当天日期作为输出子目录（精确到小时，支持一天多次总结）
    # 用户传 output/daily/ -> 实际输出 output/daily/YYYYMMDDHH/
    today_str = datetime.now().strftime('%Y%m%d%H')
    output_dir = args.output_dir.rstrip('/')
    # 如果末尾不是日期格式，自动追加当天日期
    if not re.search(r'\d{10}$', output_dir):
        output_dir = os.path.join(output_dir, today_str)
    
    # 处理专题列表
    topics = args.topic if args.topic else ['AI']
    
    # 配置
    config = {
        'input_dir': args.input_dir,
        'output_dir': output_dir,
        'workers': args.workers,
        'strategy': args.strategy,
        'min_score': args.min_score,
        'force': args.force,
        'no_ai': args.no_ai,
        'topics': topics
    }
    
    # 创建处理器实例
    processor = DailyPDFProcessor(config)
    
    # 运行处理
    success = processor.run_all()
    
    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    main()
