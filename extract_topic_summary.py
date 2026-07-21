#!/usr/bin/env python3
"""
AI专题提取工具 - 只看文件名，识别AI主题文档并汇总复制

使用方式:
    python3 extract_topic_summary.py --input output/daily/20260719/summaries
    
    或者直接运行（自动找最新的summary目录）:
    python3 extract_topic_summary.py
"""

import os
import re
import shutil
import argparse
from datetime import datetime

# AI关键词列表（只匹配文件名）
AI_KEYWORDS = [
    'AI', '人工智能', '大模型', 'LLM', 'GPT', 'Agent', '智能体',
    '算力', '光模块', '芯片', '半导体', 'GPU', '封装', 'PCB', 'HBM',
    '具身智能', '人形机器人', '机器人', '减速器', '电机',
    '量子', '脑机接口', '6G', '增强现实', 'VR', '元宇宙', 'AIGC',
    'DeepSeek', '豆包', 'Claude', 'Gemini', 'GEO', '生成式'
]


def read_summary_content(filepath):
    """读取summary文件，提取一句话总结和核心看点"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取一句话总结
        one_sentence = "暂无"
        one_sentence_match = re.search(r'##\s*一句话总结\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if one_sentence_match:
            one_sentence = one_sentence_match.group(1).strip()
        
        # 提取核心看点（支持 "1. xxx"、"- xxx"、"• xxx" 三种格式）
        key_points = []
        key_points_match = re.search(r'##\s*核心看点\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if key_points_match:
            points_text = key_points_match.group(1)
            # 按行分割，提取列表项
            for line in points_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                # 去掉前缀：数字编号(1.)、横线(-)、星号(*)、点号(•)
                line = re.sub(r'^\d+[\.\、\)]\s*', '', line)
                line = re.sub(r'^[-\*\•]\s*', '', line)
                if line and len(line) > 5:
                    key_points.append(line)
        
        return {
            'one_sentence': one_sentence,
            'key_points': key_points
        }
    except Exception as e:
        print(f"  读取失败 {filepath}: {e}")
        return None


def is_ai_document(filename):
    """判断文件名是否包含AI关键词"""
    filename_lower = filename.lower()
    
    for kw in AI_KEYWORDS:
        if kw.lower() in filename_lower:
            return True, kw
    
    return False, None


def find_latest_summaries_dir(base_path='output/daily'):
    """找到最新的summaries目录"""
    if not os.path.exists(base_path):
        return None
    
    date_dirs = [d for d in os.listdir(base_path) if re.match(r'\d{8}', d)]
    if not date_dirs:
        return None
    
    date_dirs.sort(reverse=True)
    
    for date_dir in date_dirs:
        summaries_dir = os.path.join(base_path, date_dir, 'summaries')
        if os.path.exists(summaries_dir):
            return summaries_dir
    
    return None


def extract_and_copy(input_dir, output_dir=None):
    """
    从summary目录中提取AI文档并复制，生成两份汇总报告
    
    Args:
        input_dir: summaries目录路径（如 output/daily/20260720/summaries）
        output_dir: 输出目录（默认为output/topic_summaries/AI）
    """
    # 使用当前日期作为输出目录名（什么时候总结就用哪天）
    date_str = datetime.now().strftime('%Y%m%d')
    
    # 输出结构：output_dir/YYYYMMDD/summaries/
    if output_dir is None:
        output_dir = os.path.join('output', 'topic_summaries', 'AI')
    
    date_dir = os.path.join(output_dir, date_str)
    summaries_subdir = os.path.join(date_dir, 'summaries')
    os.makedirs(summaries_subdir, exist_ok=True)
    
    # 扫描总结文件，只处理今天生成的（避免和之前的数据混淆）
    from datetime import datetime as dt
    today_start = dt.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    summary_files = []
    for f in os.listdir(input_dir):
        if not f.endswith('.md'):
            continue
        file_path = os.path.join(input_dir, f)
        mtime = dt.fromtimestamp(os.path.getmtime(file_path))
        if mtime >= today_start:
            summary_files.append(f)
    
    print(f"  筛选条件: 只处理 {date_str} 生成的文件")
    print(f"  今日文件数: {len(summary_files)}")
    
    ai_files = []
    non_ai_files = []
    
    for filename in summary_files:
        is_ai, matched_kw = is_ai_document(filename)
        if is_ai:
            ai_files.append((filename, matched_kw))
        else:
            non_ai_files.append(filename)
    
    # 复制文件并读取内容
    doc_data_list = []
    for filename, matched_kw in ai_files:
        src = os.path.join(input_dir, filename)
        dst = os.path.join(summaries_subdir, filename)
        
        shutil.copy2(src, dst)
        
        # 读取内容用于汇总
        content = read_summary_content(src)
        if content:
            clean_name = filename.replace('_summary.md', '').replace('_hybrid', '')
            doc_data_list.append({
                'name': clean_name,
                'filename': filename,
                'keyword': matched_kw,
                'one_sentence': content['one_sentence'],
                'key_points': content['key_points']
            })
    
    # ========== 生成报告1：一句话汇总 ==========
    one_sentence_path = os.path.join(date_dir, f'AI_一句话汇总_{date_str}.md')
    with open(one_sentence_path, 'w', encoding='utf-8') as f:
        f.write("# AI专题 · 一句话汇总\n\n")
        f.write(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**文档数量**：{len(doc_data_list)} 份\n\n")
        f.write("---\n\n")
        
        for i, doc in enumerate(doc_data_list, 1):
            f.write(f"### {i}. {doc['name']}\n\n")
            f.write(f"{doc['one_sentence']}\n\n")
            f.write("---\n\n")
    
    # ========== 生成报告2：核心论点汇总 ==========
    key_points_path = os.path.join(date_dir, f'AI_核心论点汇总_{date_str}.md')
    with open(key_points_path, 'w', encoding='utf-8') as f:
        f.write("# AI专题 · 核心论点汇总\n\n")
        f.write(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**文档数量**：{len(doc_data_list)} 份\n\n")
        f.write("---\n\n")
        
        for i, doc in enumerate(doc_data_list, 1):
            f.write(f"## {i}. {doc['name']}\n\n")
            f.write(f"**一句话总结**：{doc['one_sentence']}\n\n")
            
            if doc['key_points']:
                f.write("**核心看点**：\n\n")
                for j, point in enumerate(doc['key_points'], 1):
                    f.write(f"{j}. {point}\n")
                f.write("\n")
            
            f.write("---\n\n")
    
    # 生成索引文件
    index_path = os.path.join(date_dir, f'READED_{date_str}.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# AI专题文档汇总\n\n")
        f.write(f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"**AI相关文档**：{len(doc_data_list)} 份\n\n")
        f.write(f"**关键词匹配来源**：文件名\n\n")
        f.write("---\n\n")
        
        f.write("## 📁 文件说明\n\n")
        f.write(f"- `AI_一句话汇总_{date_str}.md` - 所有文档的一句话总结（快速浏览）\n")
        f.write(f"- `AI_核心论点汇总_{date_str}.md` - 包含核心看点的完整专题报告（深度阅读）\n")
        f.write(f"- `summaries/*.md` - 各文档的单独总结文件\n\n")
        
        f.write("---\n\n")
        
        f.write("## 文档列表\n\n")
        for i, doc in enumerate(doc_data_list, 1):
            f.write(f"{i}. [{doc['name']}](summaries/{doc['filename']}) 「匹配关键词：{doc['keyword']}」\n")
        
        f.write("\n---\n\n")
        f.write("## 关键词统计\n\n")
        kw_count = {}
        for doc in doc_data_list:
            kw_count[doc['keyword']] = kw_count.get(doc['keyword'], 0) + 1
        
        for kw, count in sorted(kw_count.items(), key=lambda x: -x[1]):
            f.write(f"- **{kw}**：{count} 份\n")
    
    print("\n" + "="*60)
    print("✅ AI主题文档提取完成")
    print("="*60)
    print(f"\n📊 统计:")
    print(f"  总扫描文档数：{len(summary_files)}")
    print(f"  AI相关文档数：{len(doc_data_list)}")
    print(f"  非AI文档数：{len(non_ai_files)}")
    print(f"  AI占比：{len(doc_data_list)/len(summary_files)*100:.1f}%")
    print(f"\n📂 输出目录：{date_dir}")
    print(f"\n📄 生成文件:")
    print(f"  1. READED_{date_str}.md              - 索引及统计")
    print(f"  2. AI_一句话汇总_{date_str}.md       - 快速浏览版")
    print(f"  3. AI_核心论点汇总_{date_str}.md     - 完整专题报告")
    print(f"  4. summaries/ 目录: {len(doc_data_list)} 个文档单独总结")
    print(f"\n🔑 关键词匹配统计:")
    kw_count = {}
    for doc in doc_data_list:
        kw_count[doc['keyword']] = kw_count.get(doc['keyword'], 0) + 1
    for kw, count in sorted(kw_count.items(), key=lambda x: -x[1])[:10]:
        print(f"  {kw}: {count}份")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='提取AI专题文档')
    parser.add_argument('--input', '-i', default=None,
                        help='输入summaries目录路径（如 output/daily/20260719/summaries）')
    parser.add_argument('--output', '-o', default=None,
                        help='输出目录路径（默认 output/topic_summaries/AI）')
    
    args = parser.parse_args()
    
    # 确定输入目录
    if args.input:
        input_dir = args.input
    else:
        input_dir = find_latest_summaries_dir()
        if not input_dir:
            print("❌ 未找到summaries目录，请手动指定：python3 extract_topic_summary.py -i <目录>")
            return
    
    if not os.path.exists(input_dir):
        print(f"❌ 目录不存在：{input_dir}")
        return
    
    print(f"📂 扫描目录：{input_dir}")
    
    extract_and_copy(input_dir, args.output)


if __name__ == "__main__":
    main()
