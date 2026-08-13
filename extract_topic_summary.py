#!/usr/bin/env python3
"""
专题提取工具 - 支持多专题配置（AI/新能源/医药/消费/科技/汽车...）

使用方式:
    # 默认提取AI专题
    python3 extract_topic_summary.py
    
    # 提取指定专题（支持多个）
    python3 extract_topic_summary.py --topic 新能源
    python3 extract_topic_summary.py --topic AI --topic 医药
    
    # 从指定目录提取
    python3 extract_topic_summary.py --input output/daily/20260724/summaries --topic 消费
"""

import os
import re
import shutil
import argparse
from datetime import datetime

# ========== 多专题配置 ==========
TOPIC_CONFIGS = {
    'AI': {
        'name': 'AI',
        'description': '人工智能、大模型、算力、芯片、具身智能等',
        'keywords': [
            'AI', '人工智能', '大模型', 'LLM', 'GPT', 'Agent', '智能体',
            '算力', '光模块', '芯片', '半导体', 'GPU', '封装', 'PCB', 'HBM',
            '具身智能', '人形机器人', '机器人', '减速器', '电机',
            '量子', '脑机接口', '6G', '增强现实', 'VR', '元宇宙', 'AIGC',
            'DeepSeek', '豆包', 'Claude', 'Gemini', 'GEO', '生成式'
        ]
    },
    '新能源': {
        'name': '新能源',
        'description': '光伏、储能、锂电池、新能源车、氢能等',
        'keywords': [
            '光伏', '储能', '锂电池', '锂电', '动力电池', '新能源车',
            '新能源', '氢能', '氢能源', '储能电站', '锂电池材料', '电解液',
            '正极材料', '负极材料', '三元锂', '磷酸铁锂', '锂矿',
            '光伏组件', '逆变器', '储能电池', '钠离子', '换电', '充电桩',
            '光伏装机', '储能装机', '复合集流体', '快充', '超充',
            'TOPCon', 'HJT', '钙钛矿', 'N型', '大储', '户储'
        ]
    },
    '医药': {
        'name': '医药',
        'description': '创新药、生物医药、医疗器械、CXO等',
        'keywords': [
            '创新药', '生物医药', 'CXO', '医疗器械', '医疗',
            'ADC', '双抗', '单抗', '细胞治疗', '基因治疗',
            '创新器械', '手术机器人', '内窥镜', 'IVD', '体外诊断',
            '疫苗', '中药', '化药', '生物药', '医药商业', '药房',
            '医疗服务', '医美', '康复', '眼科', '牙科'
        ]
    },
    '消费': {
        'name': '消费',
        'description': '食品饮料、零售、电商、消费电子等',
        'keywords': [
            '消费', '食品', '饮料', '零售', '电商', '消费电子',
            '白酒', '啤酒', '乳业', '零食', '茶饮', '餐饮',
            '预制菜', '调味品', '化妆品', '美妆', '个护',
            '智能家居', '家电', '消费升级', '新消费', '国潮',
            '直播电商', '社区团购', '即时零售'
        ]
    },
    '科技': {
        'name': '科技',
        'description': '半导体、电子、通信、计算机、软件等',
        'keywords': [
            '半导体', '芯片', '集成电路', '晶圆', '封测', '晶圆厂',
            '电子', '通信', '计算机', '软件', '云计算', 'SaaS',
            '操作系统', '数据库', '信创', '国产替代', '自主可控',
            '工业软件', 'EDA', 'IP核', '设备', '材料',
            '消费电子', '智能手机', '手机', '终端', 'MR', 'VR', 'AR'
        ]
    },
    '汽车': {
        'name': '汽车',
        'description': '整车、零部件、智能驾驶、自动驾驶等',
        'keywords': [
            '汽车', '整车', '乘用车', '商用车', '新能源汽车', '电动车',
            '智能驾驶', '自动驾驶', '智驾', '智能座舱', '车机',
            '汽车电子', '域控制器', '毫米波雷达', '激光雷达', '摄像头',
            '线控底盘', '空气悬架', '热管理', '一体化压铸',
            '特斯拉', '比亚迪', '理想', '蔚来', '小鹏', '长城', '吉利'
        ]
    },
    '有色': {
        'name': '有色',
        'description': '有色金属、贵金属、工业金属等',
        'keywords': [
            '有色', '铜', '铝', '金', '银', '锂', '钴', '镍',
            '稀土', '磁材', '钛', '镁', '锡', '锌', '铅',
            '贵金属', '工业金属', '小金属', '锂矿', '稀土永磁',
            '电解铝', '铜箔', '铝箔', '铜加工'
        ]
    },
    '煤炭': {
        'name': '煤炭',
        'description': '煤炭、煤化工、火电、能源等',
        'keywords': [
            '煤炭', '煤', '焦煤', '动力煤', '无烟煤', '煤化工',
            '火电', '煤电', '能源', '煤矿', '采矿', '煤炭开采'
        ]
    },
    '地产': {
        'name': '地产',
        'description': '房地产、物业、建材、家居等',
        'keywords': [
            '地产', '房地产', '房产', '房企', '物业', '物业管理',
            '建材', '水泥', '玻璃', '防水', '涂料', '瓷砖',
            '家居', '家具', '装饰', '装修', '建材家居'
        ]
    },
    '银行': {
        'name': '银行',
        'description': '银行、金融、信贷、利率等',
        'keywords': [
            '银行', '金融', '信贷', '利率', '息差', 'ROE', '净息差',
            '商业银行', '国有行', '股份行', '城商行', '农商行',
            '降息', '降准', 'LPR', '存款', '贷款', '不良率', '拨备'
        ]
    }
}


