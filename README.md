# PDF 研报总结工具

一个完整的 PDF 研报总结流水线：从PDF解析 → LLM智能总结 → 主题提取汇总，支持19大专题。按文件名开头的星球名自动区分**投资 / 自媒体 / 其他**三个批次，各自独立解析、总结、专题提取与微信读书收集，互不混同。

## 功能特点

### 🎯 核心功能
- **智能混合解析**: 自动选择最优解析策略（可选择文本 / Tesseract OCR）
- **Office 文档支持**: 自动转换 `.docx`/`.xlsx`/`.xls`（markitdown）、`.doc`（macOS textutil）和 `.pptx`（markitdown 文本 + 图片 Tesseract OCR 合并）为 Markdown，与 PDF 一样纳入总结流程
- **质量评分**: 自动评估识别质量，确保输出可靠性
- **LLM智能总结**: 使用大模型（火山引擎方舟，模型可配置）生成一句话总结和核心看点
- **19大专题自动提取**: 投资类 12 个 + 自媒体类 7 个，各批次自动匹配对应专题集
- **批次隔离**: 按文件名开头的星球名自动分类 —— 投资（全球资讯精读/速查报告库）→ `output/daily`；自媒体（知否 私域运营研习社/运营研究社）→ `output/daily_media`；其余 → `output/daily_other`。专题根（`topic_summaries`/`topic_summaries_media`）与微信读书收集（`汇总`/`汇总_media`）同样隔离
- **每日重点汇总**: 大模型二次提炼生成"每日重点汇总"（核心要闻 / 行业分类 / 深度报告精选 / 数据亮点）
- **飞书自动推送**: 总结完成后自动将"今日核心要闻"推送到飞书群
- **汇总文档自动归档**: 每日重点汇总复制到 `daily/重点汇总/`，一句话总结清单复制到 `daily/一句话总结/`，跨日期集中浏览
- **微信读书汇总收集**: 将当日重点汇总、一句话总结、所有专题核心论点汇总自动收集到 `output/汇总/YYYYMMDDHH/`，按日期隔离，方便整体导入微信读书

### ⚡ 每日批量处理
- **固定目录**: `files/` 平铺放入新文档（PDF + Office），按文件名开头的星球名自动识别类别，不做物理移动
- **主题化归档**: 处理完成后按类别归档 —— `invest_files_processed/`（投资）/ `media_files_processed/`（自媒体）/ `other_files_processed/`（其他）
- **日期隔离输出**: 自动按日期创建输出目录，每天的数据不混淆
- **文件自动移动**: 处理完成后自动归档源文件
- **非PDF自动清理**: 启动时自动将 `files/` 中不属于任何星球类别的非文档文件（图片等）移动到 `~/Downloads`；Office 文档（docx/doc/xlsx/xls/pptx）会被转换为 Markdown 纳入总结流程，转换后源文件归档到主题化归档目录
- **自动专题提取**: 主流程自动提取各批次默认专题并生成每日重点汇总
- **去重处理**: 只处理新文件，已处理过的文件不会重复总结

### 🤖 支持的19大专题

**投资批次（12个）**

| 专题 | 关键词示例 |
|------|---------|
| **AI** | AI, 人工智能, 大模型, LLM, GPT, Agent, 智能体, 算力, 光模块, 芯片, 具身智能 |
| **新能源** | 光伏, 储能, 锂电池, 动力电池, 新能源车, 氢能, 复合集流体 |
| **医药** | 创新药, 生物医药, CXO, 医疗器械, ADC, 双抗, 医疗服务 |
| **消费** | 消费, 食品饮料, 零售, 电商, 消费电子, 白酒, 啤酒, 美妆, 预制菜 |
| **科技** | 半导体, 芯片, 集成电路, 晶圆, 封测, 电子, 通信, 计算机, 软件 |
| **汽车** | 整车, 乘用车, 商用车, 新能源汽车, 智能驾驶, 自动驾驶 |
| **有色** | 有色, 铜, 铝, 金, 银, 锂, 钴, 镍, 稀土, 磁材 |
| **煤炭** | 煤炭, 煤, 焦煤, 动力煤, 煤化工, 火电, 能源 |
| **地产** | 地产, 房地产, 物业, 建材, 家居, 水泥, 玻璃, 防水 |
| **银行** | 银行, 金融, 信贷, 利率, 息差, 拨备 |
| **运动** | 运动, 体育, 健身, 户外, 电竞, 赛事, 跑步, 马拉松, 足球, 篮球, 羽毛球, 乒乓球, 网球, 瑜伽, 冰雪, 滑雪, 游泳, 露营, 骑行, 钓鱼, 健身房, 运动品牌, 安踏, 李宁, 特步 |
| **健康** | 健康, 大健康, 健康管理, 健康产业, 医疗健康, 健康中国, 保健, 保健品, 养生, 体检, 健康体检, 康养, 养老产业, 心理健康, 睡眠健康, 营养健康, 健康食品, 功能食品, 慢病管理, 健康服务, 健康消费, 健康保险, 智慧健康 |

