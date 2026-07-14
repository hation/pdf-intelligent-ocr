#!/usr/bin/env python3

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_ocr_tool.scripts.daily_500_pdf_processor import DailyPDFProcessor, main


def get_unique_output_dir(base_dir):
    """获取唯一的输出目录，同一天多次运行自动追加批次号"""
    # 检查目录是否存在，如果不存在直接返回
    if not os.path.exists(base_dir):
        return base_dir
    
    # 查找最大的批次号
    batch_num = 1
    while os.path.exists(f"{base_dir}_{batch_num:02d}"):
        batch_num += 1
    
    return f"{base_dir}_{batch_num:02d}"


if __name__ == "__main__":
    # 设置默认目录
    default_input_dir = os.path.join(os.path.dirname(__file__), "files")
    today_str = datetime.now().strftime('%Y%m%d')
    base_output_dir = os.path.join(os.path.dirname(__file__), "output", "daily", today_str)
    
    # 获取唯一输出目录（防止覆盖）
    default_output_dir = get_unique_output_dir(base_output_dir)
    
    # 如果没有提供参数，使用默认值
    if len(sys.argv) == 1:
        sys.argv.extend([default_input_dir, default_output_dir])
    
    main()
