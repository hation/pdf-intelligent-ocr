# 项目规则 - PDF 识别方案

## 识别困难PDF的处理方案

### 问题特征

如果PDF文件具有以下特征，则可能属于难以识别的类型：

* 文件大小较小但内容复杂

* 使用常规OCR方法识别到的内容极少或只有水印

* 文件可能是扫描件或图像形式

* 文本与背景对比度低

### 推荐处理流程

1. 首先尝试使用PyPDF2等基本工具检查文件是否包含可选择的文本：

```python
from PyPDF2 import PdfReader

def has_selectable_text(filename):
    reader = PdfReader(filename)
    for page_num, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text and len(text.strip()) > 100:
            print(f"第{page_num}页包含可选文本")
            return True
    print("该文件可能是扫描件或无可选文本的PDF")
    return False
```

1. 如果确认是难以识别的PDF，则立即使用我们的Tesseract OCR方案：

```bash
cd /Users/xingan/Documents/software/workspace/summary
./direct_tesseract_ocr.py <PDF文件路径>
```

1. 或者直接使用Python代码：

```python
from direct_tesseract_ocr import tesseract_ocr_on_pdf
tesseract_ocr_on_pdf("/path/to/your/difficult.pdf")
```

### 方案优势

* 直接使用Tesseract OCR引擎，识别率更高

* 包含图像预处理（对比度增强和二值化）

* 支持中文+英文双语言识别

* 可以处理各种复杂布局和低对比度的PDF文件

### 参考文件

详细方案文档: `/Users/xingan/Documents/software/workspace/summary/PDF_OCR_SOLUTION.md`
快速访问配置: `/Users/xingan/Documents/software/workspace/summary/pdf_ocr_recipe.txt`
主执行脚本: `/Users/xingan/Documents/software/workspace/summary/direct_tesseract_ocr.py`

### 成功案例

已成功处理文件: 【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf
识别结果: /Users/xingan/Documents/software/workspace/summary/outputs\_liteparse\_ocr/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.md

***

## 项目工作流程指南

### 第一步：先了解项目现状（必须做）

在开始写代码之前，先完成以下检查：

1. **先看 README.md**

   * 搞清楚这项目有什么功能

   * 看已有脚本的用途说明

2. **查看项目目录结构**

   * 看根目录有哪些 `.py` 脚本

   * 每个脚本的作用是什么

   * 现有输出目录结构是什么样的

### 第二步：使用项目已有脚本（严禁自己写新的！）

项目已有三个核心脚本：

1. **`daily_500_pdf_processor.py`**

   * 用途：完整处理新PDF

   * 流程：`files/` 目录 → PDF解析 + Office转换（docx/doc/xlsx/xls/pptx） → 生成Markdown → 生成AI总结 → 文件移动到 `files_processed/`

   * 输出位置：`output/daily/YYYYMMDDHH/`（包含 `processed/` + `summaries/` + `reports/`）

2. **`batch_summarize.py`**

   * 用途：批量为已解析的PDF生成总结

   * 注意：可能需要修改硬编码的日期目录

   * 输出：`summaries/` + `reports/`

3. **`extract_topic_summary.py`**

   * 用途：从已有总结中提取专题报告（如AI专题）

   * 输入：`output/daily/YYYYMMDDHH/summaries/` + `output/daily/YYYYMMDDHH/reports/`

   * 输出：`output/topic_summaries/<topic>/`

### 第三步：只改必要的配置，不要写新脚本

如果需要处理新日期的文件：

* 只修改脚本中硬编码的日期（如从 `20260714` 改为 `20260719`）

* 不要新建 `generate_xxx.py` 脚本！

* 不要复制 `src/` 里的模块到根目录！

***

## 昨天（2026-07-19）犯的错，下次绝对不要犯

### ❶ 自己写一堆重复脚本

* 错误做法：写了 `generate_report.py`、`generate_real_summary.py`、`ai_content_summarizer.py`...

* 避免做法：项目已经有完整功能，只需要用，不需要写新的

### ❷ 随便加 --no-ai 跳过关键步骤

* 错误做法：第一次运行时加了 `--no-ai`，导致没有 `summaries/`，后来还得单独补

* 避免做法：先确认需求，不要随便加参数

### ❸ 没看 README 就开始写代码

* 错误做法：直到被提醒才看 README

* 避免做法：每次接手任务，先看 README 和项目目录结构，了解已有功能

### ❹ 搞反需求

* 错误做法：以为只处理AI相关的，实际是处理全部再提取AI

* 避免做法：听完需求后，用自己的话复述一遍确认

***

## 今天的总结任务的标准流程

如果下次需要处理新的PDF并总结：

```bash
# 1. 确认 files/ 目录有新PDF
# 2. 运行完整处理（不要用 --no-ai）
python3 daily_500_pdf_processor.py

# 3. 如果是之前解析过但没有总结的，修改 batch_summarize.py 中的日期，然后运行
python3 batch_summarize.py

# 4. 提取专题报告（如AI）
python3 extract_topic_summary.py
```

***

## 🎯 简短提示词映射（重要）

看到以下任意提示词，直接执行**标准流程（批量总结 + 提取AI专题）**：

