"""专题提取模块 - 多专题配置与提取"""

from pdf_ocr_tool.topics.config import TOPIC_CONFIGS
from pdf_ocr_tool.topics.utils import (
    read_summary_content,
    is_topic_document,
    find_latest_summaries_dir,
    send_feishu_message,
)
from pdf_ocr_tool.topics.analyzers import (
    extract_main_themes,
    extract_core_insights,
    extract_stocks_and_sectors,
)
from pdf_ocr_tool.topics.extractor import extract_topic_by_keywords

__all__ = [
    'TOPIC_CONFIGS',
    'read_summary_content',
    'is_topic_document',
    'find_latest_summaries_dir',
    'send_feishu_message',
    'extract_main_themes',
    'extract_core_insights',
    'extract_stocks_and_sectors',
    'extract_topic_by_keywords',
]
