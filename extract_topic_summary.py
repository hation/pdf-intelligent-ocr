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
import json
import urllib.request
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
        
        summary_tool = "未知"
        tool_match = re.search(r'\*\*总结工具\*\*[:：]\s*(.+)', content)
        if tool_match:
            summary_tool = tool_match.group(1).strip()
        
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
        'summary_tool': summary_tool,
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


FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")


def send_feishu_message(text):
    if not FEISHU_WEBHOOK:
        return False
    try:
        data = json.dumps({"msg_type": "text", "content": {"text": text}}).encode('utf-8')
        req = urllib.request.Request(FEISHU_WEBHOOK, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get('code') == 0 or result.get('StatusCode') == 0
    except Exception as e:
        print(f"  [飞书推送失败] {e}")
        return False


def extract_main_themes(doc_data_list, topic_name, max_themes=8):
    theme_keywords = {
        'AI': {
            '算力基建': ['算力', '光模块', 'PCB', 'HBM', '芯片', '半导体', 'GPU', '服务器', '数据中心', '液冷', '散热', 'AIDC', '超节点', 'MLCC', '电容'],
            '大模型&应用': ['大模型', 'LLM', 'GPT', 'Agent', '智能体', '应用', 'AIGC', '生成式', 'GEO', 'DeepSeek', 'Claude', 'Gemini', '豆包'],
            '具身智能&机器人': ['具身智能', '人形机器人', '机器人', '减速器', '电机', '灵巧手', '特斯拉', 'Optimus'],
            '国产替代&自主可控': ['国产', '自主可控', '信创', '国产替代', '国产算力', '昇腾', '华为', '韬定律'],
            '半导体&封装': ['半导体', '封装', '先进封装', 'CoWoS', '晶圆', '设备', '材料', '存储', 'HBM'],
            '脑机接口&前沿科技': ['脑机接口', '量子', '6G', '增强现实', 'VR', '元宇宙', '世界模型'],
            '出海&全球化': ['出海', '全球化', '海外', '全球', '东南亚', '欧洲', '美国'],
            'AI+行业': ['AI+', '赋能', '医疗', '教育', '金融', '制造', '工业', '政务', '消费', '汽车']
        },
        '新能源': {
            '光伏': ['光伏', '组件', '逆变器', 'TOPCon', 'HJT', '钙钛矿', 'N型', '装机'],
            '储能': ['储能', '大储', '户储', '储能电站', '储能装机', '液冷', '温控'],
            '锂电池': ['锂电池', '锂电', '动力电池', '正极', '负极', '电解液', '三元锂', '磷酸铁锂', '锂矿'],
            '新能源车': ['新能源车', '电动车', '智能驾驶', '智驾', '自动驾驶', '换电', '充电桩', '快充', '超充'],
            '氢能': ['氢能', '氢能源', '电解槽', '燃料电池'],
            '钠离子': ['钠离子', '钠电', '硬碳', '双铝箔'],
            '出海&全球化': ['出海', '全球化', '海外', '全球', '欧洲', '美国', '东南亚'],
            '材料&零部件': ['材料', '零部件', '复合集流体', '结构件', '热管理']
        }
    }

    themes = theme_keywords.get(topic_name, {})
    if not themes:
        return []

    theme_counts = {name: 0 for name in themes}
    theme_examples = {name: [] for name in themes}

    for doc in doc_data_list:
        text = doc['name'] + doc['one_sentence']
        for theme_name, keywords in themes.items():
            for kw in keywords:
                if kw in text:
                    theme_counts[theme_name] += 1
                    if len(theme_examples[theme_name]) < 2:
                        theme_examples[theme_name].append(doc['name'][:30])
                    break

    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    result = []
    for theme, count in sorted_themes:
        if count > 0 and len(result) < max_themes:
            examples = '、'.join(theme_examples[theme]) if theme_examples[theme] else ''
            result.append({'theme': theme, 'count': count, 'examples': examples})

    return result


def extract_core_insights(doc_data_list, topic_name, max_insights=3):
    insight_patterns = [
        r'(增速|增长|上涨|提升|扩大|加速|爆发|放量|突破|拐点|创历史新高|超预期)',
        r'(紧缺|涨价|供需缺口|供给紧张|产能不足|供不应求|量价齐升)',
        r'(推荐|看好|建议关注|受益|投资机会|价值重估|弹性|确定性)',
        r'(国产替代|自主可控|国产化|突破|卡脖子)',
        r'(政策|监管|出台|推动|支持|规划|战略)',
        r'(商业化|落地|量产|规模化|渗透率|出货)'
    ]
    
    scored = []
    for doc in doc_data_list:
        all_points = doc.get('key_points', []) + [doc['one_sentence']]
        
        best_point = None
        best_score = 0
        
        for point in all_points:
            score = 0
            for pattern in insight_patterns:
                score += len(re.findall(pattern, point))
            if score > best_score and len(point) > 30:
                best_score = score
                best_point = point
        
        if best_point and best_score >= 2:
            clean = best_point.strip()
            if len(clean) > 70:
                clean = clean[:68] + '...'
            scored.append({'text': clean, 'score': best_score})
    
    scored.sort(key=lambda x: x['score'], reverse=True)
    
    seen = set()
    unique = []
    for item in scored:
        key = item['text'][:30]
        if key not in seen:
            seen.add(key)
            unique.append(item['text'])
            if len(unique) >= max_insights:
                break
    
    return unique


def extract_stocks_and_sectors(doc_data_list, topic_name, max_sectors=5, max_stocks=8):
    sector_keywords = {
        '光模块': ['光模块', 'CPO', 'LPO', '光通信', '光芯片'],
        '算力租赁/IDC': ['算力租赁', 'IDC', '数据中心', 'AIDC', '液冷', '超节点'],
        'PCB/CCL': ['PCB', '印刷电路板', '覆铜板', 'CCL', '电子布', 'HDI'],
        '半导体/芯片': ['半导体', '芯片', 'GPU', 'CPU', 'HBM', '存储', '封装', '设备', '材料'],
        '人形机器人': ['人形机器人', '具身智能', '减速器', '丝杠', '电机', '灵巧手'],
        'AI应用': ['AI应用', '大模型', '智能体', 'Agent', 'AIGC', 'GEO'],
        '国产算力': ['国产算力', '昇腾', '华为', '国产替代', '自主可控'],
        '消费电子': ['消费电子', '手机', '终端', '苹果', '华为', 'MR', 'VR']
    }
    
    stock_pattern = r'([\u4e00-\u9fa5]{2,8}(?:科技|股份|电子|信息|智能|通信|半导体|光电|新材|材料|技术|集团|精密|装备|制造|能源|电气|动力))'
    
    stock_blacklist = {
        '具身智能', '人工智能', '消费电子', '工业软件', '支持智能',
        '其人工智能', '赋能具身智能', '半导体行业', '电子行业',
        '科技产业', '智能经济', '智能制造', '智能工厂',
        '智能驾驶', '智能座舱', '智能硬件', '智能终端'
    }
    
    sector_counts = {name: 0 for name in sector_keywords}
    stock_counts = {}
    
    for doc in doc_data_list:
        text = doc['name'] + doc['one_sentence'] + ' '.join(doc.get('key_points', []))
        
        for sector, keywords in sector_keywords.items():
            for kw in keywords:
                if kw in text:
                    sector_counts[sector] += 1
                    break
        
        stocks = re.findall(stock_pattern, text)
        for stock in stocks:
            if 2 <= len(stock) <= 6 and stock not in stock_blacklist:
                stock_counts[stock] = stock_counts.get(stock, 0) + 1
    
    top_sectors = [(s, c) for s, c in sector_counts.items() if c > 0]
    top_sectors.sort(key=lambda x: x[1], reverse=True)
    top_sectors = top_sectors[:max_sectors]
    
    top_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)
    top_stocks = [(s, c) for s, c in top_stocks if c >= 2][:max_stocks]
    
    return top_sectors, top_stocks


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
