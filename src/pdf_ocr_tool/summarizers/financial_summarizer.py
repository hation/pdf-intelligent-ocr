#!/usr/bin/env python3
"""
AI内容总结模块 - 分析PDF处理结果并生成智能摘要
使用自然语言处理技术提取核心信息
"""

import os
import sys
import argparse
import re
import json
import time
import urllib.request
from collections import Counter
import math
from datetime import datetime
import statistics

# LLM 相关导入（支持火山引擎方舟）
try:
    from openai import OpenAI
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  未安装openai库，将使用纯算法模式")

# 支持 .env 文件加载
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 方舟模型配置
ARK_MODEL = "doubao-seed-2.0-pro"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"


class AIContentSummarizer:
    """AI内容总结器类"""
    
    def __init__(self):
        self.keywords = []
        self.sentences = []
        self.word_frequencies = Counter()
        self.important_sentences = []
    
    def clean_text(self, text):
        """清洁文本，删除多余的空格和换行"""
        # 替换多个换行和空格
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s+', '\n', text)
        return text.strip()
    
    def extract_sentences(self, text):
        """从文本中提取句子"""
        # 分割句子的正则表达式（中文和英文）
        sentence_pattern = r'[^\。\！\？\!\?\.]+[\。\！\？\!\?\.]+'
        sentences = re.findall(sentence_pattern, text)
        
        # 过滤太短的句子
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        self.sentences = sentences
        return sentences
    
    def extract_keywords(self, text):
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤常用词
        stop_words = {'the', 'and', 'is', 'are', 'in', 'to', 'for', 'that', 'with', 'this', 'as', 
                     'on', 'by', 'from', 'at', 'it', 'you', 'we', 'they', 'he', 'she', 'but'}
        
        filtered_words = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # 计算词频
        word_counts = Counter(filtered_words)
        
        # 提取频率最高的词
        top_words = word_counts.most_common(50)
        
        self.word_frequencies = word_counts
        self.keywords = [word for word, count in top_words if count >= 2]
        
        return self.keywords
    
    def calculate_sentence_importance(self, text):
        """计算句子重要性分数"""
        if not self.sentences or not self.keywords:
            return []
        
        importance_scores = []
        
        for i, sentence in enumerate(self.sentences):
            score = 0
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            
            # 关键词匹配得分
            keyword_count = len(sentence_words.intersection(self.keywords))
            score += keyword_count * 3
            
            # 句子长度得分（适中的长度更好）
            word_count = len(sentence.split())
            if 8 <= word_count <= 25:
                score += 2
            elif 5 <= word_count < 8 or 25 < word_count <= 35:
                score += 1
            
            # 位置得分（首段落和尾段落更重要）
            if i < 3 or i > len(self.sentences) - 4:
                score += 2
            
            importance_scores.append((i, score))
        
        # 排序并获取最重要的句子
        sorted_sentences = sorted(importance_scores, key=lambda x: x[1], reverse=True)
        
        self.important_sentences = [self.sentences[i] for i, score in sorted_sentences if score > 0]
        
        return self.important_sentences
    
    def generate_summary(self, text, summary_length=5):
        """生成文本摘要"""
        text = self.clean_text(text)
        
        # 提取句子和关键词
        self.extract_sentences(text)
        self.extract_keywords(text)
        
        if not self.sentences:
            return "无法提取有效内容"
        
        # 计算句子重要性
        important_sentences = self.calculate_sentence_importance(text)
        
        # 确保我们有足够的句子来生成摘要
        if len(important_sentences) < summary_length:
            selected_sentences = important_sentences
        else:
            # 选择最重要的句子
            selected_sentences = important_sentences[:summary_length]
        
        # 按原始顺序排序
        selected_indices = [i for i, sent in enumerate(self.sentences) if sent in selected_sentences]
        selected_indices.sort()
        sorted_summary = [self.sentences[i] for i in selected_indices]
        
        return ' '.join(sorted_summary)
    
    def analyze_content(self, text):
        """分析文本内容"""
        text = self.clean_text(text)
        
        self.extract_sentences(text)
        self.extract_keywords(text)
        
        # 计算统计数据
        stats = {
            'sentence_count': len(self.sentences),
            'keyword_count': len(self.keywords),
            'word_count': len(text.split()),
            'char_count': len(text),
            'unique_word_count': len(self.word_frequencies)
        }
        
        # 词频分布分析
        if self.word_frequencies:
            frequency_list = list(self.word_frequencies.values())
            stats['average_word_frequency'] = statistics.mean(frequency_list)
            stats['median_word_frequency'] = statistics.median(frequency_list)
        
        return stats
    
    def detect_topics(self, text, topic_count=5):
        """检测主要话题"""
        # 简单的话题检测
        if not self.keywords or topic_count <= 0:
            return []
        
        # 分析关键词模式
        topic_clusters = []
        
        # 简单的话题分组
        for word in self.keywords[:topic_count]:
            # 找到包含该关键词的句子
            related_sentences = [s for s in self.sentences if word in s.lower()]
            
            if related_sentences:
                # 从相关句子中提取其他关键词
                related_keywords = []
                for sent in related_sentences:
                    words = set(re.findall(r'\b\w+\b', sent.lower()))
                    related_keywords.extend(words)
                
                related_keywords = [w for w in related_keywords if w in self.keywords and w != word]
                
                topic_clusters.append({
                    'main_topic': word,
                    'related_keywords': list(set(related_keywords))[:3],
                    'sentence_count': len(related_sentences)
                })
        
        return topic_clusters
    
    def generate_analysis_report(self, text):
        """生成完整的分析报告"""
        text = self.clean_text(text)
        
        # 分析内容
        stats = self.analyze_content(text)
        topics = self.detect_topics(text)
        
        # 生成报告
        report = {}
        report['summary'] = self.generate_summary(text)
        report['statistics'] = stats
        report['keywords'] = self.keywords
        report['topics'] = topics
        
        return report


