"""图片文字提取（OCR）：Tesseract 引擎 + 对比度增强/二值化预处理。"""

import io
import os

import PIL.ImageOps
import pytesseract
from PIL import Image


def preprocess_image(img, cutoff=2, threshold=150):
    """图像预处理：自动对比度增强 + 灰度二值化，提升 OCR 识别率。

    参数：
        img: PIL Image 对象
        cutoff: autocontrast 剪裁比例（默认 2）
        threshold: 二值化阈值（默认 150，像素 < 阈值 置黑）

    返回：处理后的 PIL Image
    """
    enhanced = PIL.ImageOps.autocontrast(img, cutoff=cutoff)
    return enhanced.convert("L").point(lambda x: 0 if x < threshold else 255, "1")


def ocr_image(image, lang="chi_sim+eng", preprocessing=True, cutoff=2, threshold=150):
    """对单张图片执行 OCR。

    参数：
        image: PIL Image 对象或图片文件路径
        lang: Tesseract 语言包（默认中英混合 'chi_sim+eng'）
        preprocessing: 是否做对比度增强+二值化预处理

    返回：识别出的文本字符串（可能为空）
    """
    if isinstance(image, (str, bytes, os.PathLike)):
        image = Image.open(os.fspath(image))
        image = image.convert("RGB")

    img = preprocess_image(image, cutoff, threshold) if preprocessing else image
    return pytesseract.image_to_string(img, lang=lang)


def extract_image_text(image_path, lang="chi_sim+eng", preprocessing=True, cutoff=2, threshold=150):
    """从图片文件中提取文字（便利入口）。

    参数：
        image_path: 图片文件路径（PNG/JPG/JPEG/WebP 等 PIL 支持的格式）
        lang: Tesseract 语言包（默认中英混合）

    返回：识别出的文本字符串（可能为空）

    示例：
        >>> from doc_text_extractor import extract_image_text
        >>> text = extract_image_text("截图.png")
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    return ocr_image(image_path, lang=lang, preprocessing=preprocessing, cutoff=cutoff, threshold=threshold)
