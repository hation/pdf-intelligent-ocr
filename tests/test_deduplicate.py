#!/usr/bin/env python3
"""导入去重（deduplicate.py）单元测试。

覆盖场景：
1. 归档同名回移（files/ 与归档同名 → 移回归档跳过）
2. md5 一致副本删除（xxx (1).ext 与原始一致 → 删除）
3. md5 不同副本保留（内容不同 → 保留）
4. 无原始副本保留（只有 (1) 副本 → 保留）
5. 多个副本全部删除 / 保留
6. 大小写扩展名（.PDF vs .pdf 视为同一文档）
7. 空目录 / 无归档目录 / 归档目录不存在
8. --no-delete 模式（would_delete 报告不删除）
9. 删除失败时保留（只读文件）

运行：python3 tests/test_deduplicate.py
"""

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_ocr_tool.scripts.deduplicate import deduplicate, find_archive_dirs, _md5


class Ctx:
    """临时测试环境：input 目录 + 可选归档目录"""

    def __init__(self, archive_names=()):
        self.root = tempfile.mkdtemp(prefix='dedup_ut_')
        self.input_dir = os.path.join(self.root, 'files')
        self.archive_dirs = []
        os.makedirs(self.input_dir)
        for name in archive_names:
            d = os.path.join(self.root, name)
            os.makedirs(d)
            self.archive_dirs.append(d)

    def write(self, path, content):
        with open(os.path.join(self.input_dir, path), 'w') as f:
            f.write(content)

    def archive(self, dirname, fname, content):
        with open(os.path.join(self.root, dirname, fname), 'w') as f:
            f.write(content)

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


# ---------- 场景1：归档同名回移 ----------

def test_archive_same_name_moved_back():
    c = Ctx(archive_names=['invest_files_processed'])
    c.write('dup.pdf', 'content-a')
    c.archive('invest_files_processed', 'dup.pdf', 'content-a')  # 归档已有同名
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 0, r
    assert r['moved_to_archive'] == [('dup.pdf', 'invest_files_processed')], r
    assert not os.path.exists(os.path.join(c.input_dir, 'dup.pdf')), '原文件应移走'
    assert os.path.exists(os.path.join(c.archive_dirs[0], 'dup.pdf')), '归档应回移成功'
    print('✅ 场景1 归档同名回移')
    c.cleanup()


# ---------- 场景2：md5 一致副本删除 ----------

def test_identical_copy_deleted():
    c = Ctx()
    c.write('doc.pdf', 'same-content')
    c.write('doc (1).pdf', 'same-content')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 1, r
    assert r['deleted_copies'] == ['doc (1).pdf'], r
    assert not os.path.exists(os.path.join(c.input_dir, 'doc (1).pdf')), '副本应删除'
    assert os.path.exists(os.path.join(c.input_dir, 'doc.pdf')), '原始应保留'
    print('✅ 场景2 md5 一致副本删除')
    c.cleanup()


# ---------- 场景3：md5 不同副本保留 ----------

def test_different_copy_kept():
    c = Ctx()
    c.write('doc.pdf', 'original')
    c.write('doc (1).pdf', 'DIFFERENT-CONTENT')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 2, r  # 两份都算新文档
    assert r['kept_copies'] == ['doc (1).pdf'], r
    assert os.path.exists(os.path.join(c.input_dir, 'doc (1).pdf')), '不同内容副本应保留'
    print('✅ 场景3 md5 不同副本保留')
    c.cleanup()


# ---------- 场景4：无原始副本保留 ----------

def test_copy_without_original_kept():
    c = Ctx()
    c.write('noorig (1).pdf', 'only-copy')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 1, r
    assert r['kept_copies'] == ['noorig (1).pdf'], r
    assert os.path.exists(os.path.join(c.input_dir, 'noorig (1).pdf')), '无原始副本应保留'
    print('✅ 场景4 无原始副本保留')
    c.cleanup()


# ---------- 场景5：多个副本 ----------

def test_multiple_copies():
    c = Ctx()
    c.write('doc.pdf', 'same')
    c.write('doc (1).pdf', 'same')
    c.write('doc (2).pdf', 'same')
    c.write('other.pdf', 'other-1')
    c.write('other (1).pdf', 'other-1')
    c.write('other (2).pdf', 'DIFFERENT')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert set(r['deleted_copies']) == {'doc (1).pdf', 'doc (2).pdf', 'other (1).pdf'}, r
    assert r['kept_copies'] == ['other (2).pdf'], r
    assert r['new_count'] == 3, r  # doc.pdf + other.pdf + other (2).pdf
    print('✅ 场景5 多个副本')
    c.cleanup()


