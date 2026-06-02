#!/usr/bin/env python3
"""
磁盘空间消耗测试脚本 - 评估PDF处理系统的磁盘使用量
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time


def get_dir_size(dir_path):
    """获取目录大小"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            total += os.path.getsize(os.path.join(dirpath, filename))
    return total


def test_disk_usage():
    """测试不同策略的磁盘空间消耗"""
    temp_dir = tempfile.mkdtemp(prefix="pdf_processing_disk_usage_")
    
    try:
        # 测试Tesseract OCR
        print("=== 测试Tesseract OCR策略 ===")
        start_time = time.time()
        cmd_tesseract = f"python3 direct_tesseract_ocr.py \"files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf\" \"{os.path.join(temp_dir, 'tesseract')}\""
        
        result = subprocess.run(cmd_tesseract, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            tesseract_size = get_dir_size(os.path.join(temp_dir, 'tesseract'))
            tesseract_time = time.time() - start_time
            print(f"✅ 成功完成")
            print(f"⏱️  处理时间: {tesseract_time:.2f}秒")
            print(f"💾 输出大小: {tesseract_size / (1024 * 1024):.2f}MB")
        else:
            print("❌ 处理失败")
        
        # 测试LiteParse OCR
        print("\n=== 测试LiteParse OCR策略 ===")
        start_time = time.time()
        cmd_liteparse = f"python3 parse_with_liteparse_ocr.py \"files\" \"{os.path.join(temp_dir, 'liteparse')}\""
        
        result = subprocess.run(cmd_liteparse, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            liteparse_size = get_dir_size(os.path.join(temp_dir, 'liteparse'))
            liteparse_time = time.time() - start_time
            print(f"✅ 成功完成")
            print(f"⏱️  处理时间: {liteparse_time:.2f}秒")
            print(f"💾 输出大小: {liteparse_size / (1024 * 1024):.2f}MB")
        else:
            print("❌ 处理失败")
        
        return tesseract_size, liteparse_size
        
    finally:
        shutil.rmtree(temp_dir)


def estimate_daily_disk_usage():
    """估计每日处理500个文件的磁盘使用量"""
    print("\n=== 估计每日处理500个文件 ===")
    
    # 获取文件大小信息
    tesseract_size, liteparse_size = test_disk_usage()
    
    print("\n📊 磁盘使用估计:")
    print(f"💾 Tesseract策略: 单个文件约{tesseract_size / (1024 * 1024):.2f}MB, 500个文件约{(tesseract_size * 500) / (1024 * 1024):.1f}GB")
    print(f"💾 LiteParse策略: 单个文件约{liteparse_size / (1024 * 1024):.2f}MB, 500个文件约{(liteparse_size * 500) / (1024 * 1024):.1f}GB")
    
    # 计算差异
    if tesseract_size > liteparse_size:
        print(f"🔍 LiteParse策略比Tesseract策略节省约{100 - (liteparse_size / tesseract_size) * 100:.1f}%的磁盘空间")
    elif tesseract_size < liteparse_size:
        print(f"🔍 Tesseract策略比LiteParse策略节省约{100 - (tesseract_size / liteparse_size) * 100:.1f}%的磁盘空间")
    else:
        print("🔍 两种策略的磁盘使用量相似")


def main():
    estimate_daily_disk_usage()
    return 0


if __name__ == "__main__":
    main()
