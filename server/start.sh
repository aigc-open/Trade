#!/bin/bash
# DataTraceHub 启动脚本

echo "=== DataTraceHub Server 启动 ==="

# 检查环境变量
if [ -z "$DATABASE_ENGINE" ]; then
    echo "未设置DATABASE_ENGINE，使用默认值: sqlite3"
    export DATABASE_ENGINE=sqlite3
fi

echo "数据库引擎: $DATABASE_ENGINE"

# 等待PostgreSQL启动（如果使用PostgreSQL）
if [ "$DATABASE_ENGINE" = "postgresql" ]; then
    echo "等待PostgreSQL启动..."
    while ! nc -z ${DATABASE_HOST:-localhost} ${DATABASE_PORT:-5432}; do
        sleep 1
    done
    echo "PostgreSQL已就绪"
fi

# 等待Redis启动
echo "等待Redis启动..."
while ! nc -z ${REDIS_HOST:-localhost} ${REDIS_PORT:-6379}; do
    sleep 1
done
echo "Redis已就绪"

# 运行数据库迁移
echo "运行数据库迁移..."
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（如果不存在）
echo "检查超级用户..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@datatracehub.com', 'admin123')
    print('超级用户创建成功: admin / admin123')
else:
    print('超级用户已存在')
EOF

# 收集静态文件（生产环境）
if [ "$ENVIRONMENT" = "production" ]; then
    echo "收集静态文件..."
    python manage.py collectstatic --noinput
fi

# 启动服务
echo "启动DataTraceHub服务..."
if [ "$ENVIRONMENT" = "production" ]; then
    # 生产环境使用Gunicorn
    gunicorn core.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    # 开发环境使用Django开发服务器
    python manage.py runserver 0.0.0.0:8000
fi

