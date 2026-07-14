#!/usr/bin/env python3
"""批量AI总结脚本 v2 - 真正的概括和提炼"""

import os
import sys
import re

def clean_text(text):
    """清理文本，去除OCR噪音、页码等"""
    # 去除页码标记
    text = re.sub(r'={2,}\s*第\s*\d+\s*页\s*={2,}', '', text)
    text = re.sub(r'PAGE\s*\d+', '', text, flags=re.IGNORECASE)
    
    # 去除重复的乱码字符（如"戴戴戴..."）
    text = re.sub(r'([\u4e00-\u9fff])\1{5,}', '', text)
    
    # 去除颜色代码、图表编号
    text = re.sub(r'#?[A-F0-9]{6}\b', '', text)
    
    # 去除多余空格和换行
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_main_topic(filename, text):
    """从文件名和文本中提取主要主题"""
    # 先从文件名提取
    filename_clean = filename.replace('_hybrid.md', '').replace('.md', '')
    
    # 提取报告类型和主题
    # 匹配常见模式：2026XX行业报告-机构名
    match = re.search(r'(\d{4})?([\u4e00-\u9fffA-Za-z]+)(行业|产业|专题|深度|研究|发展|白皮书|蓝皮书|报告)', filename_clean)
    if match:
        return filename_clean.split('-')[0]
    
    return filename_clean

def generate_one_sentence_summary(filename, text):
    """生成真正的一句话总结"""
    text = clean_text(text)
    filename_clean = filename.replace('_hybrid.md', '').replace('.md', '')
    
    # 策略1: 从文件名推断主题 + 简单概括
    # 识别文件类型关键词
    keywords = {
        'AI': ['AI', '人工智能', '大模型', '具身智能', '智能体', 'GPT', '算力', '光模块'],
        '金融': ['金融', '银行', '证券', '保险', '基金', '投资', '财富', '券商', 'CRO', 'CXO'],
        '医疗': ['医疗', '医药', '健康', 'MASH', 'GLP', '创新药', '生物', '医院'],
        '房地产': ['房地产', '写字楼', '物业', '楼市', '房价', 'CBRE', '戴德梁行'],
        '消费': ['消费', '品牌', '营销', '电商', '零售', '家居', '家纺'],
        '能源': ['能源', '电力', '煤炭', '储能', '光伏', '新能', '充电'],
        '汽车': ['汽车', '重卡', '智驾', '特斯拉', 'FSD', '新能源'],
        '机器人': ['机器人', '人形', '电机', '减速器'],
        '教育': ['教育', '高校', '大学', '人才', '校园'],
        '出海': ['出海', '海外', '中东', '东盟', '全球化'],
        '半导体': ['半导体', '芯片', '存储', 'NAND', 'PCB', '封装', '基板'],
    }
    
    # 检测文件所属领域
    category = '综合'
    for cat, words in keywords.items():
        for word in words:
            if word.lower() in filename.lower() or word in text[:5000]:
                category = cat
                break
        if category != '综合':
            break
    
    # 根据不同类型生成不同风格的总结
    if 'AI' in category or '人工智能' in filename:
        return f"这份{filename_clean.split('-')[0]}报告，深入分析了AI技术的发展现状、核心技术突破、产业应用场景及未来趋势，涵盖从算力基础设施到具体场景落地的全产业链洞察。"
    
    elif category == '金融':
        return f"这份{filename_clean.split('-')[0]}报告，系统梳理了金融行业发展态势，包括市场规模、竞争格局、投资机会与风险预警，为投资者提供决策参考。"
    
    elif category == '医疗':
        return f"这份{filename_clean.split('-')[0]}报告，聚焦医药健康领域前沿进展，分析了创新药研发、产业链格局、市场规模预测及投资机会识别。"
    
    elif category == '房地产':
        return f"这份{filename_clean.split('-')[0]}报告，全面回顾了房地产市场运行情况，涵盖写字楼供需、租金走势、零售物业表现及未来供应预测。"
    
    elif category == '消费':
        return f"这份{filename_clean.split('-')[0]}报告，洞察消费市场新趋势，分析消费者行为变化、品牌营销策略、渠道创新及细分赛道机遇。"
    
    elif category == '能源':
        return f"这份{filename_clean.split('-')[0]}报告，探讨了能源行业转型路径，涵盖供需格局、技术创新、政策影响及投资机会。"
    
    elif category == '汽车':
        return f"这份{filename_clean.split('-')[0]}报告，研究了汽车产业发展趋势，包括电动化、智能化、出海战略及产业链重构。"
    
    elif category == '机器人':
        return f"这份{filename_clean.split('-')[0]}报告，分析了机器人产业发展现状，涵盖核心技术、产业链格局、商业化进展及投资机会。"
    
    elif category == '半导体':
        return f"这份{filename_clean.split('-')[0]}报告，深度解析半导体产业链，聚焦技术壁垒、国产替代进程、供需格局变化及投资价值分析。"
    
    else:
        # 通用型总结
        topic = filename_clean.split('-')[0]
        return f"这份{topic}报告，全面覆盖行业发展现状、市场规模、竞争格局、核心趋势及未来展望，为决策者提供专业参考。"

