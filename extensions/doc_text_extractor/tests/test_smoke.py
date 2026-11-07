"""doc-text-extractor 冒烟测试：质量评分 + 图片 OCR（自绘文本图）+ PDF 提取。"""

import os
from PIL import Image, ImageDraw, ImageFont

from doc_text_extractor import (
    extract_image_text,
    extract_pdf_text,
    extract_pdf_to_markdown,
    score_text_quality,
)

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def _make_text_image(path):
    img = Image.new("RGB", (800, 160), "white")
    draw = ImageDraw.Draw(img)
    font = None
    for fp in ("/System/Library/Fonts/PingFang.ttc",
               "/System/Library/Fonts/Helvetica.ttc",
               "/Library/Fonts/Arial.ttf"):
        if os.path.exists(fp):
            try:
                font = ImageFont.truetype(fp, 48)
                break
            except Exception:
                continue
    if font is None:
        font = ImageFont.load_default()
    draw.text((20, 20), "Hello World 123", fill="black", font=font)
    img.save(path)


def test_score_text_quality():
    q = score_text_quality("这是一段正常的文档内容，包含公司、市场与行业数据，长度足够长。" * 10)
    assert q["score"] >= 40
    q2 = score_text_quality("HHS ie ae ere CBE 个 HE So Th Kk Mm")
    assert q2["score"] < 40


def test_image_ocr(tmp_path):
    img_path = tmp_path / "test.png"
    _make_text_image(str(img_path))
    text = extract_image_text(str(img_path), lang="eng")
    assert "Hello" in text or "hello" in text


def test_pdf_selectable():
    pdf_path = os.path.join(TESTS_DIR, "sample_text.pdf")
    if not os.path.exists(pdf_path):
        return  # 无样本文件时跳过
    r = extract_pdf_text(pdf_path)
    assert r.success
    assert r.parser == "pypdf_selectable"
    assert len(r.text) > 50


def test_pdf_to_markdown(tmp_path):
    pdf_path = os.path.join(TESTS_DIR, "sample_text.pdf")
    if not os.path.exists(pdf_path):
        return
    md, out_path = extract_pdf_to_markdown(pdf_path, output_dir=str(tmp_path))
    assert "## 内容" in md
    assert os.path.exists(out_path)
