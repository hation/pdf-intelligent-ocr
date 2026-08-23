#!/usr/bin/env python3
"""
专题分析器 - 提取主要方向、核心观点、受益方向与标的
"""

import re


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