**自媒体批次（7个）**

| 专题 | 关键词示例 |
|------|---------|
| **抖音** | 抖音, 短视频, 直播, 直播带货, 直播间, 巨量引擎, 千川, 信息流, 投流, 本地生活, 星图, 短剧 |
| **小红书** | 小红书, 种草笔记, 买手电商, 爆文, 笔记排名, 素人, 博主, 社区电商 |
| **快手** | 快手, 磁力引擎, 快分销, 快手电商, 辛选, 老铁, 直播带货 |
| **B站** | B站, Bilibili, 哔哩哔哩, UP主, 弹幕, 中视频 |
| **视频号** | 视频号, 微信视频号, 视频号直播, 微信生态, 小程序, 企业微信 |
| **公众号** | 公众号, 微信公众号, 订阅号, 服务号, 公众号矩阵, 爆文, 内容营销 |
| **运营** | 增长, 用户增长, 裂变, 流量, 转化, 投放, 获客, 留存, 复购, 种草, 矩阵, KOL, KOC, 达人, MCN, IP |

## 快速开始

### 安装依赖

```bash
cd /Users/xingan/Documents/software/workspace/summary
pip install -r requirements.txt
```

### 配置大模型（火山引擎方舟）

所有配置统一放在 `.env` 文件（参考 `.env.example`），也可以用环境变量：

```bash
# 方式1：复制模板并填写
cp .env.example .env

# 方式2：手动创建 .env 文件
echo "OPENAI_API_KEY=你的方舟密钥" > .env
```

| 配置项 | 必填 | 默认值 | 说明 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | ✅ 是 | — | 火山引擎方舟 API Key |
| `ARK_MODEL` | 否 | `doubao-seed-2.0-pro` | 大模型名称（可切换其他模型） |
| `ARK_BASE_URL` | 否 | `https://ark.cn-beijing.volces.com/api/coding/v3` | 方舟 API 地址（可切换其他兼容服务） |
| `FEISHU_WEBHOOK` | 否 | — | 飞书群机器人 Webhook（用于推送每日核心要闻） |

> `ARK_MODEL` / `ARK_BASE_URL` 不配置时使用默认值；未配置 `OPENAI_API_KEY` 时会降级为纯算法模式（总结质量显著下降）。

### 配置飞书推送（可选）

如需在总结完成后自动推送"今日核心要闻"到飞书群，需要配置飞书群机器人 Webhook：

```bash
# 方式1：追加到 .env 文件
echo "FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/你的机器人地址" >> .env

# 方式2：设置环境变量
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/你的机器人地址"
```

> 未配置时不影响主流程，仅跳过飞书推送步骤。

### 日常使用流程

