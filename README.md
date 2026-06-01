# PDF OCR 识别工具

一个功能强大的 PDF OCR 识别工具，专门为处理大量难识别的 PDF 文件而设计。项目提供多种处理方案，以满足不同的需求。

## 功能特点

### 🎯 高精度识别方案
- **识别准确率**: 94.5%+
- **DPI**: 400（最高分辨率）
- **适合**: 文字密集型、低分辨率或复杂布局的 PDF
- **文件**: `batch_ocr_accurate.py`

### ⚡ 优化方案
- **平衡**: 识别质量和处理效率
- **DPI**: 200
- **适合**: 大规模文档处理（如单日500份）
- **处理时间**: 减少 60-70%
- **文件**: `batch_ocr_optimized.py`

### 🚀 快速识别方案
- **快速**: 直接使用 Tesseract OCR 引擎
- **适合**: 快速验证识别效果
- **文件**: `direct_tesseract_ocr.py`

### 📊 监控和管理
- **monitor_accurate.sh**: 高精度方案监控脚本
- **monitor_process.sh**: 优化方案监控脚本
- **pdf-ocr**: 快捷命令工具

## 技术特点

### 智能识别机制
- 使用 PyPDF2 快速检查 PDF 是否包含可选文本
- 只处理需要 OCR 的页面
- 自动跳过电子书类大文件

### 图像预处理
- 对比度增强
- 二值化处理
- 灰度转换

### 多进程处理
- 支持并发处理，提升效率
- 资源消耗可控

## 使用方法

### 安装依赖

```bash
pip install pdf2image pytesseract Pillow PyPDF2
```

### 基础使用

```bash
# 高精度识别
python3 batch_ocr_accurate.py "input_dir" "output_dir"

# 优化方案
python3 batch_ocr_optimized.py "input_dir" "output_dir"
```

### 监控处理

```bash
# 开始处理
./monitor_accurate.sh start

# 监控进度
./monitor_accurate.sh monitor

# 查看状态
./monitor_accurate.sh status
```

## 使用场景

| 场景 | 方案选择 | 处理能力 |
|------|----------|----------|
| 文字密集的研报、论文 | 高精度方案 | 识别准确率 94.5%+ |
| 单日500份大量文档 | 优化方案 | 处理时间 3-4小时 |
| 快速识别验证 | 快速方案 | 单份 10-20秒 |

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

## 系统要求

- **操作系统**: macOS, Linux
- **Python**: 3.8+
- **Tesseract OCR**: 需要单独安装
- **硬件**: 4核CPU, 8GB内存（推荐16GB）

## 许可证

MIT License

## 作者

Xing An
