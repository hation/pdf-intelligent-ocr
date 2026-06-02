#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_ocr_tool.parsers.hybrid_pdf_parser import main, parse_pdf_to_markdown


if __name__ == "__main__":
    main()
