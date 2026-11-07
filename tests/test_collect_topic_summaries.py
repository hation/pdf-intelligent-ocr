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
