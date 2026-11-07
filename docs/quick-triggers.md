# 简单提示词 → 功能 触发映射表

> 用途：用户常以一句话触发本项目功能（如"总结PDF+提取AI""走流程""提取新能源专题"）。本表把**简单提示词路由到对应脚本/操作**，是 Agent 判断意图的第一依据。
> 使用规则：
> 1. 命中触发词 → 按"默认行为"执行（执行细节以 `.trae/rules/project_rules.md` 为准）。
> 2. 未命中 → 先向用户确认意图（AskUserQuestion），不得自行猜测。
> 3. **新功能上线时，把触发词补进本表**。
> 4. "执行后产物"列填写触发后产生的文件路径；无文件产物时注明"无文件"。

---

## 一、标准流程类（PDF 总结 + 专题提取）

| 触发词（含别名） | 触发功能 | 默认行为 | 入口 | 执行后产物 |
|---|---|---|---|---|
| 总结PDF + 提取AI / 新PDF，处理 / 执行标准流程 / 走流程 / 继续 / 来了新的 / 今天的 | 标准流程 | 完整处理 `files/` 新文档：自动去重 → Office 转换 → 按星球分类批次 → 批量总结 → 提取默认专题 → 生成每日重点汇总 → 收集微信读书汇总 | `python3 daily_500_pdf_processor.py files output/daily/ --workers 6` | 投资批次 `output/daily/YYYYMMDDHH/`（`processed/` + `summaries/` + `reports/`）、专题 `output/topic_summaries/{专题}/YYYYMMDDHH/`、汇总 `output/汇总/YYYYMMDDHH/` |
| 总结自媒体 / 总结抖音 / 来了自媒体文档 | 自媒体批次标准流程 | 同标准流程，自媒体文档自动进 media 批次，提取 7 个自媒体专题 | `python3 daily_500_pdf_processor.py files output/daily/ --workers 6` | `output/daily_media/YYYYMMDDHH/`、`output/topic_summaries_media/{专题}/YYYYMMDDHH/`、`output/汇总_media/YYYYMMDDHH/` |

## 二、专题提取类

| 触发词（含别名） | 触发功能 | 默认行为 | 入口 | 执行后产物 |
|---|---|---|---|---|
| 提取AI专题 / 提取新能源专题 / 提取医药专题 / 提取消费专题 / 提取科技专题 / 提取汽车专题 / 提取有色专题 / 提取煤炭专题 / 提取地产专题 / 提取银行专题 / 提取运动专题 / 提取AI和新能源专题 | 提取指定专题 | 从当日 summaries 提取指定专题报告（可同时多个） | `python3 extract_topic_summary.py --topic 新能源` | `output/topic_summaries/{专题}/YYYYMMDDHH/`（summaries + 核心论点 + 一句话汇总） |
| 提取抖音专题 / 提取小红书专题（对 media 批次） | 提取自媒体专题 | 从 media 批次 summaries 提取 | `python3 extract_topic_summary.py --topic 抖音` | `output/topic_summaries_media/{专题}/YYYYMMDDHH/` |

## 三、收集与整理类

| 触发词（含别名） | 触发功能 | 默认行为 | 入口 | 执行后产物 |
|---|---|---|---|---|
| 收集存储核心论点 / 收集服务器核心论点 / 把存储内容复制出来 / 专题核心论点收集 | 专题核心论点收集 | 把指定专题全部日期的核心论点汇总复制到扁平目录（便于一次性复制研究）；省略 `--topic` 扫描全部专题 | `python3 src/pdf_ocr_tool/scripts/collect_topic_summaries.py --topic 存储 --topic 服务器` | `output/daily/{专题}核心论点/`（如 `存储核心论点/` 46 份、`服务器核心论点/` 61 份） |
| 导入去重 / 检查重复 / 去重预览 | 导入文档去重 | 归档同名回移 + md5 一致副本删除；`--no-delete` 只读预览 | `python3 src/pdf_ocr_tool/scripts/deduplicate.py files` | 移动/删除操作记录（控制台输出，无文件） |

## 四、识别与补处理类

| 触发词（含别名） | 触发功能 | 默认行为 | 入口 | 执行后产物 |
|---|---|---|---|---|
| 识别困难PDF / 识别不了 / 乱码PDF | 困难PDF 处理 | 主流程内置识别困难自动过滤（乱码/不可读文档归档到 `summaries/识别困难归档/`，不生成无效总结）；历史 Tesseract OCR 独立脚本已归档 `archive/direct_tesseract_ocr.py`，如需单独 OCR 可参考 | 主流程自动处理 / 参考 `archive/direct_tesseract_ocr.py` | `reports/识别困难文档清单_YYYYMMDDHH.md`（逐份说明失败原因） |
| 批量补总结 / 补生成总结 / 只总结不解析 | 批量总结已解析文档 | 为已解析但未总结的文档生成总结（需修改 `batch_summarize.py` 中硬编码日期） | `python3 batch_summarize.py` | `summaries/` + `reports/` |

---

## 维护约定

- **新增功能**：上线时在本表补一行（触发词 + 功能 + 默认行为 + 入口 + 执行后产物）。
- **改默认行为/产物**：同时更新本表与 `.trae/rules/project_rules.md`，保持两处一致。
- **冲突**：`.trae/rules/project_rules.md` 的规则优先；标准流程触发词以该文件"简短提示词映射"为准。
