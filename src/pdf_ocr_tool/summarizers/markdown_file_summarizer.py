#!/usr/bin/env python3
"""
Markdown文件批量总结器 - 处理已解析的Markdown文档并生成总结
"""

import os
import re
import argparse
from datetime import datetime

from pdf_ocr_tool.summarizers.aicontent_summarizer import AIContentSummarizer
from pdf_ocr_tool.summarizers.financial_research_summarizer import FinancialResearchSummarizer


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
        output_file = args.output or os.path.join(args.input, f"summary_list_{datetime.now().strftime('%Y%m%d%H')}.md")
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
