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
