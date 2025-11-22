import { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Button, Select, Statistic, Row, Col, Progress, message } from 'antd';
import {
  FundOutlined,
  SyncOutlined,
  RiseOutlined,
  FallOutlined,
  TrophyOutlined,
} from '@ant-design/icons';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '@/services/api';
import type { Position } from '@/types';
import dayjs from 'dayjs';

const Positions = () => {
  const [loading, setLoading] = useState(true);
  const [positions, setPositions] = useState<Position[]>([]);
  const [accountType, setAccountType] = useState<'all' | 'simulation' | 'real'>('all');

  // 加载持仓数据
  const loadPositions = async () => {
    setLoading(true);
    try {
      const params: any = { is_closed: false };
      if (accountType !== 'all') {
        params.account_type = accountType;
      }
      const response: any = await apiService.getPositions(params);
      const positionList = response.results || response || [];
      setPositions(positionList);
    } catch (error) {
      console.error('Failed to load positions:', error);
      message.error('加载持仓数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPositions();
  }, [accountType]);

  // 统计数据
  const stats = {
    total: positions.length,
    totalValue: positions.reduce((sum, p) => sum + parseFloat(p.market_value || '0'), 0),
    totalCost: positions.reduce((sum, p) => sum + parseFloat(p.total_cost || '0'), 0),
    totalPnl: positions.reduce((sum, p) => sum + parseFloat(p.unrealized_pnl || '0'), 0),
    profit: positions.filter(p => parseFloat(p.unrealized_pnl || '0') > 0).length,
    loss: positions.filter(p => parseFloat(p.unrealized_pnl || '0') < 0).length,
  };

  stats.totalReturn = stats.totalCost > 0 ? ((stats.totalPnl / stats.totalCost) * 100) : 0;

  // 持仓分布数据
  const positionDistData = positions.map(p => ({
    name: p.symbol,
    value: parseFloat(p.market_value || '0'),
  })).sort((a, b) => b.value - a.value);

  // 盈亏排行
  const pnlRankData = positions.map(p => ({
    symbol: p.symbol,
    pnl: parseFloat(p.unrealized_pnl || '0'),
    pnlPct: parseFloat(p.unrealized_pnl_pct || '0'),
  })).sort((a, b) => b.pnl - a.pnl);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d', '#ffc658'];

  // 表格列定义
  const columns = [
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <strong>{symbol}</strong>,
      fixed: 'left' as const,
      width: 100,
    },
    {
      title: '账户',
      dataIndex: 'account_type',
      key: 'account_type',
      render: (type: string) => (
        <Tag color={type === 'simulation' ? 'blue' : 'green'}>
          {type === 'simulation' ? '模拟' : '实盘'}
        </Tag>
      ),
      width: 80,
    },
    {
      title: '持仓数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      sorter: (a: Position, b: Position) => a.quantity - b.quantity,
    },
    {
      title: '可用/冻结',
      key: 'available',
      render: (_: any, record: Position) => (
        <div>
          <div style={{ color: '#52c41a' }}>可用: {record.available_quantity}</div>
          <div style={{ color: '#ff4d4f', fontSize: 12 }}>冻结: {record.frozen_quantity}</div>
        </div>
      ),
      width: 120,
    },
    {
      title: '成本价',
      dataIndex: 'avg_cost',
      key: 'avg_cost',
      render: (cost: string) => `¥${parseFloat(cost).toFixed(2)}`,
      width: 100,
      sorter: (a: Position, b: Position) => parseFloat(a.avg_cost) - parseFloat(b.avg_cost),
    },
    {
      title: '现价',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: string | null) => price ? `¥${parseFloat(price).toFixed(2)}` : '-',
      width: 100,
    },
    {
      title: '总成本',
      dataIndex: 'total_cost',
      key: 'total_cost',
      render: (cost: string) => `¥${parseFloat(cost).toLocaleString()}`,
      width: 120,
      sorter: (a: Position, b: Position) => parseFloat(a.total_cost) - parseFloat(b.total_cost),
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      render: (value: string | null) => value ? `¥${parseFloat(value).toLocaleString()}` : '-',
      width: 120,
      sorter: (a: Position, b: Position) => parseFloat(a.market_value || '0') - parseFloat(b.market_value || '0'),
    },
    {
      title: '浮动盈亏',
      key: 'unrealized_pnl',
      render: (_: any, record: Position) => {
        const pnl = parseFloat(record.unrealized_pnl || '0');
        const pnlPct = parseFloat(record.unrealized_pnl_pct || '0');
        return (
          <div style={{ color: pnl >= 0 ? '#3f8600' : '#cf1322', fontWeight: 'bold' }}>
            <div>{pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}</div>
            <div style={{ fontSize: 12 }}>({pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%)</div>
          </div>
        );
      },
      width: 130,
      sorter: (a: Position, b: Position) => parseFloat(a.unrealized_pnl || '0') - parseFloat(b.unrealized_pnl || '0'),
    },
    {
      title: '仓位占比',
      key: 'position_ratio',
      render: (_: any, record: Position) => {
        const ratio = stats.totalValue > 0 ? (parseFloat(record.market_value || '0') / stats.totalValue) * 100 : 0;
        return (
          <Progress
            percent={ratio}
            size="small"
            format={(percent) => `${percent?.toFixed(1)}%`}
          />
        );
      },
      width: 150,
    },
    {
      title: '持仓天数',
      dataIndex: 'holding_days',
      key: 'holding_days',
      render: (days: number) => `${days}天`,
      width: 100,
      sorter: (a: Position, b: Position) => a.holding_days - b.holding_days,
    },
    {
      title: '止损/止盈',
      key: 'stop_prices',
      render: (_: any, record: Position) => (
        <div style={{ fontSize: 12 }}>
          {record.stop_loss && <div style={{ color: '#ff4d4f' }}>止损: ¥{parseFloat(record.stop_loss).toFixed(2)}</div>}
          {record.take_profit && <div style={{ color: '#52c41a' }}>止盈: ¥{parseFloat(record.take_profit).toFixed(2)}</div>}
          {!record.stop_loss && !record.take_profit && <span style={{ color: '#999' }}>未设置</span>}
        </div>
      ),
      width: 120,
    },
    {
      title: '开仓时间',
      dataIndex: 'opened_at',
      key: 'opened_at',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD'),
      width: 120,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <h2><FundOutlined /> 持仓管理</h2>
          <Select
            value={accountType}
            onChange={setAccountType}
            style={{ width: 120 }}
            options={[
              { label: '全部账户', value: 'all' },
              { label: '模拟账户', value: 'simulation' },
              { label: '实盘账户', value: 'real' },
            ]}
          />
        </Space>
        <Button icon={<SyncOutlined />} onClick={loadPositions} loading={loading}>
          刷新
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="持仓数量"
              value={stats.total}
              suffix="个"
              prefix={<FundOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="持仓市值"
              value={stats.totalValue}
              precision={2}
              prefix="¥"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="浮动盈亏"
              value={stats.totalPnl}
              precision={2}
              prefix={stats.totalPnl >= 0 ? <RiseOutlined /> : <FallOutlined />}
              valueStyle={{ color: stats.totalPnl >= 0 ? '#3f8600' : '#cf1322' }}
              suffix={`¥ (${stats.totalReturn.toFixed(2)}%)`}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="盈亏比"
              value={`${stats.profit} : ${stats.loss}`}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: stats.profit >= stats.loss ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表分析 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="持仓分布（按市值）">
            <ResponsiveContainer width="100%" height={300}>
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
        <Col xs={24} lg={12}>
          <Card title="盈亏排行（TOP 10）">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={pnlRankData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="symbol" />
                <YAxis />
                <Tooltip
                  formatter={(value: number, name: string) => {
                    if (name === 'pnl') return [`¥${value.toFixed(2)}`, '盈亏'];
                    return [`${value.toFixed(2)}%`, '收益率'];
                  }}
                />
                <Legend />
                <Bar dataKey="pnl" fill="#1890ff" name="盈亏" />
                <Bar dataKey="pnlPct" fill="#52c41a" name="收益率(%)" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 持仓列表 */}
      <Card
        title={`持仓列表 (${positions.length}个)`}
        style={{ marginTop: 16 }}
        extra={
          <Space>
            <Tag color="green">盈利: {stats.profit}</Tag>
            <Tag color="red">亏损: {stats.loss}</Tag>
          </Space>
        }
      >
        <Table
          dataSource={positions}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个持仓`,
          }}
          scroll={{ x: 1600 }}
          rowClassName={(record) => {
            const pnl = parseFloat(record.unrealized_pnl || '0');
            return pnl > 0 ? 'row-profit' : pnl < 0 ? 'row-loss' : '';
          }}
        />
      </Card>

      <style>{`
        .row-profit {
          background-color: #f6ffed;
        }
        .row-loss {
          background-color: #fff1f0;
        }
      `}</style>
    </div>
  );
};

export default Positions;
