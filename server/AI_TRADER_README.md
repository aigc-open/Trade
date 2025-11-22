# 🤖 AI 自主交易智能体系统 - 使用指南

## 📖 系统简介

AI 自主交易智能体系统是一个基于 Django + OpenAI 的完全自主的交易系统，实现了从市场感知到交易执行再到自我进化的完整闭环。

### ✨ 核心特性

- 🧠 **六层认知架构** - 感知、记忆、规划、决策、执行、反思
- 🎭 **多智能体辩论** - 激进派、保守派、量化派、裁判协同决策
- 🧬 **策略自我进化** - 基因池、参数优化、自然选择
- 🛡️ **多层风险控制** - 实时监控、动态参数、智能预警
- 💾 **长期记忆系统** - 向量数据库、知识图谱、经验检索
- 📊 **自动化复盘** - 每日总结、洞察生成、持续改进

---

## 🏗️ 系统架构

### 六层智能体架构

```
感知层 (Perception)    -> 市场数据采集和实时监控 (30秒)
   ↓
记忆层 (Memory)        -> 知识存储与检索 (被动)
   ↓
规划层 (Planning)      -> 目标制定与任务分解 (5分钟)
   ↓
决策层 (Decision)      -> 策略生成与多智能体辩论 (60秒)
   ↓
执行层 (Execution)     -> 交易落地与风控 (30秒)
   ↓
反思层 (Reflection)    -> 经验总结与自我进化 (1小时/每日)
```

---

## 🚀 快速开始

### 1. 环境准备

```bash
# Python 3.10+
python --version

# 安装依赖
cd /workspace/code/Trade/server
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 必需：OpenAI API Key
export OPENAI_API_KEY="your-openai-api-key"

# 可选：Alpha Vantage API Key
export ALPHA_VANTAGE_API_KEY="your-key"
```

### 3. 初始化数据库

```bash
# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 加载测试数据（可选）
./load_mock_data.sh
```

### 4. 启动系统

```bash
# 方式1：一键启动所有智能体
./start_all_agents.sh

# 方式2：启动 Django 服务器
python manage.py runserver 0.0.0.0:8000

# 方式3：单独启动各层智能体
python manage.py run_perception --interval 30 &
python manage.py run_decision --interval 60 &
python manage.py run_execution --interval 30 &
python manage.py run_planning --interval 300 &
python manage.py run_reflection --interval 3600 &
```

### 5. 访问系统

- **Django Admin**: http://localhost:8000/admin
- **API 文档**: http://localhost:8000/api/schema/swagger-ui/
- **系统文档**: http://localhost:8000/api/docs/system-guide/

---

## 📡 API 接口

### 认证方式

系统支持两种认证方式：

1. **Token 认证** - 推荐用于 API 调用
   ```bash
   curl -H "Authorization: Token your-token-here" \
        http://localhost:8000/api/trades/
   ```

2. **Session 认证** - 用于浏览器访问

### 主要 API 端点

#### 1. 市场数据 `/api/market-data/`

**获取市场数据列表**
```bash
GET /api/market-data/
Query: ?symbol=000001.SZ&market=A_STOCK&limit=10
```

**获取单条市场数据**
```bash
GET /api/market-data/{id}/
```

#### 2. 智能体状态 `/api/agents/status/`

**获取所有智能体状态**
```bash
GET /api/agents/status/
```

**获取单个智能体状态**
```bash
GET /api/agents/status/{id}/
```

#### 3. 交易决策 `/api/agents/decisions/`

**获取决策列表**
```bash
GET /api/agents/decisions/
Query: ?symbol=000001.SZ&decision_type=buy
```

**获取单条决策详情**
```bash
GET /api/agents/decisions/{id}/
```

#### 4. 交易记录 `/api/trades/`

**获取交易列表**
```bash
GET /api/trades/
Query: ?account_name=simulation_main&status=filled
```

**获取单笔交易**
```bash
GET /api/trades/{id}/
```

#### 5. 持仓管理 `/api/positions/`

**获取持仓列表**
```bash
GET /api/positions/
Query: ?is_closed=false&account_name=simulation_main
```

**获取单个持仓**
```bash
GET /api/positions/{id}/
```

#### 6. 投资组合 `/api/portfolios/`

**获取组合列表**
```bash
GET /api/portfolios/
```

**获取组合详情**
```bash
GET /api/portfolios/{id}/
```

#### 7. 策略管理 `/api/strategies/`

**获取策略列表**
```bash
GET /api/strategies/
Query: ?status=active&strategy_type=trend
```

**获取策略详情**
```bash
GET /api/strategies/{id}/
```

#### 8. 复盘报告 `/api/reports/reviews/`

**获取复盘报告列表**
```bash
GET /api/reports/reviews/
Query: ?review_type=daily
```

**获取报告详情**
```bash
GET /api/reports/reviews/{id}/
```

---

## 🎯 核心功能说明

### 1. 感知层 (Perception Agent)

