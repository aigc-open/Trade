from rest_framework import pagination
INSTALLED_APPS = [
    "apps",
    #  核心模块
    # 原有模块
    "apps.token",
    "apps.user",
    # 文档模块
    "apps.docs",
    # AI交易智能体模块
    "apps.market_data",  # 市场数据
    "apps.agents",       # 智能体核心
    "apps.strategies",   # 策略管理
    "apps.trades",       # 交易记录
    "apps.memory",       # 记忆系统
    "apps.reports",      # 复盘报告
]


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = "page"
    page_size_query_param = "page_size"
