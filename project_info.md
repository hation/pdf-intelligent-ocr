# 项目信息 - PDF OCR 处理工具

## 项目概述
这是一个功能强大的 PDF OCR 识别工具，专门为每日处理大量 PDF 文件而设计。提供自动化的 PDF 识别、内容提取、智能分析和报告生成功能。

## 核心功能

### 1. 智能混合解析
- 自动选择最优解析策略（可选文本 / LiteParse / Tesseract OCR）
- 质量评分机制，确保输出可靠性
- 缓存机制，避免重复处理相同文件

### 2. 电子书识别
- 自动识别电子书类型
- 提取目录作为核心看点
- 一句话总结基于目录生成

### 3. 每日批量处理
- **固定目录**: `files/` 放入新PDF，`files_processed/` 存放已处理文件
- **日期隔离输出**: 自动按日期创建输出目录
- **文件自动移动**: 处理完成后自动归档源文件
- **跨天缓存共享**: 缓存文件跨日期共享

### 4. AI内容分析
- 智能总结生成
- 结构化报告输出
- 核心看点提取

## 技术特点

### 1. 智能识别机制
- 使用 PyPDF2 快速检查 PDF 是否包含可选文本
- 自动选择最佳解析策略
- 电子书自动识别

### 2. 图像预处理
- 对比度增强
- 二值化处理
- 灰度转换

### 3. 多进程处理
- 支持并发处理，提升效率
- 资源消耗可控

### 4. 完整的工作流
- PDF解析 → Markdown生成 → AI分析 → 文件归档

## 使用场景

### 推荐使用方案

| 场景 | 方案选择 | 说明 |
|------|----------|------|
| 每日批量处理 | 默认模式 | 自动处理 files/ 目录下的PDF |
| 单文件测试 | 指定文件 | 使用 hybrid_pdf_parser.py |
| 快速验证 | --no-ai 参数 | 跳过AI分析，仅解析 |

### 支持的文件类型
- 扫描件 PDF
- 低分辨率图像 PDF
- 文字密集型 PDF
- 复杂布局 PDF
- 双语文档（中文+英文）
- 电子书 PDF

## 项目结构

```
summary/
├── files/                      # A文件夹：放入新PDF
├── files_processed/            # B文件夹：已处理文件自动移动到此
├── output/
│   └── daily/                  # 每日输出目录
│       ├── YYYYMMDD/           # 按日期隔离
│       │   ├── processed/      # 解析后的Markdown文件
│       │   ├── reports/        # 报告文件
│       │   └── summaries/      # 单文件总结
│       └── .pdf_parse_cache.json  # 跨天共享缓存
├── src/
│   └── pdf_ocr_tool/           # 源代码目录
│       ├── parsers/            # PDF解析层
│       │   ├── hybrid_pdf_parser.py    # 混合解析器
│       │   ├── direct_tesseract_ocr.py # Tesseract OCR
│       │   └── parse_with_liteparse_ocr.py # LiteParse OCR
│       ├── pipeline/           # 处理管道
│       │   └── pdf_processing_pipeline.py
│       ├── scripts/            # 命令入口实现
│       │   └── daily_500_pdf_processor.py
│       └── summarizers/        # 总结生成器
│           └── financial_summarizer.py
├── tests/                      # 测试脚本
├── archive/                    # 旧版本代码归档
├── daily_500_pdf_processor.py  # 主入口脚本
├── ai_content_summarizer.py    # AI内容分析入口
├── hybrid_pdf_parser.py        # 单文件解析入口
├── pdf_processing_pipeline.py  # 处理管道入口
├── README.md                   # 项目说明文档
├── USAGE_GUIDE.md              # 使用指南
├── requirements.txt            # Python 依赖包
└── LICENSE                     # 许可证信息
```

## 目录结构说明

| 目录 | 用途 | 说明 |
|------|------|------|
| `files/` | 输入目录 | 每日放入新PDF文件 |
| `files_processed/` | 归档目录 | 处理完成后自动移动到此 |
| `output/daily/YYYYMMDD/` | 输出目录 | 按日期隔离的每日输出 |
| `src/pdf_ocr_tool/` | 源代码 | 核心功能实现 |
| `tests/` | 测试脚本 | 测试代码 |
| `archive/` | 归档目录 | 旧版本代码 |

## 核心文件说明

| 文件 | 用途 | 说明 |
|------|------|------|
| `daily_500_pdf_processor.py` | 主入口 | 每日批量处理命令 |
| `ai_content_summarizer.py` | AI分析 | 内容总结生成 |
| `hybrid_pdf_parser.py` | 解析器 | 单文件混合解析 |
| `pdf_processing_pipeline.py` | 管道 | 处理流程编排 |

## 使用方法

```bash
# 简化命令（使用默认固定目录）
python3 daily_500_pdf_processor.py

# 指定目录
python3 daily_500_pdf_processor.py "input_dir" "output_dir"

# 可选参数
python3 daily_500_pdf_processor.py --workers 8 --min-score 60 --force
```

## 项目名称建议
- **`pdf-ocr-tool`** - 简洁且明确
- **`pdf-intelligent-ocr`** - 突出智能识别功能
- **`daily-pdf-processor`** - 强调每日批量处理

## GitHub 仓库描述建议
> 一个功能强大的 PDF OCR 识别工具，专门为每日处理大量 PDF 文件而设计。提供智能混合解析、电子书识别、自动文件归档等功能，支持固定目录结构和跨天缓存共享。包含完整的图像预处理、多进程处理和AI内容分析功能。