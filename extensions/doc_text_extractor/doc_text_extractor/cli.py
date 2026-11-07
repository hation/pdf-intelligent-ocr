"""命令行入口：doc-text-extractor image <path> | pdf <path> [-o DIR]"""

import argparse
import os
import sys

from .image_ocr import extract_image_text
from .pdf_extractor import extract_pdf_to_markdown


def _default_output_dir():
    """扩展工具统一输出目录：<项目根>/extensions/output/（未指定 -o 时使用）"""
    here = os.path.dirname(os.path.abspath(__file__))  # .../doc_text_extractor/doc_text_extractor
    extensions_dir = os.path.dirname(os.path.dirname(here))  # .../extensions
    return os.path.join(extensions_dir, "output")


def _run_image(args):
    text = extract_image_text(args.path, lang=args.lang)
    if not text.strip():
        print("未识别到任何文本")
        return 1
    if not args.output:
        args.output = os.path.join(_default_output_dir(),
                                   f"{os.path.splitext(os.path.basename(args.path))[0]}.txt")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"已保存到: {args.output}")
    return 0


def _run_pdf(args):
    if not args.output:
        args.output = _default_output_dir()
    markdown, out_path = extract_pdf_to_markdown(args.path, output_dir=args.output,
                                                 min_score=args.min_score, lang=args.lang)
    print(f"解析方法: {out_path.split('/')[-1]}")
    print(f"已保存到: {out_path}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="doc-text-extractor",
        description="图片/PDF 文本提取：Tesseract OCR + 可选文本混合解析",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_img = sub.add_parser("image", help="提取图片中的文字（OCR）")
    p_img.add_argument("path", help="图片文件路径")
    p_img.add_argument("--lang", default="chi_sim+eng", help="Tesseract 语言包（默认 chi_sim+eng）")
    p_img.add_argument("-o", "--output", help="将文本写入该文件（默认打印到终端）")
    p_img.set_defaults(func=_run_image)

    p_pdf = sub.add_parser("pdf", help="提取 PDF 文字（可选文本 + OCR 混合）")
    p_pdf.add_argument("path", help="PDF 文件路径")
    p_pdf.add_argument("--min-score", type=int, default=40, help="质量达标阈值（默认 40）")
    p_pdf.add_argument("--lang", default="chi_sim+eng", help="Tesseract 语言包（默认 chi_sim+eng）")
    p_pdf.add_argument("-o", "--output", help="输出目录，保存 <文件名>.md（默认打印 Markdown）")
    p_pdf.set_defaults(func=_run_pdf)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
