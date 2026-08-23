#!/usr/bin/env python3
"""
AI内容总结模块 - 聚合导出（向后兼容）

原大文件已按类拆分为独立模块，本文件保留原导入路径以便兼容：
  from pdf_ocr_tool.summarizers.financial_summarizer import X
"""

from pdf_ocr_tool.summarizers.aicontent_summarizer import AIContentSummarizer
from pdf_ocr_tool.summarizers.financial_research_summarizer import FinancialResearchSummarizer
from pdf_ocr_tool.summarizers.markdown_file_summarizer import MarkdownFileSummarizer

__all__ = ['AIContentSummarizer', 'FinancialResearchSummarizer', 'MarkdownFileSummarizer']