class FinancialResearchSummarizer:
    """财经研报结构化总结器"""
    
    def __init__(self, use_llm=True):
        self.use_llm = use_llm and LLM_AVAILABLE and os.environ.get('OPENAI_API_KEY')
        self.summary_tool = "大模型(豆包)" if self.use_llm else "算法提取"
        
        if self.use_llm:
            self.llm_client = OpenAI(
                base_url=ARK_BASE_URL
            )
            print("✅ LLM模式已启用（豆包-1.5-pro）")
        else:
            import warnings
            warnings.warn("⚠️  未检测到 OPENAI_API_KEY，当前使用纯算法模式，总结质量会显著下降！")
            print("⚠️  ⚠️  ⚠️  未检测到 OPENAI_API_KEY，当前使用纯算法模式，总结质量会显著下降！ ⚠️  ⚠️  ⚠️")
        
        self.sections = {
            # ========== 核心看点（扩充） ==========
            '核心看点': [
                '公司', '产品', '客户', '订单', '产能', '认证', '供应链', '需求', '技术', '业务', '行业',
                '技术壁垒', '研发投入', '专利', '发明专利', '核心技术',
                '产能扩张', '新产能', '投产', '量产', '达产', '满产',
                '客户导入', '切入', '进入供应链', '通过认证', '供应商',
                '国产替代', '进口替代', '自主可控', '技术突破', '技术革新'
            ],
            
            # ========== 新增：AI与科技（优先级最高） ==========
            'AI科技': [
                '人工智能', '大模型', '算力', 'GPU', '光模块', 'AI芯片', '具身智能',
                'ChatGPT', 'GPT', 'AGI', '算力网络', '数据中心', '液冷', 'PCB',
                '英伟达', '昇腾', '寒武纪', '海光', '推理', '训练', 'Transformer',
                'Agent', '智能体', '应用落地', '渗透率', 'AI+', '数字经济',
                '半导体', '封装', 'Chiplet', '先进封装', 'CoWoS', 'HBM', 'DDR',
                '服务器', '交换机', '光通信', 'CPO', '800G', '400G', '1.6T',
                '人形机器人', '工业机器人', '机器视觉', '边缘计算', '云计算'
            ],
            
            # ========== 扩充：关键数据 ==========
            '关键数据': [
                '%', '亿元', '万元', '万吨', '吨', 'GWh', 'MW', 'GW', '202', '同比', '环比', '增长', '百吨', '满产', '稼动率',
                '亿美元', '万', '亿', '百万', '市占率', '渗透率', '增长率',
                '毛利率', '净利率', 'ROE', 'PE', 'PB', 'PS', 'EPS', '估值',
                'CAGR', '复合增长率', 'YoY', 'QoQ', '累计',
                '产能', '产量', '出货量', '营收', '收入', '利润', '净利润',
                '产能利用率', '利用率', '开工率',
                '万片', '万颗', '万套', '万辆', '万台'
            ],
            
            # ========== 催化因素（扩充） ==========
            '催化因素': [
                '放量', '投放', '测试', '认证', '通过', '订单', '需求', '推进', '进入', '供应链', '量产', '开发',
                '突破', '落地', '上线', '发布', '投产', '试产', '量产线',
                '中标', '中标通知书', '合同', '签约', '合作', '战略合作',
                '利好', '超预期', '超指引', '超市场预期'
            ],
            
            # ========== 新增：政策导向 ==========
            '政策导向': [
                '政策', '规划', '十四五', '十五五', '目录', '指引', '意见', '通知',
                '国务院', '工信部', '发改委', '证监会', '监管', '合规', '标准制定',
                '国产替代', '自主可控', '卡脖子', '进口替代', '自主创新', '专精特新',
                '扶持', '补贴', '税收优惠', '产业基金', '政府采购',
                '新基建', '数字经济', '双碳', '碳中和', '碳达峰', '能源转型'
            ],
            
            # ========== 新增：竞争格局 ==========
            '竞争格局': [
                '市占率', '市场份额', 'CR3', 'CR5', 'CR10', '龙头', '寡头', '垄断',
                '竞争格局', '集中度', '分散', '整合', '并购', '收购', '兼并重组',
                '进入壁垒', '护城河', '壁垒', '差异化', '性价比', '价格战', '份额'
            ],
            
            # ========== 新增：估值与财务 ==========
            '估值水平': [
                '估值', 'PE', 'PB', 'PS', '市值', '溢价', '折价', '低估', '高估',
                '合理估值', '安全边际', '性价比',
                '毛利率', '净利率', 'ROE', 'ROA', 'ROIC', '现金流', '负债率',
                '股息率', '分红', '回购', '增发', '配股', '可转债', '股权激励'
            ],
            
            # ========== 风险提示（扩充） ==========
            '风险提示': [
                '风险', '不构成', '公告', '公开报告', '为准', '波动', '不及预期',
                '不确定性', '风险因素', '提示', '审慎', '谨慎',
                '下行风险', '上行风险', '业绩承压', '压力'
            ],
            
            # ========== 新增：降权关键词（负分） ==========
            '降权关键词': [
                '免责声明', '风险提示', '不构成投资', '仅供参考', '数据来源',
                '本文摘自', '资料来源', '公开信息', '仅供学习', '转载自',
                '版权声明', '来源于网络', '侵删', '本报告仅供',
                '请务必阅读', '投资有风险', '入市需谨慎', '仅代表个人'
            ]
        }
        self.ocr_corrections = {
            '移动率': '稼动率',
            '称动率': '稼动率',
            '电路铜和范': '电路铜箔',
            '电了略铜和范': '电路铜箔',
            'ji单': '订单',
            '林单': '订单',
            '开和发': '开发',
            '公 司': '公司',
            '产 品': '产品',
            '取 得': '取得',
            '产 能': '产能',
            '3hm': '3μm',
            '3.5hm': '3.5μm',
            'HYLP': 'HVLP',
            'HVEP': 'HVLP',
            '委头部': '等头部',
            '正称步提升': '正稳步提升',
            '还悔持续提升': '还将持续提升'
        }
    
    def normalize_text(self, text):
        text = re.sub(r'\r\n?', '\n', text)
        for wrong, right in self.ocr_corrections.items():
            text = text.replace(wrong, right)
        text = re.sub(r'===\s*第\s*\d+\s*页\s*===', '\n', text)
        text = re.sub(r'市场研报资讯[^\n。；;]*', '', text)
        text = re.sub(r'国际资本市场研报资讯[^\n。；;]*', '', text)
        text = re.sub(r'\b20\d{2}\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}\b', '', text)
        text = re.sub(r'\b星期[一二三四五六日天]\b', '', text)
        text = re.sub(r'分\|', '', text)
        text = re.sub(r'@\s*风险提示', '风险提示', text)
        text = re.sub(r'\s*[|]\s*', '，', text)
        text = re.sub(r'\bpet\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bWBA:?\b', '', text)
        text = re.sub(r'^[\s，。；;：:]*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def split_sentences(self, text):
        text = self.normalize_text(text)
        text = re.sub(r'([^。！？；;])\n([^。！？；;])', r'\1 \2', text)
        parts = re.split(r'(?<=[。！？；;])|\n+', text)
        sentences = []
        for part in parts:
            sentence = self.clean_sentence(part)
            if not self.is_noise_sentence(sentence):
                sentences.append(sentence)
        return sentences
    
    def clean_sentence(self, sentence):
        sentence = re.sub(r'^[人这]+家', '这家', sentence)
        sentence = re.sub(r'\s+', ' ', sentence).strip(' ，,。；;：:')
        return sentence
    
    def is_noise_sentence(self, sentence):
        if len(sentence) < 12:
            return True
        if re.fullmatch(r'[A-Za-z0-9\s:：,，.-]+', sentence):
            return True
        if sentence.startswith('【'):
            return True
        if '风险提示' in sentence and '不构成投研观点' in sentence:
            return False
        return False
    
    def score_sentence(self, sentence, keywords):
        score = 0
        
        # ========== 第一步：先降权（套话减分） ==========
        for keyword in self.sections['降权关键词']:
            if keyword.lower() in sentence.lower():
                score -= 5  # 套话直接扣5分！
        
        # ========== 第二步：按不同类别关键词加权（动态权重） ==========
        # AI科技关键词权重最高（+3分/个）
        for keyword in self.sections['AI科技']:
            if keyword.lower() in sentence.lower():
                score += 3
        
        # 关键数据权重高（+3分/个）
        for keyword in self.sections['关键数据']:
            if keyword.lower() in sentence.lower():
                score += 3
        
        # 政策导向权重高（+2分/个）
        for keyword in self.sections['政策导向']:
            if keyword.lower() in sentence.lower():
                score += 2
        
        # 催化因素权重高（+2分/个）
        for keyword in self.sections['催化因素']:
            if keyword.lower() in sentence.lower():
                score += 2
        
        # 其他分类权重（+1分/个）
        other_keywords = self.sections['核心看点'] + self.sections['竞争格局'] + self.sections['估值水平'] + self.sections['风险提示']
        for keyword in other_keywords:
            if keyword.lower() in sentence.lower():
                score += 1
        
        # ========== 第三步：通用加分规则 ==========
        # 包含数字加分（数据重要）
        if re.search(r'\d', sentence):
            score += 2
        
        # 句子长度适中加分
        if 20 <= len(sentence) <= 120:
            score += 1
        
        # 非常短的句子可能没意义，扣分
        if len(sentence) < 15:
            score -= 3
        
        return score
    
    def pick_sentences(self, sentences, keywords, limit=4):
        scored = []
        seen = set()
        for index, sentence in enumerate(sentences):
            cleaned = self.clean_sentence(sentence)
            fingerprint = re.sub(r'\W+', '', cleaned.lower())[:50]
            if fingerprint in seen or self.is_noise_sentence(cleaned):
                continue
            seen.add(fingerprint)
            score = self.score_sentence(cleaned, keywords)
            if score > 0:
                scored.append((score, index, cleaned))
        scored.sort(key=lambda item: (-item[0], item[1]))
        picked = sorted(scored[:limit], key=lambda item: item[1])
        return [item[2] for item in picked]
    
    def pick_risk_sentences(self, sentences, limit=3):
        risks = []
        seen = set()
        for sentence in sentences:
            cleaned = self.clean_sentence(sentence)
            if not any(keyword in cleaned for keyword in self.sections['风险提示']):
                continue
            fingerprint = re.sub(r'\W+', '', cleaned.lower())[:50]
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            risks.append(cleaned)
            if len(risks) >= limit:
                break
        return risks
    
    def extract_quality_score(self, markdown_text):
        match = re.search(r'质量评分:\s*(\d+)', markdown_text)
        if match:
            return int(match.group(1))
        return None
    
    def extract_parser(self, markdown_text):
        match = re.search(r'解析方法:\s*([^\n]+)', markdown_text)
        if match:
            return match.group(1).strip()
        return ''
    
    def extract_stock_names(self, text):
        matches = re.findall(r'关联个股\s*([^\n]+)', text)
        stocks = []
        for match in matches:
            cleaned = match.strip()
            if cleaned:
                stocks.append(cleaned)
        return stocks[:3]
    
    def is_ebook(self, text):
        ebook_markers = ['目录', 'Contents', 'Table of Contents', '前言', '序言', '版权', 'Chapter', '章节']
        marker_count = sum(1 for marker in ebook_markers if marker.lower() in text.lower())
        chapter_matches = re.findall(r'(?:第\s*[一二三四五六七八九十百零0-9]+\s*[章节篇部]|Chapter\s+\d+|\d+(?:\.\d+){0,2}\s+[^\n]{2,60})', text, flags=re.IGNORECASE)
        return marker_count >= 2 and len(chapter_matches) >= 5
    
    def clean_toc_item(self, line):
        line = re.sub(r'^[#\-*•\s]+', '', line.strip())
        line = re.sub(r'\s*[.·…]{2,}\s*\d+\s*$', '', line)
        line = re.sub(r'\s+\d+\s*$', '', line)
        line = re.sub(r'\s+', ' ', line)
        return line.strip(' ，,。；;')
    
    def is_toc_item(self, line):
        if len(line) < 3 or len(line) > 90:
            return False
        if re.fullmatch(r'\d+', line):
            return False
        patterns = [
            r'^第\s*[一二三四五六七八九十百零0-9]+\s*(?:部分|章节|章|节|篇|部)',
            r'^Chapter\s+\d+',
            r'^\d+(?:\.\d+){0,2}\s+\S+',
            r'^[一二三四五六七八九十]+[、.．]\s*\S+'
        ]
        return any(re.search(pattern, line, flags=re.IGNORECASE) for pattern in patterns)
    
    def extract_ebook_toc(self, text, limit=30):
        lines = [self.clean_toc_item(line) for line in text.splitlines()]
        toc_lines = []
        in_toc = False
        non_toc_count = 0
        seen = set()
        for line in lines:
            if not line:
                continue
            if re.fullmatch(r'(目录|Contents|Table of Contents)', line, flags=re.IGNORECASE):
                in_toc = True
                non_toc_count = 0
                continue
            if in_toc:
                if self.is_toc_item(line):
                    if line not in seen:
                        toc_lines.append(line)
                        seen.add(line)
                    non_toc_count = 0
                else:
                    non_toc_count += 1
                if non_toc_count >= 8 or len(toc_lines) >= limit:
                    break
        if len(toc_lines) < 5:
            for line in lines:
                if self.is_toc_item(line) and line not in seen:
                    toc_lines.append(line)
                    seen.add(line)
                if len(toc_lines) >= limit:
                    break
        return toc_lines
    
    def make_ebook_one_line_conclusion(self, title, toc_items):
        cleaned_title = re.sub(r'_hybrid|_tesseract|_liteparse|\.md$', '', title)
        topics = []
        for item in toc_items[:6]:
            topic = re.sub(r'^(第\s*[一二三四五六七八九十百零0-9]+\s*(?:部分|章节|章|节|篇|部)|Chapter\s+\d+|\d+(?:\.\d+){0,2}|[一二三四五六七八九十]+[、.．])\s*', '', item, flags=re.IGNORECASE)
            topic = topic.strip(' ：:，,。；;')
            if topic:
                topics.append(topic)
        if topics:
            return f"该电子书围绕{cleaned_title}展开，主要覆盖{'、'.join(topics[:4])}等内容。"
        return f"该电子书围绕{cleaned_title}展开，主要内容可从目录结构把握。"
    
    def llm_generate_one_line_summary(self, title, text):
        """使用LLM生成真正的一句话总结"""
        if not self.use_llm:
            return None
        
        try:
            # 取前5000字符，避免token超限
            short_text = text[:5000] if len(text) > 5000 else text
            
            # 清理文件名
            clean_title = re.sub(r'_hybrid|_tesseract|_liteparse|\.md$', '', title)
            
            prompt = f"""文档标题：{clean_title}

文档内容：
{short_text}

请用200字左右总结核心，必须含1个关键数据/结论，不要背景，不要评价，直接输出。"""
            
            response = self.llm_client.chat.completions.create(
                model=ARK_MODEL,
                temperature=0.3,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": "你是一位专业的财经研报分析师，擅长用一句话概括研报核心。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"  ⚠️  LLM调用失败: {e}")
            return None
    
    def llm_generate_highlights(self, title, text):
        """使用LLM生成核心看点"""
        if not self.use_llm:
            return None
        
        try:
            # 取前5000字符，避免token超限
            short_text = text[:5000] if len(text) > 5000 else text
            
            # 清理文件名
            clean_title = re.sub(r'_hybrid|_tesseract|_liteparse|\.md$', '', title)
            
            prompt = f"""文档标题：{clean_title}

文档内容：
{short_text}

请提取本文的5个核心论点，每点用一句话概括，不要背景铺垫，直接列出。"""
            
            response = self.llm_client.chat.completions.create(
                model=ARK_MODEL,
                temperature=0.3,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "你是一位专业的财经研报分析师，擅长提取核心论点。"},
                    {"role": "user", "content": prompt}
                ]
            )
            
            highlights_text = response.choices[0].message.content.strip()
            
            # 解析返回的内容，按行分割，提取非空行
            highlights = []
            for line in highlights_text.split('\n'):
                line = line.strip()
                # 去掉编号（如 "1. "、"（1）" 等格式）
                line = re.sub(r'^\d+[\.、]\s*', '', line)
                line = re.sub(r'^[\(（]\d+[\)）]\s*', '', line)
                line = line.strip('- ').strip('• ').strip()
                if line and len(line) > 10:
                    highlights.append(line)
            
            return highlights[:5] if highlights else None
            
        except Exception as e:
            print(f"  ⚠️  LLM调用失败: {e}")
            return None
    
    def make_one_line_conclusion(self, title, highlights, full_text=None):
        # 如果有全文且启用了LLM，优先用LLM生成
        if self.use_llm and full_text:
            llm_result = self.llm_generate_one_line_summary(title, full_text)
            if llm_result:
                return llm_result
        
        # 回退到算法模式
        if highlights:
            first = highlights[0]
            if len(first) > 90:
                first = first[:90] + '...'
            return first
        cleaned_title = re.sub(r'_hybrid|_tesseract|_liteparse|\.md$', '', title)
        return f"该文件主要围绕{cleaned_title}展开。"
    
    def summarize(self, filename, markdown_text, plain_text):
        text = self.normalize_text(plain_text)
        quality_score = self.extract_quality_score(markdown_text)
        parser = self.extract_parser(markdown_text)
        toc_items = self.extract_ebook_toc(text)
        
        # ========== 电子书模式也保留8个维度，不全是空了！ ==========
        if toc_items and self.is_ebook(text):
            sentences = self.split_sentences(text)
            # 电子书也优先用LLM
            conclusion = self.make_one_line_conclusion(filename, toc_items, text)
            # 优先用LLM生成核心看点
            if self.use_llm:
                llm_highlights = self.llm_generate_highlights(filename, text)
                highlights = llm_highlights if llm_highlights else toc_items
            else:
                highlights = toc_items
            return {
                'one_line_conclusion': conclusion,
                'highlights': highlights,
                'ai_tech': self.pick_sentences(sentences, self.sections['AI科技'], 4),
                'key_data': self.pick_sentences(sentences, self.sections['关键数据'], 5),
                'catalysts': self.pick_sentences(sentences, self.sections['催化因素'], 4),
                'policy': self.pick_sentences(sentences, self.sections['政策导向'], 3),
                'competition': self.pick_sentences(sentences, self.sections['竞争格局'], 3),
                'valuation': self.pick_sentences(sentences, self.sections['估值水平'], 3),
                'risks': self.pick_risk_sentences(sentences, 3),
                'stocks': self.extract_stock_names(text),
                'quotes': toc_items[:3],
                'quality_score': quality_score,
                'parser': parser,
                'summary_tool': self.summary_tool
            }
        
        sentences = self.split_sentences(text)
        
        # 优先用LLM生成核心看点
        if self.use_llm:
            llm_highlights = self.llm_generate_highlights(filename, text)
            if llm_highlights:
                highlights = llm_highlights
            else:
                highlights = self.pick_sentences(sentences, self.sections['核心看点'], 5)
        else:
            highlights = self.pick_sentences(sentences, self.sections['核心看点'], 5)
        
        conclusion = self.make_one_line_conclusion(filename, highlights, text)
        quotes = highlights[:3] or sentences[:3]
        
        return {
            'one_line_conclusion': conclusion,
            'highlights': highlights,
            'ai_tech': self.pick_sentences(sentences, self.sections['AI科技'], 4),
            'key_data': self.pick_sentences(sentences, self.sections['关键数据'], 5),
            'catalysts': self.pick_sentences(sentences, self.sections['催化因素'], 4),
            'policy': self.pick_sentences(sentences, self.sections['政策导向'], 3),
            'competition': self.pick_sentences(sentences, self.sections['竞争格局'], 3),
            'valuation': self.pick_sentences(sentences, self.sections['估值水平'], 3),
            'risks': self.pick_risk_sentences(sentences, 3),
            'stocks': self.extract_stock_names(text),
            'quotes': quotes,
            'quality_score': quality_score,
            'parser': parser,
            'summary_tool': self.summary_tool
        }

    def generate_daily_highlight_report(self, summary_dir, output_file, date_str=None):
        """生成每日重点汇总文档（大模型二次提炼）
        
        Args:
            summary_dir: summaries目录
            output_file: 输出文件路径
            date_str: 日期字符串
        """
        if not self.use_llm:
            print("⚠️  未启用大模型，跳过每日重点汇总生成")
            return False
        
        if not os.path.isdir(summary_dir):
            print(f"⚠️  summaries目录不存在: {summary_dir}")
            return False
        
        if date_str is None:
            date_str = datetime.now().strftime('%Y%m%d')
        
        summary_files = sorted([f for f in os.listdir(summary_dir) if f.endswith('_summary.md')])
        if not summary_files:
            print("⚠️  没有找到总结文件，跳过每日重点汇总")
            return False
        
        all_content = ''
        for sf in summary_files:
            sf_path = os.path.join(summary_dir, sf)
            try:
                with open(sf_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                doc_name = sf.replace('_summary.md', '')
                for suffix in ['_hybrid', '_tesseract', '_liteparse']:
                    if doc_name.endswith(suffix):
                        doc_name = doc_name[:-len(suffix)]
                        break
                
                tool = ''
                m = re.search(r'\*\*总结工具\*\*[:：]\s*(.+)', text)
                if m:
                    tool = m.group(1).strip()
                
                one_sentence = ''
                m = re.search(r'##\s*一句话总结\s*\n\s*(.*?)(?=\n##|\Z)', text, re.DOTALL)
                if m:
                    one_sentence = m.group(1).strip()
                
                key_points = ''
                m = re.search(r'##\s*核心看点\s*\n\s*(.*?)(?=\n##|\Z)', text, re.DOTALL)
                if m:
                    key_points = m.group(1).strip()
                
                all_content += f'【文档】{doc_name}\n'
                all_content += f'【总结工具】{tool}\n'
                all_content += f'【一句话总结】{one_sentence}\n'
                all_content += f'【核心看点】{key_points}\n'
                all_content += '---\n'
            except Exception:
                continue
        
        if not all_content.strip():
            print("⚠️  无法收集总结内容，跳过每日重点汇总")
            return False
        
        prompt = f"""你是一位专业的投研编辑，需要将一批研报和资讯的总结整合成一份"每日重点汇总"文档。

请阅读以下{len(summary_files)}份文档的总结内容，生成一份结构清晰、重点突出的汇总文档。

文档内容：
{all_content}

---

请按照以下结构输出（Markdown格式）：

# 每日重点汇总 {date_str}

## 一、今日核心要闻（10-15条）
从所有文档中提炼出最有价值、最值得关注的10~15条核心观点/事件/数据，每条用一句话概括，按重要性排序。每条标注所属行业标签（如【AI】【半导体】【机器人】【医药】【新能源】【消费】【宏观】等）。

## 二、行业分类速览
将所有文档按行业分类整理，每个行业下列出文档名称，以及1~2句核心内容摘要。分类包括但不限于：
- AI与算力
- 半导体与先进封装
- 机器人与具身智能
- 新能源与汽车
- 医药与生物科技
- 消费与白酒
- 宏观与策略
- 其他

## 三、深度报告精选（5~10份）
从所有文档中挑选出5~10份最有深度、最值得花时间细读的研报/行业报告，每份给出：
- 文档名称
- 推荐理由（为什么值得读）
- 3~5条核心看点

## 四、今日数据亮点
提取文档中出现的关键数据（增速、规模、估值、订单等），用列表形式呈现。

注意：
1. 内容要客观、精炼，基于原文总结，不要凭空编造
2. 不要用表格格式，全部用标题+段落+列表
3. 语言风格偏向投资研究报告风格，专业但不晦涩
4. 总字数控制在5000字以内
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=ARK_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=8000,
            )
            result = response.choices[0].message.content
            
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            
            print(f"每日重点汇总已保存到: {output_file}")
            
            # 推送今日核心要闻到飞书
            self.push_highlight_to_feishu(result, date_str, len(summary_files), output_file)
            
            return True
        except Exception as e:
            print(f"❌ 生成每日重点汇总失败: {e}")
            return False
    
    def push_highlight_to_feishu(self, highlight_content, date_str, total_docs, output_file):
        """将今日核心要闻推送到飞书
        
        Args:
            highlight_content: 每日重点汇总全文
            date_str: 日期
            total_docs: 总文档数
            output_file: 输出文件路径
        """
        feishu_webhook = os.environ.get("FEISHU_WEBHOOK", "")
        if not feishu_webhook:
            print("⚠️  未配置FEISHU_WEBHOOK，跳过飞书推送")
            return False
        
        core_news = ''
        m = re.search(
            r'##\s*一、今日核心要闻.*?\n\s*(.*?)(?=\n##|\Z)',
            highlight_content, re.DOTALL
        )
        if m:
            core_news = m.group(1).strip()
        
        if not core_news:
            print("⚠️  未找到今日核心要闻内容，跳过飞书推送")
            return False
        
        lines = core_news.split('\n')
        news_items = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            line = re.sub(r'^\d+[\.、]\s*', '', line)
            line = re.sub(r'^[-*]\s*', '', line)
            if line:
                news_items.append(line)
                if len(news_items) >= 12:
                    break
        
        if not news_items:
            print("⚠️  核心要闻解析为空，跳过飞书推送")
            return False
        
        news_text = '\n'.join([f'{i+1}. {item}' for i, item in enumerate(news_items)])
        
        feishu_text = (
            f'📰 每日重点汇总 {date_str}\n\n'
            f'今日处理PDF：{total_docs} 份\n'
            f'核心要闻：{len(news_items)} 条\n\n'
            f'{news_text}\n\n'
            f'📂 完整报告：{output_file}'
        )
        
        try:
            data = json.dumps({"msg_type": "text", "content": {"text": feishu_text}}).encode('utf-8')
            req = urllib.request.Request(feishu_webhook, data=data, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                success = result.get('code') == 0 or result.get('StatusCode') == 0
                if success:
                    print("📨 飞书推送成功（每日核心要闻）")
                else:
                    print(f"⚠️  飞书推送返回异常: {result}")
                return success
        except Exception as e:
            print(f"❌ 飞书推送失败: {e}")
            return False

class MarkdownFileSummarizer:
    """Markdown文件分析器"""
    
    def __init__(self):
        self.summarizer = AIContentSummarizer()
        self.financial_summarizer = FinancialResearchSummarizer()
    
    def extract_markdown_content(self, md_text):
        """提取Markdown正文内容"""
        if '## 内容' in md_text:
            text = md_text.split('## 内容', 1)[1]
        else:
            text = md_text
        text = re.sub(r'#+\s.*', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]*`', '', text)
        return text.strip()
    
    def extract_text_from_markdown(self, md_text):
        """从Markdown中提取纯文本"""
        return self.summarizer.clean_text(self.extract_markdown_content(md_text))
    
    def process_markdown_file(self, file_path):
        """处理单个Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 提取文本
            raw_text = self.extract_markdown_content(md_content)
            text = self.summarizer.clean_text(raw_text)
            
            # 分析内容
            analysis = self.summarizer.generate_analysis_report(text)
            analysis['structured_summary'] = self.financial_summarizer.summarize(
                os.path.basename(file_path),
                md_content,
                raw_text
            )
            
            return analysis
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None
    
    def batch_process_markdown_files(self, directory, only_new=False, summaries_dir=None, workers=6, write_incrementally=True, batch_write_size=50):
        """批量处理Markdown文件（支持只处理新文件+并行处理+批量增量写入）

        Args:
            directory: processed目录
            only_new: 是否只处理未生成总结的新文件
            summaries_dir: summaries目录（用于判断是否已处理 + 增量写入目标）
            workers: 并行线程数（LLM是IO密集型，用线程池）
            write_incrementally: 是否边处理边写入单文件总结（默认True）
            batch_write_size: 每处理多少份批量写入一次（默认50份）
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import threading

        write_lock = threading.Lock()

        # 收集需要处理的文件
        files_to_process = []
        for filename in os.listdir(directory):
            if not filename.endswith('.md'):
                continue
            if filename.startswith(('structured_analysis', 'ai_analysis', 'daily_summary', 'content_analysis', 'optimization_report')):
                continue

            # 如果只处理新文件，检查是否已有总结
            if only_new and summaries_dir:
                summary_name = self.sanitize_summary_filename(filename)
                summary_path = os.path.join(summaries_dir, summary_name)
                if os.path.exists(summary_path):
                    continue  # 已有总结，跳过

            files_to_process.append(filename)

        if not files_to_process:
            print(f"✓ 没有需要处理的文件（所有文件已有总结）")
            return []

        print(f"📊 共 {len(files_to_process)} 个文件需要处理，使用 {workers} 个并行线程")

        if write_incrementally and summaries_dir:
            os.makedirs(summaries_dir, exist_ok=True)

        results = []
        completed_count = 0
        total_count = len(files_to_process)
        batch_buffer = []  # 批量写入缓冲区

        # 使用多线程并行处理（LLM是IO密集型）
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任务
            future_to_filename = {
                executor.submit(self.process_markdown_file, os.path.join(directory, filename)): filename
                for filename in files_to_process
            }

            # 按完成顺序收集结果
            for future in as_completed(future_to_filename):
                filename = future_to_filename[future]
                completed_count += 1

                try:
                    analysis = future.result()
                    if analysis:
                        analysis['filename'] = filename
                        results.append(analysis)
                        batch_buffer.append(analysis)
                        print(f"  [{completed_count}/{total_count}] ✓ {filename[:50]}")

                        # 每 batch_write_size 份批量写入一次
                        if write_incrementally and summaries_dir and len(batch_buffer) >= batch_write_size:
                            with write_lock:
                                for ana in batch_buffer:
                                    self._write_single_summary(ana, summaries_dir)
                                batch_buffer.clear()
                except Exception as e:
                    print(f"  [{completed_count}/{total_count}] ✗ {filename[:50]}: {e}")

        # 处理完后写入剩余的缓冲区
        if write_incrementally and summaries_dir and batch_buffer:
            for ana in batch_buffer:
                self._write_single_summary(ana, summaries_dir)
            batch_buffer.clear()

        print(f"\n✓ 并行处理完成: {len(results)}/{total_count} 成功")
        return results

    def _write_single_summary(self, analysis, summary_dir):
        """写入单个总结文件（用于增量写入）"""
        filename = analysis['filename']
        one_line, highlights = self.get_structured_fields(analysis)
        output_file = os.path.join(summary_dir, self.sanitize_summary_filename(filename))
        tool = analysis.get("structured_summary", {}).get("summary_tool", "未知")
        content = f"# {filename}\n\n"
        content += f"**总结工具**：{tool}\n\n"
        content += f"## 一句话总结\n\n{one_line}\n\n"
        content += "## 核心看点\n\n"
        if highlights:
            for item in highlights:
                content += f"- {item}\n"
        else:
            content += "- 未提取到明确内容\n"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def format_list_section(self, title, items):
        """格式化结构化列表段落"""
        content = f"\n#### {title}\n"
        if not items:
            return content + "- 未提取到明确内容\n"
        for item in items:
            content += f"- {item}\n"
        return content
    
    def get_structured_fields(self, analysis):
        """提取一句话总结和核心看点"""
        structured = analysis.get('structured_summary', {})
        if structured:
            one_line = structured.get('one_line_conclusion', '未提取到有效结论')
            highlights = structured.get('highlights', [])
        else:
            one_line = analysis.get('summary', '未提取到有效结论')
            highlights = []
        return one_line, highlights
    
    def sanitize_summary_filename(self, filename):
        """生成单文件总结文件名"""
        base_name = os.path.splitext(filename)[0]
        base_name = re.sub(r'_(hybrid|tesseract|liteparse)$', '', base_name)
        return f"{base_name}_summary.md"
    
    def generate_summary_list_report(self, analyses, output_file, summary_dir=None):
        """生成一句话总结清单（累积模式：包含当天所有已总结的文档）
        
        Args:
            analyses: 本次处理的文档列表
            output_file: 清单输出路径
            summary_dir: summaries目录，用于累积所有已总结文档
        """
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        
        all_summaries = []
        
        if summary_dir and os.path.exists(summary_dir):
            for fname in os.listdir(summary_dir):
                if not fname.endswith('_summary.md'):
                    continue
                summary_path = os.path.join(summary_dir, fname)
                try:
                    with open(summary_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    one_sentence = "暂无"
                    one_sentence_match = re.search(r'##\s*一句话总结\s*\n\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
                    if one_sentence_match:
                        one_sentence = one_sentence_match.group(1).strip()
                    
                    summary_tool = ""
                    tool_match = re.search(r'\*\*总结工具\*\*[:：]\s*(.+)', content)
                    if tool_match:
                        summary_tool = tool_match.group(1).strip()
                    
                    doc_name = fname.replace('_summary.md', '')
                    for suffix in ['_hybrid', '_tesseract', '_liteparse']:
                        if doc_name.endswith(suffix):
                            doc_name = doc_name[:-len(suffix)]
                            break
                    
                    all_summaries.append({
                        'filename': doc_name,
                        'one_line': one_sentence,
                        'summary_tool': summary_tool
                    })
                except Exception:
                    continue
        else:
            for analysis in analyses:
                filename = analysis['filename']
                one_line, _ = self.get_structured_fields(analysis)
                tool = analysis.get("structured_summary", {}).get("summary_tool", "")
                clean_name = filename
                for suffix in ['_hybrid', '_tesseract', '_liteparse']:
                    if clean_name.endswith(suffix):
                        clean_name = clean_name[:-len(suffix)]
                        break
                all_summaries.append({
                    'filename': clean_name,
                    'one_line': one_line,
                    'summary_tool': tool
                })
        
        # 生成报告（标题+段落格式，适配不支持表格的阅读器）
        date_str = datetime.now().strftime('%Y%m%d')
        report_content = f"# 总结清单 {date_str}\n\n"
        report_content += f"**文档总数**：{len(all_summaries)} 份\n\n---\n\n"
        for summary in all_summaries:
            filename = summary['filename']
            one_line = summary['one_line']
            tool = summary.get('summary_tool', '')
            report_content += f"## {filename}\n\n"
            if tool:
                report_content += f"*总结工具：{tool}*\n\n"
            report_content += f"{one_line}\n\n---\n\n"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"总结清单已保存到: {output_file}（共 {len(all_summaries)} 份文档）")
        return True
    
    
    def generate_single_summary_files(self, analyses, summary_dir):
        """为每个Markdown生成单独总结文件"""
        if not analyses:
            return []
        os.makedirs(summary_dir, exist_ok=True)
        output_files = []
        for analysis in analyses:
            filename = analysis['filename']
            one_line, highlights = self.get_structured_fields(analysis)
            output_file = os.path.join(summary_dir, self.sanitize_summary_filename(filename))
            tool = analysis.get("structured_summary", {}).get("summary_tool", "未知")
            content = f"# {filename}\n\n"
            content += f"**总结工具**：{tool}\n\n"
            content += f"## 一句话总结\n\n{one_line}\n\n"
            content += "## 核心看点\n\n"
            if highlights:
                for item in highlights:
                    content += f"- {item}\n"
            else:
                content += "- 未提取到明确内容\n"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            output_files.append(output_file)
        print(f"单文件总结已保存到: {summary_dir}")
        return output_files
    
    def generate_summary_outputs(self, analyses, summary_list_file, summary_dir):
        """生成总结清单和单文件总结"""
        list_result = self.generate_summary_list_report(analyses, summary_list_file, summary_dir)
        single_files = self.generate_single_summary_files(analyses, summary_dir)
        return list_result and bool(single_files)
    
    def generate_batch_report(self, analyses, output_file):
        """兼容旧接口：生成一句话总结清单"""
        summary_dir = os.path.join(os.path.dirname(os.path.dirname(output_file)), 'summaries')
        return self.generate_summary_outputs(analyses, output_file, summary_dir)


def main():
    parser = argparse.ArgumentParser(
        description="AI内容总结器 - 分析PDF处理结果并生成智能摘要"
    )
    
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='总结清单输出路径')
    parser.add_argument('--summary-dir', help='单文件总结输出目录')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    
    args = parser.parse_args()
    
    summarizer = MarkdownFileSummarizer()
    
    # 处理输入
    if os.path.isdir(args.input):
        # 批量处理目录
        if args.verbose:
            print(f"正在批量分析目录: {args.input}")
        
        analyses = summarizer.batch_process_markdown_files(args.input)
        
        if not analyses:
            print("没有找到可处理的Markdown文件")
            return 1
        
        # 生成总结清单和单文件总结
        output_file = args.output or os.path.join(args.input, f"summary_list_{datetime.now().strftime('%Y%m%d')}.md")
        summary_dir = args.summary_dir or os.path.join(os.path.dirname(args.input), 'summaries')
        summarizer.generate_summary_outputs(analyses, output_file, summary_dir)
    
    elif os.path.isfile(args.input):
        # 处理单个文件
        if args.input.endswith('.md'):
            analysis = summarizer.process_markdown_file(args.input)
            
            if analysis:
                one_line, highlights = summarizer.get_structured_fields(analysis)
                print(f"\n=== 文件总结结果 ===")
                print(f"文件名: {args.input}")
                print(f"一句话总结: {one_line}")
                print("核心看点:")
                if highlights:
                    for item in highlights:
                        print(f"- {item}")
                else:
                    print("- 未提取到明确内容")
            else:
                print("无法分析该文件")
        
        else:
            print("不支持的文件格式，请提供Markdown文件")
            return 1
    
    else:
        print("输入路径无效")
        return 1
    
    return 0


if __name__ == "__main__":
    main()
