import { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Table, Tag, Progress, Select, DatePicker, Space, Button } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  WalletOutlined,
  SyncOutlined,
  TrophyOutlined,
  FallOutlined,
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService } from '@/services/api';
import type { Portfolio, Position } from '@/types';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const PortfolioPage = () => {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [accountType, setAccountType] = useState<'simulation' | 'real'>('simulation');

  // 加载数据
  const loadData = async () => {
    setLoading(true);
    try {
      const [portfolioRes, positionsRes]: any = await Promise.all([
        apiService.getPortfolios({ account_type: accountType }),
        apiService.getPositions({ account_type: accountType, is_closed: false }),
      ]);

      setPortfolio(portfolioRes.results?.[0] || portfolioRes[0] || null);
      setPositions(positionsRes.results || positionsRes || []);
    } catch (error) {
      console.error('Failed to load portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [accountType]);

  // 模拟30天收益数据
  const generateEquityData = () => {
    const data = [];
    const baseValue = parseFloat(portfolio?.initial_capital || '1000000');
    const finalValue = parseFloat(portfolio?.total_asset || '1025300');
    const days = 30;

    for (let i = 0; i <= days; i++) {
      const progress = i / days;
      const randomWalk = Math.sin(i * 0.5) * 5000;
      const value = baseValue + (finalValue - baseValue) * progress + randomWalk;
      
      data.push({
        date: dayjs().subtract(days - i, 'day').format('MM-DD'),
        equity: Math.round(value),
        cash: Math.round(value * 0.3),
        position: Math.round(value * 0.7),
      });
    }
    return data;
  };

  // 持仓分布数据
  const positionDistData = positions.map((p) => ({
    name: p.symbol,
    value: parseFloat(p.market_value || '0'),
    pnl: parseFloat(p.unrealized_pnl || '0'),
  }));

  // 收益分布数据
  const pnlDistData = [
    { name: '已实现盈亏', value: parseFloat(portfolio?.total_pnl || '0') * 0.6 },
    { name: '浮动盈亏', value: parseFloat(portfolio?.total_pnl || '0') * 0.4 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

  // 持仓列表
  const positionColumns = [
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <strong>{symbol}</strong>,
    },
    {
      title: '持仓数量',
      dataIndex: 'quantity',
      key: 'quantity',
    },
    {
      title: '可用数量',
      dataIndex: 'available_quantity',
      key: 'available_quantity',
    },
    {
      title: '成本价',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (cost: string) => `¥${parseFloat(cost).toFixed(2)}`,
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: string | null) => price ? `¥${parseFloat(price).toFixed(2)}` : '-',
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      render: (value: string | null) => value ? `¥${parseFloat(value).toLocaleString()}` : '-',
    },
    {
      title: '浮动盈亏',
      dataIndex: 'unrealized_pnl',
      key: 'unrealized_pnl',
      render: (pnl: string | null, record: Position) => {
        const pnlValue = parseFloat(pnl || '0');
        const pnlPct = parseFloat(record.unrealized_pnl_pct || '0');
        return (
          <div style={{ color: pnlValue >= 0 ? '#3f8600' : '#cf1322' }}>
            <div>{pnlValue >= 0 ? '+' : ''}{pnlValue.toFixed(2)}</div>
            <div style={{ fontSize: 12 }}>({pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%)</div>
          </div>
        );
      },
    },
    {
      title: '持仓天数',
      dataIndex: 'holding_days',
      key: 'holding_days',
      render: (days: number) => `${days}天`,
    },
  ];

  const equityData = portfolio ? generateEquityData() : [];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <h2><WalletOutlined /> 投资组合</h2>
          <Select
            value={accountType}
            onChange={setAccountType}
            style={{ width: 120 }}
            options={[
              { label: '模拟账户', value: 'simulation' },
              { label: '实盘账户', value: 'real' },
            ]}
          />
        </Space>
        <Button icon={<SyncOutlined />} onClick={loadData} loading={loading}>
          刷新
        </Button>
      </div>

      {/* 账户概览 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总资产"
              value={parseFloat(portfolio?.total_asset || '0')}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              初始资金: ¥{parseFloat(portfolio?.initial_capital || '0').toLocaleString()}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总盈亏"
              value={parseFloat(portfolio?.total_pnl || '0')}
              precision={2}
              prefix={parseFloat(portfolio?.total_pnl || '0') >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: parseFloat(portfolio?.total_pnl || '0') >= 0 ? '#3f8600' : '#cf1322' }}
              suffix={`¥ (${(parseFloat(portfolio?.total_return || '0') * 100).toFixed(2)}%)`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="可用资金"
              value={parseFloat(portfolio?.available_cash || '0')}
              precision={2}
              prefix="¥"
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              总现金: ¥{parseFloat(portfolio?.cash || '0').toLocaleString()}
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="持仓市值"
              value={parseFloat(portfolio?.market_value || '0')}
              precision={2}
              prefix="¥"
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              持仓数: {positions.length}个
            </div>
          </Card>
        </Col>
      </Row>

      {/* 业绩指标 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="胜率"
              value={parseFloat(portfolio?.win_rate || '0')}
              precision={2}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="最大回撤"
              value={parseFloat(portfolio?.max_drawdown || '0') * 100}
              precision={2}
              suffix="%"
              prefix={<FallOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="夏普比率"
              value={parseFloat(portfolio?.sharpe_ratio || '0')}
              precision={2}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="交易次数"
              value={portfolio?.total_trades || 0}
              suffix="次"
            />
            <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
              盈: {portfolio?.win_trades || 0} / 亏: {portfolio?.lose_trades || 0}
            </div>
          </Card>
        </Col>
      </Row>

      {/* 权益曲线和资产分布 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="权益曲线" extra={<Tag color="blue">近30天</Tag>}>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={equityData}>
                <defs>
                  <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#1890ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: number) => `¥${value.toLocaleString()}`} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="equity"
                  stroke="#1890ff"
                  fillOpacity={1}
                  fill="url(#colorEquity)"
                  name="总资产"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="持仓分布">
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={positionDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}`}
                  outerRadius={100}
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

      {/* 现金与持仓趋势 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="资产构成趋势">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={equityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value: number) => `¥${value.toLocaleString()}`} />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="cash"
                  stackId="1"
                  stroke="#52c41a"
                  fill="#52c41a"
                  name="现金"
                />
                <Area
                  type="monotone"
                  dataKey="position"
                  stackId="1"
                  stroke="#1890ff"
                  fill="#1890ff"
                  name="持仓"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 持仓明细 */}
      <Card title="持仓明细" style={{ marginTop: 16 }}>
        <Table
          dataSource={positions}
          columns={positionColumns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          scroll={{ x: 1000 }}
        />
      </Card>
    </div>
  );
};

export default PortfolioPage;
