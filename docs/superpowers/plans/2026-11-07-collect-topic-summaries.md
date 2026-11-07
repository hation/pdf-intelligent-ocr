# 专题核心论点收集脚本 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新建独立脚本 `collect_topic_summaries.py`，把指定专题的"核心论点汇总"文档复制到 `output/daily/{专题}核心论点/` 扁平目录，支持指定专题列表与自动扫描全部专题。

**Architecture:** 一个轻量命令行脚本（argparse），核心逻辑为 `collect_topic(topic, project_root) -> list[(src,dst)]`：从 `output/topic_summaries/{专题}/核心论点/` 复制 `{专题}_核心论点汇总_*.md` 到 `output/daily/{专题}核心论点/`。复制风格沿用 `daily_processor.copy_reports_to_collections`（shutil.copy2、扁平、保留日期后缀）。配套 pytest 风格单测（项目惯例：`tests/test_*.py`，直接 `python3` 运行）。

**Tech Stack:** Python 3.12，argparse + shutil + os + re，无第三方依赖。

---

## 文件结构

- Create: `src/pdf_ocr_tool/scripts/collect_topic_summaries.py` — 脚本本体（`collect_topic` 核心函数 + `main` CLI）
- Create: `tests/test_collect_topic_summaries.py` — 单元测试（临时目录 + 模拟文件，验证复制行为与边界）
- No existing files modified.

路径规则：`_project_root()` 定位项目根（脚本位于 `<root>/src/pdf_ocr_tool/scripts/`，向上 4 级），与 `deduplicate.py` 一致。

---

### Task 1: 编写核心复制函数并验证

**Files:**
- Create: `src/pdf_ocr_tool/scripts/collect_topic_summaries.py`
- Test: `tests/test_collect_topic_summaries.py`

- [ ] **Step 1: 先写失败测试**

Create `tests/test_collect_topic_summaries.py`:

```python
#!/usr/bin/env python3
"""collect_topic_summaries.py 单元测试。

覆盖场景：
1. 复制指定专题的全部核心论点汇总文件到扁平目录
2. 目标目录自动创建
3. 目标已有同名文件 → 覆盖（幂等）
4. 专题目录不存在 → 返回空列表
5. 核心论点目录不存在 → 返回空列表
6. 无匹配文件（非核心论点汇总的 md）→ 不复制
7. 输出文件名与源一致（保留日期后缀）

运行：python3 tests/test_collect_topic_summaries.py
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_ocr_tool.scripts.collect_topic_summaries import collect_topic


def make_env():
    """构造临时项目结构：output/topic_summaries/{专题}/核心论点/ + output/daily/"""
    root = tempfile.mkdtemp(prefix='collect_ut_')
    output = os.path.join(root, 'output')
    os.makedirs(output)
    os.makedirs(os.path.join(output, 'daily'))
    core_dir = os.path.join(output, 'topic_summaries', '存储', '核心论点')
    os.makedirs(core_dir)
    with open(os.path.join(core_dir, '存储_核心论点汇总_2026110707.md'), 'w', encoding='utf-8') as f:
        f.write('# 存储核心论点 2026110707\n')
    with open(os.path.join(core_dir, '存储_核心论点汇总_2026110223.md'), 'w', encoding='utf-8') as f:
        f.write('# 存储核心论点 2026110223\n')
    # 非核心论点文件（不应被复制）
    with open(os.path.join(core_dir, '存储_一句话汇总_2026110707.md'), 'w', encoding='utf-8') as f:
        f.write('# 存储一句话\n')
    return root


def test_basic_copy():
    root = make_env()
    copies = collect_topic('存储', root)
    assert len(copies) == 2, f'应复制2份，实际{len(copies)}'
    dst_dir = os.path.join(root, 'output', 'daily', '存储核心论点')
    assert os.path.isdir(dst_dir), '目标目录未创建'
    assert os.path.exists(os.path.join(dst_dir, '存储_核心论点汇总_2026110707.md'))
    assert os.path.exists(os.path.join(dst_dir, '存储_核心论点汇总_2026110223.md'))
    # 非核心论点文件未被复制
    assert not os.path.exists(os.path.join(dst_dir, '存储_一句话汇总_2026110707.md'))


def test_idempotent():
    """重复运行结果一致（覆盖同名文件，不报错）"""
    root = make_env()
    collect_topic('存储', root)
    copies2 = collect_topic('存储', root)
    assert len(copies2) == 2


def test_topic_not_exists():
    root = make_env()
    copies = collect_topic('不存在的专题', root)
    assert copies == []


def test_core_dir_not_exists():
    root = tempfile.mkdtemp(prefix='collect_ut_')
    output = os.path.join(root, 'output')
    os.makedirs(os.path.join(output, 'topic_summaries', 'AI'))  # 无 核心论点 子目录
    copies = collect_topic('AI', root)
    assert copies == []


def test_no_matching_files():
    """核心论点目录只有无关 md → 空结果"""
    root = tempfile.mkdtemp(prefix='collect_ut_')
    core_dir = os.path.join(root, 'output', 'topic_summaries', 'AI', '核心论点')
    os.makedirs(core_dir)
    with open(os.path.join(core_dir, '随便一个文件.md'), 'w', encoding='utf-8') as f:
        f.write('x')
    copies = collect_topic('AI', root)
    assert copies == []


def test_filename_preserved():
    root = make_env()
    copies = collect_topic('存储', root)
    src_bases = sorted(os.path.basename(s) for s, _ in copies)
    assert src_bases == ['存储_核心论点汇总_2026110223.md', '存储_核心论点汇总_2026110707.md']


if __name__ == '__main__':
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f'PASS: {name}')
            except AssertionError as e:
                failures += 1
                print(f'FAIL: {name}: {e}')
            except Exception as e:
                failures += 1
                print(f'ERROR: {name}: {e}')
    print(f'\n{6 - failures}/6 通过' if failures == 0 else f'\n失败 {failures}/6')
    sys.exit(1 if failures else 0)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python3 tests/test_collect_topic_summaries.py`
