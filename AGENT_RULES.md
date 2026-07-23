# Agent 执行规则

## 🎯 简短提示词映射

| 用户提示词 | 对应操作 |
|-----------|---------|
| `总结PDF + 提取AI` | 执行标准流程 |
| `新PDF，处理` | 执行标准流程 |
| `执行标准流程` | 执行标准流程 |
| `走流程` | 执行标准流程 |
| `继续` | 执行标准流程 |
| `来了新的` | 执行标准流程 |
| `今天的` | 执行标准流程 |

---

## 📋 标准流程（固定）

1. **检查**：`files/` 目录的PDF数量
2. **批量总结**：`python3 daily_500_pdf_processor.py files output/daily/ --workers 6`
   - 自动用当天日期
   - 自动加载 `OPENAI_API_KEY`（从环境变量或 `.env`）
   - 只处理新文件（不重复）
3. **提取AI专题**：`python3 extract_topic_summary.py`
   - 只提取当天生成的文档
   - 输出到 `output/topic_summaries/AI/YYYYMMDD/`

---

## 📊 固定输出格式

执行完成后必须告诉我：
- 处理了多少份PDF
- 筛选出多少份AI文档 + 占比
- 关键词分布统计（Top 5）
- 输出目录路径
