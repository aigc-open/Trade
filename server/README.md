# DataTraceHub Server

DataTraceHub 通用数据报表与分析系统 - 服务端


## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建超级用户

```bash
python manage.py createsuperuser
```

### 5. 启动服务

```bash
python manage.py runserver 0.0.0.0:8000
```

### 6. 访问API文档

打开浏览器访问: http://localhost:8000/docs/


## 部署

### Docker部署

```bash
docker-compose up -d
```

### 生产环境配置

1. 设置环境变量
2. 配置PostgreSQL数据库
3. 配置Redis
4. 运行数据库迁移
5. 收集静态文件: `python manage.py collectstatic`
6. 使用Gunicorn启动: `gunicorn core.wsgi:application --bind 0.0.0.0:8000`


## 开发指南

### 创建新的App

```bash
python manage.py create_app your_app_name
```

### 运行测试

```bash
pytest
```

## 许可证

MIT License