Expected: `ERROR: test_basic_copy: ModuleNotFoundError: No module named 'pdf_ocr_tool.scripts.collect_topic_summaries'`（或类似导入失败）

- [ ] **Step 3: 实现脚本**

Create `src/pdf_ocr_tool/scripts/collect_topic_summaries.py`:

```python
#!/usr/bin/env python3
"""专题核心论点收集：把指定专题的核心论点汇总文档复制到 output/daily/{专题}核心论点/。

参考 output/daily/重点汇总/ 与 output/daily/一句话总结/ 的收集方式：
将 output/topic_summaries/{专题}/核心论点/ 下的 {专题}_核心论点汇总_*.md
用 shutil.copy2 复制到 output/daily/{专题}核心论点/（扁平 + 保留日期后缀命名）。

用法：
  python3 collect_topic_summaries.py --topic 存储 --topic 服务器   # 指定专题（可多次）
  python3 collect_topic_summaries.py                               # 扫描全部专题
"""

import argparse
import os
import re
import shutil
import sys


def _project_root():
    """定位项目根目录（脚本位于 <root>/src/pdf_ocr_tool/scripts/）"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _list_topics(project_root):
    """扫描 output/topic_summaries/ 下的全部专题名（跳过非目录项）"""
    topics_root = os.path.join(project_root, 'output', 'topic_summaries')
    if not os.path.isdir(topics_root):
        return []
    return sorted(name for name in os.listdir(topics_root)
                  if os.path.isdir(os.path.join(topics_root, name)))


def collect_topic(topic, project_root):
    """把单专题的核心论点汇总复制到 output/daily/{专题}核心论点/。

    Args:
        topic: 专题名（如 '存储'）
        project_root: 项目根目录

    Returns:
        list[(src, dst)]: 成功复制的 (源文件, 目标文件) 列表；无匹配时为空列表
    """
    src_dir = os.path.join(project_root, 'output', 'topic_summaries', topic, '核心论点')
    if not os.path.isdir(src_dir):
        return []

    dst_dir = os.path.join(project_root, 'output', 'daily', f'{topic}核心论点')
    os.makedirs(dst_dir, exist_ok=True)

    pattern = re.compile(rf'^{re.escape(topic)}_核心论点汇总_.*\.md$')
    copies = []
    for fname in sorted(os.listdir(src_dir)):
        if not fname.endswith('.md') or not pattern.match(fname):
            continue
        src = os.path.join(src_dir, fname)
        dst = os.path.join(dst_dir, fname)
        shutil.copy2(src, dst)
        copies.append((src, dst))
    return copies


def main():
    parser = argparse.ArgumentParser(description='收集专题核心论点汇总到 output/daily/{专题}核心论点/')
    parser.add_argument('--topic', action='append', help='专题名，可多次指定；省略则扫描全部专题')
    args = parser.parse_args()

    project_root = _project_root()

    if args.topic:
        topics = args.topic
    else:
        topics = _list_topics(project_root)
        if not topics:
            print('未发现 output/topic_summaries/ 下的专题，退出')
            return 1

    total = 0
    for topic in topics:
        copies = collect_topic(topic, project_root)
        if not copies:
            print(f'⚠️  {topic}: 无核心论点汇总文档（或目录不存在）')
            continue
        print(f'=== {topic}（{len(copies)} 份）===')
        for src, dst in copies:
            print(f'  复制: {dst}')
        total += len(copies)

    print(f'\n共复制 {total} 份')
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python3 tests/test_collect_topic_summaries.py`
Expected: 6 个 PASS，输出 `6/6 通过`

