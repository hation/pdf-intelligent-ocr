#!/usr/bin/env python3
"""
资源消耗测试脚本 - 测试PDF处理系统的CPU、内存和磁盘消耗
"""

import os
import sys
import time
import psutil
import subprocess
import tempfile
import shutil


def run_and_monitor(cmd, timeout=60):
    """运行命令并监控资源消耗"""
    # 开始监控
    start_time = time.time()
    
    # 创建过程
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # 资源使用数据
    cpu_usage = []
    memory_usage = []
    
    # 监控过程
    try:
        while process.poll() is None and (time.time() - start_time) < timeout:
            # 获取过程资源使用情况
            try:
                proc = psutil.Process(process.pid)
                # 获取CPU使用率
                cpu_percent = proc.cpu_percent()
                cpu_usage.append(cpu_percent)
                # 获取内存使用情况
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)
                memory_usage.append(memory_mb)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
            time.sleep(0.1)
    
        # 等待过程完成或超时
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            return False, [], [], time.time() - start_time
    
    except Exception as e:
        print(f"监控过程出错: {e}")
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
        return False, [], [], time.time() - start_time
    
    return True, cpu_usage, memory_usage, time.time() - start_time


def test_tesseract_ocr():
    """测试Tesseract OCR处理的资源消耗"""
    print("=== 测试Tesseract OCR处理 ===")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="pdf_processing_test_")
    
    try:
        # 运行Tesseract OCR
        cmd = f"python3 direct_tesseract_ocr.py \"files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf\" \"{temp_dir}\""
        
        success, cpu_usage, memory_usage, total_time = run_and_monitor(cmd)
        
        if not success:
            print("❌ 处理失败")
            return
        
        print(f"✅ 成功处理")
        print(f"⏱️  总时间: {total_time:.2f}秒")
        
        if cpu_usage:
            max_cpu = max(cpu_usage)
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            print(f"💻 CPU使用率: 平均{avg_cpu:.1f}%, 最大{max_cpu:.1f}%")
        
        if memory_usage:
            max_memory = max(memory_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            print(f"💾 内存使用: 平均{avg_memory:.1f}MB, 最大{max_memory:.1f}MB")
        
        # 检查输出文件大小
        output_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith('.md')]
        if output_files:
            file_size = os.path.getsize(output_files[0]) / (1024 * 1024)
            print(f"📄 输出文件: {file_size:.2f}MB")
        
    finally:
        shutil.rmtree(temp_dir)
    
    return total_time, avg_cpu, max_cpu, avg_memory, max_memory


def test_ai_summarization():
    """测试AI内容分析的资源消耗"""
    print("\n=== 测试AI内容分析 ===")
    
    temp_dir = tempfile.mkdtemp(prefix="pdf_processing_test_")
    
    try:
        # 先运行Tesseract OCR
        cmd_ocr = f"python3 direct_tesseract_ocr.py \"files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf\" \"{temp_dir}\""
        subprocess.run(cmd_ocr, shell=True, capture_output=True, text=True)
        
        # 运行AI内容分析
        cmd_ai = f"python3 ai_content_summarizer.py \"{temp_dir}\" -o \"{temp_dir}/analysis.md\""
        
        success, cpu_usage, memory_usage, total_time = run_and_monitor(cmd_ai)
        
        if not success:
            print("❌ 分析失败")
            return
        
        print(f"✅ 成功分析")
        print(f"⏱️  总时间: {total_time:.2f}秒")
        
        if cpu_usage:
            max_cpu = max(cpu_usage)
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            print(f"💻 CPU使用率: 平均{avg_cpu:.1f}%, 最大{max_cpu:.1f}%")
        
        if memory_usage:
            max_memory = max(memory_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            print(f"💾 内存使用: 平均{avg_memory:.1f}MB, 最大{max_memory:.1f}MB")
        
    finally:
        shutil.rmtree(temp_dir)
    
    return total_time, avg_cpu, max_cpu, avg_memory, max_memory


def test_full_process():
    """测试完整处理流程的资源消耗"""
    print("\n=== 测试完整处理流程 ===")
    
    temp_dir = tempfile.mkdtemp(prefix="pdf_processing_test_")
    
    try:
        cmd = f"python3 daily_500_pdf_processor.py \"files\" \"{temp_dir}\" --workers 2 --strategy tesseract --no-ai"
        
        success, cpu_usage, memory_usage, total_time = run_and_monitor(cmd, timeout=300)
        
        if not success:
            print("❌ 处理失败")
            return
        
        print(f"✅ 成功处理")
        print(f"⏱️  总时间: {total_time:.2f}秒")
        
        if cpu_usage:
            max_cpu = max(cpu_usage)
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            print(f"💻 CPU使用率: 平均{avg_cpu:.1f}%, 最大{max_cpu:.1f}%")
        
        if memory_usage:
            max_memory = max(memory_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            print(f"💾 内存使用: 平均{avg_memory:.1f}MB, 最大{max_memory:.1f}MB")
        
        # 计算磁盘使用
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(temp_dir):
            for filename in filenames:
                total_size += os.path.getsize(os.path.join(dirpath, filename))
        
        print(f"💾 磁盘使用: {total_size / (1024 * 1024):.2f}MB")
        
    finally:
        shutil.rmtree(temp_dir)
    
    return total_time, avg_cpu, max_cpu, avg_memory, max_memory


def main():
    # 测试单个文件处理
    tesseract_time, tesseract_avg_cpu, tesseract_max_cpu, tesseract_avg_mem, tesseract_max_mem = test_tesseract_ocr()
    
    # 测试AI分析
    ai_time, ai_avg_cpu, ai_max_cpu, ai_avg_mem, ai_max_mem = test_ai_summarization()
    
    print("\n=== 资源消耗总结 ===")
    print(f"⏱️  单文件处理时间: {tesseract_time:.2f}秒")
    print(f"⏱️  AI分析时间: {ai_time:.2f}秒")
    print(f"💻 CPU: OCR平均{tesseract_avg_cpu:.1f}%, 最大{tesseract_max_cpu:.1f}%; AI平均{ai_avg_cpu:.1f}%, 最大{ai_max_cpu:.1f}%")
    print(f"💾 内存: OCR平均{tesseract_avg_mem:.1f}MB, 最大{tesseract_max_mem:.1f}MB; AI平均{ai_avg_mem:.1f}MB, 最大{ai_max_mem:.1f}MB")
    
    # 计算每日处理500个文件的估计资源消耗
    print("\n=== 每日处理500个文件估计 ===")
    total_time = (tesseract_time + ai_time) * 500 / 3600
    total_memory = max(tesseract_max_mem, ai_max_mem)
    print(f"⏱️  总处理时间: {total_time:.1f}小时")
    print(f"💾 峰值内存需求: {total_memory:.1f}MB")
    
    return 0


if __name__ == "__main__":
    main()
