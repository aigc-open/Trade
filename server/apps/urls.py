from django.urls import path, include

urlpatterns = [
    #  核心API
    
    # 原有API
    path("api/token/", include("apps.token.urls")),
    path("api/user/", include("apps.user.urls")),
    
    # 文档API
    path("api/docs/", include("apps.docs.urls")),
    
    # AI 交易智能体系统 API
    path("api/market-data/", include("apps.market_data.urls")),
    path("api/agents/", include("apps.agents.urls")),
    path("api/strategies/", include("apps.strategies.urls")),
    path("api/trades/", include("apps.trades.urls")),
    path("api/memory/", include("apps.memory.urls")),
    path("api/reports/", include("apps.reports.urls")),
]