```bash
# ======================================
# Step 1: 批量总结所有PDF（每天运行一次）
# ======================================
# 默认提取AI专题
python3 daily_500_pdf_processor.py files output/daily/

# 主流程自动执行：
#   1. 移除非PDF文件到 ~/Downloads
#   2. 解析PDF -> processed/
#   3. LLM总结 -> summaries/
#   4. 提取AI专题 -> output/topic_summaries/AI/YYYYMMDDHH/
#   5. 生成每日重点汇总 -> reports/每日重点汇总_YYYYMMDDHH.md
#   6. 推送今日核心要闻到飞书（已配置FEISHU_WEBHOOK时）
#   7. 复制汇总文档 -> daily/重点汇总/ + daily/一句话总结/（参考核心论点复制规则）
#   8. 收集当日汇总文档 -> 汇总/YYYYMMDDHH/（重点汇总+一句话总结+各专题核心论点，微信读书导入用）

# 输出目录： output/daily/YYYYMMDDHH/
#   ├── processed/    # PDF解析后的Markdown
#   ├── summaries/    # 单文件总结（一句话总结 + 核心看点）
#   └── reports/      # 每日重点汇总 + 总结清单
# 另外复制到 output/daily/（跨日期集中浏览）：
#   ├── 重点汇总/     # 每日重点汇总_YYYYMMDDHH.md
#   └── 一句话总结/   # summary_list_YYYYMMDDHH.md
# 另外收集到 output/汇总/YYYYMMDDHH/（微信读书导入用）：
#   ├── 每日重点汇总_YYYYMMDDHH.md
#   ├── summary_list_YYYYMMDDHH.md
#   └── {专题}_核心论点汇总_YYYYMMDDHH.md（当天所有专题）


# 提取多个专题（投资批次支持19大专题，--topic 覆盖投资默认专题）
python3 daily_500_pdf_processor.py files output/daily/ --topic AI --topic 新能源 --topic 医药


# ======================================
# Step 2: 单独提取其他专题报告（可选）
# ======================================
python3 extract_topic_summary.py --topic 新能源
python3 extract_topic_summary.py --topic 医药 --topic 消费

# 输出目录： output/topic_summaries/{专题名}/YYYYMMDDHH/
#   ├── READED_YYYYMMDDHH.md               # 文档索引
#   ├── {专题名}_一句话汇总_YYYYMMDDHH.md   # 快速浏览版
#   ├── {专题名}_核心论点汇总_YYYYMMDDHH.md # 完整专题报告
#   └── summaries/                       # 该专题相关文档单独总结
```

### 历史日期补充每日重点汇总

已处理过的历史日期如果缺少"每日重点汇总"，可用批量脚本一次性补齐：

```bash
# 为所有有 summaries 的历史日期生成每日重点汇总并推送飞书
python3 scripts/generate_all_daily_highlights.py

# 只处理指定日期区间（如只补2026年8月的数据）
python3 scripts/generate_all_daily_highlights.py --start 20260801 --end 20260831

# 生成结果：output/daily/YYYYMMDD/reports/每日重点汇总_YYYYMMDD.md
# 特性：自动跳过已存在 / 无总结的日期，可重复运行不重复生成
```

> 每个日期会调用大模型二次提炼（约2-5分钟），并自动推送"今日核心要闻"到飞书（已配置 FEISHU_WEBHOOK 时）。

### 常用参数

```bash
# daily_500_pdf_processor.py 参数
--workers 6        # 并行进程数，默认8
--min-score 40    # 最低解析质量评分，默认60
--force           # 强制重新解析（忽略缓存）
--no-ai          # 不生成总结和专题提取（只解析PDF）
--topic, -t      # 指定要提取的专题（可多次指定，仅覆盖投资批次默认专题）
                  # 投资支持：AI/新能源/医药/消费/科技/汽车/有色/煤炭/地产/银行/运动/健康
                  # 自媒体批次固定提取：抖音/小红书/快手/B站/视频号/公众号/运营

# 示例：提取3个专题
python3 daily_500_pdf_processor.py files output/daily/ -t 新能源 -t 医药 -t 消费


# extract_topic_summary.py 参数
-i, --input       # 指定输入summaries目录（自动找最新，一般不用）
--topic, -t       # 提取的专题（可多次指定）
--list-topics     # 列出所有支持的专题


# generate_all_daily_highlights.py 参数
--start YYYYMMDD  # 起始日期（可选）
--end YYYYMMDD    # 结束日期（可选）
```

## 📂 完整目录结构

