# doc-text-extractor

图片 / PDF 文本提取库（summary 项目内对外扩展模块，位于 `extensions/`，与 `src/` 内部源码隔离）。核心基于 PyPDF2 + Tesseract OCR（轻量、易安装），LiteParse 作为可选增强（处理复杂排版）。

## 安装

```bash
pip install -e /Users/xingan/Documents/software/workspace/summary/extensions/doc_text_extractor

# 可选：启用 LiteParse 增强（Rust 引擎，体积大）
pip install -e "/Users/xingan/Documents/software/workspace/summary/extensions/doc_text_extractor[liteparse]"
```

系统依赖（需单独安装）：

```bash
brew install tesseract tesseract-lang  # OCR 引擎（含中文语言包 chi_sim）
brew install poppler                    # pdf2image 依赖
```

## 使用

### Python API

```python
from doc_text_extractor import extract_image_text, extract_pdf_text, extract_pdf_to_markdown

# 1) 图片 → 文字
text = extract_image_text("截图.png", lang="chi_sim+eng")

# 2) PDF → 文字（自动选择策略：可选文本 → LiteParse → OCR，含质量评分）
r = extract_pdf_text("研报.pdf")
print(r.text)            # 提取的全文
print(r.quality["score"])  # 质量分 0-100
print(r.parser)          # 实际策略：pypdf_selectable / liteparse_text / tesseract_*_dpi_t* / *_best_effort
print(r.success)         # 是否达到 min_score

# 3) PDF → Markdown（返回字符串，或指定目录写入 <文件名>.md）
md = extract_pdf_to_markdown("研报.pdf", output_dir="./out")
```

质量分可调：`extract_pdf_text("x.pdf", min_score=60)`（默认 40）。
中文场景需安装 tesseract 中文语言包：`brew install tesseract-lang`。

### 命令行

```bash
doc-text-extractor image 截图.png
doc-text-extractor pdf   研报.pdf
doc-text-extractor pdf   研报.pdf -o ./out
```

未指定 `-o` 时，结果统一输出到 **`<项目根>/extensions/output/`**（image → `<文件名>.txt`，pdf → `<文件名>.md`），便于集中管理扩展工具产物。

## API 一览

| 函数 | 说明 |
|------|------|
| `extract_image_text(path, lang="chi_sim+eng")` | 图片文件 → 文本（OCR） |
| `ocr_image(image, lang=..., preprocessing=True)` | PIL 图片对象 → 文本 |
| `extract_pdf_text(path, min_score=40, ...)` | PDF → `ExtractionResult`（text/quality/parser/success） |
| `extract_pdf_to_markdown(path, output_dir=None, ...)` | PDF → Markdown 字符串（可写文件） |
| `extract_selectable_text(path)` | 仅提取 PDF 可选文本 |
| `score_text_quality(text, path=None, keywords=None)` | 文本质量评分 0-100 |

## 解析策略（PDF）

1. **pypdf_selectable** — 直接提取 PDF 可选文本（最快）
2. **liteparse_text** — LiteParse 非 OCR（可选，未安装自动跳过）
3. **tesseract_ocr** — 多档参数 OCR（300/400 DPI × 不同二值化阈值），适合扫描件
4. **best_effort** — 全部未达标时返回质量最高的结果（`success=False`）

所有策略输出均经质量评分（长度 / 中文占比 / 乱码噪声 / 关键词命中）过滤。

## 测试

```bash
pip install -e "/Users/xingan/Documents/software/workspace/summary/extensions/doc_text_extractor[dev]"
pytest /Users/xingan/Documents/software/workspace/summary/extensions/doc_text_extractor/tests
```
