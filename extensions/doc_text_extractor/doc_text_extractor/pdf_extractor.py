"""PDF 文本提取：可选文本(PyPDF2) → LiteParse(可选) → Tesseract OCR 混合解析。

带文本质量评分：优先返回质量达标的策略结果，全部不达标时返回最优努力结果
（success=False），方便调用方自行判断。
"""

import os
from dataclasses import dataclass, field

import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

from .image_ocr import preprocess_image
from .quality import score_text_quality

try:
    from liteparse import LiteParse
except Exception:
    LiteParse = None


@dataclass
class ExtractionResult:
    """PDF 提取结果。

    属性：
        text: 提取出的文本（best effort，可能为空）
        page_count: PDF 页数
        quality: score_text_quality 返回的质量详情 dict
        parser: 实际使用的解析策略（pypdf_selectable / liteparse_text /
                 tesseract_ocr / best_effort / none）
        success: 质量是否达到 min_score
        error: 失败原因（无）
    """

    text: str = ""
    page_count: int = 0
    quality: dict = field(default_factory=dict)
    parser: str = "none"
    success: bool = False
    error: str = None


def get_pdf_info(pdf_path):
    """读取 PDF 基础信息：页数、前几页可选文本样本。"""
    info = {
        "page_count": 0,
        "sample_text": "",
        "selectable_chars": 0,
        "has_selectable_text": False,
        "error": None,
    }
    try:
        reader = PdfReader(pdf_path)
        info["page_count"] = len(reader.pages)
        sample = []
        for page in reader.pages[: min(3, len(reader.pages))]:
            text = page.extract_text() or ""
            if text.strip():
                sample.append(text.strip())
        sample_text = "\n".join(sample)
        info["sample_text"] = sample_text
        info["selectable_chars"] = len(sample_text)
        info["has_selectable_text"] = score_text_quality(sample_text, pdf_path)["score"] >= 65
    except Exception as e:
        info["error"] = str(e)
    return info


def extract_selectable_text(pdf_path):
    """使用 PyPDF2 提取 PDF 的可选文本。返回 (text, page_count)。"""
    reader = PdfReader(pdf_path)
    pages = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"=== 第 {index} 页 ===\n{text.strip()}")
    return "\n\n".join(pages), len(reader.pages)


def extract_liteparse_text(pdf_path):
    """使用 LiteParse（非 OCR）提取 PDF 文本。LiteParse 不可用时返回 None。"""
    if LiteParse is None:
        return None, 0
    parser = LiteParse(ocr_enabled=False, quiet=True)
    result = parser.parse(pdf_path)
    return (result.text or ""), len(result.pages)


def extract_ocr_text(pdf_path, dpi=300, threshold=150, lang="chi_sim+eng", max_pages=None):
    """使用 Tesseract OCR 提取 PDF 全部页面文本。返回 (text, page_count)。"""
    images = convert_from_path(pdf_path, dpi=dpi, grayscale=True)
    if max_pages:
        images = images[:max_pages]
    pages = []
    for index, img in enumerate(images, 1):
        enhanced = preprocess_image(img, threshold=threshold)
        text = pytesseract.image_to_string(enhanced, lang=lang)
        if text.strip():
            pages.append(f"=== 第 {index} 页 ===\n{text.strip()}")
    return "\n\n".join(pages), len(images)


def _best_attempt(attempts):
    candidates = [a for a in attempts if "quality" in a]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item["quality"]["score"])