**功能**：
- 实时采集市场数据（OHLCV）
- 计算技术指标（MA、RSI、MACD、Bollinger Bands）
- 识别交易机会
- 监控市场情绪

**运行**：
```bash
python manage.py run_perception --interval 30
```

**日志**：`logs/perception.log`

### 2. 决策层 (Decision Agent)

**功能**：
- 多智能体辩论机制
  - 激进派：积极做多
  - 保守派：谨慎观望
  - 量化派：数据分析
  - 裁判：综合决策
- 生成交易决策
- 设定止损止盈

**运行**：
```bash
python manage.py run_decision --interval 60
```

**日志**：`logs/decision.log`

### 3. 执行层 (Execution Agent)

**功能**：
- 交易前风险控制
  - 单笔交易限额：5%
  - 仓位集中度：30%
  - 当日亏损限制：5%
  - 最大回撤：15%
- 模拟交易执行
- 持仓监控

**运行**：
```bash
python manage.py run_execution --interval 30
```

**日志**：`logs/execution.log`

### 4. 规划层 (Planning Agent)

**功能**：
- 制定交易计划（日度/周度/月度）
- 策略选择与配置
- 资金分配优化
- 监控计划执行

**运行**：
```bash
python manage.py run_planning --interval 300
```

**日志**：`logs/planning.log`

### 5. 反思层 (Reflection Agent)

**功能**：
- 每日自动复盘
- 成功/失败案例分析
- 策略自动进化
- 认知偏差检测

**运行**：
```bash
python manage.py run_reflection --interval 3600
```

**日志**：`logs/reflection.log`

### 6. 记忆层 (Memory Agent)

**功能**：
- 长期记忆存储（ChromaDB）
- 语义搜索
- 知识图谱构建
- 经验检索

**运行模式**：被动调用

---

## 🛠️ 常用命令

### 数据采集

```bash
# 采集 A 股数据
python manage.py collect_market_data --market CN --symbols 000001.SZ,600000.SH

# 采集美股数据
python manage.py collect_market_data --market US --symbols AAPL,GOOGL,MSFT
```

### 系统管理

```bash
# 启动所有智能体
./start_all_agents.sh

# 停止所有智能体
./stop_all_agents.sh

# 查看日志
tail -f logs/*.log
tail -f logs/perception.log

# 查看智能体状态
curl http://localhost:8000/api/agents/status/
```

### 数据库管理

```bash
# 创建迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 进入 Django Shell
python manage.py shell

# 加载测试数据
./load_mock_data.sh

# 清空数据库
python manage.py flush
```

---

## 📊 监控与调试

### 1. Django Admin

访问：http://localhost:8000/admin

**可以查看**：
- 智能体运行状态
- 交易记录
- 决策历史
- 持仓情况
- 复盘报告
- 策略表现

### 2. API 文档

访问：http://localhost:8000/api/schema/swagger-ui/

**功能**：
- 查看所有 API 端点
- 在线测试 API
- 查看请求/响应格式

### 3. 日志系统

```bash
# 实时查看所有日志
tail -f logs/*.log

# 查看特定智能体
tail -f logs/perception.log
tail -f logs/decision.log
tail -f logs/execution.log

# 搜索错误
grep -i error logs/*.log

# 查看最近100行
tail -n 100 logs/reflection.log
```

---

## 🔧 配置说明

### settings.py 配置

```python
# OpenAI 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# AI 交易系统配置
AI_TRADER_CONFIG = {
    'initial_funds': 1000000,      # 初始资金
    'simulation_mode': True,       # 模拟模式
    'risk_control': {
        'max_position_per_symbol': 0.05,  # 单标的最大仓位 5%
        'max_sector_exposure': 0.30,      # 行业最大暴露 30%
        'max_daily_loss': 0.03,           # 单日最大亏损 3%
        'stop_loss_pct': 0.05,            # 止损比例 5%
        'max_drawdown': 0.15,             # 最大回撤 15%
    },
    'agent_schedule': {
        'perception_interval': 30,    # 感知层间隔（秒）
        'decision_interval': 60,      # 决策层间隔（秒）
        'execution_interval': 30,     # 执行层间隔（秒）
        'planning_interval': 300,     # 规划层间隔（秒）
        'reflection_interval': 3600,  # 反思层间隔（秒）
    }
}
```

---

## 🐛 故障排查

### 问题 1: OpenAI API 错误

**症状**：`openai.error.AuthenticationError`

**解决**：
```bash
# 检查 API Key
echo $OPENAI_API_KEY

# 重新设置
export OPENAI_API_KEY="sk-your-key"
```

### 问题 2: 智能体未运行

**症状**：Admin 中看不到智能体状态更新

**解决**：
```bash
# 检查进程
ps aux | grep run_

# 查看日志
tail -f logs/*.log

# 重启智能体
./stop_all_agents.sh
./start_all_agents.sh
```

### 问题 3: 数据采集失败

**症状**：市场数据为空

