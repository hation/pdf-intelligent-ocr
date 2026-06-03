#!/usr/bin/env python3
"""
高级 OCR 解析脚本，尝试多种策略来提高识别率
"""

from liteparse import LiteParse
import os

def parse_with_multiple_strategies():
    filename = "files/【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满.pdf"
    
    # 策略列表
    strategies = [
        {
            'name': '无OCR（纯文本提取）',
            'ocr_enabled': False
        },
        {
            'name': '标准OCR（150DPI）',
            'ocr_enabled': True,
            'dpi': 150
        },
        {
            'name': '高质量OCR（300DPI）',
            'ocr_enabled': True,
            'dpi': 300
        },
        {
            'name': '超高质量OCR（400DPI）',
            'ocr_enabled': True,
            'dpi': 400
        },
        {
            'name': '高精度OCR（600DPI）',
            'ocr_enabled': True,
            'dpi': 600
        }
    ]
    
    print(f"开始解析文件: {filename}")
    
    results = []
    
    for i, strategy in enumerate(strategies):
        print(f"\n策略 {i+1}: {strategy['name']}")
        
        parser = LiteParse(
            ocr_enabled=strategy['ocr_enabled'], 
            dpi=strategy.get('dpi', 150),
            quiet=True
        )
        
        result = parser.parse(filename)
        
        # 评估质量指标
        char_count = len(result.text)
        word_count = len(result.text.split())
        unique_chars = len(set(result.text))
        
        results.append({
            'strategy': strategy['name'],
            'chars': char_count,
            'words': word_count,
            'unique_chars': unique_chars,
            'text': result.text
        })
        
        print(f"字符数: {char_count} | 单词数: {word_count} | 独特字符: {unique_chars}")
        
        if word_count > 0:
            first_100_chars = ' '.join(result.text.split())[:100]
            print(f"前100字符: {first_100_chars}")
    
    # 找出最佳结果
    # 首先过滤掉无OCR策略（我们知道这没用）
    ocr_results = [r for r in results if 'OCR' in r['strategy']]
    
    if not ocr_results:
        print("没有成功的OCR策略")
        return False
    
    # 评估最佳结果
    best_result = max(
        ocr_results, 
        key=lambda r: r['chars'] * 0.8 + r['words'] * 0.2  # 字符数权重高，单词数权重低
    )
    
    print(f"\n=== 最佳策略: {best_result['strategy']} ===")
    print(f"字符数: {best_result['chars']}")
    print(f"单词数: {best_result['words']}")
    print(f"独特字符: {best_result['unique_chars']}")
    
    if best_result['chars'] < 100:
        print("警告: 所有OCR策略的结果都很差，可能是图像质量问题")
    
    # 保存结果
    output_file = f"outputs_liteparse_ocr/{os.path.splitext(os.path.basename(filename))[0]}_best.md"
    
    md_content = f"# 【机构调研】这家铜箔供应商相继攻克HVLP1-4代产品，公司5月稼动率已打满\n\n"
    md_content += f"## 文件统计\n"
    md_content += f"解析策略: {best_result['strategy']}\n"
    md_content += f"页数: 1\n"
    md_content += f"字符数: {best_result['chars']}\n"
    md_content += f"单词数: {best_result['words']}\n"
    md_content += f"独特字符: {best_result['unique_chars']}\n\n"
    
    md_content += f"## 内容\n"
    md_content += best_result['text']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"结果已保存到: {output_file}")
    
    return True

if __name__ == "__main__":
    parse_with_multiple_strategies()
