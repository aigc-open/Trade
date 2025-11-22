# 📦 Mock 测试数据说明

本目录包含 AI Trading Agent 系统的测试数据，用于快速初始化和演示系统功能。

---

## 📋 数据文件列表

### 1. 用户与认证
- **users.json** - 系统用户数据
  - 包含管理员账户
  - 用户名: `admin`
  - 密码: `admin123456`

- **tokens.json** - API Token 数据

### 2. 市场数据
- **market_data.json** - 市场 OHLCV 数据
  - 包含 A 股数据: 000001.SZ, 600000.SH
  - 包含美股数据: AAPL
  - 技术指标已计算

### 3. 智能体数据
- **agent_status.json** - 智能体运行状态
  - 5 个智能体的状态信息
  - 性能指标和心跳数据

- **market_opportunities.json** - 市场机会
  - 3 个交易机会
  - 突破型、价值型、动量型

- **decisions.json** - 交易决策
  - 3 条决策记录
  - 包含多智能体辩论过程
  - 买入、观望决策

- **trading_plans.json** - 交易计划
  - 日度计划和周度计划
  - 包含策略配置和执行进度

### 4. 交易数据
- **portfolios.json** - 投资组合
  - 2 个模拟账户
  - 包含资金、持仓、收益数据

- **trades.json** - 交易记录
  - 3 笔交易记录
  - 买入、卖出操作
  - 执行质量数据

- **positions.json** - 持仓数据
  - 2 个活跃持仓
  - 1 个已平仓持仓
  - 盈亏数据

### 5. 策略数据
- **strategies.json** - 交易策略
  - 趋势跟踪策略
  - 价值投资策略
  - 动量策略
  - 包含历史表现数据

### 6. 报告数据
- **review_reports.json** - 复盘报告
  - 日度复盘报告
  - 周度复盘报告
  - 成功/失败案例分析
  - 改进建议

---

## 🚀 快速使用

### 方式 1: 使用加载脚本（推荐）

```bash
# 在 server 目录下执行
./load_mock_data.sh
```

这个脚本会：
1. 询问是否清空现有数据
2. 按依赖顺序加载所有 mock 数据
3. 显示加载统计信息

### 方式 2: 手动加载

```bash
# 加载单个 fixture
python manage.py loaddata mock/users.json

# 按顺序加载所有数据
python manage.py loaddata mock/users.json
python manage.py loaddata mock/tokens.json
python manage.py loaddata mock/portfolios.json
python manage.py loaddata mock/strategies.json
python manage.py loaddata mock/market_data.json
python manage.py loaddata mock/agent_status.json
python manage.py loaddata mock/market_opportunities.json
python manage.py loaddata mock/trading_plans.json
python manage.py loaddata mock/decisions.json
python manage.py loaddata mock/trades.json
python manage.py loaddata mock/positions.json
python manage.py loaddata mock/review_reports.json
```

### 方式 3: 清空并重新加载

```bash
# 清空数据库
python manage.py flush --no-input

# 加载所有 mock 数据
./load_mock_data.sh
```

---

## 📊 数据统计

加载完成后的数据量：

| 模型 | 记录数 | 说明 |
|------|--------|------|
| 用户 | 1 | 管理员账户 |
| 市场数据 | 3 | A股 + 美股 |
| 智能体状态 | 5 | 5层智能体 |
| 市场机会 | 3 | 不同类型机会 |
| 交易决策 | 3 | 含辩论过程 |
| 交易记录 | 3 | 买入/卖出 |
| 持仓 | 3 | 2活跃+1已平 |
| 投资组合 | 2 | 模拟账户 |
| 策略 | 3 | 不同策略类型 |
| 交易计划 | 2 | 日度+周度 |
| 复盘报告 | 2 | 日度+周度 |

---

## 🎯 使用场景

### 1. 开发测试
在开发新功能时，使用 mock 数据快速验证功能。

```bash
# 加载测试数据
./load_mock_data.sh

# 启动开发服务器
python manage.py runserver

# 测试 API
curl http://localhost:8000/api/trades/
```

### 2. 演示展示
向他人演示系统功能时，使用完整的测试数据。

```bash
# 准备演示环境
./load_mock_data.sh

# 访问 Admin 查看数据
# http://localhost:8000/admin
```

### 3. 学习系统
了解系统数据结构和关系。

```bash
# 加载数据后进入 Django Shell
python manage.py shell

# 查询数据
from apps.trades.models import TradeModel
trades = TradeModel.objects.all()
for trade in trades:
    print(f"{trade.symbol}: {trade.action} {trade.filled_quantity}")
```

---

## 🔍 数据说明

### 投资组合数据
- **simulation_main**: 主模拟账户
  - 初始资金: 100万
  - 当前总资产: 102.53万
  - 收益率: 2.53%
  - 持仓: 3个

- **simulation_test**: 测试账户
  - 初始资金: 50万
  - 当前总资产: 50.82万
  - 收益率: 1.64%
  - 持仓: 2个

### 策略数据
1. **趋势跟踪策略** (trend_following_001)
   - 胜率: 71.11%
   - 总收益: 18.56%
   - 夏普比率: 2.15

2. **价值投资策略** (value_investing_001)
   - 胜率: 75.00%
   - 总收益: 22.45%
   - 夏普比率: 1.95

3. **动量策略** (momentum_001)
   - 胜率: 61.29%
   - 总收益: 15.23%
   - 夏普比率: 1.72

### 智能体状态
所有 5 层智能体均处于运行状态：
- ✅ Perception Agent - 感知层
- ✅ Decision Agent - 决策层
- ✅ Execution Agent - 执行层
- ✅ Planning Agent - 规划层
- ✅ Reflection Agent - 反思层

---

## 🛠️ 自定义数据

### 添加新的 Mock 数据

1. 创建新的 JSON 文件：
```json
[
  {
    "model": "app_name.modelname",
    "pk": 1,
    "fields": {
      "field1": "value1",
      "field2": "value2"
    }
  }
]
```

2. 加载到数据库：
```bash
python manage.py loaddata mock/your_file.json
```

### 导出当前数据为 Mock

```bash
# 导出特定模型
python manage.py dumpdata trades.trademodel --indent 2 > mock/new_trades.json

# 导出整个应用
python manage.py dumpdata trades --indent 2 > mock/trades_full.json

# 导出所有数据
python manage.py dumpdata --indent 2 > mock/full_backup.json
```

---

## ⚠️ 注意事项

1. **数据依赖关系**
   - 务必按照依赖顺序加载数据
   - 用户 → 组合 → 策略 → 交易 → 持仓

2. **外键关联**
   - 决策记录关联到交易记录
   - 持仓关联到交易记录
   - 确保 ID 匹配

3. **时间戳**
   - Mock 数据中的时间戳是示例值
   - 可以根据需要调整为当前时间

4. **敏感信息**
   - 密码已加密
   - 测试账户密码: `admin123456`
   - 生产环境请使用强密码

5. **数据清理**
   ```bash
   # 清空所有数据
   python manage.py flush --no-input
   
   # 删除特定模型数据
   python manage.py shell -c "from apps.trades.models import TradeModel; TradeModel.objects.all().delete()"
   ```

---

## 📚 相关文档

- [项目 README](../README.md)
- [快速开始指南](../QUICK_START_GUIDE.md)
- [系统架构](../ARCHITECTURE.md)
- [开发状态](../DEVELOPMENT_STATUS.md)

---

## 🤝 贡献

如果你创建了有用的 mock 数据，欢迎提交到此目录！

---

**Happy Testing! 🧪✨**

