# PDF OCR 识别工具

一个功能强大的 PDF OCR 识别工具，专门为处理大量难识别的 PDF 文件而设计。项目提供自动化的 PDF 识别、内容提取、智能分析和报告生成功能。

## 功能特点

### 🎯 核心功能
- **智能混合解析**: 自动选择最优解析策略（可选文本 / LiteParse / Tesseract OCR）
- **质量评分**: 自动评估识别质量，确保输出可靠性
- **缓存机制**: 跨天共享缓存，避免重复处理相同文件
- **电子书识别**: 自动识别电子书，提取目录作为核心看点

### ⚡ 每日批量处理
- **固定目录**: `files/` 放入新PDF，`files_processed/` 存放已处理文件
- **日期隔离输出**: 自动按日期创建输出目录
- **文件自动移动**: 处理完成后自动归档源文件

### 📊 AI内容分析
- **智能总结**: 自动生成一句话总结和核心看点
- **结构化报告**: 生成每日报告和优化建议

## 快速开始

### 安装依赖

```bash
cd /Users/xingan/Documents/software/workspace/summary
pip install -r requirements.txt
```

### 基础使用

```bash
# 方式1：简化命令（使用默认固定目录）
python3 daily_500_pdf_processor.py

# 方式2：指定目录
python3 daily_500_pdf_processor.py "input_dir" "output_dir"

# 可选参数
python3 daily_500_pdf_processor.py --workers 8 --min-score 60 --force
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | 输入目录（包含PDF文件） | `files/` |
| `output_dir` | 输出目录 | `output/daily/YYYYMMDD/` |
| `--workers` | 并行工作进程数 | 8 |
| `--min-score` | 最低解析质量评分 | 60 |
| `--force` | 强制重新解析（忽略缓存） | false |
| `--no-ai` | 禁用AI内容分析 | false |

## 工作流程

```
1. 将PDF文件放入 files/ 目录
2. 运行 python3 daily_500_pdf_processor.py
3. 系统自动处理：
   - 解析PDF → 生成Markdown
   - AI分析 → 生成总结
   - 文件移动 → 移至 files_processed/
4. 结果保存在 output/daily/YYYYMMDD/
```

## 项目结构

```
summary/
├── files/              # A文件夹：放入新PDF
├── files_processed/    # B文件夹：已处理文件
├── output/
│   └── daily/          # 每日输出目录
│       ├── YYYYMMDD/   # 按日期隔离
│       │   ├── processed/    # 解析后的Markdown
│       │   ├── reports/      # 报告文件
│       │   └── summaries/    # 单文件总结
│       └── .pdf_parse_cache.json  # 跨天共享缓存
├── src/
│   └── pdf_ocr_tool/
│       ├── parsers/          # PDF解析层
│       ├── pipeline/         # 处理管道
│       ├── scripts/          # 命令入口
│       └── summarizers/      # 总结生成器
├── tests/             # 测试脚本
├── archive/           # 旧版本代码归档
└── README.md
```

## 系统要求

- **操作系统**: macOS, Linux
- **Python**: 3.8+
- **Tesseract OCR**: 需要单独安装
- **硬件**: 4核CPU, 8GB内存（推荐16GB）

## 许可证

MIT License