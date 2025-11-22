#!/bin/bash

# AI Trading Agent 停止脚本
# 停止所有智能体进程

echo "=========================================="
echo "AI Trading Agent - Stopping All Agents"
echo "=========================================="

PID_FILE="./logs/agents.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Error: PID file not found at $PID_FILE"
    echo "Agents may not be running or were started manually."
    exit 1
fi

echo "Reading PIDs from $PID_FILE..."

while IFS= read -r pid; do
    if [ -n "$pid" ]; then
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "Stopping process $pid..."
            kill "$pid"
            sleep 1
            # 如果进程还在运行，强制终止
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "Force killing process $pid..."
                kill -9 "$pid"
            fi
        else
            echo "Process $pid not found (already stopped)"
        fi
    fi
done < "$PID_FILE"

# 清理 PID 文件
rm "$PID_FILE"

echo ""
echo "=========================================="
echo "All agents stopped successfully!"
echo "=========================================="

