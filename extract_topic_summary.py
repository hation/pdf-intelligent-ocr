#!/usr/bin/env python3
"""
专题报告提取工具 - 从已处理的文档中提取指定主题的报告
"""

import os
import re
import argparse
from datetime import datetime

# 主题分类规则配置
TOPIC_RULES = {
    "AI": {
        "name": "AI与科技",
        "main_category": "AI与科技",
        "sub_categories": {
            "ai_model": {
                "name": "🤖 AI大模型与应用",
                "keywords": ["AI", "大模型", "Agent", "GPT", "生成式", "AIAgent", "人工智能", "大语言", "LLM"]
            },
            "computing_power": {
                "name": "🔧 AI算力与硬件",
                "keywords": ["算力", "光模块", "芯片", "半导体", "GPU", "封装", "IC", "存储", "NAND", "PCB"]
            },
            "robotics": {
                "name": "🤖 具身智能与机器人",
                "keywords": ["具身智能", "人形机器人", "机器人", "减速器", "电机"]
            },
            "frontier": {
                "name": "🔬 前沿科技",
                "keywords": ["量子", "脑机接口", "6G", "AR", "VR", "元宇宙", "全息"]
            }
        }
    }
}


def parse_summary_list(summary_list_path, target_category):
    """
    从summary_list.md中解析指定分类的文档
    
    Args:
        summary_list_path: summary_list.md文件路径
        target_category: 目标分类名称（如"AI与科技"）
    
    Returns:
        文档名称列表
    """
    if not os.path.exists(summary_list_path):
        return []
    
    with open(summary_list_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到目标分类的部分
    pattern = rf'##\s+{re.escape(target_category)}\s*\((\d+)份\)\s*\n(.*?)(?=\n##\s|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return []
    
    category_content = match.group(2)
    
    # 提取所有文档名称（从第一列）
    # 格式: | 文档名 | 总结 |
    doc_pattern = r'\|\s+([^|]+?)\s+\|'
    docs = re.findall(doc_pattern, category_content)
    
    # 过滤掉表头
    docs = [d.strip() for d in docs if d.strip() and '文档名称' not in d]
    
    return docs


def categorize_document(doc_name, topic_config):
    """
    将文档分配到最合适的子分类
    
    Args:
        doc_name: 文档名称
        topic_config: 主题配置（TOPIC_RULES中的配置）
    
    Returns:
        子分类key
    """
    doc_name_lower = doc_name.lower()
    
    sub_cats = topic_config.get('sub_categories', {})
    best_match = list(sub_cats.keys())[0] if sub_cats else None
    max_score = 0
    
    for key, config in sub_cats.items():
        score = 0
        for keyword in config['keywords']:
            if keyword.lower() in doc_name_lower:
                score += 1
        
        if score > max_score:
            max_score = score
            best_match = key
    
    return best_match


def read_document_summary(summary_dir, doc_name):
    """
    读取文档的summary文件
    
    Args:
        summary_dir: summaries目录路径
        doc_name: 文档名称（不含_summary.md）
    
    Returns:
        dict containing one_sentence and key_points
    """
    # 尝试多种可能的文件名
    possible_names = [
        f"{doc_name}_summary.md",
        f"{doc_name}.md".replace('_hybrid', '_summary'),
        f"{doc_name}_summary_summary.md"  # handle double summary case
    ]
    
    for filename in possible_names:
        filepath = os.path.join(summary_dir, filename)
        if os.path.exists(filepath):
            break
    else:
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取一句话总结
        one_sentence_match = re.search(r'##\s*一句话总结\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        one_sentence = one_sentence_match.group(1).strip() if one_sentence_match else "暂无总结"
        
        # 提取核心看点
        key_points_match = re.search(r'##\s*核心看点\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        key_points = []
        if key_points_match:
            points_text = key_points_match.group(1)
            # 提取每个要点（1. xxx, 2. xxx等）
            points = re.findall(r'\d+\.\s*(.*?)(?=\n\d+\.|\Z)', points_text, re.DOTALL)
            key_points = [p.strip() for p in points if p.strip()]
        
        return {
            'name': doc_name,
            'one_sentence': one_sentence,
            'key_points': key_points[:5]  # 最多5个看点
        }
    except Exception as e:
        print(f"  读取失败 {doc_name}: {e}")
        return None


def generate_report(docs_by_category, topic_config, output_path, date_str):
    """
    生成markdown报告
    
    Args:
        docs_by_category: {sub_cat_key: [doc_summaries]}
        topic_config: 主题配置
        output_path: 输出文件路径
        date_str: 日期字符串
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    lines = []
    lines.append(f"# {topic_config['name']}专题报告\n")
    lines.append(f"**生成时间：** {date_str}\n")
    
    # 概览统计
    total_docs = sum(len(docs) for docs in docs_by_category.values())
    lines.append("## 概览统计\n")
    lines.append(f"- **总文档数：** {total_docs}份\n")
    lines.append("- **子分类统计：**")
    
    for key, config in topic_config['sub_categories'].items():
        count = len(docs_by_category.get(key, []))
        lines.append(f"  - {config['name']}：{count}份")
    lines.append("")
    
    # 按子分类生成内容
    for key, config in topic_config['sub_categories'].items():
        docs = docs_by_category.get(key, [])
        if not docs:
            continue
        
        cat_name = config['name']
        lines.append(f"## {cat_name}（{len(docs)}份）\n")
        
        for i, doc in enumerate(docs, 1):
            lines.append(f"### {i}. {doc['name']}\n")
            lines.append(f"**一句话总结**：{doc['one_sentence']}\n")
            lines.append("\n**核心看点**：")
            
            for j, point in enumerate(doc['key_points'], 1):
                lines.append(f"{j}. {point}")
            
            lines.append("")  # spacing between docs
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ 报告已生成：{output_path}")
    print(f"   包含 {total_docs} 份文档")


# Quick manual tests
def test_categorization():
    config = TOPIC_RULES['AI']
    assert categorize_document("2026中国具身智能产业发展报告", config) == "robotics"
    assert categorize_document("2026年中国光模块行业发展", config) == "computing_power"
    assert categorize_document("AI大模型治理白皮书", config) == "ai_model"
    print("Categorization tests passed")


def find_summary_list(base_dir):
    """找到最新的summary_list.md文件"""
    reports_dir = os.path.join(base_dir, 'reports')
    if not os.path.exists(reports_dir):
        return None
    
    # 找最新的summary_list文件
    latest = None
    latest_time = 0
    
    for filename in os.listdir(reports_dir):
        if filename.startswith('summary_list_') and filename.endswith('.md'):
            filepath = os.path.join(reports_dir, filename)
            mtime = os.path.getmtime(filepath)
            if mtime > latest_time:
                latest_time = mtime
                latest = filepath
    
    return latest


def main():
    parser = argparse.ArgumentParser(description='生成主题专题报告')
    parser.add_argument('--input', '-i', default='output/daily/20260714',
                        help='输入目录（包含summaries/和reports/）')
    parser.add_argument('--topic', '-t', default='AI',
                        help='主题名称（AI/finance/medical等）')
    parser.add_argument('--output', '-o', default=None,
                        help='输出文件路径（可选）')
    parser.add_argument('--date', '-d', default=None,
                        help='日期字符串（可选，默认今天）')
    
    args = parser.parse_args()
    
    # 验证主题
    if args.topic not in TOPIC_RULES:
        print(f"❌ 不支持的主题：{args.topic}")
        print(f"   支持的主题：{', '.join(TOPIC_RULES.keys())}")
        return
    
    topic_config = TOPIC_RULES[args.topic]
    date_str = args.date or datetime.now().strftime('%Y%m%d')
    
    # 找到summary_list文件
    summary_list_path = find_summary_list(args.input)
    if not summary_list_path:
        print(f"❌ 未找到summary_list.md文件")
        return
    print(f"📄 使用汇总列表：{os.path.basename(summary_list_path)}")
    
    # 解析文档列表
    doc_names = parse_summary_list(summary_list_path, topic_config['main_category'])
    print(f"📋 找到 {len(doc_names)} 份{topic_config['name']}相关文档")
    
    # 读取每个文档的总结
    summary_dir = os.path.join(args.input, 'summaries')
    doc_summaries = []
    
    for doc_name in doc_names:
        summary = read_document_summary(summary_dir, doc_name)
        if summary:
            doc_summaries.append(summary)
        else:
            print(f"  ⚠️  未找到总结：{doc_name[:40]}...")
    
    print(f"✅ 成功读取 {len(doc_summaries)} 份文档总结")
    
    # 按子分类分组
    docs_by_category = {}
    for key in topic_config['sub_categories'].keys():
        docs_by_category[key] = []
    
    for doc in doc_summaries:
        cat_key = categorize_document(doc['name'], topic_config)
        if cat_key:
            docs_by_category[cat_key].append(doc)
    
    # 生成输出路径
    if args.output:
        output_path = args.output
    else:
        output_dir = os.path.join('output', 'topic_summaries', args.topic)
        output_path = os.path.join(output_dir, f"{args.topic}_documents_summary_{date_str}.md")
    
    # 生成报告
    generate_report(docs_by_category, topic_config, output_path, date_str)


if __name__ == "__main__":
    main()