# ---------- 场景6：大小写扩展名 ----------

def test_case_insensitive_ext():
    c = Ctx()
    c.write('doc.PDF', 'same')
    c.write('doc (1).pdf', 'same')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['deleted_copies'] == ['doc (1).pdf'], r
    print('✅ 场景6 大小写扩展名')
    c.cleanup()


# ---------- 场景7：空目录 / 无归档 ----------

def test_empty_dir_and_no_archive():
    c = Ctx()
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 0 and r['deleted_copies'] == [] and r['moved_to_archive'] == [], r
    # 归档目录不存在时也不报错
    r2 = deduplicate(c.input_dir, [os.path.join(c.root, 'nonexistent_processed')], delete_copies=True)
    assert r2['new_count'] == 0, r2
    print('✅ 场景7 空目录 / 无归档目录')
    c.cleanup()


# ---------- 场景8：--no-delete（would_delete 报告） ----------

def test_no_delete_mode():
    c = Ctx()
    c.write('doc.pdf', 'same')
    c.write('doc (1).pdf', 'same')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=False)
    assert r['would_delete'] == ['doc (1).pdf'], r
    assert r['deleted_copies'] == [], r
    assert os.path.exists(os.path.join(c.input_dir, 'doc (1).pdf')), '只读模式不应删除'
    print('✅ 场景8 --no-delete 只读模式')
    c.cleanup()


# ---------- 场景9：删除失败时保留（模拟 os.remove 抛 OSError） ----------

def test_delete_failure_keeps_copy():
    import unittest.mock as mock
    c = Ctx()
    c.write('doc.pdf', 'same')
    c.write('doc (1).pdf', 'same')
    with mock.patch('os.remove', side_effect=OSError('permission denied')):
        r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
        assert r['deleted_copies'] == [], r
        assert r['kept_copies'] == ['doc (1).pdf'], r
    assert os.path.exists(os.path.join(c.input_dir, 'doc (1).pdf')), '删除失败副本应保留'
    print('✅ 场景9 删除失败保留')
    c.cleanup()


# ---------- 场景10：归档同名 + 副本混合 ----------

def test_mixed_scenarios():
    c = Ctx(archive_names=['media_files_processed'])
    c.write('a.pdf', 'a')                       # 新文档
    c.write('b.pdf', 'b')                       # 新文档
    c.write('b (1).pdf', 'b')                   # 副本 → 删除
    c.write('c.pdf', 'c')                       # 归档同名 → 回移
    c.archive('media_files_processed', 'c.pdf', 'c')
    r = deduplicate(c.input_dir, c.archive_dirs, delete_copies=True)
    assert r['new_count'] == 2, r               # a.pdf + b.pdf
    assert r['deleted_copies'] == ['b (1).pdf'], r
    assert r['moved_to_archive'] == [('c.pdf', 'media_files_processed')], r
    print('✅ 场景10 混合场景')
    c.cleanup()


# ---------- find_archive_dirs 自动发现 ----------

def test_find_archive_dirs_autodiscovery():
    c = Ctx(archive_names=['invest_files_processed', 'media_files_processed',
                           'other_files_processed', 'problematic_pdfs'])
    os.makedirs(os.path.join(c.root, 'unrelated_dir'))  # 不应匹配
    dirs = find_archive_dirs(c.root)
    names = {os.path.basename(d) for d in dirs}
    assert names == {'invest_files_processed', 'media_files_processed',
                     'other_files_processed', 'problematic_pdfs'}, names
    print('✅ find_archive_dirs 自动发现')
    c.cleanup()


# ---------- _md5 流式计算 ----------

def test_md5_streaming():
    c = Ctx()
    c.write('f.pdf', 'hello-world' * 1000)
    expected = _md5(os.path.join(c.input_dir, 'f.pdf'))
    import hashlib
    with open(os.path.join(c.input_dir, 'f.pdf'), 'rb') as f:
        assert hashlib.md5(f.read()).hexdigest() == expected, 'md5 应一致'
    print('✅ _md5 流式计算')
    c.cleanup()


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items()) if k.startswith('test_')]
    print(f"运行 {len(tests)} 个测试...\n")
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"❌ {t.__name__} 失败: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ {t.__name__} 异常: {e!r}")
            sys.exit(1)
    print("\n🎉 全部测试通过")
