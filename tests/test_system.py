#!/usr/bin/env python3
"""
系统功能测试脚本 - 验证每日500个PDF处理系统的核心功能
"""

import os
import sys
import tempfile
import shutil
import subprocess
import time


def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, str(e), ""


def test_dependencies():
    """检查系统依赖"""
    print("=== 检查依赖 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python版本必须至少3.8")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}")
    
    # 检查pip是否可用
    if run_command("pip --version")[0] != 0:
        print("❌ pip不可用")
        return False
    
    print("✅ pip可用")
    
    return True


def test_imports():
    """测试模块导入"""
    print("\n=== 测试模块导入 ===")
    
    try:
        import pdf_processing_pipeline
        print("✅ pdf_processing_pipeline模块可用")
    except Exception as e:
        print(f"❌ 导入pdf_processing_pipeline失败: {e}")
        return False
    
    try:
        import ai_content_summarizer
        print("✅ ai_content_summarizer模块可用")
    except Exception as e:
        print(f"❌ 导入ai_content_summarizer失败: {e}")
        return False
    
    try:
        from liteparse import LiteParse
        print("✅ liteparse模块可用")
    except Exception as e:
        print(f"❌ 导入liteparse失败: {e}")
        return False
    
    return True


def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 测试目录创建
        test_dir = os.path.join(temp_dir, "test_output")
        os.makedirs(test_dir, exist_ok=True)
        
        if os.path.exists(test_dir):
            print("✅ 目录创建成功")
        else:
            print("❌ 目录创建失败")
            return False
        
        # 测试文件写入
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("测试内容")
        
        if os.path.exists(test_file):
            print("✅ 文件写入成功")
        else:
            print("❌ 文件写入失败")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ 文件操作测试失败: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir)


def test_command_line():
    """测试命令行接口"""
    print("\n=== 测试命令行接口 ===")
    
    try:
        # 测试帮助信息
        result = run_command("python daily_500_pdf_processor.py --help")
        
        if result[0] == 0:
            print("✅ 命令行接口可用")
            return True
        else:
            print(f"❌ 命令行接口测试失败: {result[1]}")
            return False
    
    except Exception as e:
        print(f"❌ 命令行接口测试失败: {e}")
        return False


def test_config():
    """检查配置文件"""
    print("\n=== 检查配置文件 ===")
    
    required_files = [
        'daily_500_pdf_processor.py',
        'pdf_processing_pipeline.py',
        'ai_content_summarizer.py',
        'requirements.txt',
        'package.json'
    ]
    
    all_files_found = True
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name} 存在")
        else:
            print(f"❌ {file_name} 不存在")
            all_files_found = False
    
    return all_files_found


def create_test_pdf():
    """创建一个简单的测试PDF（使用LaTeX）"""
    temp_dir = tempfile.mkdtemp()
    
    # 创建简单的TeX文件
    tex_content = """
\\documentclass{article}
\\usepackage[UTF8]{ctex}
\\begin{document}
\\title{测试文档}
\\author{系统测试}
\\date{}
\\maketitle

这是一个用于系统功能测试的简单文档。

\\section{测试章节}

内容包括：
- 测试文字
- 列表项
- 公式 $E=mc^2$

\\end{document}
    """.strip()
    
    tex_file = os.path.join(temp_dir, "test.tex")
    
    with open(tex_file, 'w') as f:
        f.write(tex_content)
    
    # 编译为PDF
    try:
        run_command(f"cd {temp_dir} && pdflatex -quiet test.tex 2>&1 >/dev/null")
        
        pdf_file = os.path.join(temp_dir, "test.pdf")
        if os.path.exists(pdf_file):
            return temp_dir, pdf_file
        
    except Exception as e:
        print(f"警告: 无法创建测试PDF: {e}")
    
    return None, None


def run_system_tests():
    """运行完整的系统测试"""
    print("=== 每日500个PDF处理系统测试 ===")
    
    start_time = time.time()
    
    test_results = []
    
    tests = [
        ("依赖检查", test_dependencies),
        ("模块导入", test_imports),
        ("文件操作", test_file_operations),
        ("命令行接口", test_command_line),
        ("配置文件", test_config)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 失败: {e}")
            test_results.append((test_name, False))
    
    # 统计结果
    passed = sum(1 for test in test_results if test[1])
    total = len(test_results)
    
    print(f"\n=== 测试完成 ===\n")
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("✅ 系统功能基本正常")
        
        # 建议下一步操作
        print("\n=== 下一步操作建议 ===")
        print("1. 准备您的PDF文件")
        print("2. 创建输入和输出目录")
        print("3. 运行: python daily_500_pdf_processor.py /path/to/input /path/to/output")
        print("4. 查看 reports/ 目录下的报告")
    else:
        print(f"❌ 有 {total - passed} 个测试失败，请检查")
    
    print(f"\n测试时间: {time.time() - start_time:.2f} 秒")
    
    return passed == total


if __name__ == "__main__":
    run_system_tests()