| 用户提示词          | 对应操作   |
| -------------- | ------ |
| `总结PDF + 提取AI` | 执行标准流程 |
| `新PDF，处理`      | 执行标准流程 |
| `执行标准流程`       | 执行标准流程 |
| `走流程`          | 执行标准流程 |
| `继续`           | 执行标准流程 |
| `来了新的`         | 执行标准流程 |
| `今天的`          | 执行标准流程 |

**指定专题示例**：

* 同时提取AI和新能源：`python3 daily_500_pdf_processor.py files output/daily/ --topic AI --topic 新能源`

* 提取新能源+医药+消费：`python3 daily_500_pdf_processor.py files output/daily/ -t 新能源 -t 医药 -t 消费`

***

## 📋 标准流程（固定）

1. **Office文档转换 + 移除非文档文件**（内置自动执行）：

   * `.docx/.doc/.xlsx/.xls/.pptx` 会自动转换为 Markdown 纳入总结流程（docx/xlsx/xls 用 markitdown，doc 用 macOS 自带 textutil，pptx 用 markitdown 文本 + 图片 Tesseract OCR 合并；xls 需要 xlrd），转换后源文件归档到 `files_processed/`

   * 其余非文档文件（图片等）移动到 `~/Downloads`
2. **批量总结**：`python3 daily_500_pdf_processor.py files output/daily/ --workers 6`

   * 自动用当天日期

   * 自动加载 `OPENAI_API_KEY`（从环境变量或 `.env`）

   * 只处理新文件（不重复）

   * Office文档（docx/doc/xlsx/xls/pptx）自动转换纳入总结流程
3. **提取AI专题**（内置自动执行）：主流程自动提取指定专题（默认 AI）

   * 输出到 `output/topic_summaries/AI/YYYYMMDDHH/`
4. **生成每日重点汇总**（内置自动执行）：主流程自动用大模型二次提炼生成重点汇总

   * 输出到 `output/daily/YYYYMMDDHH/reports/每日重点汇总_YYYYMMDDHH.md`

   * 包含：核心要闻、行业分类速览、深度报告精选、数据亮点
5. **收集微信读书汇总**（内置自动执行）：主流程自动把当日重点汇总、一句话总结、各专题核心论点汇总收集到 `output/汇总/YYYYMMDDHH/`

   * 用于整体导入微信读书，按日期隔离

***

## 🧪 测试输出目录（重要）

* **测试输出统一存放到** **`output/test_word_pipeline/`**，该目录**不要清理、不要删除**

* 测试流程必须使用独立输出目录，**不得干扰正式流程**（`output/daily/` 等）

* 测试产物与正式产物分开存放，避免混在一起

***

## ⏱️ 长任务汇报方式（重要，用户明确要求）

**运行耗时较长的任务（如批量总结、批量生成重点汇总）时：**

* 启动后台任务后，**不要频繁轮询/持续汇报进度**

* 等任务**跑完（或失败/卡住）后，一次性告知结果**

* 只汇报固定输出格式要求的内容即可

***

## 📊 固定输出格式

执行完成后必须告诉我：

* 处理了多少份文档（PDF 数量 + Word 转换数量）

* 筛选出多少份AI文档 + 占比

* 关键词分布统计（Top 5）

* 每日重点汇总是否生成成功

* 输出目录路径

***

## 🔍 提取其他专题的触发关键字（重要）

如果用户提到以下专题名称，直接执行对应的专题提取：

| 用户提示词        | 对应操作                                                      |
| ------------ | --------------------------------------------------------- |
| `提取新能源专题`    | `python3 extract_topic_summary.py --topic 新能源`            |
| `提取医药专题`     | `python3 extract_topic_summary.py --topic 医药`             |
| `提取消费专题`     | `python3 extract_topic_summary.py --topic 消费`             |
| `提取科技专题`     | `python3 extract_topic_summary.py --topic 科技`             |
| `提取汽车专题`     | `python3 extract_topic_summary.py --topic 汽车`             |
| `提取有色专题`     | `python3 extract_topic_summary.py --topic 有色`             |
| `提取煤炭专题`     | `python3 extract_topic_summary.py --topic 煤炭`             |
| `提取地产专题`     | `python3 extract_topic_summary.py --topic 地产`             |
| `提取银行专题`     | `python3 extract_topic_summary.py --topic 银行`             |
| `提取运动专题`     | `python3 extract_topic_summary.py --topic 运动`             |
| `提取AI和新能源专题` | `python3 extract_topic_summary.py --topic AI --topic 新能源` |

**支持的专题列表（11个）**：

1. **AI** - 人工智能、大模型、算力、芯片、具身智能等
2. **新能源** - 光伏、储能、锂电池、新能源车、氢能等
3. **医药** - 创新药、生物医药、医疗器械、CXO等
4. **消费** - 食品饮料、零售、电商、消费电子等
5. **科技** - 半导体、电子、通信、计算机、软件等
6. **汽车** - 整车、零部件、智能驾驶、自动驾驶等
7. **有色** - 有色金属、贵金属、工业金属等
8. **煤炭** - 煤炭、煤化工、火电、能源等
9. **地产** - 房地产、物业、建材、家居等
10. **银行** - 银行、金融、信贷、利率等
11. **运动** - 体育、运动服饰、健身、户外、电竞等

**备注**：

* 用户可以同时提多个专题（如"提取AI和新能源"）

* 默认用当天日期的summaries目录

* 输出目录：`output/topic_summaries/{专题名}/YYYYMMDDHH/`

