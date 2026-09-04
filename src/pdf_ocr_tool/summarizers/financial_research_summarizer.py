#!/usr/bin/env python3
"""
财经研报结构化总结器 - 对研报/资讯生成结构化摘要
支持大模型(火山引擎方舟)与纯算法两种模式
"""

import os
import re
import json
import urllib.request
from datetime import datetime

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

# 方舟模型配置（支持通过 .env / 环境变量覆盖）
ARK_MODEL = os.environ.get("ARK_MODEL", "doubao-seed-2.0-pro")
ARK_BASE_URL = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/coding/v3")


class FinancialResearchSummarizer:
    """财经研报结构化总结器"""
    
    def __init__(self, use_llm=True):
        self.use_llm = use_llm and LLM_AVAILABLE and os.environ.get('OPENAI_API_KEY')
        self.summary_tool = "大模型(豆包)" if self.use_llm else "算法提取"
        
        if self.use_llm:
            self.llm_client = OpenAI(
                base_url=ARK_BASE_URL
            )
            print(f"✅ LLM模式已启用（{ARK_MODEL}）")
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
            date_str = datetime.now().strftime('%Y%m%d%H')
        
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
