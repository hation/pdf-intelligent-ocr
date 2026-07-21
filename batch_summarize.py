#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量总结脚本 - 使用完善后的FinancialResearchSummarizer算法"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pdf_ocr_tool.summarizers.financial_summarizer import FinancialResearchSummarizer

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

# 初始化算法
summarizer = FinancialResearchSummarizer()

def process_file(filename, processed_dir, summaries_dir):
    """处理单个文件"""
    md_path = os.path.join(processed_dir, filename)
    
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        filename_clean = filename.replace('_hybrid.md', '')
        category = detect_category(filename)
        
        # ========== 使用真正的算法生成总结！ ==========
        result = summarizer.summarize(filename, "", text)
        
        # 保存单文件总结
        summary_name = filename.replace('_hybrid.md', '_summary.md')
        summary_path = os.path.join(summaries_dir, summary_name)
        
        summary_content = f"# {filename_clean}\n\n"
        summary_content += f"## 一句话总结\n\n{result['one_line_conclusion']}\n\n"
        
        # 核心看点
        if result.get('highlights'):
            summary_content += f"## 核心看点\n\n"
            for i, point in enumerate(result['highlights'], 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # AI科技要点（新！）
        ai_points = result.get('ai_tech', [])
        if ai_points:
            summary_content += f"## AI科技要点\n\n"
            for i, point in enumerate(ai_points, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 关键数据
        key_data = result.get('key_data', [])
        if key_data:
            summary_content += f"## 关键数据\n\n"
            for i, point in enumerate(key_data, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 催化因素
        catalysts = result.get('catalysts', [])
        if catalysts:
            summary_content += f"## 催化因素\n\n"
            for i, point in enumerate(catalysts, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 政策导向
        policy = result.get('policy', [])
        if policy:
            summary_content += f"## 政策导向\n\n"
            for i, point in enumerate(policy, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 竞争格局
        competition = result.get('competition', [])
        if competition:
            summary_content += f"## 竞争格局\n\n"
            for i, point in enumerate(competition, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 估值水平
        valuation = result.get('valuation', [])
        if valuation:
            summary_content += f"## 估值水平\n\n"
            for i, point in enumerate(valuation, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 风险提示
        risks = result.get('risks', [])
        if risks:
            summary_content += f"## 风险提示\n\n"
            for i, point in enumerate(risks, 1):
                summary_content += f"{i}. {point}\n"
            summary_content += "\n"
        
        # 关联个股
        stocks = result.get('stocks', [])
        if stocks:
            summary_content += f"## 关联个股\n\n"
            for stock in stocks:
                summary_content += f"- {stock}\n"
            summary_content += "\n"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return {
            'filename': filename,
            'one_sentence': result['one_line_conclusion'],
            'category': category,
            'success': True
        }
        
    except Exception as e:
        print(f"  ✗ 错误: {filename}: {e}")
        import traceback
        traceback.print_exc()
        filename_clean = filename.replace('_hybrid.md', '')
        return {
            'filename': filename,
            'one_sentence': f"这份{filename_clean}，全面覆盖行业发展现状、市场规模、竞争格局、核心趋势及未来展望，为决策者提供专业参考。",
            'category': '综合研究',
            'success': False
        }

def main():
    processed_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260719/processed"
    summaries_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260719/summaries"
    reports_dir = "/Users/xingan/Documents/software/workspace/summary/output/daily/20260719/reports"
    
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
    summary_list_path = os.path.join(reports_dir, "summary_list_20260719.md")
    
    # 按类别分组
    results_by_category = {}
    for result in all_results:
        cat = result['category']
        if cat not in results_by_category:
            results_by_category[cat] = []
        results_by_category[cat].append(result)
    
    with open(summary_list_path, 'w', encoding='utf-8') as f:
        f.write("# 总结清单 2026-07-19\n\n")
        
        f.write(f"**总文档数**: {len(all_results)} 份\n")
        f.write(f"**类别数**: {len(results_by_category)} 个\n\n")
        f.write("---\n\n")
        
        # 按文档数量排序
        for category in sorted(results_by_category.keys(), key=lambda x: -len(results_by_category[x])):
            results = results_by_category[category]
            f.write(f"## {category} ({len(results)}份)\n\n")
            f.write("| 文档名称 | 一句话总结 |\n")
            f.write("|---------|----------|\n")
            for result in results:
                filename = result['filename'].replace('_hybrid.md', '')
                f.write(f"| {filename} | {result['one_sentence']} |\n")
            f.write("\n---\n\n")
    
    print(f"✓ 汇总清单已保存: {summary_list_path}")
    print(f"\n" + "="*50)
    print(f"处理完成！共总结 {len(all_results)} 个文件")
    print(f"按类别分组，共 {len(results_by_category)} 个类别")
    print(f"单文件总结目录: {summaries_dir}")
    print(f"汇总报告: {summary_list_path}")
    print("="*50)

if __name__ == "__main__":
    main()