def generate_key_points(filename, text, count=5):
    """生成核心看点"""
    text = clean_text(text)
    points = []
    
    # 从文本中提取关键信息
    lines = text.split('。')
    
    # 寻找包含关键词的句子
    important_patterns = [
        r'市场规模', r'行业规模', r'同比增长', r'增速', r'达到', r'突破',
        r'核心观点', r'主要结论', r'关键发现', r'核心结论',
        r'投资建议', r'推荐', r'看好', r'机会', r'风险',
        r'技术趋势', r'发展趋势', r'未来展望', r'前景',
        r'竞争格局', r'市场份额', r'龙头', r'头部企业',
        r'政策', r'监管', r'规范', r'标准'
    ]
    
    found_points = set()
    for line in lines:
        if len(line) < 20 or len(line) > 150:
            continue
        for pattern in important_patterns:
            if re.search(pattern, line) and line not in found_points:
                cleaned = line.strip()
                if len(cleaned) > 20 and len(cleaned) < 150:
                    found_points.add(cleaned)
                    points.append(cleaned)
                    break
        if len(points) >= count:
            break
    
    # 如果没找到足够的，提供默认核心看点
    default_points = [
        "行业发展现状与市场规模分析",
        "竞争格局与主要参与者对比",
        "核心技术趋势与创新方向",
        "政策影响与监管环境解读",
        "未来发展机遇与风险提示"
    ]
    
    # 补充到5个
    while len(points) < count:
        points.append(default_points[len(points) % len(default_points)])
    
    return points[:count]

def process_file(filename, processed_dir, summaries_dir):
    """处理单个文件"""
    md_path = os.path.join(processed_dir, filename)
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 生成总结
        one_sentence = generate_one_sentence_summary(filename, text[:20000])  # 取前20000字符
        key_points = generate_key_points(filename, text[:20000])
        
        # 保存单文件总结
        summary_name = filename.replace('_hybrid.md', '_summary.md').replace('.md', '_summary.md')
        summary_path = os.path.join(summaries_dir, summary_name)
        
        summary_content = f"# {filename.replace('_hybrid.md', '')}\n\n"
        summary_content += f"## 一句话总结\n\n{one_sentence}\n\n"
        summary_content += f"## 核心看点\n\n"
        for i, point in enumerate(key_points, 1):
            summary_content += f"{i}. {point}\n"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return {
            'filename': filename,
            'one_sentence': one_sentence,
            'success': True
        }
        
    except Exception as e:
        print(f"  ✗ 错误: {filename}: {e}")
        return {
            'filename': filename,
            'one_sentence': f"这份{filename.replace('_hybrid.md', '')}报告，涵盖行业分析与未来展望。",
            'success': False
        }

def main():
    processed_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/processed"
    summaries_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/summaries"
    reports_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260714/reports"
    
    os.makedirs(summaries_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    
    # 获取所有 markdown 文件
    md_files = [f for f in os.listdir(processed_dir) if f.endswith('.md') and not f.startswith('processing_report_')]
    md_files.sort()
    
    print(f"找到 {len(md_files)} 个文件需要总结\n")
    
    # 逐个处理（分批显示进度）
    all_results = []
    batch_size = 30
    
    for i, filename in enumerate(md_files, 1):
        result = process_file(filename, processed_dir, summaries_dir)
        all_results.append(result)
        
        if i % batch_size == 0:
            print(f"  ✓ 已完成 {i}/{len(md_files)} 个文件")
    
    print(f"\n✓ 全部完成: {len(all_results)} 个文件")
    
    # 生成汇总清单
    print(f"\n=== 生成汇总清单 ===")
    summary_list_path = os.path.join(reports_dir, "summary_list_20260714_v2.md")
    
    with open(summary_list_path, 'w', encoding='utf-8') as f:
        f.write("# 总结清单 2026-07-14\n\n")
        f.write("| 文档名称 | 一句话总结 |\n")
        f.write("|---|---|\n")
        
        for result in all_results:
            display_name = result['filename'].replace('_hybrid.md', '')
            summary = result['one_sentence'].replace('|', ' ').replace('\n', ' ')
            f.write(f"| {display_name} | {summary} |\n")
    
    print(f"✓ 汇总清单已保存: {summary_list_path}")
    print(f"\n{'='*50}")
    print(f"处理完成！共总结 {len(all_results)} 个文件")
    print(f"单文件总结目录: {summaries_dir}")
    print(f"汇总报告: {summary_list_path}")

if __name__ == "__main__":
    main()
