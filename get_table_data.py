#!/usr/bin/env python3
"""
从资源消耗报告中提取表格数据的脚本
"""

import os
import re


def get_table_data():
    report_path = os.path.join(os.path.dirname(__file__), "RESOURCE_CONSUMPTION_REPORT.md")
    
    if not os.path.exists(report_path):
        print("资源消耗报告不存在")
        return
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 找到表格部分
    table_pattern = r"\| 资源类型       \| Tesseract策略 \| LiteParse策略 \| 综合策略 \|\n(?:\|.*?\|\n)*"
    table_match = re.search(table_pattern, report_content, re.DOTALL)
    
    if not table_match:
        print("未找到表格数据")
        return
    
    table_content = table_match.group(0)
    
    # 解析表格
    rows = []
    lines = table_content.strip().split('\n')
    
    for line in lines:
        if line.strip():
            # 解析每一行
            cells = re.split(r'\|', line)
            cells = [cell.strip() for cell in cells if cell.strip()]
            
            if len(cells) == 4:
                # 确保这是一个有效的行
                rows.append(cells)
    
    # 解析标题
    headers = rows[0]
    data = []
    
    # 解析数据行
    for row in rows[1:-1]:  # 排除标题和分隔线
        if len(row) == 4:
            row_data = {}
            for i in range(len(row)):
                row_data[headers[i]] = row[i]
            data.append(row_data)
    
    return data


def print_resource_usage(data):
    if not data:
        print("未找到资源使用数据")
        return
    
    print("每日500个PDF处理系统资源消耗（综合策略）：")
    print("=" * 60)
    
    for item in data:
        resource_type = item['资源类型']
        tesseract = item['Tesseract策略']
        liteparse = item['LiteParse策略']
        combined = item['综合策略']
        
        # 使用综合策略的数据，因为这是推荐的
        if combined not in ['综合策略', '-']:
            if resource_type == '处理时间':
                # 格式化时间显示
                combined = combined.strip().replace(' ', '').replace('≈', '').strip()
                if '小时' in combined:
                    print(f"⏱️  总处理时间：{combined}")
                elif '分钟' in combined:
                    print(f"⏱️  总处理时间：{combined}")
                elif '天' in combined:
                    print(f"⏱️  总处理时间：{combined}")
            elif resource_type == '峰值内存':
                print(f"💾 峰值内存：{combined.strip()}")
            elif resource_type == '磁盘空间':
                print(f"💿 磁盘空间：{combined.strip()}")
            elif resource_type == '平均CPU使用率':
                print(f"💻 平均CPU使用率：{combined.strip()}")
    
    print("\n" + "=" * 60)
    print("策略对比（单个文件处理）：")
    
    for item in data:
        resource_type = item['资源类型']
        tesseract = item['Tesseract策略']
        liteparse = item['LiteParse策略']
        combined = item['综合策略']
        
        if resource_type == '处理时间':
            if tesseract and tesseract not in ['Tesseract策略', '-'] and '小时' not in tesseract:
                print(f"⏱️  Tesseract策略单个文件处理时间：{tesseract.strip()}")
            if liteparse and liteparse not in ['LiteParse策略', '-'] and '小时' not in liteparse:
                print(f"⏱️  LiteParse策略单个文件处理时间：{liteparse.strip()}")


def main():
    data = get_table_data()
    if data:
        print_resource_usage(data)


if __name__ == "__main__":
    main()
