# 专题核心论点收集脚本 - 设计文档

**日期**：2026-11-07
**状态**：已批准（方案 A）

## 目标

参考现有 `output/daily/重点汇总/` 和 `output/daily/一句话总结/` 的收集方式，把指定专题的"核心论点汇总"文档按日期累积复制到一个扁平目录，便于一次性全选复制研究。后续新增专题只需加参数，无需改脚本。

## 背景

当前专题核心论点文档生成在 `output/topic_summaries/{专题}/核心论点/{专题}_核心论点汇总_YYYYMMDDHH.md`（如 `output/topic_summaries/存储/核心论点/存储_核心论点汇总_2026110707.md`），分散在专题目录下，用户难以一次性查看某个专题的全部历史内容。

现有收集方式参考（`src/pdf_ocr_tool/scripts/daily_processor.py` 的 `copy_reports_to_collections`）：

- `每日重点汇总_*.md` → `output/daily/重点汇总/`（扁平）
- `summary_list_*.md` → `output/daily/一句话总结/`（扁平）
- 用 `shutil.copy2` 复制，保留日期后缀命名

## 方案

新建独立脚本 `src/pdf_ocr_tool/scripts/collect_topic_summaries.py`，用法：

```bash
python3 collect_topic_summaries.py --topic 存储 --topic 服务器
```

### 行为

1. 解析 `--topic` 参数（可多次指定；`--topic 全部` 或省略时扫描 `output/topic_summaries/` 下全部专题）
2. 对每个指定专题：
   - 源目录：`output/topic_summaries/{专题}/核心论点/`
   - 目标目录：`output/daily/{专题}核心论点/`
   - 复制所有匹配 `{专题}_核心论点汇总_*.md` 的文件（`shutil.copy2`，保留原文件名即日期后缀）
3. 输出复制结果清单（源 → 目标），统计每个专题复制份数

### 目标目录命名

与现有 `重点汇总`、`一句话总结` 平级，位于 `output/daily/` 下：

- `output/daily/存储核心论点/`
- `output/daily/服务器核心论点/`
- （新增专题自动命名）`output/daily/{专题}核心论点/`

### 边界处理

- 源目录不存在 → 跳过该专题并提示
- 无匹配文件 → 提示"该专题暂无核心论点文档"
- 目标目录自动创建（`os.makedirs(exist_ok=True)`）
- 目标已有同名文件 → `copy2` 直接覆盖（幂等，重复运行无害）

### 不做的事（YAGNI）

- 不合并多个日期文件为一个总文件（用户只要复制研究）
- 不加入主流程自动执行（用户选择手动运行）
- 不做去重/清理目标目录

## 测试

- 用现有数据跑 `--topic 存储 --topic 服务器`，验证：
  - 存储：46 份全部复制到 `output/daily/存储核心论点/`
  - 服务器：61 份全部复制到 `output/daily/服务器核心论点/`
  - 文件名与源一致
- 重复运行验证幂等
- 空专题/不存在专题验证提示
