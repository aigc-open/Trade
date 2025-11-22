# 🤖 AI自动交易系统使用指南

## 📋 系统自动化说明

是的，这个系统设计为**完全自动化**运行，包括：

### 🔄 自动化流程

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 自动交易循环                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. 📊 自动获取数据 (每30秒)                                  │
│     ├─ 实时市场行情                                          │
│     ├─ 市场指数                                              │
│     ├─ 新闻事件                                              │
│     └─ 市场情绪                                              │
│                                                               │
│  2. 🔍 自动分析 (每60秒)                                     │
│     ├─ 技术面分析                                            │
│     ├─ 基本面分析                                            │
│     ├─ 情绪分析                                              │
│     ├─ 机会识别                                              │
│     └─ AI多智能体辩论决策                                     │
│                                                               │
│  3. 💰 自动交易 (每30秒)                                     │
│     ├─ 执行买入决策                                          │
│     ├─ 执行卖出决策                                          │
│     ├─ 止损/止盈监控                                         │
│     └─ 仓位管理                                              │
│                                                               │
│  4. 📈 自动规划 (每5分钟)                                    │
│     ├─ 制定交易计划                                          │
│     ├─ 策略选择                                              │
│     └─ 资金分配                                              │
│                                                               │
│  5. 🧠 自动学习 (每小时)                                     │
│     ├─ 复盘分析                                              │
│     ├─ 经验总结                                              │
│     ├─ 策略优化                                              │
│     └─ 认知偏见检测                                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速启动完整系统

### 步骤 1: 配置环境

```bash
cd /workspace/code/Trade/server

# 1. 配置 OpenAI API Key（用于AI决策）
# 编辑 core/settings.py，设置：
# OPENAI_API_KEY = 'your-api-key-here'

# 2. 配置数据源（可选，根据需要配置）
# - Alpha Vantage API Key（美股数据）
# - Tushare Token（A股数据）
```

### 步骤 2: 初始化数据库

```bash
# 创建数据库表
python manage.py migrate

# 加载初始Mock数据
./load_mock_data.sh
```

### 步骤 3: 启动Django服务器（终端1）

```bash
# 在第一个终端启动API服务器
python manage.py runserver 0.0.0.0:8000
```

### 步骤 4: 启动所有AI智能体（终端2）

```bash
# 在第二个终端启动全部智能体
./start_all_agents.sh
```

这会自动启动：
- ✅ **感知层（Perception）**: 每30秒监控市场
- ✅ **决策层（Decision）**: 每60秒分析决策  
- ✅ **执行层（Execution）**: 每30秒执行交易
- ✅ **规划层（Planning）**: 每5分钟制定计划
- ✅ **反思层（Reflection）**: 每小时学习优化

### 步骤 5: 启动前端监控界面（终端3）

```bash
# 在第三个终端启动前端
cd /workspace/code/Trade/web
npm run dev
```

访问: http://localhost:3000

## 📊 运行状态监控

### 查看智能体日志

```bash
# 实时查看所有智能体日志
cd /workspace/code/Trade/server
tail -f logs/*.log

# 查看单个智能体
tail -f logs/perception.log   # 感知层
tail -f logs/decision.log      # 决策层
tail -f logs/execution.log     # 执行层
tail -f logs/planning.log      # 规划层
tail -f logs/reflection.log    # 反思层
```

### 停止所有智能体

```bash
./stop_all_agents.sh
```

## ⚠️ 重要说明

### 1. 模拟交易模式

当前系统运行在**模拟交易模式**：
- ✅ 不会真实买卖股票
- ✅ 使用虚拟资金（初始100万）
- ✅ 所有交易在数据库中记录
- ✅ 安全学习和测试策略

### 2. 数据源配置

系统支持多个数据源，需要配置API密钥：

#### A股数据（Tushare/AKShare）
```python
# core/settings.py
TUSHARE_TOKEN = 'your-tushare-token'
```

#### 美股数据（Alpha Vantage/Yahoo Finance）
```python
# core/settings.py
ALPHAVANTAGE_API_KEY = 'your-alphavantage-key'
```

#### 获取数据的命令
```bash
# 手动采集市场数据
python manage.py collect_market_data --symbols AAPL,TSLA,NVDA --market US_STOCK

# A股
python manage.py collect_market_data --symbols 000001.SZ,600000.SH --market A_STOCK
```

### 3. AI决策需要OpenAI API

AI多智能体决策系统使用OpenAI GPT模型：

```python
# core/settings.py
OPENAI_API_KEY = 'sk-...'  # 您的OpenAI API密钥
OPENAI_MODEL = 'gpt-4'      # 可选 gpt-3.5-turbo, gpt-4
```

没有配置时，系统会使用**规则引擎**进行简单决策。

## 🎯 系统功能详解

### 1. 📊 感知层（Perception Agent）

**运行频率**: 每30秒

**功能**：
- 实时采集市场数据
- 监控价格变动
- 识别市场异常
- 扫描交易机会
- 检测风险信号

**输出**：
- MarketOpportunityModel（市场机会）
- 异常信号
- 风险警告

### 2. 🧠 决策层（Decision Agent）

**运行频率**: 每60秒

**功能**：
- 读取感知层发现的机会
- 多智能体辩论（激进派、保守派、量化派、裁判）
- AI分析（使用OpenAI GPT）
- 生成买入/卖出决策
- 设置止损/止盈

