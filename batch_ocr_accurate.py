#!/usr/bin/env python3
"""
高精度批量OCR处理脚本 - 以识别质量为首要目标
特点：
- 最高DPI设置，确保最佳识别质量
- 完整的图像预处理，优化OCR识别
- 智能识别，只处理需要OCR的页面
- 支持多进程并行处理
- 实时进度监控
- 精确的字符识别（适合文字密集型文档）
"""

from pdf2image import convert_from_path
import pytesseract
import PIL.ImageOps
import os
import sys
from concurrent.futures import ProcessPoolExecutor
import argparse
import shutil
from pathlib import Path

# 高精度配置
HIGH_ACCURACY_CONFIG = {
    'dpi': 400,  # 最高DPI，确保最佳识别质量
    'cutoff': 2,  # 适中的对比度增强强度
    'threshold': 150,  # 标准二值化阈值
    'lang': 'chi_sim+eng',
    'num_workers': 2  # 减少进程数，避免资源竞争
}

def has_selectable_text(filename):
    """
    快速检查PDF是否包含可选文本（不需要OCR）
    """
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(filename)
        total_text = ""
        
        # 检查前几页
        check_pages = min(3, len(reader.pages))
        for i in range(check_pages):
            text = reader.pages[i].extract_text()
            if text:
                total_text += text.strip()
        
        # 判断是否有足够的文本
        if len(total_text) > 100:
            return True
        
        return False
    except Exception as e:
        print(f"检查可选文本时出错 {filename}: {e}")
        return False

def high_accuracy_ocr_process(filename, dpi, cutoff, threshold, lang):
    """
    高精度OCR处理函数
    """
    try:
        # 将PDF转换为图像（最高分辨率）
        images = convert_from_path(filename, dpi=dpi, grayscale=True)
        
        full_text = []
        
        for i, img in enumerate(images, 1):
            # 完整图像预处理
            enhanced_img = img
            
            # 对比度增强
            enhanced_img = PIL.ImageOps.autocontrast(enhanced_img, cutoff=cutoff)
            
            # 标准二值化处理
            enhanced_img = enhanced_img.convert('L').point(lambda x: 0 if x < threshold else 255, '1')
            
            # 进行OCR识别
            text = pytesseract.image_to_string(enhanced_img, lang=lang)
            
            if text.strip():
                full_text.append(f"=== 第 {i} 页 ===\n{text.strip()}")
        
        return '\n\n'.join(full_text)
        
    except Exception as e:
        print(f"处理文件失败 {filename}: {e}")
        return None

def save_to_markdown(text, filename, output_dir):
    """
    保存结果到Markdown文件
    """
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/{os.path.splitext(os.path.basename(filename))[0]}.md"
    
    md_content = f"# {os.path.splitext(os.path.basename(filename))[0]}\n\n"
    md_content += f"## 文件统计\n"
    md_content += f"解析方法: 高精度Tesseract OCR识别\n"
    md_content += f"配置: DPI={HIGH_ACCURACY_CONFIG['dpi']}, 对比度增强={HIGH_ACCURACY_CONFIG['cutoff']}%, 二值化阈值={HIGH_ACCURACY_CONFIG['threshold']}\n"
    md_content += f"字符数: {len(text)}\n"
    md_content += f"单词数: {len(text.split())}\n\n"
    
    md_content += f"## 内容\n"
    md_content += text
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_file

def process_file_task(file_info):
    """
    单个文件处理任务
    """
    filename, output_dir, config = file_info
    
    print(f"开始处理: {os.path.basename(filename)}")
    
    try:
        # 首先检查是否有可选文本
        if has_selectable_text(filename):
            print(f"文件 {os.path.basename(filename)} 包含可选文本，跳过OCR")
            return filename, False
        
        # 使用高精度OCR处理
        text = high_accuracy_ocr_process(
            filename, 
            config['dpi'], 
            config['cutoff'], 
            config['threshold'], 
            config['lang']
        )
        
        if text:
            save_to_markdown(text, filename, output_dir)
            print(f"完成: {os.path.basename(filename)} ({len(text)}字符)")
            return filename, True
        else:
            print(f"警告: 未识别到文本 {os.path.basename(filename)}")
            return filename, False
            
    except Exception as e:
        print(f"处理失败 {os.path.basename(filename)}: {e}")
        return filename, False

def batch_process(directory, output_dir, config, recursive=False):
    """
    批量处理指定目录下的PDF文件
    """
    # 查找所有PDF文件
    pdf_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            if file.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory, file)):
                pdf_files.append(os.path.join(directory, file))
    
    print(f"找到 {len(pdf_files)} 个PDF文件")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 准备任务信息
    tasks = [(f, output_dir, config) for f in pdf_files]
    
    # 使用多进程并行处理
    success_count = 0
    failed_count = 0
    
    with ProcessPoolExecutor(max_workers=config['num_workers']) as executor:
        results = list(executor.map(process_file_task, tasks))
        
    # 统计结果
    for filename, success in results:
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\n处理完成:")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    
    return success_count, failed_count

def main():
    parser = argparse.ArgumentParser(description="高精度PDF批量OCR处理工具")
    parser.add_argument("input_dir", help="输入目录（包含PDF文件）")
    parser.add_argument("output_dir", help="输出目录（保存Markdown结果）")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归扫描子目录")
    parser.add_argument("-w", "--workers", type=int, default=2, help="并行工作进程数（默认: 2）")
    parser.add_argument("-d", "--dpi", type=int, default=400, help="DPI设置（默认: 400）")
    parser.add_argument("-c", "--cutoff", type=int, default=2, help="对比度增强强度（默认: 2）")
    parser.add_argument("-t", "--threshold", type=int, default=150, help="二值化阈值（默认: 150）")
    
    args = parser.parse_args()
    
    # 更新配置
    config = HIGH_ACCURACY_CONFIG.copy()
    config['num_workers'] = args.workers
    config['dpi'] = args.dpi
    config['cutoff'] = args.cutoff
    config['threshold'] = args.threshold
    
    # 执行处理
    try:
        success, failed = batch_process(args.input_dir, args.output_dir, config, args.recursive)
        return 0 if success > 0 else 1
    except Exception as e:
        print(f"批量处理失败: {e}")
        return 1

if __name__ == "__main__":
    # 检查依赖
    if not shutil.which("tesseract"):
        print("错误: 未找到Tesseract OCR引擎")
        sys.exit(1)
    
    try:
        import PyPDF2
    except ImportError:
        print("警告: 未找到PyPDF2库，无法检测可选文本功能")
    
    sys.exit(main())