```
summary/
├── .env                       # 本地配置（API密钥/模型名/Webhook，不入库）
├── .env.example               # 配置模板（含默认值说明，入库）
├── files/                       # 平铺放入新文档（PDF + Office，按星球名自动分类，不移动）
├── invest_files_processed/      # 投资批次归档（原 files_processed/）
├── media_files_processed/       # 自媒体批次归档
├── other_files_processed/       # 其他批次归档
│
├── output/
│   ├── daily/                   # 投资批次每日处理结果
│   │   ├── 重点汇总/              # 每日重点汇总集中归档（跨日期）
│   │   ├── 一句话总结/            # 一句话总结清单集中归档（跨日期）
│   │   └── 20260720/
│   │       ├── processed/       # PDF解析Markdown
│   │       ├── summaries/       # 单文件总结（一句话 + 核心看点）
│   │       └── reports/         # 每日重点汇总 + summary_list + 优化报告
│   │
│   ├── daily_media/             # 自媒体批次每日处理结果（结构与 daily/ 相同）
│   │   └── 2026090616/          # processed/ + summaries/ + reports/
│   │
│   ├── 汇总/                     # 投资批次微信读书导入（按日期收集当日汇总文档）
│   │   └── 20260828/            # 每日重点汇总 + summary_list + 各专题核心论点
│   │
│   ├── 汇总_media/               # 自媒体批次微信读书导入（与投资批次隔离）
│   │   └── 2026090616/
│   │
│   ├── topic_summaries/         # 投资批次专题报告（按主题隔离）
│   │   ├── AI/
│   │   │   ├── 20260720/
│   │   │   │   ├── READED_20260720.md
│   │   │   │   ├── AI_一句话汇总_20260720.md
│   │   │   │   ├── AI_核心论点汇总_20260720.md
│   │   │   │   └── summaries/        # 该专题相关文档单独总结
│   │   │   ├── 20260721/        # 每天一个新目录，互不干扰
│   │   │   └── ...
│   │   ├── 新能源/
│   │   ├── 医药/
│   │   └── ... （其他投资专题）
│   │
│   └── topic_summaries_media/   # 自媒体批次专题报告（抖音/小红书/快手/B站/视频号/公众号/运营）
│
├── src/
│   └── pdf_ocr_tool/
│       ├── parsers/             # PDF解析器
│       ├── pipeline/            # 处理管道
│       ├── summarizers/         # 总结生成器（按类拆分）
│       │   ├── aicontent_summarizer.py        # 基础NLP算法
│       │   ├── financial_research_summarizer.py # 财经结构化总结 + 每日重点汇总 + 飞书推送
│       │   ├── markdown_file_summarizer.py    # 批量处理 + CLI
│       │   └── financial_summarizer.py        # 聚合导出（兼容旧导入路径）
│       ├── topics/              # 专题提取模块
│       │   ├── config.py        # 19大专题关键词配置 + 星球名分类规则
│       │   ├── utils.py         # 文件读取 / 文档判断 / 飞书推送
│       │   ├── analyzers.py     # 主题 / 观点 / 受益方向分析
│       │   └── extractor.py     # 专题提取主函数
│       └── scripts/             # 主流程
│           ├── daily_processor.py           # DailyPDFProcessor 核心类
│           └── daily_500_pdf_processor.py   # CLI 入口（分类批次 + 隔离输出）
│
├── daily_500_pdf_processor.py    # 入口1：批量解析+总结+多专题提取
├── extract_topic_summary.py       # 入口2：提取指定专题汇总
│
├── scripts/                       # 辅助工具脚本
│   ├── generate_all_daily_highlights.py  # 批量补齐历史日期每日重点汇总
│   ├── rerun_summaries.py                # 单日期强制重跑总结
│   └── batch_rerun_dates.py              # 批量重跑多日期总结
│
├── run_llm_summary.py            # 单日LLM总结工具（已解析缺总结时用）
└── batch_summarize.py            # 批量为已解析PDF生成总结
```

## 🎯 使用场景

### 场景1：新到一批研报，全部总结

```bash
# 1. 把PDF放入 files/

# 2. 批量处理（解析+LLM总结+AI专题提取）
python3 daily_500_pdf_processor.py files output/daily/ --workers 6

# 3. 查看结果
# 所有文档总结在 output/daily/YYYYMMDDHH/summaries/
# AI专题汇总在 output/topic_summaries/AI/YYYYMMDDHH/
```

### 场景2：同时提取AI+新能源+医药三个专题

```bash
# 批量总结+同时提取3个专题
python3 daily_500_pdf_processor.py files output/daily/ -t AI -t 新能源 -t 医药

# 查看专题汇总：
# output/topic_summaries/AI/YYYYMMDDHH/
# output/topic_summaries/新能源/YYYYMMDDHH/
# output/topic_summaries/医药/YYYYMMDDHH/
```

### 场景3：先解析，后续再总结

