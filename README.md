# PDF 研报总结工具

一个完整的 PDF 研报总结流水线：从PDF解析 → LLM智能总结 → 主题提取汇总，特别为AI研究报告优化。

## 功能特点

### 🎯 核心功能
- **智能混合解析**: 自动选择最优解析策略（可选择文本 / Tesseract OCR）
- **质量评分**: 自动评估识别质量，确保输出可靠性
- **LLM智能总结**: 使用豆包模型生成一句话总结和核心看点
- **AI专题自动提取**: 从所有文档中筛选AI相关文档，生成专题报告

### ⚡ 每日批量处理
- **固定目录**: `files/` 放入新PDF，`files_processed/` 存放已处理文件
- **日期隔离输出**: 自动按日期创建输出目录，每天的数据不混淆
- **文件自动移动**: 处理完成后自动归档源文件

### 🤖 AI主题筛选（30个关键词）
| 类别 | 关键词 |
|------|--------|
| 大模型 | AI, 人工智能, 大模型, LLM, GPT, Agent, 智能体, AIGC, 生成式 |
| 算力硬件 | 算力, 光模块, 芯片, 半导体, GPU, PCB, 封装, HBM |
| 机器人 | 具身智能, 人形机器人, 机器人, 减速器, 电机 |
| 前沿科技 | 量子, 脑机接口, 6G, 增强现实, VR, 元宇宙, DeepSeek, 豆包, Claude, GEO |

## 快速开始

### 安装依赖

```bash
cd /Users/xingan/Documents/software/workspace/summary
pip install -r requirements.txt
```

### 配置豆包方舟密钥

```bash
# 方式1：创建 .env 文件
echo "ARK_API_KEY=你的方舟密钥" > .env

# 方式2：设置环境变量
export ARK_API_KEY="你的方舟密钥"
```

### 日常使用流程

```bash
# ======================================
# Step 1: 批量总结所有PDF（每天运行一次）
# ======================================
python3 daily_500_pdf_processor.py

# 输出目录： output/daily/YYYYMMDD/
#   ├── processed/    # PDF解析后的Markdown
#   └── summaries/    # 单文件总结（一句话总结 + 核心看点）


# ======================================
# Step 2: 提取AI专题报告（单独汇总）
# ======================================
python3 extract_topic_summary.py

# 输出目录： output/topic_summaries/AI/YYYYMMDD/
#   ├── READED_YYYYMMDD.md               # 文档索引
#   ├── AI_一句话汇总_YYYYMMDD.md         # 快速浏览版
#   ├── AI_核心论点汇总_YYYYMMDD.md       # 完整专题报告
#   └── summaries/                       # AI相关文档单独总结
```

### 常用参数

```bash
# daily_500_pdf_processor.py 参数
--workers 6        # 并行进程数，默认8
--min-score 40    # 最低解析质量评分，默认60
--force           # 强制重新解析（忽略缓存）
--no-ai          # 不生成总结（先解析后单独总结）

# extract_topic_summary.py 参数
-i, --input       # 指定输入summaries目录（自动找最新，一般不用）
-o, --output      # 自定义输出目录
```

## 📂 完整目录结构

```
summary/
├── files/                       # 放入新PDF
├── files_processed/             # 处理后自动归档
│
├── output/
│   ├── daily/                   # 每日批量处理结果
│   │   └── 20260720/
│   │       ├── processed/       # PDF解析Markdown (138个)
│   │       ├── summaries/       # 单文件总结（一句话 + 核心看点）
│   │       └── reports/         # 当日汇总报告
│   │
│   └── topic_summaries/         # 专题报告（按主题隔离）
│       └── AI/
│           ├── 20260720/
│           │   ├── READED_20260720.md
│           │   ├── AI_一句话汇总_20260720.md
│           │   ├── AI_核心论点汇总_20260720.md
│           │   └── summaries/        # 54个AI文档单独总结
│           ├── 20260721/        # 每天一个新目录，互不干扰
│           └── ...
│
├── src/
│   └── pdf_ocr_tool/
│       ├── parsers/          # PDF解析器
│       ├── pipeline/         # 处理管道
│       └── summarizers/      # 总结生成器（含LLM调用）
│
├── daily_500_pdf_processor.py    # 入口1：批量解析+总结
└── extract_topic_summary.py       # 入口2：提取AI专题汇总
```

## 🎯 使用场景

### 场景1：新到一批研报，全部总结

```bash
# 1. 把PDF放入 files/

# 2. 批量处理（解析+LLM总结）
python3 daily_500_pdf_processor.py --workers 6

# 3. 查看结果
# 所有文档总结在 output/daily/YYYYMMDD/summaries/
```

### 场景2：只要AI相关的报告

```bash
# 按场景1做完批量总结后，提取AI专题
python3 extract_topic_summary.py

# 查看AI专题汇总：
# output/topic_summaries/AI/YYYYMMDD/
#   - AI_一句话汇总_YYYYMMDD.md     # 快速浏览54份AI文档
#   - AI_核心论点汇总_YYYYMMDD.md     # 每份AI文档的核心看点
```

### 场景3：先解析，后续再总结

```bash
# Day 1：只解析，不调用LLM（省token）
python3 daily_500_pdf_processor.py --no-ai

# Day 2：生成总结（调用batch_summary.py或批量总结脚本）
# ...
```

## 📝 输出文件说明

| 文件名 | 内容 | 用途 |
|--------|------|------|
| `AI_一句话汇总_YYYYMMDD.md` | 所有AI文档的一句话总结 | 快速浏览，了解行业全貌 |
| `AI_核心论点汇总_YYYYMMDD.md` | 每文档一句话+5条核心看点 | 深度研读，提取投资机会 |
| `summaries/*.md` | 单个文档的完整总结 | 需要仔细研读某份文档时看 |
| `READED_YYYYMMDD.md` | 文档列表+关键词统计 | 索引，快速定位感兴趣文档 |

## 系统要求

- **操作系统**: macOS, Linux
- **Python**: 3.8+
- **Tesseract OCR**: 需要单独安装 (`brew install tesseract`)
- **豆包方舟**: 需要API密钥（使用LLM总结功能）
- **硬件**: 4核CPU, 8GB内存（推荐16GB）

## 许可证

MIT License
