"""
ASGI config for AI Trader project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# 设置 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# 初始化 Django ASGI application
django_asgi_app = get_asgi_application()

# 导入 Channels 组件（在 Django 初始化之后）
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# WebSocket 路由配置（待实现）
websocket_urlpatterns = [
    # 示例：实时市场数据推送
    # path('ws/market/', MarketConsumer.as_asgi()),
    # path('ws/alerts/', AlertConsumer.as_asgi()),
]

# ASGI application 配置
application = ProtocolTypeRouter({
    # HTTP 请求
    "http": django_asgi_app,
    
    # WebSocket 请求
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
