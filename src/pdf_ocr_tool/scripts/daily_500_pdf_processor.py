#!/usr/bin/env python3
"""
每日500个PDF处理系统 - 命令行入口
用法: python3 daily_500_pdf_processor.py files output/daily/ [--workers 6] [--topic AI]
"""

import os
import re
import shutil
import argparse
from datetime import datetime

from pdf_ocr_tool.scripts.daily_processor import DailyPDFProcessor
from pdf_ocr_tool.topics.config import FILENAME_CLASSIFIER, CLASS_LAYOUT


def classify_and_dispatch(input_dir):
    """按文件名开头的星球名把文档分类，移到对应类别子目录。

    只处理输入目录顶层的文档文件（PDF + Office 可转换文档）；
    invest 类留在输入目录顶层（不移动）；media/other 类移到
    {input_dir}/{input_sub}/ 子目录。返回 {class_name: [文件名]}。

    Args:
        input_dir: 用户放置文档的目录（如 files/）

    Returns:
        dict: {类别名: 该类别文件名列表}
    """
    doc_exts = ('.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx')
    files = [f for f in os.listdir(input_dir)
             if f.lower().endswith(doc_exts)
             and os.path.isfile(os.path.join(input_dir, f))]

    classes = {c['class']: [] for c in FILENAME_CLASSIFIER}
    classes['other'] = []

    for fname in files:
        # 归一化连续空格为单个空格再匹配，避免星球名/标题间空格数量差异导致漏分
        norm_name = re.sub(r'\s+', ' ', fname)
        matched = None
        for c in FILENAME_CLASSIFIER:
            if any(norm_name.startswith(p) for p in c['patterns']):
                matched = c['class']
                break
        cls = matched if matched else 'other'
        sub = CLASS_LAYOUT[cls]['input_sub']
        if sub:
            sub_dir = os.path.join(input_dir, sub)
            os.makedirs(sub_dir, exist_ok=True)
            src = os.path.join(input_dir, fname)
            dst = os.path.join(sub_dir, fname)
            if os.path.abspath(src) != os.path.abspath(dst):
                shutil.move(src, dst)
        classes[cls].append(fname)

    return classes


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
    
    # 处理专题列表
    topics = args.topic if args.topic else ['AI']
    
    # 按文件名开头的星球名自动分流：投资/自媒体/其他各自独立批次，
    # 输出与专题、微信读书收集均隔离，避免混在一起
    classes = classify_and_dispatch(args.input_dir)
    
    any_success = False
    for cls in ['invest', 'media', 'other']:
        if not classes.get(cls):
            continue
        
        layout = CLASS_LAYOUT[cls]
        input_dir = os.path.join(args.input_dir, layout['input_sub']) if layout['input_sub'] else args.input_dir
        
        # 自动追加当天日期作为输出子目录（精确到小时，支持一天多次总结）
        today_str = datetime.now().strftime('%Y%m%d%H')
        output_dir = layout['output_root'].rstrip('/')
        if not re.search(r'\d{10}$', output_dir):
            output_dir = os.path.join(output_dir, today_str)
        
        print(f"\n===== 处理【{cls}】批次: {len(classes[cls])} 个文档 =====")
        print(f"  输入目录: {input_dir}")
        print(f"  输出目录: {output_dir}")
        
        config = {
            'input_dir': input_dir,
            'output_dir': output_dir,
            'workers': args.workers,
            'strategy': args.strategy,
            'min_score': args.min_score,
            'force': args.force,
            'no_ai': args.no_ai,
            'topics': topics,
        }
        
        processor = DailyPDFProcessor(config)
        ok = processor.run_all()
        any_success = any_success or ok
    
    return 0 if any_success else 1


if __name__ == "__main__":
    main()