- [ ] **Step 5: 提交**

```bash
git add src/pdf_ocr_tool/scripts/collect_topic_summaries.py tests/test_collect_topic_summaries.py
git commit -m "feat(topic-summaries): 新增专题核心论点收集脚本

- 原因：专题核心论点分散在 topic_summaries/{专题}/核心论点/，用户需要一次性复制研究
- 改动：新增 collect_topic_summaries.py，按 --topic 指定或扫描全部专题，复制到 output/daily/{专题}核心论点/（扁平+保留日期后缀）；配套单测 6 例
- 影响：仅新增文件，不影响主流程；测试 6/6 通过"
```

---

### Task 2: 用真实数据验证（存储 + 服务器）

**Files:**
- Run: `src/pdf_ocr_tool/scripts/collect_topic_summaries.py`

- [ ] **Step 1: 运行脚本收集存储与服务器**

Run: `python3 src/pdf_ocr_tool/scripts/collect_topic_summaries.py --topic 存储 --topic 服务器`
Expected:
- `=== 存储（46 份）===` 且逐个列出复制目标
- `=== 服务器（61 份）===` 且逐个列出复制目标
- 结尾 `共复制 107 份`

- [ ] **Step 2: 验证目标目录内容**

Run: `ls output/daily/存储核心论点/ | wc -l` 和 `ls output/daily/服务器核心论点/ | wc -l`
Expected: `46` 和 `61`

- [ ] **Step 3: 验证文件名与源一致（抽查 2 份）**

Run: `ls output/daily/存储核心论点/ | tail -3` 与 `ls output/topic_summaries/存储/核心论点/ | tail -3`
Expected: 两组末尾文件名一致（如均含 `存储_核心论点汇总_2026110707.md`）

- [ ] **Step 4: 幂等验证（重复运行）**

Run: `python3 src/pdf_ocr_tool/scripts/collect_topic_summaries.py --topic 存储`
Expected: `=== 存储（46 份）===`，`共复制 46 份`，无报错

- [ ] **Step 5: 提交（如脚本有迭代改动）**

仅当 Step 1-4 发现问题并改动脚本/测试时执行：
```bash
git add -A
git commit -m "fix(topic-summaries): 真实数据验证后的修正"
```
若全部通过且无改动，跳过此步。

---

### Task 3: 更新项目规则文档

**Files:**
- Modify: `.trae/rules/project_rules.md`

- [ ] **Step 1: 在"提取其他专题的触发关键字"表格后追加说明**

在 `.trae/rules/project_rules.md` 的"**备注**"段落前插入新段落（定位到"## 🔍 提取其他专题的触发关键字"小节末尾的"**备注**："行之前）：

```markdown
**专题核心论点收集（手动运行）**：

* 把指定专题的核心论点汇总复制到 `output/daily/{专题}核心论点/`（与 `重点汇总`、`一句话总结` 平级的扁平目录，便于一次性复制研究）
* 运行：`python3 src/pdf_ocr_tool/scripts/collect_topic_summaries.py --topic 存储 --topic 服务器`
* 省略 `--topic` 时扫描 `output/topic_summaries/` 下全部专题；新增专题无需改脚本
* 已收集：存储 46 份、服务器 61 份（2026-11-07 首次运行）
```

- [ ] **Step 2: 提交**

```bash
git add .trae/rules/project_rules.md
git commit -m "docs(topic-summaries): 项目规则补充专题核心论点收集说明"
```

---

## Self-Review

- **Spec coverage**: Spec 要求全部覆盖 —— 独立脚本（Task 1）、`--topic` 可多次 + 省略扫描全部（Task 1 main）、扁平目录 `output/daily/{专题}核心论点/`（Task 1 collect_topic）、幂等覆盖（Task 1 test_idempotent + Task 2 Step 4）、边界处理（Task 1 空专题/无核心论点目录/无匹配文件 三个测试）。无遗漏。
- **Placeholder scan**: 无 TBD/TODO；每个步骤含完整代码或确切命令。Task 2 Step 5 / Task 3 Step 2 的 commit 为条件执行（明确注明仅在改动时执行），非占位符。
- **Type consistency**: `collect_topic(topic, project_root) -> list[(src,dst)]` 在测试与实现中签名一致；`_project_root`、`_list_topics`、`main` 命名在实现内一致；`sys.exit(main())` 返回 0/1 与测试无关（测试直接 import collect_topic）。`make_env` 中 `核心论点` 目录路径与实现一致。
