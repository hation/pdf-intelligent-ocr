"""
doc_text_extractor — 图片/PDF 文本提取库。

核心 API：
- extract_image_text(image_path, lang="chi_sim+eng") -> str
- extract_pdf_text(pdf_path, min_score=40) -> ExtractionResult
- extract_pdf_to_markdown(pdf_path, output_dir=None) -> str

解析策略（PDF）：可选文本(PyPDF2) → LiteParse(可选) → Tesseract OCR(多档参数)，
并带文本质量评分，自动跳过乱码结果。
"""

from .quality import score_text_quality
from .image_ocr import extract_image_text, ocr_image, preprocess_image
from .pdf_extractor import (
    ExtractionResult,
    extract_pdf_text,
    extract_pdf_to_markdown,
    extract_selectable_text,
)

__version__ = "0.1.0"

__all__ = [
    "ExtractionResult",
    "extract_image_text",
    "extract_pdf_text",
    "extract_pdf_to_markdown",
    "extract_selectable_text",
    "ocr_image",
    "preprocess_image",
    "score_text_quality",
]
