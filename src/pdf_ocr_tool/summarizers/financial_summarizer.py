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
from collections import Counter
import math
from datetime import datetime
import statistics


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
    
    def __init__(self):
        self.sections = {
            '核心看点': ['公司', '产品', '客户', '订单', '产能', '认证', '供应链', '需求', '技术', '业务', '行业'],
            '关键数据': ['%', '亿元', '万元', '万吨', '吨', 'GWh', 'MW', 'GW', '202', '同比', '环比', '增长', '百吨', '满产', '稼动率'],
            '催化因素': ['放量', '投放', '测试', '认证', '通过', '订单', '需求', '推进', '进入', '供应链', '量产', '开发'],
            '风险提示': ['风险', '不构成', '公告', '公开报告', '为准', '波动', '不及预期']
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
        for keyword in keywords:
            if keyword.lower() in sentence.lower():
                score += 2
        if re.search(r'\d', sentence):
            score += 2
        if len(sentence) <= 120:
            score += 1
        if any(word in sentence for word in ['公司', '产品', '客户', '订单', '产能', '供应链']):
            score += 2
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
    
    def make_one_line_conclusion(self, title, highlights):
        if highlights:
            first = highlights[0]
            if len(first) > 90:
                first = first[:90] + '...'
            return first
        cleaned_title = re.sub(r'_hybrid|_tesseract|_liteparse|\.md$', '', title)
        return f"该文件主要围绕{cleaned_title}展开。"
    
    def summarize(self, filename, markdown_text, plain_text):
        text = self.normalize_text(plain_text)
        sentences = self.split_sentences(text)
        highlights = self.pick_sentences(sentences, self.sections['核心看点'], 5)
        key_data = self.pick_sentences(sentences, self.sections['关键数据'], 5)
        catalysts = self.pick_sentences(sentences, self.sections['催化因素'], 4)
        risks = self.pick_risk_sentences(sentences, 3)
        stocks = self.extract_stock_names(text)
        quality_score = self.extract_quality_score(markdown_text)
        parser = self.extract_parser(markdown_text)
        conclusion = self.make_one_line_conclusion(filename, highlights)
        quotes = highlights[:3] or sentences[:3]
        return {
            'one_line_conclusion': conclusion,
            'highlights': highlights,
            'key_data': key_data,
            'catalysts': catalysts,
            'risks': risks,
            'stocks': stocks,
            'quotes': quotes,
            'quality_score': quality_score,
            'parser': parser
        }


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
    
    def batch_process_markdown_files(self, directory):
        """批量处理Markdown文件"""
        results = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.md') and not filename.startswith(('structured_analysis', 'ai_analysis', 'daily_summary', 'content_analysis', 'optimization_report')):
                file_path = os.path.join(directory, filename)
                
                print(f"正在分析: {filename}")
                
                analysis = self.process_markdown_file(file_path)
                
                if analysis:
                    analysis['filename'] = filename
                    results.append(analysis)
        
        return results
    
    def format_list_section(self, title, items):
        """格式化结构化列表段落"""
        content = f"\n#### {title}\n"
        if not items:
            return content + "- 未提取到明确内容\n"
        for item in items:
            content += f"- {item}\n"
        return content
    
    def generate_batch_report(self, analyses, output_file):
        """生成批量分析报告"""
        if not analyses:
            return False
        
        report_content = f"# 每日PDF内容分析报告 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # 总体统计
        report_content += f"## 总体统计\n"
        report_content += f"- 分析文件数: {len(analyses)}\n\n"
        
        report_content += f"## 文件详情分析\n"
        
        # 详细报告
        for analysis in analyses:
            filename = analysis['filename']
            structured = analysis.get('structured_summary', {})
            
            report_content += f"\n### 文件: {filename}\n"
            
            if structured:
                report_content += f"\n#### 一句话总结\n{structured.get('one_line_conclusion', '未提取到有效结论')}\n"
                report_content += self.format_list_section('核心看点', structured.get('highlights', []))
            else:
                report_content += f"\n#### 一句话总结\n{analysis['summary']}\n"
                report_content += "\n#### 核心看点\n- 未提取到明确内容\n"
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"报告已保存到: {output_file}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="AI内容总结器 - 分析PDF处理结果并生成智能摘要"
    )
    
    parser.add_argument('input', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出文件路径')
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
        
        # 生成报告
        output_file = args.output or os.path.join(args.input, f"content_analysis_{datetime.now().strftime('%Y%m%d')}.md")
        summarizer.generate_batch_report(analyses, output_file)
    
    elif os.path.isfile(args.input):
        # 处理单个文件
        if args.input.endswith('.md'):
            analysis = summarizer.process_markdown_file(args.input)
            
            if analysis:
                print(f"\n=== 文件分析结果 ===")
                print(f"文件名: {args.input}")
                print(f"摘要: {analysis['summary']}")
                print(f"关键词: {', '.join(analysis['keywords'][:10])}")
                
                if 'statistics' in analysis:
                    stats = analysis['statistics']
                    print(f"字符数: {stats['char_count']}")
                    print(f"单词数: {stats['word_count']}")
                    print(f"句子数: {stats['sentence_count']}")
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
