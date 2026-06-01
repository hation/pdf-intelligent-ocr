# 项目信息 - PDF OCR 处理工具

## 项目概述
这是一个功能强大的 PDF OCR 识别工具，专门为处理大量难识别的 PDF 文件而设计。项目包含多种处理方案，以满足不同的需求。

## 核心功能

### 1. 高精度识别方案
- `batch_ocr_accurate.py` - 以识别质量为首要目标
- DPI: 400（最高分辨率）
- 适合文字密集型、低分辨率或复杂布局的 PDF
- 识别准确率: 94.5%+

### 2. 优化方案
- `batch_ocr_optimized.py` - 平衡识别质量和处理效率
- DPI: 200
- 适合大规模文档处理（如单日500份）
- 处理时间减少 60-70%

### 3. 快速识别方案
- `direct_tesseract_ocr.py` - 快速处理单文件
- 直接使用 Tesseract OCR 引擎
- 适合快速验证识别效果

### 4. 监控和管理
- `monitor_accurate.sh` - 高精度方案监控脚本
- `monitor_process.sh` - 优化方案监控脚本
- `pdf-ocr` - 快捷命令工具

## 技术特点

### 1. 智能识别机制
- 使用 PyPDF2 快速检查 PDF 是否包含可选文本
- 只处理需要 OCR 的页面
- 自动跳过电子书类大文件

### 2. 图像预处理
- 对比度增强
- 二值化处理
- 灰度转换

### 3. 多进程处理
- 支持并发处理，提升效率
- 资源消耗可控

## 使用场景

### 推荐使用方案

| 场景 | 方案选择 | 处理能力 |
|------|----------|----------|
| 文字密集的研报、论文 | 高精度方案 | 识别准确率 94.5%+ |
| 单日500份大量文档 | 优化方案 | 处理时间 3-4小时 |
| 快速识别验证 | 快速方案 | 单份 10-20秒 |

### 支持的文件类型
- 扫描件 PDF
- 低分辨率图像 PDF
- 文字密集型 PDF
- 复杂布局 PDF
- 双语文档（中文+英文）

## 项目结构

```
pdf-ocr-tool/
├── README.md              # 项目说明文档
├── LICENSE                # 许可证信息
├── requirements.txt       # Python 依赖包
├── .gitignore            # git 忽略文件
├── batch_ocr_accurate.py  # 高精度识别脚本
├── batch_ocr_optimized.py # 优化方案脚本
├── direct_tesseract_ocr.py # 快速识别脚本
├── monitor_accurate.sh    # 高精度方案监控脚本
├── monitor_process.sh     # 优化方案监控脚本
├── pdf-ocr               # 快捷命令工具
├── resource_optimization_report.md # 资源优化报告
└── high_accuracy_report.md # 高精度方案报告
```

## 项目名称建议
- **`pdf-ocr-tool`** - 简洁且明确
- **`pdf-intelligent-ocr`** - 突出智能识别功能
- **`precision-pdf-recognizer`** - 强调高精度识别

## GitHub 仓库描述建议
> 一个功能强大的 PDF OCR 识别工具，提供多种处理方案以满足不同需求。支持高精度识别、快速处理和智能优化三种模式，专门为处理大量难识别的 PDF 文件而设计。项目包含完整的图像预处理、多进程处理和进度监控功能，识别准确率高，资源消耗可控。
