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


class MarkdownFileSummarizer:
    """Markdown文件分析器"""
    
    def __init__(self):
        self.summarizer = AIContentSummarizer()
    
    def extract_text_from_markdown(self, md_text):
        """从Markdown中提取纯文本"""
        # 删除Markdown标题
        text = re.sub(r'#+\s.*', '', md_text)
        
        # 删除链接格式
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        
        # 删除图片格式
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
        
        # 删除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # 删除行内代码
        text = re.sub(r'`[^`]*`', '', text)
        
        return self.summarizer.clean_text(text)
    
    def process_markdown_file(self, file_path):
        """处理单个Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 提取文本
            text = self.extract_text_from_markdown(md_content)
            
            # 分析内容
            analysis = self.summarizer.generate_analysis_report(text)
            
            return analysis
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None
    
    def batch_process_markdown_files(self, directory):
        """批量处理Markdown文件"""
        results = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                file_path = os.path.join(directory, filename)
                
                print(f"正在分析: {filename}")
                
                analysis = self.process_markdown_file(file_path)
                
                if analysis:
                    analysis['filename'] = filename
                    results.append(analysis)
        
        return results
    
    def generate_batch_report(self, analyses, output_file):
        """生成批量分析报告"""
        if not analyses:
            return False
        
        report_content = f"# 每日PDF内容分析报告 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # 总体统计
        report_content += f"## 总体统计\n"
        report_content += f"- 分析文件数: {len(analyses)}\n"
        
        # 文件内容质量统计
        quality_counts = {
            '高质量': 0,
            '中等质量': 0,
            '低质量': 0
        }
        
        for analysis in analyses:
            char_count = analysis['statistics']['char_count']
            if char_count > 2000:
                quality_counts['高质量'] += 1
            elif char_count > 1000:
                quality_counts['中等质量'] += 1
            else:
                quality_counts['低质量'] += 1
        
        report_content += f"- 高质量内容: {quality_counts['高质量']}个文件\n"
        report_content += f"- 中等质量: {quality_counts['中等质量']}个文件\n"
        report_content += f"- 低质量内容: {quality_counts['低质量']}个文件\n\n"
        
        # 常见话题
        all_topics = []
        for analysis in analyses:
            if 'topics' in analysis and analysis['topics']:
                for topic in analysis['topics']:
                    all_topics.append(topic['main_topic'])
        
        topic_counts = Counter(all_topics)
        if topic_counts:
            top_topics = topic_counts.most_common(10)
            report_content += f"## 热门话题\n"
            for topic, count in top_topics:
                report_content += f"- {topic}: {count}个文件\n"
        
        report_content += f"\n## 文件详情分析\n"
        
        # 详细报告
        for analysis in analyses:
            filename = analysis['filename']
            
            report_content += f"\n### 文件: {filename}\n"
            report_content += f"**摘要:** {analysis['summary']}\n"
            
            if 'keywords' in analysis:
                report_content += f"**关键词:** {', '.join(analysis['keywords'][:10])}\n"
            
            if 'statistics' in analysis:
                stats = analysis['statistics']
                report_content += f"**字符数:** {stats['char_count']} | **单词数:** {stats['word_count']}\n"
        
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