**解决**：
```bash
# 检查网络
ping akshare.xyz

# 手动运行
python manage.py collect_market_data --market CN --symbols 000001.SZ

# 查看日志
tail -f logs/perception.log
```

### 问题 4: 数据库锁定

**症状**：`database is locked` (SQLite)

**解决**：
```bash
# 停止所有智能体
./stop_all_agents.sh

# 等待几秒
sleep 5

# 重启
./start_all_agents.sh
```

---

## 📈 使用场景

### 场景 1: 模拟交易

系统默认运行在模拟模式，使用虚拟资金进行交易。

```python
# 在 settings.py 中配置
AI_TRADER_CONFIG = {
    'initial_funds': 1000000,  # 初始资金 100 万
    'simulation_mode': True,   # 模拟模式
}
```

### 场景 2: 策略回测

通过 API 创建回测任务：

```bash
POST /api/strategies/backtest/
{
  "strategy_id": 1,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "initial_capital": 1000000
}
```

### 场景 3: 策略优化

系统会自动进行策略进化：

1. 每日复盘评估策略表现
2. 识别表现不佳的策略
3. 自动调整参数（变异）
4. 记录进化日志

---

## 📚 技术栈

### 后端框架
- Django 5.1.3
- Django REST Framework 3.15.2
- Django Channels 4.2.0

### AI & ML
- OpenAI GPT-4o-mini
- ChromaDB 0.5.23
- LangChain 0.3.13

### 数据处理
- Pandas 2.2.3
- NumPy 2.0.2
- AKShare 1.15.22
- yfinance 0.2.50

### 数据库
- SQLite（开发）
- PostgreSQL（生产推荐）

---

## 🔐 安全说明

### 1. API 认证

所有 API 端点都需要认证：

```bash
# 获取 Token
curl -X POST http://localhost:8000/api/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123456"}'

# 使用 Token 调用 API
curl -H "Authorization: Token your-token" \
     http://localhost:8000/api/trades/
```

### 2. 风险控制

系统内置多层风控：

1. **策略层风控** - 策略有效性验证
2. **决策层风控** - 决策信心评分
3. **执行前风控** - 5项核心检查
4. **执行中风控** - 持仓实时监控
5. **事后风控** - 交易质量评估

### 3. 模拟模式

**强烈建议**：
- 新用户在模拟模式下运行至少1个月
- 观察智能体决策质量
- 根据复盘报告优化参数
- 验证策略有效性后再考虑实盘

---

## 🎓 学习路径

### 初级（第1周）

1. ✅ 启动系统并观察日志
2. ✅ 通过 Admin 查看智能体状态
3. ✅ 查看生成的交易决策
4. ✅ 阅读每日复盘报告

### 中级（第2-4周）

1. 📊 分析策略表现
2. 🔧 调整风控参数
3. 🎯 创建自定义策略
4. 📈 优化资金分配

### 高级（第2个月+）

1. 🧬 研究策略进化机制
2. 🤖 开发新的智能体层
3. 🔗 集成实盘接口
4. 🖥️ 开发前端界面

---

## 📞 获取帮助

### 文档资源

- **系统文档**: http://localhost:8000/api/docs/system-guide/
- **API 文档**: http://localhost:8000/api/schema/swagger-ui/
- **设计文档**: `/workspace/code/Trade/functions.MD`

### 调试工具

```bash
# Django Shell
python manage.py shell

# 测试智能体
from services.agents.perception import PerceptionAgent
agent = PerceptionAgent()
result = agent.run()
print(result)

# 查看数据库
python manage.py dbshell
```

### 常见问题

1. **智能体不工作**？检查日志和进程状态
2. **API 调用失败**？检查认证 Token
3. **数据不更新**？检查数据采集器运行状态
4. **决策质量差**？调整策略参数和风控阈值

---

## 🚀 下一步计划

### 近期（1-2月）

- [ ] 完善回测系统
- [ ] 增加更多策略类型
- [ ] 优化决策算法
- [ ] 开发 React 前端界面

### 中期（3-6月）

- [ ] 实盘接口对接
- [ ] 多账户支持
- [ ] 分布式部署
- [ ] 性能监控系统

### 长期（6月+）

- [ ] 机器学习策略
- [ ] 高频交易支持
- [ ] 跨市场套利
- [ ] 社区版本发布

---

## 📄 许可证

本项目仅供学习和研究使用。

**免责声明**：
- 本系统为教育和研究目的开发
- 不构成任何投资建议
- 实盘交易风险自负
- 请遵守当地法律法规

---

## 🎉 开始使用

```bash
# 1. 配置 API Key
export OPENAI_API_KEY="your-key"

# 2. 初始化
python manage.py migrate
./load_mock_data.sh

# 3. 启动
./start_all_agents.sh
python manage.py runserver

# 4. 访问
open http://localhost:8000/admin
```

**祝交易顺利！🚀📈**

---

*最后更新: 2025-11-22*

