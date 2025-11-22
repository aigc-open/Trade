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
echo "Step 2: Scanning mock directory for JSON files..."
echo ""

# 自动扫描 mock 目录下的所有 .json 文件
# 定义优先加载顺序（按依赖关系）
# 重要：按照外键依赖顺序排列
declare -a priority_order=(
    "users"
    "portfolios"
    "strategies"
    "market_data"
    "agent_status"
    "trading_plans"
    "decisions"
    "market_opportunities"
    "trades"
    "positions"
    "review_reports"
    "tokens"
)

# 收集所有 JSON 文件
declare -a all_fixtures=()
for json_file in mock/*.json; do
    if [ -f "$json_file" ]; then
        # 提取文件名（不含路径和扩展名）
        fixture_name=$(basename "$json_file" .json)
        all_fixtures+=("$fixture_name")
    fi
done

# 按优先级排序：先加载优先级列表中的，再加载其他的
declare -a fixtures=()

# 1. 先加载优先级列表中的文件
for priority_fixture in "${priority_order[@]}"; do
    for fixture in "${all_fixtures[@]}"; do
        if [ "$fixture" = "$priority_fixture" ]; then
            fixtures+=("$fixture")
            break
        fi
    done
done

# 2. 再加载其他文件（不在优先级列表中的）
for fixture in "${all_fixtures[@]}"; do
    # 检查是否已在 fixtures 数组中
    skip=false
    for loaded in "${fixtures[@]}"; do
        if [ "$loaded" = "$fixture" ]; then
            skip=true
            break
        fi
    done
    if [ "$skip" = false ]; then
        fixtures+=("$fixture")
    fi
done

echo "Found ${#fixtures[@]} JSON files in mock directory"
echo "Will load in the following order:"
for fixture in "${fixtures[@]}"; do
    echo "  - ${fixture}.json"
done
echo ""
echo "Note: Some files may fail due to field mismatches - this is normal"
echo ""

# 加载每个 fixture
declare -a loaded_fixtures=()
declare -a failed_fixtures=()

for fixture in "${fixtures[@]}"; do
    fixture_file="mock/${fixture}.json"
    
    if [ -f "$fixture_file" ]; then
        echo "Loading ${fixture}.json..."
        python manage.py loaddata "$fixture_file" 2>&1 | tee /tmp/loaddata_output.log
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            echo "✅ ${fixture}.json loaded successfully"
            loaded_fixtures+=("${fixture}")
        else
            echo "❌ Failed to load ${fixture}.json"
            echo "   (This may be due to field mismatches - check model definitions)"
            failed_fixtures+=("${fixture}")
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

if [ ${#loaded_fixtures[@]} -gt 0 ]; then
    echo "✅ Successfully loaded fixtures (${#loaded_fixtures[@]}):"
    for fixture in "${loaded_fixtures[@]}"; do
        echo "  ✅ ${fixture}.json"
    done
    echo ""
fi

if [ ${#failed_fixtures[@]} -gt 0 ]; then
    echo "❌ Failed to load fixtures (${#failed_fixtures[@]}):"
    for fixture in "${failed_fixtures[@]}"; do
        echo "  ❌ ${fixture}.json"
    done
    echo ""
    echo "Note: Failed fixtures may have field mismatches with current models."
    echo "      You can manually create this data through Django shell or admin."
    echo ""
fi

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
