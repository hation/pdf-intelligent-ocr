#!/usr/bin/env python3
"""
每日500个PDF处理系统 - 完整解决方案
包含：PDF识别、内容提取、AI分析和报告生成
"""

import os
import sys
import argparse
import time
import json
import logging
from datetime import datetime
import subprocess
import shutil
import tempfile

from pdf_ocr_tool.pipeline import pdf_processing_pipeline
from pdf_ocr_tool.summarizers import financial_summarizer as ai_content_summarizer


class DailyPDFProcessor:
    """每日PDF处理系统类"""
    
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp(prefix="pdf_processing_")
        self.logger.info(f"临时目录: {self.temp_dir}")
        
        # 固定缓存位置（在输出根目录）
        self.cache_file = self._get_cache_file()
    
    def _get_cache_file(self):
        """获取固定的缓存文件路径"""
        # 找到 output 根目录
        output_dir = self.config['output_dir']
        # 向上查找直到找到 daily 目录的父目录（output）
        while True:
            parent = os.path.dirname(output_dir)
            if os.path.basename(output_dir) == 'daily' or parent == output_dir:
                break
            output_dir = parent
        
        # 缓存文件放在 output 根目录
        return os.path.join(output_dir, '.pdf_parse_cache.json')
    
    def setup_logging(self):
        """设置日志系统"""
        log_dir = os.path.join(self.config['output_dir'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"daily_processor_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='a', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def prepare_directories(self):
        """准备目录结构"""
        directories = [
            self.config['output_dir'],
            os.path.join(self.config['output_dir'], 'processed'),
            os.path.join(self.config['output_dir'], 'reports'),
            os.path.join(self.config['output_dir'], 'failed')
        ]
        
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)
    
    def validate_input(self):
        """验证输入目录"""
        if not os.path.exists(self.config['input_dir']):
            self.logger.error(f"输入目录不存在: {self.config['input_dir']}")
            return False
        
        pdf_files = [f for f in os.listdir(self.config['input_dir']) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.logger.warning("输入目录中没有找到PDF文件")
            return False
        
        self.logger.info(f"找到 {len(pdf_files)} 个PDF文件需要处理")
        
        return True
    
    def run_processing_pipeline(self):
        """运行处理管道"""
        # 创建处理管道实例
        pipeline = pdf_processing_pipeline.PDFProcessingPipeline(self.config)
        
        # 传递固定缓存文件路径
        self.config['cache_file'] = self.cache_file
        
        success = pipeline.run_pipeline(
            self.config['input_dir'], 
            os.path.join(self.config['output_dir'], 'processed')
        )
        
        if success:
            # 生成每日报告
            pipeline.generate_summary_report(os.path.join(self.config['output_dir'], 'processed'))
        
        return success, pipeline
    
    def move_processed_files(self):
        """将已处理的PDF文件移动到B文件夹"""
        input_dir = self.config['input_dir']
        # B文件夹路径：input_dir的同级目录，命名为 files_processed
        processed_dir = os.path.join(os.path.dirname(input_dir), "files_processed")
        
        os.makedirs(processed_dir, exist_ok=True)
        
        # 获取已处理成功的文件列表
        processed_md_dir = os.path.join(self.config['output_dir'], 'processed')
        if not os.path.exists(processed_md_dir):
            self.logger.warning(f"处理目录不存在: {processed_md_dir}")
            return
        
        # 获取所有已生成的markdown文件名（不含扩展名）
        processed_files = set()
        for md_file in os.listdir(processed_md_dir):
            if md_file.endswith('.md'):
                # 移除 .md 扩展名
                base_name = md_file[:-3]
                # 移除可能的后缀如 _hybrid
                if '_hybrid' in base_name:
                    base_name = base_name.replace('_hybrid', '')
                elif '_tesseract' in base_name:
                    base_name = base_name.replace('_tesseract', '')
                elif '_liteparse' in base_name:
                    base_name = base_name.replace('_liteparse', '')
                processed_files.add(base_name)
        
        # 移动对应的PDF文件
        moved_count = 0
        for pdf_file in os.listdir(input_dir):
            if pdf_file.lower().endswith('.pdf'):
                pdf_base_name = pdf_file[:-4]  # 移除 .pdf 扩展名
                if pdf_base_name in processed_files:
                    src_path = os.path.join(input_dir, pdf_file)
                    dst_path = os.path.join(processed_dir, pdf_file)
                    
                    try:
                        shutil.move(src_path, dst_path)
                        self.logger.info(f"已移动文件: {pdf_file} -> {processed_dir}")
                        moved_count += 1
                    except Exception as e:
                        self.logger.error(f"移动文件失败 {pdf_file}: {e}")
        
        self.logger.info(f"共移动 {moved_count} 个文件到 {processed_dir}")
    
    def run_ai_analysis(self):
        """运行AI内容分析"""
        processed_dir = os.path.join(self.config['output_dir'], 'processed')
        summary_list_file = os.path.join(self.config['output_dir'], 'reports', 
                                     f"summary_list_{datetime.now().strftime('%Y%m%d')}.md")
        summary_dir = os.path.join(self.config['output_dir'], 'summaries')
        
        summarizer = ai_content_summarizer.MarkdownFileSummarizer()
        analyses = summarizer.batch_process_markdown_files(processed_dir)
        
        if analyses:
            summarizer.generate_summary_outputs(analyses, summary_list_file, summary_dir)
            self.logger.info(f"总结清单已保存到: {summary_list_file}")
            self.logger.info(f"单文件总结已保存到: {summary_dir}")
        else:
            self.logger.warning("没有找到可分析的文件")
    
    def clean_up(self):
        """清理临时文件"""
        try:
            shutil.rmtree(self.temp_dir)
            self.logger.info("临时目录已清理")
        except Exception as e:
            self.logger.warning(f"清理临时文件失败: {e}")
    
    def run_optimization_analysis(self):
        """运行处理优化分析"""
        processed_dir = os.path.join(self.config['output_dir'], 'processed')
        reports_dir = os.path.join(self.config['output_dir'], 'reports')
        
        if not os.path.exists(processed_dir):
            return
        
        md_files = [f for f in os.listdir(processed_dir) if f.endswith('.md')]
        
        if not md_files:
            return
        
        optimization_report = {
            'total_files': len(md_files),
            'avg_char_count': 0,
            'avg_processing_time': 0,
            'files_per_minute': 0,
            'strategies_used': {},
            'file_sizes': []
        }
        
        char_counts = []
        
        for md_file in md_files:
            file_path = os.path.join(processed_dir, md_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                char_counts.append(len(content))
            except Exception as e:
                self.logger.error(f"读取文件时出错 {md_file}: {e}")
        
        if char_counts:
            optimization_report['avg_char_count'] = sum(char_counts) / len(char_counts)
        
        self.generate_optimization_report(optimization_report, reports_dir)
    
    def generate_optimization_report(self, report, reports_dir):
        """生成优化报告"""
        report_file = os.path.join(reports_dir, f"optimization_report_{datetime.now().strftime('%Y%m%d')}.md")
        
        content = f"# 每日处理优化报告 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        content += f"## 处理统计\n"
        content += f"- 成功处理文件: {report['total_files']}\n"
        content += f"- 平均字符数: {report['avg_char_count']:.0f}\n"
        
        content += f"\n## 优化建议\n"
        content += f"根据处理结果，建议:\n\n"
        content += f"- 如果平均字符数 < 200，可能需要调整OCR策略\n"
        content += f"- 如果处理时间过长，考虑调整工作进程数\n"
        content += f"- 对于频繁失败的文件，检查源文件质量\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"优化报告已生成: {os.path.basename(report_file)}")
    
    def run_all(self):
        """运行完整的每日处理流程"""
        self.logger.info("=== 开始每日PDF处理系统 ===")
        
        try:
            # 准备目录
            self.prepare_directories()
            
            # 验证输入
            if not self.validate_input():
                self.logger.warning("没有找到有效的PDF文件，处理流程将终止")
                return False
            
            # 运行处理管道
            processing_start_time = time.time()
            self.logger.info("正在运行处理管道...")
            pipeline_success, pipeline = self.run_processing_pipeline()
            
            if pipeline_success:
                self.logger.info("处理管道运行成功")
            else:
                self.logger.error("处理管道运行失败")
                return False
            
            # 运行AI内容分析
            if not self.config.get('no_ai', False):
                self.logger.info("正在运行AI内容分析...")
                self.run_ai_analysis()
            else:
                self.logger.info("已跳过AI内容分析")
            
            # 运行优化分析
            self.logger.info("正在生成优化报告...")
            self.run_optimization_analysis()
            
            # 移动已处理的文件到B文件夹
            self.logger.info("正在移动已处理的文件...")
            self.move_processed_files()
            
            total_time = time.time() - processing_start_time
            self.logger.info(f"=== 处理完成 ===")
            self.logger.info(f"总处理时间: {total_time:.2f} 秒")
            self.logger.info(f"输出目录: {self.config['output_dir']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {e}")
            import traceback
            self.logger.error(f"错误详情: {traceback.format_exc()}")
            return False
            
        finally:
            self.clean_up()


def main():
    parser = argparse.ArgumentParser(
        description="每日500个PDF处理系统 - 完整解决方案"
    )
    
    parser.add_argument('input_dir', help='输入目录（包含PDF文件）')
    parser.add_argument('output_dir', help='输出目录（保存处理结果）')
    parser.add_argument('--workers', type=int, default=8, 
                       help='并行工作进程数（默认: 8）')
    parser.add_argument('--strategy', choices=['auto', 'tesseract', 'liteparse', 'optimized'], 
                       default='auto', help='处理策略（默认: 自动选择）')
    parser.add_argument('--no-ai', action='store_true', 
                       help='禁用AI内容分析')
    parser.add_argument('--min-score', type=int, default=60,
                       help='进入总结的最低解析质量评分（默认: 60）')
    parser.add_argument('--force', action='store_true',
                       help='忽略缓存，强制重新解析PDF')
    
    args = parser.parse_args()
    
    # 配置
    config = {
        'input_dir': args.input_dir,
        'output_dir': args.output_dir,
        'workers': args.workers,
        'strategy': args.strategy,
        'min_score': args.min_score,
        'force': args.force,
        'no_ai': args.no_ai
    }
    
    # 创建处理器实例
    processor = DailyPDFProcessor(config)
    
    # 运行处理
    success = processor.run_all()
    
    if success:
        return 0
    else:
        return 1


if __name__ == "__main__":
    main()
