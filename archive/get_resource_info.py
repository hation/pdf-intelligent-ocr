#!/usr/bin/env python3
"""
直接从资源消耗报告中获取关键信息的脚本
"""

import os

def get_resource_info():
    report_path = os.path.join(os.path.dirname(__file__), "RESOURCE_CONSUMPTION_REPORT.md")
    
    if not os.path.exists(report_path):
        print("资源消耗报告不存在")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    lines = report_content.split('\n')
    
    # 初始化结果字典
    info = {
        'tesseract': {
            'time': '',
            'memory': '',
            'cpu': '',
            'disk': ''
        },
        'liteparse': {
            'time': '',
            'memory': '',
            'cpu': '',
            'disk': ''
        },
        'combined': {
            'time': '',
            'memory': '',
            'cpu': '',
            'disk': ''
        }
    }
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 查找500个PDF文件的处理时间部分
        if "500个PDF文件总体消耗评估" in line:
            i += 1
            while i < len(lines) and lines[i].strip() != "## 最佳配置建议":
                l = lines[i].strip()
                
                if "最佳情况（全部使用Tesseract策略）" in l:
                    # 提取Tesseract策略信息
                    for j in range(i+1, len(lines)):
                        if "最坏情况（全部使用LiteParse策略）" in lines[j].strip():
                            break
                        
                        j_line = lines[j].strip()
                        if "总处理时间" in j_line and "≈" in j_line and "分钟" in j_line:
                            info['tesseract']['time'] = j_line.split("≈")[-1].strip()
                        elif "峰值内存需求" in j_line and "GB" in j_line:
                            info['tesseract']['memory'] = j_line.split("：")[-1].strip()
                        elif "磁盘空间" in j_line and "GB" in j_line:
                            info['tesseract']['disk'] = j_line.split("：")[-1].strip()
                        elif "平均CPU使用率" in j_line and "%" in j_line:
                            info['tesseract']['cpu'] = j_line.split("：")[-1].strip()
                
                elif "最坏情况（全部使用LiteParse策略）" in l:
                    # 提取LiteParse策略信息
                    for j in range(i+1, len(lines)):
                        if "综合策略（自动选择）" in lines[j].strip():
                            break
                        
                        j_line = lines[j].strip()
                        if "总处理时间" in j_line and "≈" in j_line and "小时" in j_line:
                            info['liteparse']['time'] = j_line.split("≈")[-1].strip()
                        elif "峰值内存需求" in j_line and "GB" in j_line:
                            info['liteparse']['memory'] = j_line.split("：")[-1].strip()
                        elif "磁盘空间" in j_line and "GB" in j_line:
                            info['liteparse']['disk'] = j_line.split("：")[-1].strip()
                        elif "平均CPU使用率" in j_line and "%" in j_line:
                            info['liteparse']['cpu'] = j_line.split("：")[-1].strip()
                
                elif "综合策略（自动选择）" in l:
                    # 提取综合策略信息
                    for j in range(i+1, len(lines)):
                        if "## 最佳配置建议" in lines[j].strip():
                            break
                        
                        j_line = lines[j].strip()
                        if "总处理时间" in j_line and "≈" in j_line and "小时" in j_line:
                            info['combined']['time'] = j_line.split("≈")[-1].strip()
                        elif "峰值内存需求" in j_line and "GB" in j_line:
                            info['combined']['memory'] = j_line.split("：")[-1].strip()
                        elif "磁盘空间" in j_line and "GB" in j_line:
                            info['combined']['disk'] = j_line.split("：")[-1].strip()
                        elif "平均CPU使用率" in j_line and "%" in j_line:
                            info['combined']['cpu'] = j_line.split("：")[-1].strip()
                
                i += 1
            
            break
        
        i += 1
    
    return info


def print_resource_info(info):
    print("每日500个PDF处理系统资源消耗信息：")
    print("=" * 60)
    
    print("\n1. Tesseract OCR策略（全部使用Tesseract）：")
    print(f"   - 处理时间：{info['tesseract']['time']}")
    print(f"   - 峰值内存：{info['tesseract']['memory']}")
    print(f"   - 磁盘空间：{info['tesseract']['disk']}")
    print(f"   - CPU使用率：{info['tesseract']['cpu']}")
    
    print("\n2. LiteParse OCR策略（全部使用LiteParse）：")
    print(f"   - 处理时间：{info['liteparse']['time']}")
    print(f"   - 峰值内存：{info['liteparse']['memory']}")
    print(f"   - 磁盘空间：{info['liteparse']['disk']}")
    print(f"   - CPU使用率：{info['liteparse']['cpu']}")
    
    print("\n3. 综合策略（自动选择，推荐）：")
    print(f"   - 处理时间：{info['combined']['time']}")
    print(f"   - 峰值内存：{info['combined']['memory']}")
    print(f"   - 磁盘空间：{info['combined']['disk']}")
    print(f"   - CPU使用率：{info['combined']['cpu']}")
    
    print("\n" + "=" * 60)
    print("注：以上信息基于测试环境的估计值，实际消耗可能因硬件配置和文件特性而有所不同")


def main():
    info = get_resource_info()
    
    if info:
        print_resource_info(info)
    else:
        print("无法获取资源消耗信息")


if __name__ == "__main__":
    main()
