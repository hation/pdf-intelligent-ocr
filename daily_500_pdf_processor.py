#!/usr/bin/env python3

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_ocr_tool.scripts.daily_500_pdf_processor import DailyPDFProcessor, main


if __name__ == "__main__":
    # 设置默认目录
    default_input_dir = os.path.join(os.path.dirname(__file__), "files")
    today_str = datetime.now().strftime('%Y%m%d')
    default_output_dir = os.path.join(os.path.dirname(__file__), "output", "daily", today_str)
    
    # 如果没有提供参数，使用默认值
    if len(sys.argv) == 1:
        sys.argv.extend([default_input_dir, default_output_dir])
    
    main()
