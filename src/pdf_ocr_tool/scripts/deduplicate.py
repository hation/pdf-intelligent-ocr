#!/usr/bin/env python3
"""导入文档去重：归档同名回移 + (N)副本删除。

在主流程 classify_and_dispatch 之后自动调用，每次处理新文档前
消除与已处理文档的重复，避免重复解析与重复 AI 总结。

执行步骤：
1. 归档同名：files/ 中与任一归档目录同名的文件 → 移回归档（跳过处理）
2. (N) 副本：files/ 内 "xxx (1).ext" 存在原始 "xxx.ext" 且 md5 一致 → 删除副本
3. 输出摘要：新文档数 / 移回归档 / 删副本 / 保留副本

安全边界：
- 仅删除 md5 完全一致的副本，无破坏风险
- 归档移动为覆盖已有同名文件，非破坏性
"""

import argparse
import hashlib
import os
import re
import sys

# 文档扩展名（与主流程保持一致）
DOC_EXTS = ('.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx')

# 副本命名模式：xxx (1).pdf / xxx (2).docx ...
COPY_RE = re.compile(r'^(?P<base>.+?) \((?P<num>\d+)\)(?P<ext>\.[^.]+)$')


def _project_root():
    """定位项目根目录（脚本位于 <root>/src/pdf_ocr_tool/scripts/）"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _is_doc(fname):
    return fname.lower().endswith(DOC_EXTS)


def _md5(path, chunk_size=1024 * 1024):
    """计算文件 md5（流式，避免大文件占用内存）"""
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()


def find_archive_dirs(project_root):
    """自动发现归档目录：*_processed/ 与 problematic_pdfs/"""
    dirs = []
    for name in os.listdir(project_root):
        p = os.path.join(project_root, name)
        if os.path.isdir(p) and (name.endswith('_processed') or name == 'problematic_pdfs'):
            dirs.append(p)
    return dirs


def deduplicate(input_dir, archive_dirs=None, delete_copies=True):
    """执行去重，返回摘要 dict。

    Args:
        input_dir: 用户文档目录（如 files/）
        archive_dirs: 归档目录列表；None 时自动发现
        delete_copies: 是否删除 md5 一致的副本（False 时仅报告不动手）

    Returns:
        dict: {
            'new_count': 待处理新文档数,
            'moved_to_archive': [(文件名, 归档目录名), ...],
            'deleted_copies': [副本文件名, ...],
            'would_delete': [副本文件名, ...],  # --no-delete 模式下 md5 一致、本应删除的副本
            'kept_copies': [副本文件名, ...],  # 无原始或 md5 不同，保留处理
        }
    """
    if archive_dirs is None:
        archive_dirs = find_archive_dirs(_project_root())

    docs = [f for f in os.listdir(input_dir)
            if _is_doc(f) and os.path.isfile(os.path.join(input_dir, f))]

    # 归档目录文件名集合（同名即视为已处理过）
    archived_names = set()
    for d in archive_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if os.path.isfile(os.path.join(d, f)):
                archived_names.add(f)

    result = {
        'new_count': 0,
        'moved_to_archive': [],
        'deleted_copies': [],
        'would_delete': [],
        'kept_copies': [],
    }

    # 1) 归档同名 → 移回归档
    remaining = []
    for fname in docs:
        if fname in archived_names:
            dest_dir = next(d for d in archive_dirs
                            if os.path.isfile(os.path.join(d, fname)))
            src = os.path.join(input_dir, fname)
            try:
                os.replace(src, os.path.join(dest_dir, fname))
                result['moved_to_archive'].append((fname, os.path.basename(dest_dir)))
            except OSError:
                remaining.append(fname)  # 移动失败则保留，不阻塞流程
        else:
            remaining.append(fname)

    # 2) (N) 副本检测
    by_base = {}
    for fname in remaining:
        m = COPY_RE.match(fname)
        if m:
            by_base.setdefault((m.group('base'), m.group('ext').lower()), []).append(fname)
        else:
            by_base.setdefault((fname.rsplit('.', 1)[0], '.' + fname.rsplit('.', 1)[-1].lower()), []).append(fname)

    for (base, ext), group in by_base.items():
        originals = [f for f in group if not COPY_RE.match(f)]
        copies = [f for f in group if COPY_RE.match(f)]
        if not copies:
            continue
        # 有原始才比对；无原始一律保留（可能是唯一文件）
        if originals:
            orig_hash = _md5(os.path.join(input_dir, originals[0]))
            for copy_name in copies:
                if orig_hash and _md5(os.path.join(input_dir, copy_name)) == orig_hash:
                    if delete_copies:
                        try:
                            os.remove(os.path.join(input_dir, copy_name))
                            result['deleted_copies'].append(copy_name)
                        except OSError:
                            result['kept_copies'].append(copy_name)
                    else:
                        result['would_delete'].append(copy_name)
                else:
                    result['kept_copies'].append(copy_name)
        else:
            result['kept_copies'].extend(copies)

    # 3) 剩余文件即为新文档（含保留副本）
    remaining = [f for f in remaining if f not in result['deleted_copies']]
    result['new_count'] = len(remaining)
    return result


def main():
    parser = argparse.ArgumentParser(description="导入文档去重：归档同名回移 + 副本删除")
    parser.add_argument('input_dir', nargs='?', default='files', help='文档目录（默认 files/）')
    parser.add_argument('--no-delete', action='store_true', help='只报告副本，不删除')
    args = parser.parse_args()

    project_root = _project_root()
    input_dir = args.input_dir if os.path.isabs(args.input_dir) else os.path.join(project_root, args.input_dir)
    archive_dirs = find_archive_dirs(project_root)

    r = deduplicate(input_dir, archive_dirs, delete_copies=not args.no_delete)

    print(f"\n===== 文档去重结果（{input_dir}）=====")
    print(f"  待处理新文档: {r['new_count']} 份")
    if r['moved_to_archive']:
        print(f"  归档同名回移: {len(r['moved_to_archive'])} 份")
        for fname, dest in r['moved_to_archive']:
            print(f"    - {fname} -> {dest}/")
    if r['deleted_copies']:
        print(f"  删除重复副本: {len(r['deleted_copies'])} 份")
        for fname in r['deleted_copies']:
            print(f"    - {fname}")
    if r['would_delete']:
        print(f"  [只读]待删除副本(未执行): {len(r['would_delete'])} 份")
        for fname in r['would_delete']:
            print(f"    - {fname}")
    if r['kept_copies']:
        print(f"  保留副本: {len(r['kept_copies'])} 份")
        for fname in r['kept_copies']:
            print(f"    - {fname}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
