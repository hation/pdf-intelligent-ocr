#!/usr/bin/env python3
"""
从资源消耗报告中提取关键信息
"""

import os
import re


def extract_report_summary():
    report_path = os.path.join(os.path.dirname(__file__), "RESOURCE_CONSUMPTION_REPORT.md")
    
    if not os.path.exists(report_path):
        print("资源消耗报告不存在")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 提取关键点
    summary = {}
    
    # 提取500个PDF文件的处理时间（综合策略）
    time_pattern = r"综合策略：.*?总处理时间估计：.*?≈ ([\d\.]+小时)"
    time_match = re.search(time_pattern, report_content, re.DOTALL)
    if time_match:
        summary["总处理时间"] = time_match.group(1)
    
    # 提取内存消耗
    memory_pattern = r"综合策略：.*?最大([\d\.]+ GB)"
    memory_match = re.search(memory_pattern, report_content, re.DOTALL)
    if memory_match:
        summary["峰值内存"] = memory_match.group(1)
    
    # 提取磁盘空间
    disk_pattern = r"综合策略：.*?估计约([\d\.]+ MB)"
    disk_match = re.search(disk_pattern, report_content, re.DOTALL)
    if disk_match:
        summary["磁盘空间"] = disk_match.group(1)
    
    # 提取CPU使用率
    cpu_pattern = r"综合策略：.*?平均约([\d\.]+%)"
    cpu_match = re.search(cpu_pattern, report_content, re.DOTALL)
    if cpu_match:
        summary["平均CPU使用率"] = cpu_match.group(1)
    
    return summary


def main():
    summary = extract_report_summary()
    if summary:
        print("每日500个PDF处理系统资源消耗总结：")
        print(f"1. 总处理时间：{summary['总处理时间']}")
        print(f"2. 峰值内存需求：{summary['峰值内存']}")
        print(f"3. 磁盘空间需求：{summary['磁盘空间']}")
        print(f"4. 平均CPU使用率：{summary['平均CPU使用率']}")
    else:
        print("无法提取报告信息")


if __name__ == "__main__":
    main()