```bash
# Day 1：只解析，不调用LLM（省token）
python3 daily_500_pdf_processor.py files output/daily/ --no-ai

# Day 2：后续补充提取某专题
python3 extract_topic_summary.py -i output/daily/YYYYMMDDHH/summaries/ --topic 科技
```

### 场景4：查看所有支持的专题

```bash
python3 extract_topic_summary.py --list-topics
```

## 📝 输出文件说明

### 每日批量处理结果（output/daily/YYYYMMDDHH/）

| 文件/目录 | 内容 | 用途 |
|-----------|------|------|
| `processed/*.md` | PDF解析后的完整Markdown | 原始文本，供阅读或二次处理 |
| `summaries/*_summary.md` | 每个文档的一句话总结 + 核心看点 | 快速了解每份研报核心内容 |
| `reports/summary_list_YYYYMMDDHH.md` | 当日全部文档的一句话总结清单（标题+段落格式） | 快速浏览当天全部研报，适配不支持表格的阅读器 |
| `reports/每日重点汇总_YYYYMMDDHH.md` | 大模型二次提炼的核心要闻 + 行业分类 + 深度报告精选 + 数据亮点 | 快速掌握当天最重要的信息 |
| `daily/重点汇总/每日重点汇总_YYYYMMDDHH.md` | 每日重点汇总的跨日期集中副本 | 不进入具体日期目录即可浏览历史重点 |
| `daily/一句话总结/summary_list_YYYYMMDDHH.md` | 一句话总结清单的跨日期集中副本 | 不进入具体日期目录即可浏览历史总结 |
| `汇总/YYYYMMDDHH/每日重点汇总_YYYYMMDDHH.md` | 当日重点总结（微信读书导入用） | 与一句话总结、各专题核心论点一并整体导入微信读书 |
| `汇总/YYYYMMDDHH/summary_list_YYYYMMDDHH.md` | 当日一句话总结清单（微信读书导入用） | 与重点汇总、各专题核心论点一并整体导入微信读书 |
| `汇总/YYYYMMDDHH/{专题}_核心论点汇总_YYYYMMDDHH.md` | 当日各专题核心论点汇总（微信读书导入用） | 自动收集当天所有已提取专题 |

### 专题报告（topic_summaries/）

| 文件名 | 内容 | 用途 |
|--------|------|------|
| `{专题名}_一句话汇总_YYYYMMDDHH.md` | 该专题所有文档的一句话总结 | 快速浏览，了解行业全貌 |
| `{专题名}_核心论点汇总_YYYYMMDDHH.md` | 每文档一句话+5条核心看点 | 深度研读，提取投资机会 |
| `summaries/*.md` | 单个文档的完整总结 | 需要仔细研读某份文档时看 |
| `READED_YYYYMMDDHH.md` | 文档列表+关键词统计 | 索引，快速定位感兴趣文档 |

## 🛠️ 辅助工具脚本

| 脚本 | 解决什么问题 | 用法 |
|------|------------|------|
| `scripts/generate_all_daily_highlights.py` | 历史日期缺少每日重点汇总时批量补齐 | `python3 scripts/generate_all_daily_highlights.py [--start YYYYMMDD] [--end YYYYMMDD]` |
| `scripts/copy_reports_to_collections.py` | 历史日期的每日重点汇总/一句话总结未归档时批量复制到集合文件夹 | `python3 scripts/copy_reports_to_collections.py [--start YYYYMMDD] [--end YYYYMMDD]` |
| `scripts/rerun_summaries.py` | 单日期总结质量不合格时强制重跑 | `python3 scripts/rerun_summaries.py <YYYYMMDD> [workers]` |
| `scripts/batch_rerun_dates.py` | 多个历史日期总结质量不合格时批量重跑 | `python3 scripts/batch_rerun_dates.py <date1> <date2> ... [workers]` |
| `run_llm_summary.py` | processed/ 已解析但缺少 summaries/ 时生成总结 | `python3 run_llm_summary.py` |
| `batch_summarize.py` | 批量为已解析PDF生成总结（需修改日期） | `python3 batch_summarize.py` |

## 系统要求

- **操作系统**: macOS, Linux
- **Python**: 3.8+
- **Tesseract OCR**: 需要单独安装 (`brew install tesseract`)
- **豆包方舟**: 需要API密钥（使用LLM总结功能）
- **硬件**: 4核CPU, 8GB内存（推荐16GB）

## 许可证

MIT License
