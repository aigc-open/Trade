import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Tag, Table, Spin, Space, Button } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  RiseOutlined,
  FallOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  SyncOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '../../services/api';
import type { AgentStatus, Portfolio, Strategy, Trade, Position } from '../../types';
import './index.css';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const [portfolioRes, agentsRes, strategiesRes, tradesRes, positionsRes]: any = await Promise.all([
        apiService.getPortfolios({ account_name: 'simulation_main' }),
        apiService.getAgentStatus(),
        apiService.getStrategies({ status: 'active', ordering: '-score' }),
        apiService.getTrades({ ordering: '-order_time', limit: 10 }),
        apiService.getPositions({ is_closed: false, ordering: '-unrealized_pnl_pct' }),
      ]);

      setPortfolio(portfolioRes.results?.[0] || portfolioRes[0] || null);
      setAgents(agentsRes.results || agentsRes || []);
      setStrategies(strategiesRes.results || strategiesRes || []);
      setRecentTrades(tradesRes.results || tradesRes || []);
      setPositions(positionsRes.results || positionsRes || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // 每30秒刷新一次
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 智能体状态映射
  const agentTypeNames: Record<string, string> = {
    perception: '感知层',
    memory: '记忆层',
    planning: '规划层',
    decision: '决策层',
    execution: '执行层',
    reflection: '反思层',
  };

  // 智能体状态颜色
  const agentStatusColor: Record<string, string> = {
    running: 'success',
    stopped: 'default',
    error: 'error',
    paused: 'warning',
  };

  // 智能体状态文本
  const agentStatusText: Record<string, string> = {
    running: '运行中',
    stopped: '已停止',
    error: '错误',
    paused: '已暂停',
  };

  // 模拟收益曲线数据
  const profitData = [
    { date: '11-15', value: 1000000 },
    { date: '11-16', value: 1005000 },
    { date: '11-17', value: 1012000 },
    { date: '11-18', value: 1018000 },
    { date: '11-19', value: 1015000 },
    { date: '11-20', value: 1020000 },
    { date: '11-21', value: 1022000 },
    { date: '11-22', value: parseFloat(portfolio?.total_asset || '1025300') },
  ];

  // 策略表现数据
  const strategyPerformanceData = strategies.slice(0, 5).map(s => ({
    name: s.name.slice(0, 6),
    return: parseFloat(s.total_return || '0') * 100,
    winRate: parseFloat(s.win_rate || '0'),
  }));

  // 持仓分布数据
  const positionDistData = positions.slice(0, 5).map(p => ({
    name: p.symbol,
    value: parseFloat(p.market_value || '0'),
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // 交易列表列定义
  const tradeColumns = [
    {
      title: '时间',
      dataIndex: 'filled_time',
      key: 'filled_time',
      render: (text: string) => text ? new Date(text).toLocaleString('zh-CN') : '-',
      width: 160,
    },
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag color={action === 'BUY' ? 'green' : 'red'}>
          {action === 'BUY' ? '买入' : '卖出'}
        </Tag>
      ),
    },
    {
      title: '数量',
      dataIndex: 'filled_quantity',
      key: 'filled_quantity',
    },
    {
      title: '成交价',
      dataIndex: 'filled_price',
      key: 'filled_price',
      render: (price: string) => `¥${parseFloat(price || '0').toFixed(2)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string; color: string }> = {
          filled: { text: '已成交', color: 'success' },
          pending: { text: '待执行', color: 'processing' },
          cancelled: { text: '已取消', color: 'default' },
          failed: { text: '失败', color: 'error' },
        };
        const s = statusMap[status] || { text: status, color: 'default' };
        return <Tag color={s.color}>{s.text}</Tag>;
      },
    },
  ];

  return (
    <div className="dashboard">
      {/* 顶部统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总资产"
              value={parseFloat(portfolio?.total_asset || '0')}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#3f8600' }}
              suffix={
                <span style={{ fontSize: 14, color: '#999' }}>
                  ({(parseFloat(portfolio?.total_return || '0') * 100).toFixed(2)}%)
                </span>
              }
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日盈亏"
              value={parseFloat(portfolio?.today_pnl || '0')}
              precision={2}
              prefix={parseFloat(portfolio?.today_pnl || '0') >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: parseFloat(portfolio?.today_pnl || '0') >= 0 ? '#3f8600' : '#cf1322' }}
              suffix={`¥ (${(parseFloat(portfolio?.today_return || '0') * 100).toFixed(2)}%)`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="持仓数量"
              value={positions.length}
              suffix="个"
              prefix={<FallOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="胜率"
              value={parseFloat(portfolio?.win_rate || '0')}
              precision={2}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 智能体状态 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card
            title={
              <Space>
                <RobotOutlined />
                <span>智能体状态监控</span>
              </Space>
            }
            extra={
              <Button icon={<SyncOutlined />} onClick={loadData}>
                刷新
              </Button>
            }
          >
            <Row gutter={[16, 16]}>
              {agents.map((agent) => (
                <Col key={agent.id} xs={24} sm={12} lg={8} xl={4}>
                  <Card size="small" className="agent-card">
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: 24, marginBottom: 8 }}>
                        {agent.status === 'running' ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> : '⏸️'}
                      </div>
                      <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
                        {agentTypeNames[agent.agent_type]}
                      </div>
                      <Tag color={agentStatusColor[agent.status]}>
                        {agentStatusText[agent.status]}
                      </Tag>
                      {agent.metrics?.success_rate && (
                        <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                          成功率: {agent.metrics.success_rate.toFixed(1)}%
                        </div>
                      )}
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 收益曲线和策略表现 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="资产趋势" extra={<Tag color="blue">近7天</Tag>}>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={profitData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: number) => `¥${value.toLocaleString()}`} />
                <Area type="monotone" dataKey="value" stroke="#1890ff" fillOpacity={1} fill="url(#colorValue)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="持仓分布">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={positionDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${(entry.value / positionDistData.reduce((a, b) => a + b.value, 0) * 100).toFixed(1)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {positionDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number) => `¥${value.toLocaleString()}`} />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 策略表现 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title={<Space><ThunderboltOutlined />活跃策略表现</Space>}>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={strategyPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="return" fill="#1890ff" name="收益率(%)" />
                <Bar yAxisId="right" dataKey="winRate" fill="#52c41a" name="胜率(%)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="最新交易">
            <Table
              dataSource={recentTrades}
              columns={tradeColumns}
              rowKey="id"
              pagination={false}
              size="small"
              scroll={{ x: 600 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;

