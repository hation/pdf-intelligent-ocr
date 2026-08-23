#!/usr/bin/env python3
"""
专题提取器 - 按关键词配置提取指定专题文档并生成汇总报告
"""

import os
import re
import shutil
from datetime import datetime, timedelta

from pdf_ocr_tool.topics.utils import (
    read_summary_content,
    is_topic_document,
    send_feishu_message,
)
from pdf_ocr_tool.topics.analyzers import (
    extract_main_themes,
    extract_core_insights,
    extract_stocks_and_sectors,
)


def extract_topic_by_keywords(input_dir, topic_config, output_dir=None, date_str=None):
    """
    按关键词配置提取指定专题文档并生成汇总报告
    
    Args:
        input_dir: summaries目录路径
        topic_config: 专题配置字典（含name、keywords等）
        output_dir: 输出目录（默认为 output/topic_summaries/{topic_name}）
        date_str: 日期字符串（如 20260813），不传则使用当前日期
    """
    topic_name = topic_config['name']
    topic_keywords = topic_config['keywords']
    
    if date_str is None:
        date_str = datetime.now().strftime('%Y%m%d')
    
    if output_dir is None:
        output_dir = os.path.join('output', 'topic_summaries', topic_name)
    
    date_dir = os.path.join(output_dir, date_str)
    summaries_subdir = os.path.join(date_dir, 'summaries')
    os.makedirs(summaries_subdir, exist_ok=True)
    
    from datetime import datetime as dt
    # 用传入的 date_str 计算起始时间，而不是用当前日期
    # 允许 date_str 前后 +1 天的宽容度（应对跨零点生成的文件或手动补跑）
    target_day = dt.strptime(date_str, '%Y%m%d')
    day_start = target_day.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    window_start = day_start - timedelta(days=1)  # 前一天 0 点
    
    summary_files = []
    for f in os.listdir(input_dir):
        if not f.endswith('.md'):
            continue
        file_path = os.path.join(input_dir, f)
        mtime = dt.fromtimestamp(os.path.getmtime(file_path))
        if mtime >= window_start:
            summary_files.append(f)
    
    print(f"\n========== 提取【{topic_name}】专题 ==========")
    print(f"  日期基准: {date_str}（文件修改时间 >= {window_start.strftime('%Y-%m-%d')}）")
    print(f"  筛选文件数: {len(summary_files)}")
    
    topic_files = []
    non_topic_files = []
    
    for filename in summary_files:
        is_match, matched_kw = is_topic_document(filename, topic_keywords)
        if is_match:
            topic_files.append((filename, matched_kw))
        else:
            non_topic_files.append(filename)
    
    doc_data_list = []
    kw_match_counts = {}
    for filename, matched_kw in topic_files:
        src = os.path.join(input_dir, filename)
        dst = os.path.join(summaries_subdir, filename)
        
        shutil.copy2(src, dst)
        
        content = read_summary_content(src)
        if content:
            clean_name = filename.replace('_summary.md', '').replace('_hybrid', '')
            doc_data_list.append({
                'name': clean_name,
                'filename': filename,
                'keyword': matched_kw,
                'one_sentence': content['one_sentence'],
                'key_points': content['key_points'],
                'summary_tool': content.get('summary_tool', '未知')
            })
            kw_match_counts[matched_kw] = kw_match_counts.get(matched_kw, 0) + 1
    
    doc_data_list.sort(key=lambda x: (x['keyword'], x['name']))
    
    sorted_keywords = sorted(kw_match_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n============================================================")
    print(f"✅ 【{topic_name}】专题提取完成")
    print(f"============================================================")
    print(f"\n📊 统计:")
    print(f"  总扫描文档数：{len(summary_files)}")
    print(f"  {topic_name}相关文档数：{len(doc_data_list)}")
    print(f"  非{topic_name}文档数：{len(summary_files) - len(doc_data_list)}")
    print(f"  {topic_name}占比：{len(doc_data_list)/len(summary_files)*100:.1f}%")
    
    print(f"\n📂 输出目录：{date_dir}")
    print(f"\n📄 生成文件:")
    print(f"  1. READED_{date_str}.md              - 索引及统计")
    print(f"  2. {topic_name}_一句话汇总_{date_str}.md       - 快速浏览版")
    print(f"  3. {topic_name}_核心论点汇总_{date_str}.md     - 完整专题报告")
    print(f"  4. summaries/ 目录: {len(doc_data_list)} 个文档单独总结")
    
    print(f"\n🔑 关键词匹配统计:")
    for kw, count in sorted_keywords[:10]:
        print(f"  {kw}: {count}份")
    
    print("============================================================")
    
    index_content = f"# {topic_name}专题索引 {date_str}\n\n"
    index_content += f"## 统计信息\n\n"
    index_content += f"- 总扫描文档: {len(summary_files)}份\n"
    index_content += f"- {topic_name}相关文档: {len(doc_data_list)}份 ({len(doc_data_list)/len(summary_files)*100:.1f}%)\n\n"
    index_content += f"## 关键词匹配统计\n\n"
    for kw, count in sorted_keywords:
        index_content += f"- {kw}: {count}份\n"
    index_content += f"\n## 文件列表\n\n"
    for doc in doc_data_list:
        index_content += f"- [{doc['name']}](summaries/{doc['filename']}) (关键词: {doc['keyword']})\n"
    
    with open(os.path.join(date_dir, f'READED_{date_str}.md'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    one_sentence_content = f"# {topic_name}专题 · 一句话汇总 {date_str}\n\n"
    for doc in doc_data_list:
        tool = doc.get('summary_tool', '未知')
        one_sentence_content += f"## {doc['name']}\n\n"
        one_sentence_content += f"*总结工具：{tool}*\n\n"
        one_sentence_content += f"{doc['one_sentence']}\n\n"
    
    with open(os.path.join(date_dir, f'{topic_name}_一句话汇总_{date_str}.md'), 'w', encoding='utf-8') as f:
        f.write(one_sentence_content)
    
    key_points_content = f"# {topic_name}专题 · 核心论点汇总 {date_str}\n\n"
    for doc in doc_data_list:
        tool = doc.get('summary_tool', '未知')
        key_points_content += f"## {doc['name']}\n\n"
        key_points_content += f"*总结工具：{tool}*\n\n"
        key_points_content += f"**一句话总结**：{doc['one_sentence']}\n\n"
        if doc['key_points']:
            key_points_content += f"**核心看点**：\n\n"
            for i, point in enumerate(doc['key_points'][:5], 1):
                key_points_content += f"{i}. {point}\n\n"
        key_points_content += "---\n\n"
    
    key_points_file = os.path.join(date_dir, f'{topic_name}_核心论点汇总_{date_str}.md')
    with open(key_points_file, 'w', encoding='utf-8') as f:
        f.write(key_points_content)
    
    summary_root_dir = os.path.join(output_dir, '核心论点')
    os.makedirs(summary_root_dir, exist_ok=True)
    root_copy_path = os.path.join(summary_root_dir, f'{topic_name}_核心论点汇总_{date_str}.md')
    shutil.copy2(key_points_file, root_copy_path)
    
    themes = extract_main_themes(doc_data_list, topic_name)
    theme_text = ''
    if themes:
        theme_text = '\n主要内容方向：'
        for i, t in enumerate(themes[:5], 1):
            theme_text += f'\n  {i}. {t["theme"]}（{t["count"]}篇）'
    
    insights = extract_core_insights(doc_data_list, topic_name)
    insight_text = ''
    if insights:
        insight_text = '\n\n核心观点：'
        for i, ins in enumerate(insights, 1):
            insight_text += f'\n  {i}. {ins}'
    
    top_sectors, top_stocks = extract_stocks_and_sectors(doc_data_list, topic_name)
    benefit_text = ''
    if top_sectors:
        benefit_text = '\n\n受益方向：'
        for s, c in top_sectors:
            benefit_text += f'\n  · {s}（{c}篇提及）'
        if top_stocks:
            benefit_text += '\n\n高频提及标的：'
            benefit_text += '、'.join([s for s, _ in top_stocks])
    
    feishu_text = (
        f'📊 {topic_name}专题报告已生成（{date_str}）\n\n'
        f'今日处理PDF：{len(summary_files)} 份\n'
        f'{topic_name}相关：{len(doc_data_list)} 份（占比 {len(doc_data_list)/len(summary_files)*100:.1f}%）'
        f'{theme_text}'
        f'{insight_text}'
        f'{benefit_text}\n\n'
        f'📂 输出目录：{date_dir}'
    )
    send_feishu_message(feishu_text)
    print(f"\n📨 飞书通知已发送")
    
    return date_dir
