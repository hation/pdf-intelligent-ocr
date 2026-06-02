#!/usr/bin/env python3
"""
混合PDF解析器：按缓存、可选文本、LiteParse非OCR、Tesseract OCR与质量评分协同解析PDF。
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime

import PIL.ImageOps
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader

try:
    from liteparse import LiteParse
except Exception:
    LiteParse = None


DOMAIN_KEYWORDS = [
    "公司", "产品", "客户", "订单", "产能", "认证", "供应链", "需求", "风险", "调研",
    "机构", "收入", "利润", "同比", "增长", "服务器", "华为", "长鑫", "长存", "算力",
    "电子", "材料", "行业", "市场", "业务", "公告", "分析师", "投资", "项目", "技术",
    "HVLP", "AIDC", "AI", "PCB", "铜箔", "半导体", "商业航天"
]

NOISE_PATTERN = re.compile(r"[A-Za-z]{1,4}(?:\s+[A-Za-z]{1,4}){3,}")
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
ALNUM_PATTERN = re.compile(r"[A-Za-z0-9\u4e00-\u9fff]")


def safe_basename(pdf_path):
    return os.path.splitext(os.path.basename(pdf_path))[0]


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def compute_file_hash(path, chunk_size=1024 * 1024):
    digest = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def cache_path(output_dir):
    return os.path.join(output_dir, ".pdf_parse_cache.json")


def load_cache(output_dir):
    path = cache_path(output_dir)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_cache(output_dir, cache):
    path = cache_path(output_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def extract_content_from_markdown(markdown):
    marker = "## 内容"
    if marker in markdown:
        return markdown.split(marker, 1)[1].strip()
    return markdown.strip()


def get_pdf_info(pdf_path):
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


def score_text_quality(text, pdf_path=None):
    stripped = text.strip()
    total_len = len(stripped)
    chinese_count = len(CHINESE_PATTERN.findall(stripped))
    alnum_count = len(ALNUM_PATTERN.findall(stripped))
    chinese_ratio = chinese_count / total_len if total_len else 0
    alnum_ratio = alnum_count / total_len if total_len else 0
    noise_matches = NOISE_PATTERN.findall(stripped)
    noise_len = sum(len(match) for match in noise_matches)
    noise_ratio = noise_len / total_len if total_len else 0
    keyword_hits = sum(1 for word in DOMAIN_KEYWORDS if word.lower() in stripped.lower())
    line_count = len([line for line in stripped.splitlines() if line.strip()])
    avg_line_len = total_len / line_count if line_count else 0
    title_hits = 0

    if pdf_path:
        title_tokens = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,}", safe_basename(pdf_path))
        important_tokens = [token for token in title_tokens if len(token) >= 2]
        title_hits = sum(1 for token in important_tokens[:12] if token.lower() in stripped.lower())

    score = 0

    if total_len >= 1500:
        score += 25
    elif total_len >= 800:
        score += 20
    elif total_len >= 400:
        score += 12
    elif total_len >= 150:
        score += 5

    if chinese_ratio >= 0.45:
        score += 25
    elif chinese_ratio >= 0.3:
        score += 18
    elif chinese_ratio >= 0.18:
        score += 10
    elif chinese_ratio >= 0.08:
        score += 4

    if keyword_hits >= 8:
        score += 25
    elif keyword_hits >= 5:
        score += 18
    elif keyword_hits >= 3:
        score += 10
    elif keyword_hits >= 1:
        score += 4

    if title_hits >= 4:
        score += 15
    elif title_hits >= 2:
        score += 10
    elif title_hits >= 1:
        score += 5

    if alnum_ratio >= 0.55:
        score += 5

    if 12 <= avg_line_len <= 120:
        score += 5

    if noise_ratio > 0.3:
        score -= 25
    elif noise_ratio > 0.18:
        score -= 15
    elif noise_ratio > 0.1:
        score -= 8

    if total_len < 120:
        score -= 20

    score = max(0, min(100, score))

    return {
        "score": score,
        "total_len": total_len,
        "chinese_ratio": round(chinese_ratio, 4),
        "alnum_ratio": round(alnum_ratio, 4),
        "noise_ratio": round(noise_ratio, 4),
        "keyword_hits": keyword_hits,
        "title_hits": title_hits,
        "line_count": line_count,
        "avg_line_len": round(avg_line_len, 2),
    }


def build_markdown(pdf_path, parser_name, text, quality, meta=None):
    meta = meta or {}
    lines = [
        f"# {safe_basename(pdf_path)}",
        "",
        "## 文件统计",
        f"解析方法: {parser_name}",
        f"质量评分: {quality['score']}",
        f"字符数: {quality['total_len']}",
        f"中文比例: {quality['chinese_ratio']}",
        f"关键词命中: {quality['keyword_hits']}",
        f"标题命中: {quality['title_hits']}",
    ]
    for key, value in meta.items():
        lines.append(f"{key}: {value}")
    lines.extend(["", "## 内容", text.strip()])
    return "\n".join(lines)


def parse_selectable_text(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for index, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"=== 第 {index} 页 ===\n{text.strip()}")
    return "\n\n".join(pages), len(reader.pages)


def parse_liteparse_text(pdf_path):
    if LiteParse is None:
        return None, {"error": "liteparse不可用"}
    parser = LiteParse(ocr_enabled=False, quiet=True)
    result = parser.parse(pdf_path)
    return result.text or "", {"页数": len(result.pages)}


def preprocess_image(img, cutoff, threshold):
    enhanced = PIL.ImageOps.autocontrast(img, cutoff=cutoff)
    return enhanced.convert("L").point(lambda x: 0 if x < threshold else 255, "1")


def parse_tesseract(pdf_path, dpi=300, cutoff=2, threshold=150, max_pages=None):
    images = convert_from_path(pdf_path, dpi=dpi, grayscale=True)
    if max_pages:
        images = images[:max_pages]
    pages = []
    for index, img in enumerate(images, 1):
        enhanced = preprocess_image(img, cutoff, threshold)
        text = pytesseract.image_to_string(enhanced, lang="chi_sim+eng")
        if text.strip():
            pages.append(f"=== 第 {index} 页 ===\n{text.strip()}")
    return "\n\n".join(pages), {"页数": len(images), "DPI": dpi, "阈值": threshold}


def write_result(output_dir, pdf_path, parser_name, text, quality, meta=None):
    ensure_dir(output_dir)
    md_path = os.path.join(output_dir, f"{safe_basename(pdf_path)}_hybrid.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_markdown(pdf_path, parser_name, text, quality, meta))
    return md_path


def validate_cached_result(entry, pdf_hash):
    if not entry:
        return False
    md_path = entry.get("md_path")
    return entry.get("pdf_hash") == pdf_hash and md_path and os.path.exists(md_path) and entry.get("quality_score", 0) >= 60


def parse_pdf_to_markdown(pdf_path, output_dir, min_score=60, force=False):
    ensure_dir(output_dir)
    pdf_hash = compute_file_hash(pdf_path)
    cache = load_cache(output_dir)
    cache_key = os.path.abspath(pdf_path)
    cached = cache.get(cache_key)

    if not force and validate_cached_result(cached, pdf_hash):
        return {
            "success": True,
            "md_path": cached["md_path"],
            "parser": cached.get("parser", "cached"),
            "quality_score": cached.get("quality_score", 0),
            "from_cache": True,
            "quality": cached.get("quality", {}),
        }

    started_at = time.time()
    attempts = []
    pdf_info = get_pdf_info(pdf_path)
    page_count = pdf_info.get("page_count", 0)
    large_pdf = page_count > 20

    if pdf_info.get("has_selectable_text"):
        try:
            text, pages = parse_selectable_text(pdf_path)
            quality = score_text_quality(text, pdf_path)
            attempts.append({"parser": "pypdf_selectable", "quality": quality})
            if quality["score"] >= min_score:
                md_path = write_result(output_dir, pdf_path, "PyPDF2可选文本", text, quality, {"页数": pages})
                result = save_parse_cache(cache, cache_key, pdf_hash, md_path, "pypdf_selectable", quality, started_at, attempts, output_dir)
                return result
        except Exception as e:
            attempts.append({"parser": "pypdf_selectable", "error": str(e)})

    if LiteParse is not None:
        try:
            text, meta = parse_liteparse_text(pdf_path)
            quality = score_text_quality(text, pdf_path)
            attempts.append({"parser": "liteparse_text", "quality": quality})
            if quality["score"] >= min_score:
                md_path = write_result(output_dir, pdf_path, "LiteParse非OCR", text, quality, meta)
                result = save_parse_cache(cache, cache_key, pdf_hash, md_path, "liteparse_text", quality, started_at, attempts, output_dir)
                return result
        except Exception as e:
            attempts.append({"parser": "liteparse_text", "error": str(e)})

    if large_pdf and pdf_info.get("selectable_chars", 0) > 500:
        best_attempt = select_best_attempt(attempts)
        if best_attempt:
            parser_name = best_attempt["parser"]
            quality = best_attempt["quality"]
            text = pdf_info.get("sample_text", "")
            md_path = write_result(output_dir, pdf_path, f"{parser_name}_low_quality", text, quality, {"页数": page_count, "状态": "大文件跳过全量OCR"})
            result = save_parse_cache(cache, cache_key, pdf_hash, md_path, parser_name, quality, started_at, attempts, output_dir, success=False)
            return result

    for dpi, threshold in [(300, 150), (400, 150), (400, 180)]:
        try:
            text, meta = parse_tesseract(pdf_path, dpi=dpi, threshold=threshold)
            quality = score_text_quality(text, pdf_path)
            parser_name = f"tesseract_{dpi}dpi_t{threshold}"
            attempts.append({"parser": parser_name, "quality": quality})
            if quality["score"] >= min_score:
                md_path = write_result(output_dir, pdf_path, f"Tesseract OCR {dpi}DPI", text, quality, meta)
                result = save_parse_cache(cache, cache_key, pdf_hash, md_path, parser_name, quality, started_at, attempts, output_dir)
                return result
        except Exception as e:
            attempts.append({"parser": f"tesseract_{dpi}dpi_t{threshold}", "error": str(e)})

    best = select_best_attempt(attempts)
    if best:
        parser_name = best["parser"]
        quality = best["quality"]
        text = ""
        try:
            text, meta = parse_tesseract(pdf_path, dpi=400, threshold=150)
        except Exception:
            meta = {}
        md_path = write_result(output_dir, pdf_path, f"{parser_name}_best_effort", text, quality, {**meta, "状态": "质量未达标"})
        return save_parse_cache(cache, cache_key, pdf_hash, md_path, parser_name, quality, started_at, attempts, output_dir, success=False)

    return {
        "success": False,
        "md_path": None,
        "parser": "none",
        "quality_score": 0,
        "from_cache": False,
        "attempts": attempts,
    }


def select_best_attempt(attempts):
    candidates = [attempt for attempt in attempts if "quality" in attempt]
    if not candidates:
        return None
    return max(candidates, key=lambda item: item["quality"]["score"])


def save_parse_cache(cache, cache_key, pdf_hash, md_path, parser, quality, started_at, attempts, output_dir, success=True):
    entry = {
        "pdf_hash": pdf_hash,
        "md_path": md_path,
        "parser": parser,
        "quality_score": quality["score"],
        "quality": quality,
        "success": success,
        "attempts": attempts,
        "updated_at": datetime.now().isoformat(),
        "elapsed_seconds": round(time.time() - started_at, 2),
    }
    cache[cache_key] = entry
    save_cache(output_dir, cache)
    return {
        "success": success,
        "md_path": md_path,
        "parser": parser,
        "quality_score": quality["score"],
        "quality": quality,
        "from_cache": False,
        "attempts": attempts,
        "elapsed_seconds": entry["elapsed_seconds"],
    }


def main():
    parser = argparse.ArgumentParser(description="混合PDF解析器")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("output_dir", help="Markdown输出目录")
    parser.add_argument("--min-score", type=int, default=60, help="最低质量评分")
    parser.add_argument("--force", action="store_true", help="忽略缓存强制重跑")
    args = parser.parse_args()

    result = parse_pdf_to_markdown(args.pdf_path, args.output_dir, args.min_score, args.force)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