def extract_pdf_text(pdf_path, min_score=40, lang="chi_sim+eng",
                     use_liteparse=True, dpi_levels=((300, 150), (400, 150), (400, 180)),
                     max_pages=None, keywords=None):
    """从 PDF 提取文本（混合策略）。

    参数：
        pdf_path: PDF 文件路径
        min_score: 质量达标阈值（0-100，默认 40）
        lang: OCR 语言包（默认中英混合）
        use_liteparse: 是否尝试 LiteParse（未安装时自动跳过）
        dpi_levels: OCR 尝试的 (DPI, 二值化阈值) 档位序列
        max_pages: 仅对 OCR 路径生效的页数上限（可选文本路径不受限）
        keywords: 质量评分关键词表（None 用默认词表，[] 关闭关键词加分）

    返回：ExtractionResult

    示例：
        >>> from doc_text_extractor import extract_pdf_text
        >>> r = extract_pdf_text("研报.pdf")
        >>> print(r.text[:200], r.quality["score"], r.parser)
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    attempts = []
    pdf_info = get_pdf_info(pdf_path)
    page_count = pdf_info.get("page_count", 0)

    # 1) 可选文本：总是尝试 PyPDF2（速度最快），质量交给 min_score 把关
    try:
        text, pages = extract_selectable_text(pdf_path)
        quality = score_text_quality(text, pdf_path, keywords=keywords)
        attempts.append({"parser": "pypdf_selectable", "quality": quality})
        if quality["score"] >= min_score:
            return ExtractionResult(text=text, page_count=pages, quality=quality,
                                    parser="pypdf_selectable", success=True)
    except Exception as e:
        attempts.append({"parser": "pypdf_selectable", "error": str(e)})

    # 2) LiteParse（可选增强，处理复杂排版）
    if use_liteparse and LiteParse is not None:
        try:
            text, pages = extract_liteparse_text(pdf_path)
            quality = score_text_quality(text, pdf_path, keywords=keywords)
            attempts.append({"parser": "liteparse_text", "quality": quality})
            if quality["score"] >= min_score:
                return ExtractionResult(text=text, page_count=pages, quality=quality,
                                        parser="liteparse_text", success=True)
        except Exception as e:
            attempts.append({"parser": "liteparse_text", "error": str(e)})

    # 3) Tesseract OCR 多档参数
    for dpi, threshold in dpi_levels:
        try:
            text, pages = extract_ocr_text(pdf_path, dpi=dpi, threshold=threshold,
                                           lang=lang, max_pages=max_pages)
            quality = score_text_quality(text, pdf_path, keywords=keywords)
            parser = f"tesseract_{dpi}dpi_t{threshold}"
            attempts.append({"parser": parser, "quality": quality})
            if quality["score"] >= min_score:
                return ExtractionResult(text=text, page_count=pages, quality=quality,
                                        parser=parser, success=True)
        except Exception as e:
            attempts.append({"parser": f"tesseract_{dpi}dpi_t{threshold}", "error": str(e)})

    # 4) 最优努力：全部不达标时返回质量最高的结果
    best = _best_attempt(attempts)
    if best:
        quality = best["quality"]
        text = ""
        meta_pages = page_count
        try:
            text, meta_pages = extract_ocr_text(pdf_path, dpi=400, threshold=150,
                                                lang=lang, max_pages=max_pages)
        except Exception:
            pass
        return ExtractionResult(text=text, page_count=meta_pages, quality=quality,
                                parser=f"{best['parser']}_best_effort", success=False)

    return ExtractionResult(text="", page_count=page_count, quality={"score": 0},
                            parser="none", success=False,
                            error=f"所有解析策略均失败: {[a.get('error') for a in attempts]}")


def extract_pdf_to_markdown(pdf_path, output_dir=None, min_score=40, lang="chi_sim+eng",
                            use_liteparse=True, keywords=None):
    """提取 PDF 文本并渲染为 Markdown 字符串；指定 output_dir 时同时写入文件。

    参数：
        pdf_path: PDF 文件路径
        output_dir: 输出目录（可选，指定时写入 <文件名>.md）
        min_score / lang / use_liteparse / keywords: 同 extract_pdf_text

    返回：
        markdown 文本（str）；写入文件时返回 (markdown, 文件路径)
    """
    result = extract_pdf_text(pdf_path, min_score=min_score, lang=lang,
                              use_liteparse=use_liteparse, keywords=keywords)
    basename = os.path.splitext(os.path.basename(pdf_path))[0]
    status = "✓ 达标" if result.success else "⚠️ 未达标"
    q = result.quality
    lines = [
        f"# {basename}",
        "",
        "## 解析信息",
        f"- 解析方法: {result.parser}",
        f"- 质量评分: {q.get('score', 0)} ({status})",
        f"- 字符数: {q.get('total_len', len(result.text))}",
        f"- 页数: {result.page_count}",
        "",
        "## 内容",
        result.text.strip(),
    ]
    markdown = "\n".join(lines)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"{basename}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return markdown, out_path
    return markdown
