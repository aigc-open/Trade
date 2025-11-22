import { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Button, Input, Select, DatePicker, Statistic, Row, Col, Modal, Descriptions } from 'antd';
import {
  LineChartOutlined,
  SearchOutlined,
  SyncOutlined,
  EyeOutlined,
  FilterOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '@/services/api';
import type { Trade } from '@/types';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const Trades = () => {
  const [loading, setLoading] = useState(true);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filteredTrades, setFilteredTrades] = useState<Trade[]>([]);
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  
  // 筛选条件
  const [filters, setFilters] = useState({
    symbol: '',
    action: 'all',
    status: 'all',
    accountType: 'all',
  });

  // 加载交易数据
  const loadTrades = async () => {
    setLoading(true);
    try {
      const response: any = await apiService.getTrades({ ordering: '-order_time' });
      const tradeList = response.results || response || [];
      setTrades(tradeList);
      setFilteredTrades(tradeList);
    } catch (error) {
      console.error('Failed to load trades:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrades();
  }, []);

  // 应用筛选
  useEffect(() => {
    let filtered = [...trades];
    
    if (filters.symbol) {
      filtered = filtered.filter(t => t.symbol.toLowerCase().includes(filters.symbol.toLowerCase()));
    }
    if (filters.action !== 'all') {
      filtered = filtered.filter(t => t.action === filters.action);
    }
    if (filters.status !== 'all') {
      filtered = filtered.filter(t => t.status === filters.status);
    }
    if (filters.accountType !== 'all') {
      filtered = filtered.filter(t => t.account_type === filters.accountType);
    }
    
    setFilteredTrades(filtered);
  }, [filters, trades]);

  // 统计数据
  const stats = {
    total: filteredTrades.length,
    buy: filteredTrades.filter(t => t.action === 'BUY').length,
    sell: filteredTrades.filter(t => t.action === 'SELL').length,
    filled: filteredTrades.filter(t => t.status === 'filled').length,
    profit: filteredTrades.filter(t => parseFloat(t.pnl || '0') > 0).length,
    loss: filteredTrades.filter(t => parseFloat(t.pnl || '0') < 0).length,
    totalProfit: filteredTrades.reduce((sum, t) => sum + parseFloat(t.pnl || '0'), 0),
  };

  // 操作类型分布
  const actionDistData = [
    { name: '买入', value: stats.buy },
    { name: '卖出', value: stats.sell },
  ];

  // 状态分布
  const statusDistData = [
    { name: '已成交', value: filteredTrades.filter(t => t.status === 'filled').length },
    { name: '待执行', value: filteredTrades.filter(t => t.status === 'pending').length },
    { name: '部分成交', value: filteredTrades.filter(t => t.status === 'partial_filled').length },
    { name: '已取消', value: filteredTrades.filter(t => t.status === 'cancelled').length },
    { name: '失败', value: filteredTrades.filter(t => t.status === 'failed').length },
  ].filter(item => item.value > 0);

  const COLORS = ['#52c41a', '#1890ff', '#faad14', '#ff4d4f', '#722ed1'];

  // 查看详情
  const showDetail = (trade: Trade) => {
    setSelectedTrade(trade);
    setModalVisible(true);
  };

  // 表格列定义
  const columns = [
    {
      title: '时间',
      dataIndex: 'order_time',
      key: 'order_time',
      render: (time: string) => dayjs(time).format('YYYY-MM-DD HH:mm:ss'),
      width: 160,
      sorter: (a: Trade, b: Trade) => dayjs(a.order_time).unix() - dayjs(b.order_time).unix(),
    },
    {
      title: '交易ID',
      dataIndex: 'trade_id',
      key: 'trade_id',
      width: 160,
    },
    {
      title: '标的',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <strong>{symbol}</strong>,
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
      filters: [
        { text: '买入', value: 'BUY' },
        { text: '卖出', value: 'SELL' },
      ],
      onFilter: (value: any, record: Trade) => record.action === value,
    },
    {
      title: '数量',
      dataIndex: 'filled_quantity',
      key: 'filled_quantity',
    },
    {
      title: '委托价',
      dataIndex: 'order_price',
      key: 'order_price',
      render: (price: string) => `¥${parseFloat(price).toFixed(2)}`,
    },
    {
      title: '成交价',
      dataIndex: 'filled_price',
      key: 'filled_price',
      render: (price: string | null) => price ? `¥${parseFloat(price).toFixed(2)}` : '-',
    },
    {
      title: '成交额',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (amount: string) => `¥${parseFloat(amount).toLocaleString()}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { text: string; color: string }> = {
          filled: { text: '已成交', color: 'success' },
          pending: { text: '待执行', color: 'processing' },
          partial_filled: { text: '部分成交', color: 'warning' },
          submitted: { text: '已提交', color: 'default' },
          cancelled: { text: '已取消', color: 'default' },
          failed: { text: '失败', color: 'error' },
        };
        const s = statusMap[status] || { text: status, color: 'default' };
        return <Tag color={s.color}>{s.text}</Tag>;
      },
      filters: [
        { text: '已成交', value: 'filled' },
        { text: '待执行', value: 'pending' },
        { text: '部分成交', value: 'partial_filled' },
        { text: '已取消', value: 'cancelled' },
        { text: '失败', value: 'failed' },
      ],
      onFilter: (value: any, record: Trade) => record.status === value,
    },
    {
      title: '盈亏',
      dataIndex: 'pnl',
      key: 'pnl',
      render: (pnl: string | null, record: Trade) => {
        if (!pnl) return '-';
        const pnlValue = parseFloat(pnl);
        const pnlPct = parseFloat(record.pnl_pct || '0');
        return (
          <div style={{ color: pnlValue >= 0 ? '#3f8600' : '#cf1322' }}>
            <div>{pnlValue >= 0 ? '+' : ''}{pnlValue.toFixed(2)}</div>
            <div style={{ fontSize: 12 }}>({pnlPct >= 0 ? '+' : ''}{pnlPct.toFixed(2)}%)</div>
          </div>
        );
      },
      sorter: (a: Trade, b: Trade) => parseFloat(a.pnl || '0') - parseFloat(b.pnl || '0'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Trade) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => showDetail(record)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2><LineChartOutlined /> 交易记录</h2>
        <Button icon={<SyncOutlined />} onClick={loadTrades} loading={loading}>
          刷新
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic title="总交易" value={stats.total} suffix="笔" />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic title="买入" value={stats.buy} suffix="笔" valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic title="卖出" value={stats.sell} suffix="笔" valueStyle={{ color: '#ff4d4f' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic title="已成交" value={stats.filled} suffix="笔" valueStyle={{ color: '#1890ff' }} />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic
              title="总盈亏"
              value={stats.totalProfit}
              precision={2}
              prefix={stats.totalProfit >= 0 ? <RiseOutlined /> : <FallOutlined />}
              valueStyle={{ color: stats.totalProfit >= 0 ? '#3f8600' : '#cf1322' }}
              suffix="¥"
            />
          </Card>
        </Col>
        <Col xs={12} sm={8} lg={4}>
          <Card>
            <Statistic
              title="胜率"
              value={stats.profit + stats.loss > 0 ? (stats.profit / (stats.profit + stats.loss)) * 100 : 0}
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选条件 */}
      <Card title={<Space><FilterOutlined />筛选条件</Space>} style={{ marginTop: 16 }}>
        <Row gutter={16}>
          <Col xs={24} sm={12} md={6}>
            <Input
              placeholder="搜索标的代码"
              prefix={<SearchOutlined />}
              value={filters.symbol}
              onChange={(e) => setFilters({ ...filters, symbol: e.target.value })}
              allowClear
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              style={{ width: '100%' }}
              value={filters.action}
              onChange={(value) => setFilters({ ...filters, action: value })}
              options={[
                { label: '全部操作', value: 'all' },
                { label: '买入', value: 'BUY' },
                { label: '卖出', value: 'SELL' },
              ]}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              style={{ width: '100%' }}
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
              options={[
                { label: '全部状态', value: 'all' },
                { label: '已成交', value: 'filled' },
                { label: '待执行', value: 'pending' },
                { label: '部分成交', value: 'partial_filled' },
                { label: '已取消', value: 'cancelled' },
                { label: '失败', value: 'failed' },
              ]}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              style={{ width: '100%' }}
              value={filters.accountType}
              onChange={(value) => setFilters({ ...filters, accountType: value })}
              options={[
                { label: '全部账户', value: 'all' },
                { label: '模拟账户', value: 'simulation' },
                { label: '实盘账户', value: 'real' },
              ]}
            />
          </Col>
        </Row>
      </Card>

      {/* 图表分析 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} md={12}>
          <Card title="操作类型分布">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={actionDistData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {actionDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="交易状态分布">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={statusDistData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1890ff" name="数量" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 交易列表 */}
      <Card title={`交易列表 (${filteredTrades.length}笔)`} style={{ marginTop: 16 }}>
        <Table
          dataSource={filteredTrades}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 笔交易`,
          }}
          scroll={{ x: 1400 }}
        />
      </Card>

      {/* 详情模态框 */}
      <Modal
        title="交易详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedTrade && (
          <Descriptions bordered column={2}>
            <Descriptions.Item label="交易ID" span={2}>{selectedTrade.trade_id}</Descriptions.Item>
            <Descriptions.Item label="标的">{selectedTrade.symbol}</Descriptions.Item>
            <Descriptions.Item label="操作">
              <Tag color={selectedTrade.action === 'BUY' ? 'green' : 'red'}>
                {selectedTrade.action === 'BUY' ? '买入' : '卖出'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="账户类型">
              {selectedTrade.account_type === 'simulation' ? '模拟账户' : '实盘账户'}
            </Descriptions.Item>
            <Descriptions.Item label="账户名">{selectedTrade.account_name}</Descriptions.Item>
            <Descriptions.Item label="委托价格">¥{parseFloat(selectedTrade.order_price).toFixed(2)}</Descriptions.Item>
            <Descriptions.Item label="委托数量">{selectedTrade.order_quantity}</Descriptions.Item>
            <Descriptions.Item label="成交价格">
              {selectedTrade.filled_price ? `¥${parseFloat(selectedTrade.filled_price).toFixed(2)}` : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="成交数量">{selectedTrade.filled_quantity}</Descriptions.Item>
            <Descriptions.Item label="成交金额">¥{parseFloat(selectedTrade.total_amount).toLocaleString()}</Descriptions.Item>
            <Descriptions.Item label="手续费">¥{parseFloat(selectedTrade.commission).toFixed(2)}</Descriptions.Item>
            <Descriptions.Item label="滑点">¥{parseFloat(selectedTrade.slippage).toFixed(2)}</Descriptions.Item>
            <Descriptions.Item label="盈亏">
              {selectedTrade.pnl ? (
                <span style={{ color: parseFloat(selectedTrade.pnl) >= 0 ? '#3f8600' : '#cf1322' }}>
                  ¥{parseFloat(selectedTrade.pnl).toFixed(2)} ({parseFloat(selectedTrade.pnl_pct || '0').toFixed(2)}%)
                </span>
              ) : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="状态">
              <Tag color={
                selectedTrade.status === 'filled' ? 'success' :
                selectedTrade.status === 'failed' ? 'error' : 'processing'
              }>
                {selectedTrade.status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="委托时间" span={2}>
              {dayjs(selectedTrade.order_time).format('YYYY-MM-DD HH:mm:ss')}
            </Descriptions.Item>
            <Descriptions.Item label="成交时间" span={2}>
              {selectedTrade.filled_time ? dayjs(selectedTrade.filled_time).format('YYYY-MM-DD HH:mm:ss') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="交易原因" span={2}>{selectedTrade.reason}</Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default Trades;
