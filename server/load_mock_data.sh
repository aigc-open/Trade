#!/bin/bash

# AI Trading Agent - 加载 Mock 测试数据脚本
# 用于快速初始化系统测试数据

echo "=========================================="
echo "AI Trading Agent - Loading Mock Data"
echo "=========================================="

# 检查环境
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the server directory."
    exit 1
fi

# 检查 mock 目录
if [ ! -d "mock" ]; then
    echo "Error: mock directory not found."
    exit 1
fi

echo ""
echo "Step 1: Clearing existing data (optional)..."
echo "Warning: This will delete all existing data!"
read -p "Do you want to clear existing data? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Flushing database..."
    python manage.py flush --no-input
    echo "✅ Database cleared"
else
    echo "⏭️  Skipping database flush"
fi

echo ""
echo "Step 2: Loading mock data..."
echo ""

# 定义加载顺序（按照依赖关系）
# 注意：只包含已验证通过的 fixtures
declare -a fixtures=(
    "users"
    "portfolios"
    "strategies"
    "market_data"
    "agent_status"
)

# 以下fixtures由于字段不匹配暂时禁用，建议通过系统运行后自动生成
# "tokens"
# "market_opportunities"
# "trading_plans"
# "decisions"
# "trades"
# "positions"
# "review_reports"

# 加载每个 fixture
for fixture in "${fixtures[@]}"; do
    fixture_file="mock/${fixture}.json"
    
    if [ -f "$fixture_file" ]; then
        echo "Loading ${fixture}.json..."
        python manage.py loaddata "$fixture_file"
        
        if [ $? -eq 0 ]; then
            echo "✅ ${fixture}.json loaded successfully"
        else
            echo "❌ Failed to load ${fixture}.json"
            exit 1
        fi
    else
        echo "⚠️  ${fixture}.json not found, skipping..."
    fi
    
    echo ""
done

echo "=========================================="
echo "Mock Data Loading Complete!"
echo "=========================================="
echo ""
echo "Loaded fixtures:"
for fixture in "${fixtures[@]}"; do
    if [ -f "mock/${fixture}.json" ]; then
        echo "  ✅ ${fixture}.json"
    fi
done

echo ""
echo "Quick Stats:"
python manage.py shell -c "
from apps.market_data.models import MarketDataModel
from apps.agents.models import AgentStatusModel, DecisionRecordModel, MarketOpportunityModel
from apps.trades.models import TradeModel, PositionModel, PortfolioModel
from apps.strategies.models import StrategyModel
from apps.reports.models import ReviewReportModel

print(f'  - Market Data: {MarketDataModel.objects.count()} records')
print(f'  - Agent Status: {AgentStatusModel.objects.count()} agents')
print(f'  - Market Opportunities: {MarketOpportunityModel.objects.count()} opportunities')
print(f'  - Trading Decisions: {DecisionRecordModel.objects.count()} decisions')
print(f'  - Trades: {TradeModel.objects.count()} trades')
print(f'  - Positions: {PositionModel.objects.count()} positions')
print(f'  - Portfolios: {PortfolioModel.objects.count()} portfolios')
print(f'  - Strategies: {StrategyModel.objects.count()} strategies')
print(f'  - Review Reports: {ReviewReportModel.objects.count()} reports')
"

echo ""
echo "=========================================="
echo "You can now:"
echo "  1. Access Django Admin: http://localhost:8000/admin"
echo "  2. View API: http://localhost:8000/api/"
echo "  3. Check Swagger: http://localhost:8000/api/schema/swagger-ui/"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: admin123456"
echo "=========================================="
