#!/usr/bin/env python3
"""
PDF 自动化处理管道 - 每天处理500个PDF文件的高效解决方案
整合OCR识别、内容提取和智能总结功能
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
import json

# 导入项目核心功能
from parse_with_liteparse_ocr import parse_pdf_with_liteparse_ocr
from batch_ocr_optimized import batch_process as optimized_batch_process
from batch_ocr_accurate import batch_process as accurate_batch_process
from pdf_summarizer import extract_text_from_pdf, analyze_text
from direct_tesseract_ocr import tesseract_ocr_on_pdf


class PDFProcessingPipeline:
    """PDF处理管道类，管理整个处理流程"""
    
    def __init__(self, config):
        self.config = config
        self.setup_logging()
        self.stats = {
            'total_files': 0,
            'success_count': 0,
            'failed_count': 0,
            'processing_time': 0,
            'file_stats': []
        }
    
    def setup_logging(self):
        """设置日志系统"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f"processing_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='a', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_pdf_files(self, input_dir):
        """查找所有PDF文件"""
        pdf_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    pdf_files.append(file_path)
        
        self.logger.info(f"找到 {len(pdf_files)} 个PDF文件需要处理")
        self.stats['total_files'] = len(pdf_files)
        return pdf_files
    
    def determine_processing_strategy(self, filename):
        """根据文件特征确定处理策略"""
        file_size = os.path.getsize(filename)
        
        # 策略决策逻辑
        if file_size < 100 * 1024:  # 小于100KB的小文件，可能是扫描件
            return 'tesseract'
        elif file_size < 1 * 1024 * 1024:  # 小于1MB的中等文件
            return 'liteparse_ocr'
        else:  # 大于1MB的大文件，可能是文档
            return 'optimized_batch'
    
    def process_single_file(self, filename, output_dir):
        """处理单个PDF文件的统一接口"""
        start_time = time.time()
        
        try:
            strategy = self.determine_processing_strategy(filename)
            
            self.logger.info(f"处理文件: {os.path.basename(filename)} ({strategy}策略)")
            
            # 根据策略选择处理方法
            if strategy == 'tesseract':
                # 直接使用Tesseract OCR
                result = tesseract_ocr_on_pdf(filename)
                if result:
                    # 保存到Markdown
                    output_file = os.path.join(output_dir, 
                                              f"{os.path.splitext(os.path.basename(filename))[0]}.md")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result)
                    self.logger.info(f"成功保存结果: {os.path.basename(output_file)}")
                    return True, 'tesseract', len(result)
            
            elif strategy == 'liteparse_ocr':
                # 使用LiteParse OCR
                from parse_with_liteparse_ocr import ensure_directory_exists
                ensure_directory_exists(output_dir)
                
                from liteparse import LiteParse
                parser = LiteParse(ocr_enabled=True, quiet=True)
                result = parser.parse(filename)
                
                if result and result.text:
                    output_file = os.path.join(output_dir, 
                                              f"{os.path.splitext(os.path.basename(filename))[0]}.md")
                    md_content = f"# {os.path.splitext(os.path.basename(filename))[0]}\n\n"
                    md_content += f"## 文件统计\n"
                    md_content += f"页数: {len(result.pages)}\n"
                    md_content += f"文本长度: {len(result.text)} 字符\n"
                    md_content += f"处理策略: LiteParse OCR\n"
                    md_content += f"\n## 内容\n{result.text}"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    
                    self.logger.info(f"成功保存结果: {os.path.basename(output_file)}")
                    return True, 'liteparse_ocr', len(result.text)
            
            elif strategy == 'optimized_batch':
                # 使用优化批量处理方案
                temp_output = os.path.join(output_dir, 'temp')
                os.makedirs(temp_output, exist_ok=True)
                
                from batch_ocr_optimized import process_file_task
                config = {
                    'dpi': 200,
                    'cutoff': 3,
                    'threshold': 180,
                    'lang': 'chi_sim+eng',
                    'num_workers': 1
                }
                
                result, success = process_file_task((filename, temp_output, config))
                if success:
                    # 读取保存的Markdown文件
                    output_file = os.path.join(temp_output, 
                                              f"{os.path.splitext(os.path.basename(filename))[0]}.md")
                    if os.path.exists(output_file):
                        with open(output_file, 'r', encoding='utf-8') as f:
                            text = f.read()
                        return True, 'optimized_batch', len(text)
                    else:
                        return False, 'optimized_batch', 0
            
            return False, strategy, 0
            
        except Exception as e:
            self.logger.error(f"处理文件失败 {os.path.basename(filename)}: {e}")
            return False, 'error', 0
    
    def run_pipeline(self, input_dir, output_dir):
        """运行完整的处理管道"""
        self.logger.info("=== 开始PDF处理管道 ===")
        start_time = time.time()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        # 创建临时配置字典，不修改原配置
        temp_config = self.config.copy()
        temp_config['output_dir'] = output_dir
        
        # 查找所有PDF文件
        pdf_files = self.find_pdf_files(input_dir)
        
        if not pdf_files:
            self.logger.warning("未找到PDF文件需要处理")
            return False
        
        # 使用多进程处理
        self.logger.info(f"使用 {self.config['workers']} 个工作进程")
        
        processed_files = []
        with ProcessPoolExecutor(max_workers=self.config['workers']) as executor:
            # 提交任务
            future_to_file = {executor.submit(self.process_single_file, file, output_dir): file for file in pdf_files}
            
            # 获取结果
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    success, strategy, char_count = future.result()
                    processed_files.append({
                        'filename': file,
                        'success': success,
                        'strategy': strategy,
                        'char_count': char_count
                    })
                    
                    if success:
                        self.stats['success_count'] += 1
                        self.stats['file_stats'].append({
                            'filename': os.path.basename(file),
                            'strategy': strategy,
                            'char_count': char_count,
                            'processing_time': time.time() - start_time
                        })
                    else:
                        self.stats['failed_count'] += 1
                        
                except Exception as e:
                    self.logger.error(f"处理文件时发生异常 {os.path.basename(file)}: {e}")
                    self.stats['failed_count'] += 1
        
        # 计算处理时间
        self.stats['processing_time'] = time.time() - start_time
        
        # 生成报告
        self.generate_report(output_dir)
        
        self.logger.info("=== 处理完成 ===")
        return True
    
    def generate_report(self, output_dir):
        """生成处理报告"""
        report_file = os.path.join(output_dir, 
                                 f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # 计算平均速度
        if self.stats['processing_time'] > 0:
            files_per_minute = self.stats['success_count'] / (self.stats['processing_time'] / 60)
        else:
            files_per_minute = 0
            
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': self.stats['total_files'],
            'success_count': self.stats['success_count'],
            'failed_count': self.stats['failed_count'],
            'processing_time': self.stats['processing_time'],
            'files_per_minute': files_per_minute,
            'average_time_per_file': self.stats['processing_time'] / self.stats['total_files'] if self.stats['total_files'] > 0 else 0,
            'detailed_stats': self.stats['file_stats']
        }
        
        # 保存到self.stats中用于后续访问
        self.stats['files_per_minute'] = files_per_minute
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印简洁报告
        self.logger.info(f"成功处理: {self.stats['success_count']} 个文件")
        self.logger.info(f"处理失败: {self.stats['failed_count']} 个文件")
        self.logger.info(f"总处理时间: {self.stats['processing_time']:.2f} 秒")
        self.logger.info(f"平均速度: {self.stats['files_per_minute']:.1f} 文件/分钟")
        self.logger.info(f"报告已保存到: {os.path.basename(report_file)}")
    
    def generate_summary_report(self, output_dir):
        """生成每日总结报告"""
        # 查找所有Markdown文件，包括temp子目录中的
        markdown_files = []
        
        # 检查主输出目录
        if os.path.exists(output_dir):
            for f in os.listdir(output_dir):
                if f.endswith('.md') and os.path.isfile(os.path.join(output_dir, f)):
                    markdown_files.append(os.path.join(output_dir, f))
        
        # 检查temp子目录（optimized_batch策略的输出）
        temp_dir = os.path.join(output_dir, 'temp')
        if os.path.exists(temp_dir):
            for f in os.listdir(temp_dir):
                if f.endswith('.md') and os.path.isfile(os.path.join(temp_dir, f)):
                    markdown_files.append(os.path.join(temp_dir, f))
        
        self.logger.info(f"找到 {len(markdown_files)} 个处理完成的Markdown文件")
        
        # 分析内容
        all_texts = []
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    all_texts.append(f.read())
            except Exception as e:
                self.logger.error(f"读取文件失败 {os.path.basename(md_file)}: {e}")
        
        # 生成汇总报告到reports目录
        reports_dir = os.path.join(os.path.dirname(output_dir), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        summary_file = os.path.join(reports_dir, f"daily_summary_{datetime.now().strftime('%Y%m%d')}.md")
        
        summary_content = f"# 每日PDF处理报告 {datetime.now().strftime('%Y-%m-%d')}\n\n"
        summary_content += f"## 总体统计\n"
        summary_content += f"- 总文件数: {self.stats['total_files']}\n"
        summary_content += f"- 成功处理: {self.stats['success_count']}\n"
        summary_content += f"- 处理失败: {self.stats['failed_count']}\n"
        summary_content += f"- 处理时间: {self.stats['processing_time']:.2f} 秒\n"
        summary_content += f"- 平均速度: {self.stats['files_per_minute']:.1f} 文件/分钟\n\n"
        
        summary_content += f"## 详细文件列表\n"
        for file_stat in self.stats['file_stats']:
            summary_content += f"- **{file_stat['filename']}** ({file_stat['strategy']}): {file_stat['char_count']} 字符\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        self.logger.info(f"每日报告已保存到: {os.path.basename(summary_file)}")


def main():
    parser = argparse.ArgumentParser(
        description="PDF自动化处理管道 - 每天处理500个PDF文件的高效解决方案"
    )
    
    parser.add_argument('input_dir', help='输入目录（包含PDF文件）')
    parser.add_argument('output_dir', help='输出目录（保存结果）')
    parser.add_argument('--workers', type=int, default=8, 
                       help='并行工作进程数（默认: 8）')
    parser.add_argument('--strategy', choices=['auto', 'tesseract', 'liteparse', 'optimized'], 
                       default='auto', help='处理策略（默认: 自动选择）')
    
    args = parser.parse_args()
    
    # 验证输入
    if not os.path.exists(args.input_dir):
        print(f"错误: 输入目录 '{args.input_dir}' 不存在")
        return 1
    
    # 配置
    config = {
        'workers': args.workers,
        'strategy': args.strategy,
        'output_dir': args.output_dir
    }
    
    # 创建并运行处理管道
    pipeline = PDFProcessingPipeline(config)
    success = pipeline.run_pipeline(args.input_dir, args.output_dir)
    
    if success:
        pipeline.generate_summary_report(args.output_dir)
        print(f"\n处理完成！报告已生成在: {args.output_dir}")
        return 0
    else:
        print("处理过程中发生错误")
        return 1


if __name__ == "__main__":
    main()
