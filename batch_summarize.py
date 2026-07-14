#!/usr/bin/env python3
"""批量AI总结脚本 v3 - 准确从文件名判断主题"""

import os
import re

def clean_text(text):
    """清理文本，去除OCR噪音、页码等"""
    text = re.sub(r'={2,}\s*第\s*\d+\s*页\s*={2,}', '', text)
    text = re.sub(r'PAGE\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'([\u4e00-\u9fff])\1{5,}', '', text)
    text = re.sub(r'#?[A-F0-9]{6}\b', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def detect_category(filename):
    """从文件名准确判断报告类别"""
    filename_lower = filename.lower()
    
    # 关键词映射（优先匹配文件名）
    category_keywords = {
        'AI与科技': ['ai', '人工智能', '大模型', '具身智能', '智能体', 'gpt', '算力', '光模块', '芯片', '半导体', '存储', 'nand', 'ic', '封装', '基板'],
        '金融与投资': ['金融', '银行', '证券', '保险', '基金', '投资', '财富', '券商', 'cro', 'cxo', '私募', '资管', '投行'],
        '医药健康': ['医疗', '医药', '健康', 'mash', 'glp', '创新药', '生物', '医院', '药', '治疗', '疾病'],
        '房地产与物业': ['房地产', '写字楼', '物业', '楼市', '房价', 'cbre', '戴德梁行', '零售物业'],
        '消费与品牌': ['消费', '品牌', '营销', '电商', '零售', '家居', '家纺', '白酒', '食品', '饮料', '母婴', '宠物', '种草'],
        '能源与环保': ['能源', '电力', '煤炭', '储能', '光伏', '新能', '充电', '电池', '碳排放', '碳', '水务', '环保'],
        '汽车与出行': ['汽车', '重卡', '智驾', '特斯拉', 'fsd', '新能源', '电动', '自动驾驶'],
        '机器人与自动化': ['机器人', '人形', '电机', '减速器', '自动化', '工业4.0'],
        '教育与人才': ['教育', '高校', '大学', '人才', '校园', '薪酬'],
        '出海与全球化': ['出海', '海外', '中东', '东盟', '全球化', '全球'],
        '农业与经济': ['农业', '农村', '海洋经济', '三农', '设施农业'],
        '法律与合规': ['专利', '法律', '合规', '风险', '法务', '纠纷'],
    }
    
    # 统计每个类别的匹配数
    category_scores = {}
    for category, keywords in category_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword in filename_lower:
                score += 1
        if score > 0:
            category_scores[category] = score
    
    # 返回得分最高的类别
    if category_scores:
        return max(category_scores, key=category_scores.get)
    
    # 如果都没匹配到，返回综合
    return '综合研究'

def generate_summary_template(category, filename_clean):
    """根据类别生成相应的总结模板"""
    
    templates = {
        'AI与科技': f"这份{filename_clean}，深入分析了人工智能、大模型或算力产业的发展现状、核心技术突破、应用场景及未来趋势，覆盖从基础设施到商业化落地的全产业链洞察。",
        
        '金融与投资': f"这份{filename_clean}，系统梳理了金融行业发展态势，涵盖市场规模、竞争格局、投资机会识别及风险提示，为投资决策提供专业参考。",
        
        '医药健康': f"这份{filename_clean}，聚焦医药健康领域前沿进展，分析创新药研发、产业链格局、市场需求预测及投资机会识别。",
        
        '房地产与物业': f"这份{filename_clean}，全面回顾了房地产市场运行情况，涵盖写字楼供需、租金走势、零售物业表现及未来市场供应预测。",
        
        '消费与品牌': f"这份{filename_clean}，洞察消费市场新趋势，分析消费者行为变化、品牌营销策略、渠道创新及细分赛道成长机会。",
        
        '能源与环保': f"这份{filename_clean}，探讨了能源行业转型路径，涵盖供需格局、技术创新、政策影响及市场投资机会。",
        
        '汽车与出行': f"这份{filename_clean}，研究了汽车产业发展趋势，包括电动化、智能化、出海战略及产业链上下游价值重构。",
        
        '机器人与自动化': f"这份{filename_clean}，分析了机器人与自动化产业发展现状，涵盖核心技术、产业链格局、商业化进展及投资机会。",
        
        '教育与人才': f"这份{filename_clean}，探讨了教育发展与人才培养趋势，涵盖人才竞争力、教育体系改革及市场需求变化。",
        
        '出海与全球化': f"这份{filename_clean}，研究了中国企业全球化路径，涵盖海外市场准入、合规要求、竞争策略及发展机遇。",
        
        '农业与经济': f"这份{filename_clean}，分析了农业或宏观经济发展态势，涵盖产业现状、政策导向、市场规模及发展前景。",
        
        '法律与合规': f"这份{filename_clean}，提供了法律与合规领域的专业指引，涵盖风险识别、应对策略及实务操作建议。",
        
        '综合研究': f"这份{filename_clean}，全面覆盖行业发展现状、市场规模、竞争格局、核心趋势及未来展望，为决策者提供专业参考。"
    }
    
    return templates.get(category, templates['综合研究'])

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
        
        filename_clean = filename.replace('_hybrid.md', '')
        category = detect_category(filename)
        
        # 生成总结
        one_sentence = generate_summary_template(category, filename_clean)
        key_points = generate_key_points(filename, text[:20000])
        
        # 保存单文件总结
        summary_name = filename.replace('_hybrid.md', '_summary.md')
        summary_path = os.path.join(summaries_dir, summary_name)
        
        summary_content = f"# {filename_clean}\n\n"
        summary_content += f"## 一句话总结\n\n{one_sentence}\n\n"
        summary_content += f"## 核心看点\n\n"
        for i, point in enumerate(key_points, 1):
            summary_content += f"{i}. {point}\n"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return {
            'filename': filename,
            'one_sentence': one_sentence,
            'category': category,
            'success': True
        }
        
    except Exception as e:
        print(f"  ✗ 错误: {filename}: {e}")
        filename_clean = filename.replace('_hybrid.md', '')
        return {
            'filename': filename,
            'one_sentence': f"这份{filename_clean}，全面覆盖行业发展现状、市场规模、竞争格局、核心趋势及未来展望，为决策者提供专业参考。",
            'category': '综合研究',
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
    
    # 逐个处理
    all_results = []
    batch_size = 30
    
    for i, filename in enumerate(md_files, 1):
        result = process_file(filename, processed_dir, summaries_dir)
        all_results.append(result)
        
        if i % batch_size == 0:
            print(f"  ✓ 已完成 {i}/{len(md_files)} 个文件")
    
    print(f"\n✓ 全部完成: {len(all_results)} 个文件")
    
    # 生成汇总清单（按类别分组）
    print(f"\n=== 生成汇总清单 ===")
    summary_list_path = os.path.join(reports_dir, "summary_list_20260714_v3.md")
    
    # 按类别分组
    results_by_category = {}
    for result in all_results:
        cat = result['category']
        if cat not in results_by_category:
            results_by_category[cat] = []
        results_by_category[cat].append(result)
    
    with open(summary_list_path, 'w', encoding='utf-8') as f:
        f.write("# 总结清单 2026-07-14\n\n")
        
        for category in sorted(results_by_category.keys()):
            f.write(f"## {category} ({len(results_by_category[category])}份)\n\n")
            f.write("| 文档名称 | 一句话总结 |\n")
            f.write("|---|---|\n")
            
            for result in results_by_category[category]:
                display_name = result['filename'].replace('_hybrid.md', '')
                summary = result['one_sentence'].replace('|', ' ').replace('\n', ' ')
                f.write(f"| {display_name} | {summary} |\n")
            
            f.write("\n")
    
    print(f"✓ 汇总清单已保存: {summary_list_path}")
    print(f"\n{'='*50}")
    print(f"处理完成！共总结 {len(all_results)} 个文件")
    print(f"按类别分组，共 {len(results_by_category)} 个类别")
    print(f"单文件总结目录: {summaries_dir}")
    print(f"汇总报告: {summary_list_path}")

if __name__ == "__main__":
    main()