**输出**：
- DecisionRecordModel（决策记录）
- 包含仓位建议、目标价格、风险评估

### 3. 💰 执行层（Execution Agent）

**运行频率**: 每30秒

**功能**：
- 读取决策层的决策
- 多级风控检查（交易前、交易中、交易后）
- 执行模拟交易
- 更新持仓
- 监控止损/止盈

**输出**：
- TradeModel（交易记录）
- PositionModel（持仓）
- PortfolioModel（投资组合更新）
- RiskControlLogModel（风控日志）

### 4. 📈 规划层（Planning Agent）

**运行频率**: 每5分钟

**功能**：
- 分析市场环境
- 制定交易计划
- 策略选择和配置
- 资金分配优化
- 风险预算

**输出**：
- TradingPlanModel（交易计划）

### 5. 🧠 反思层（Reflection Agent）

**运行频率**: 每小时（可配置为每日）

**功能**：
- 自动复盘交易
- 成功/失败案例分析
- AI生成改进建议
- 策略进化
- 认知偏见检测

**输出**：
- ReviewReportModel（复盘报告）
- 策略优化建议
- 学习经验

## 📱 前端监控界面

访问 http://localhost:3000 查看：

1. **仪表板（Dashboard）**
   - 实时收益曲线
   - 智能体运行状态
   - 关键指标

2. **智能体监控（Agents）**
   - 各智能体状态
   - 执行日志
   - 性能指标

3. **投资组合（Portfolio）**
   - 账户总览
   - 资产曲线
   - 仓位分布

4. **持仓明细（Positions）**
   - 当前持仓
   - 浮动盈亏
   - 持仓时间

5. **交易记录（Trades）**
   - 所有交易历史
   - 买入/卖出明细
   - 盈亏统计

6. **策略管理（Strategies）**
   - 策略列表
   - 策略表现
   - 参数配置

7. **复盘报告（Reports）**
   - AI自动生成的复盘
   - 改进建议
   - 学习总结

## 🔧 高级配置

### 调整智能体运行频率

编辑 `start_all_agents.sh`：

```bash
# 感知层：每15秒运行一次（默认30秒）
nohup python manage.py run_perception --interval 15 > "$PERCEPTION_LOG" 2>&1 &

# 决策层：每30秒运行一次（默认60秒）
nohup python manage.py run_decision --interval 30 > "$DECISION_LOG" 2>&1 &
```

### 单独运行某个智能体

```bash
# 只运行感知层（持续）
python manage.py run_perception --interval 30

# 只运行一次决策层
python manage.py run_decision --once

# 只运行执行层
python manage.py run_execution --interval 30
```

### 风控参数配置

编辑 `services/agents/execution.py` 中的风控参数：

```python
max_single_trade = Decimal('0.05')      # 单笔最大5%
max_position = Decimal('0.30')          # 单一持仓最大30%
max_daily_loss = Decimal('-0.05')       # 日度最大亏损-5%
max_drawdown_limit = 0.15               # 最大回撤15%
```

## 📝 常见问题

### Q1: 系统会自动买卖真实股票吗？

**A**: 不会！当前是**模拟交易模式**。所有交易都在数据库中记录，不会真实执行。

### Q2: 需要一直运行吗？

**A**: 是的，智能体需要持续运行才能自动监控和交易。您可以：
- 使用 `nohup` 后台运行（已在启动脚本中配置）
- 使用 `screen` 或 `tmux` 会话
- 配置为系统服务（systemd）

### Q3: 如何切换到真实交易？

**A**: 需要：
1. 集成券商API（如富途、老虎证券、盈透证券）
2. 修改 `ExecutionAgent` 中的交易执行逻辑
3. 通过严格的回测和小资金测试
4. **风险自负，建议咨询专业人士**

### Q4: AI决策准确吗？

**A**: AI决策基于：
- 历史数据分析
- 技术指标
- 市场情绪
- 多智能体辩论

但**不保证盈利**，投资有风险。系统是学习和研究工具。

### Q5: 如何添加新策略？

**A**: 
1. 在 Django Admin 中添加策略：http://localhost:8000/admin
2. 或通过API添加
3. 策略会自动参与决策评选

## 🎓 学习建议

1. **先观察**：运行系统几天，观察决策逻辑
2. **查看日志**：理解每个智能体的工作流程
3. **分析复盘**：查看AI生成的复盘报告
4. **调整参数**：优化风控和策略参数
5. **添加数据源**：接入更多市场数据
6. **扩展策略**：开发自己的交易策略

## 🔐 安全提示

1. ✅ 永远使用模拟交易测试
2. ✅ 不要泄露API密钥
3. ✅ 定期备份数据库
4. ✅ 监控系统资源使用
5. ✅ 真实交易前充分测试

## 📞 技术支持

- 查看日志: `tail -f logs/*.log`
- Django Admin: http://localhost:8000/admin
- API文档: http://localhost:8000/api/schema/swagger-ui/
- 前端界面: http://localhost:3000

---

## 🎉 开始使用

```bash
# 一键启动所有服务（需要3个终端）

# 终端1: Django服务器
cd /workspace/code/Trade/server
python manage.py runserver

# 终端2: AI智能体
cd /workspace/code/Trade/server
./start_all_agents.sh

# 终端3: 前端界面
cd /workspace/code/Trade/web
npm run dev
```

**祝您使用愉快！📈🤖**

