#!/bin/bash

# AI Trading Agent Frontend - 启动脚本

echo "=========================================="
echo "🤖 AI Trading Agent - Frontend"
echo "=========================================="
echo ""

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 依赖未安装，正在安装..."
    npm install
    echo ""
fi

# 检查后端是否运行
echo "🔍 检查后端服务..."
if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
    echo "✅ 后端服务正常运行"
else
    echo "⚠️  警告：后端服务未运行或无法访问"
    echo "   请确保后端运行在 http://localhost:8000"
    echo ""
    echo "   启动后端："
    echo "   cd /workspace/code/Trade/server"
    echo "   python manage.py runserver 0.0.0.0:8000"
    echo ""
fi

echo ""
echo "🚀 启动前端开发服务器..."
echo "   访问: http://localhost:3000"
echo "   登录: admin / admin123456"
echo ""
echo "=========================================="
echo ""

npm run dev

