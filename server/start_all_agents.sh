#!/bin/bash

# AI Trading Agent 全自动启动脚本
# 启动所有智能体进程

echo "=========================================="
echo "AI Trading Agent - Starting All Agents"
echo "=========================================="

# 检查环境
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the server directory."
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 定义日志文件
LOG_DIR="./logs"
PERCEPTION_LOG="$LOG_DIR/perception.log"
DECISION_LOG="$LOG_DIR/decision.log"
EXECUTION_LOG="$LOG_DIR/execution.log"
PLANNING_LOG="$LOG_DIR/planning.log"
REFLECTION_LOG="$LOG_DIR/reflection.log"

echo "Starting agents..."

# 1. 启动感知层 (每30秒)
echo "Starting Perception Agent..."
nohup python manage.py run_perception --interval 30 > "$PERCEPTION_LOG" 2>&1 &
PERCEPTION_PID=$!
echo "Perception Agent started (PID: $PERCEPTION_PID)"

# 2. 启动决策层 (每60秒)
echo "Starting Decision Agent..."
nohup python manage.py run_decision --interval 60 > "$DECISION_LOG" 2>&1 &
DECISION_PID=$!
echo "Decision Agent started (PID: $DECISION_PID)"

# 3. 启动执行层 (每30秒)
echo "Starting Execution Agent..."
nohup python manage.py run_execution --interval 30 > "$EXECUTION_LOG" 2>&1 &
EXECUTION_PID=$!
echo "Execution Agent started (PID: $EXECUTION_PID)"

# 4. 启动规划层 (每5分钟)
echo "Starting Planning Agent..."
nohup python manage.py run_planning --interval 300 > "$PLANNING_LOG" 2>&1 &
PLANNING_PID=$!
echo "Planning Agent started (PID: $PLANNING_PID)"

# 5. 启动反思层 (每1小时)
echo "Starting Reflection Agent..."
nohup python manage.py run_reflection --interval 3600 > "$REFLECTION_LOG" 2>&1 &
REFLECTION_PID=$!
echo "Reflection Agent started (PID: $REFLECTION_PID)"

# 保存 PID 到文件
PID_FILE="$LOG_DIR/agents.pid"
echo "$PERCEPTION_PID" > "$PID_FILE"
echo "$DECISION_PID" >> "$PID_FILE"
echo "$EXECUTION_PID" >> "$PID_FILE"
echo "$PLANNING_PID" >> "$PID_FILE"
echo "$REFLECTION_PID" >> "$PID_FILE"

echo ""
echo "=========================================="
echo "All agents started successfully!"
echo "=========================================="
echo ""
echo "Process IDs saved to: $PID_FILE"
echo ""
echo "Log files:"
echo "  - Perception:  $PERCEPTION_LOG"
echo "  - Decision:    $DECISION_LOG"
echo "  - Execution:   $EXECUTION_LOG"
echo "  - Planning:    $PLANNING_LOG"
echo "  - Reflection:  $REFLECTION_LOG"
echo ""
echo "To stop all agents, run: ./stop_all_agents.sh"
echo "To view logs: tail -f logs/*.log"
echo "=========================================="