def read_summary_content(filepath):
    """读取summary文件，提取一句话总结和核心看点"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        one_sentence = "暂无"
        one_sentence_match = re.search(r'##\s*一句话总结\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if one_sentence_match:
            one_sentence = one_sentence_match.group(1).strip()
        
        key_points = []
        key_points_match = re.search(r'##\s*核心看点\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if key_points_match:
            points_text = key_points_match.group(1)
            for line in points_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
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


def is_topic_document(filename, topic_keywords):
    """判断文件名是否包含指定专题的关键词"""
    filename_lower = filename.lower()
    
    for kw in topic_keywords:
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


def extract_topic_by_keywords(input_dir, topic_config, output_dir=None):
    """
    按关键词配置提取指定专题文档并生成汇总报告
    
    Args:
        input_dir: summaries目录路径
        topic_config: 专题配置字典（含name、keywords等）
        output_dir: 输出目录（默认为 output/topic_summaries/{topic_name}）
    """
    topic_name = topic_config['name']
    topic_keywords = topic_config['keywords']
    
    date_str = datetime.now().strftime('%Y%m%d')
    
    if output_dir is None:
        output_dir = os.path.join('output', 'topic_summaries', topic_name)
    
    date_dir = os.path.join(output_dir, date_str)
    summaries_subdir = os.path.join(date_dir, 'summaries')
    os.makedirs(summaries_subdir, exist_ok=True)
    
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
    
    print(f"\n========== 提取【{topic_name}】专题 ==========")
    print(f"  筛选条件: 只处理 {date_str} 生成的文件")
    print(f"  今日文件数: {len(summary_files)}")
    
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
                'key_points': content['key_points']
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
        one_sentence_content += f"## {doc['name']}\n\n{doc['one_sentence']}\n\n"
    
    with open(os.path.join(date_dir, f'{topic_name}_一句话汇总_{date_str}.md'), 'w', encoding='utf-8') as f:
        f.write(one_sentence_content)
    
    key_points_content = f"# {topic_name}专题 · 核心论点汇总 {date_str}\n\n"
    for doc in doc_data_list:
        key_points_content += f"## {doc['name']}\n\n"
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
    
    return date_dir


def main():
    parser = argparse.ArgumentParser(
        description='专题提取工具 - 支持多专题配置（AI/新能源/医药/消费/科技/汽车/有色/煤炭/地产/银行）'
    )
    parser.add_argument('--input', '-i', help='输入summaries目录（默认自动找最新的）')
    parser.add_argument('--topic', '-t', action='append', 
                        help=f'提取的专题（可重复指定），支持：{", ".join(TOPIC_CONFIGS.keys())}（默认提取AI）')
    parser.add_argument('--list-topics', action='store_true', help='列出所有支持的专题')
    
    args = parser.parse_args()
    
    if args.list_topics:
        print("支持的专题列表:")
        for name, config in TOPIC_CONFIGS.items():
            print(f"  - {name}: {config['description']}")
            print(f"    关键词示例: {', '.join(config['keywords'][:5])}...")
        return
    
    input_dir = args.input if args.input else find_latest_summaries_dir()
    if not input_dir:
        print("❌ 未找到summaries目录，请指定--input参数")
        return
    
    topics = args.topic if args.topic else ['AI']
    
    for topic in topics:
        if topic not in TOPIC_CONFIGS:
            print(f"❌ 不支持的专题: {topic}")
            print(f"支持的专题: {', '.join(TOPIC_CONFIGS.keys())}")
            continue
        
        extract_topic_by_keywords(input_dir, TOPIC_CONFIGS[topic])
    
    print(f"\n✅ 共提取 {len(topics)} 个专题报告")


if __name__ == "__main__":
    main()
