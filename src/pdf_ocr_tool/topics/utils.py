#!/usr/bin/env python3
"""
专题提取工具函数 - 文件读取、专题文档判断、目录查找、飞书推送
"""

import os
import re
import json
import urllib.request


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
