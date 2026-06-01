#!/bin/bash
# 高精度OCR处理监控脚本 - 以识别质量为首要目标

INPUT_DIR="files"
OUTPUT_DIR="outputs_high_accuracy"
LOG_FILE="ocr_accuracy_processing.log"

# 显示资源使用情况
show_resource_usage() {
    echo "=== 资源使用情况 ==="
    echo "CPU使用: $(top -l 1 | awk '/CPU usage/ {print $3}')"
    echo "内存使用: $(vm_stat | awk '/Pages active:/ {printf "%.2f GB\n", $3 * 4096 / 1024 / 1024 / 1024}')"
    echo "磁盘空间: $(df -h | grep / | awk '{print $5 " available"}')"
    echo "---------------------------------"
}

# 显示处理进度
show_progress() {
    local processed=$(ls "$OUTPUT_DIR"/*.md 2>/dev/null | wc -l)
    local total=$(ls "$INPUT_DIR"/*.pdf 2>/dev/null | wc -l)
    
    if [ $total -gt 0 ]; then
        local percent=$((processed * 100 / total))
        echo "=== 处理进度 ==="
        echo "已处理: $processed / $total"
        echo "进度: $percent%"
        echo "---------------------------------"
    fi
}

# 显示失败日志
show_errors() {
    local error_count=$(grep "失败" "$LOG_FILE" 2>/dev/null | wc -l)
    if [ $error_count -gt 0 ]; then
        echo "=== 错误统计 ==="
        echo "失败文件数: $error_count"
        echo "---------------------------------"
        grep "失败" "$LOG_FILE" | head -5
    fi
}

# 清理临时文件
cleanup() {
    echo "=== 清理临时文件 ==="
    
    # 清理pdf2image临时文件
    rm -f /tmp/*pdf2image* 2>/dev/null
    rm -f /private/tmp/*pdf2image* 2>/dev/null
    
    # 清理tesseract临时文件
    rm -f /tmp/tess* 2>/dev/null
    rm -f /private/tmp/tess* 2>/dev/null
    
    echo "临时文件清理完成"
    echo "---------------------------------"
}

# 显示帮助信息
show_help() {
    echo "高精度OCR处理监控脚本"
    echo "------------------------------------------"
    echo "Usage: $0 [选项]"
    echo "选项说明:"
    echo "  status    显示当前状态"
    echo "  monitor   持续监控"
    echo "  cleanup   清理临时文件"
    echo "  start     开始处理"
    echo "  stop      停止处理"
    echo "  help      显示帮助"
}

# 开始处理
start_processing() {
    if pgrep -f "batch_ocr_accurate.py" > /dev/null; then
        echo "处理进程已在运行"
        return 1
    fi
    
    echo "开始高精度OCR处理..."
    echo "输入目录: $INPUT_DIR"
    echo "输出目录: $OUTPUT_DIR"
    echo "日志文件: $LOG_FILE"
    
    mkdir -p "$OUTPUT_DIR"
    
    nohup python3 batch_ocr_accurate.py "$INPUT_DIR" "$OUTPUT_DIR" -r >> "$LOG_FILE" 2>&1 &
    
    echo "处理进程已启动 (PID: $!)"
    echo "输出到: $LOG_FILE"
}

# 停止处理
stop_processing() {
    if pgrep -f "batch_ocr_accurate.py" > /dev/null; then
        echo "正在停止处理进程..."
        pkill -f "batch_ocr_accurate.py"
        sleep 2
        
        if pgrep -f "batch_ocr_accurate.py" > /dev/null; then
            pkill -9 -f "batch_ocr_accurate.py"
        fi
        
        echo "处理进程已停止"
    else
        echo "处理进程未在运行"
    fi
}

# 持续监控
continuous_monitor() {
    echo "开始持续监控..."
    while true; do
        clear
        show_resource_usage
        show_progress
        show_errors
        echo "按 Ctrl+C 停止监控"
        sleep 5
    done
}

# 主函数
main() {
    case "$1" in
        status)
            show_resource_usage
            show_progress
            show_errors
            ;;
        monitor)
            continuous_monitor
            ;;
        cleanup)
            cleanup
            ;;
        start)
            start_processing
            ;;
        stop)
            stop_processing
            ;;
        help | *)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@"
