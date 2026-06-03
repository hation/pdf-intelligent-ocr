# 每日PDF处理系统使用指南

## 系统概述

这个系统专门为每日处理大量PDF文件而设计，提供自动化的PDF识别、内容提取、智能分析和报告生成功能。

## 系统架构

```
daily_500_pdf_processor.py (主入口)
├── pdf_processing_pipeline.py (处理管道)
└── ai_content_summarizer.py (AI内容分析)
    └── financial_summarizer.py (总结生成器)
```

## 快速开始

### 1. 安装依赖

```bash
cd /Users/xingan/Documents/software/workspace/summary
pip install -r requirements.txt
```

### 2. 基本使用方法

```bash
# 方式1：简化命令（使用默认固定目录）
python3 daily_500_pdf_processor.py

# 方式2：指定目录（保留灵活性）
python3 daily_500_pdf_processor.py /path/to/input /path/to/output

# 使用4个工作进程处理
python3 daily_500_pdf_processor.py --workers 4

# 禁用AI内容分析（快速模式）
python3 daily_500_pdf_processor.py --no-ai
```

### 3. 工作流程

```
1. 将PDF文件放入 files/ 目录
2. 运行 python3 daily_500_pdf_processor.py
3. 系统自动处理：
   - 解析PDF → 生成Markdown
   - AI分析 → 生成总结
   - 文件移动 → 移至 files_processed/
4. 结果保存在 output/daily/YYYYMMDD/
```

## 参数说明

| 参数 | 类型 | 描述 | 默认值 |
|------|------|------|--------|
| 输入目录 | 可选 | 包含PDF文件的目录路径 | `files/` |
| 输出目录 | 可选 | 结果保存目录 | `output/daily/YYYYMMDD/` |
| --workers | 可选 | 工作进程数 | 8 |
| --no-ai | 可选 | 禁用AI内容分析，提高处理速度 | false |
| --force | 可选 | 强制重新解析，忽略缓存 | false |
| --min-score | 可选 | 最低解析质量评分 | 60 |
| --help | 可选 | 显示帮助信息 | - |

## 目录结构

### 输入输出目录

```
summary/
├── files/              # A文件夹：放入新PDF
├── files_processed/    # B文件夹：已处理文件自动移动到此
└── output/
    └── daily/          # 每日输出目录
        ├── YYYYMMDD/   # 按日期隔离的输出
        │   ├── processed/    # 解析后的Markdown文件
        │   ├── reports/      # 分析报告
        │   └── summaries/    # 单文件总结
        └── .pdf_parse_cache.json  # 跨天共享缓存
```

## 输出文件结构

```
output/daily/YYYYMMDD/
├── processed/
│   ├── filename1_hybrid.md
│   ├── filename2_hybrid.md
│   └── processing_report_YYYYMMDD_HHMMSS.json
├── reports/
│   ├── summary_list_YYYYMMDD.md        # 一句话总结清单
│   ├── daily_summary_YYYYMMDD.md        # 每日报告
│   └── optimization_report_YYYYMMDD.md  # 优化报告
└── summaries/
    ├── filename1_summary.md
    ├── filename2_summary.md
    └── ...
```

## 报告说明

### 1. 一句话总结清单 (`summary_list_YYYYMMDD.md`)

包含所有文件的一句话总结，方便快速浏览。

### 2. 每日报告 (`daily_summary_YYYYMMDD.md`)

包含：
- 处理的文件总数
- 成功处理的文件数
- 失败处理的文件数
- 总处理时间
- 平均处理速度

### 3. 优化报告 (`optimization_report_YYYYMMDD.md`)

包含性能分析和优化建议。

### 4. 单文件总结 (`filename_summary.md`)

包含：
- 一句话总结
- 核心看点

## 系统特点

### 1. 智能策略选择

系统会根据PDF文件类型自动选择最佳处理策略：

- 包含可选文本的文件：直接提取文本
- 需要OCR的文件：使用LiteParse或Tesseract OCR
- 大文件：智能跳过全量OCR

### 2. 电子书识别

自动识别电子书类型：
- 提取目录作为核心看点
- 一句话总结基于目录生成

### 3. 文件自动移动

处理完成后自动将源文件从 `files/` 移动到 `files_processed/`。

### 4. 跨天缓存共享

缓存文件放在 `output/daily/.pdf_parse_cache.json`，避免重复处理相同文件。

### 5. 多进程处理

支持配置工作进程数，提高处理效率。

### 6. 错误处理

系统具有完善的错误处理机制：
- 识别处理失败的文件并记录详细信息
- 自动跳过损坏的PDF文件

## 常见问题

### 1. 系统找不到文件

确保 `files/` 目录包含PDF文件。

### 2. 处理速度慢

可以尝试：
- 增加工作进程数（使用--workers参数）
- 禁用AI内容分析（使用--no-ai参数）
- 确保系统有足够的内存和CPU资源

### 3. 识别质量差

对于识别质量差的文件，可以尝试：
- 使用--force参数强制重新解析
- 降低--min-score阈值

### 4. 文件没有自动移动

检查 `files_processed/` 目录是否存在，确保有写入权限。

## 高级使用

### 1. 自定义工作进程数

```bash
# 使用8个工作进程（默认）
python3 daily_500_pdf_processor.py --workers 8

# 使用12个工作进程
python3 daily_500_pdf_processor.py --workers 12
```

### 2. 强制重新解析

```bash
python3 daily_500_pdf_processor.py --force
```

### 3. 定期自动化运行

可以使用cron定时任务定期运行处理系统：

```bash
# 每天上午8点运行
0 8 * * * cd /Users/xingan/Documents/software/workspace/summary && python3 daily_500_pdf_processor.py
```

## 系统要求

- Python 3.8+
- macOS或Linux系统
- 至少8GB内存
- 至少4个CPU核心
- Tesseract OCR引擎

## 总结

这个PDF处理系统提供了一个完整的解决方案，帮助你每天高效地处理大量PDF文件。通过智能策略选择、多进程处理和完善的错误处理机制，确保了处理过程的高效和稳定。

---

**作者：** TraeAI 自动生成
**创建时间：** 2026年6月