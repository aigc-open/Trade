import { useEffect, useState } from 'react';
import { Card, Table, Tag, Space, Button, Select, Statistic, Row, Col, Modal, Descriptions, Progress } from 'antd';
import {
  ThunderboltOutlined,
  SyncOutlined,
  EyeOutlined,
  TrophyOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { apiService } from '@/services/api';
import type { Strategy } from '@/types';
import dayjs from 'dayjs';

const Strategies = () => {
  const [loading, setLoading] = useState(true);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // 加载策略数据
  const loadStrategies = async () => {
    setLoading(true);
    try {
      const params: any = { ordering: '-score' };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response: any = await apiService.getStrategies(params);
      const strategyList = response.results || response || [];
      setStrategies(strategyList);
    } catch (error) {
      console.error('Failed to load strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStrategies();
  }, [statusFilter]);

  // 查看详情
  const showDetail = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setModalVisible(true);
  };

  // 统计数据
  const stats = {
    total: strategies.length,
    active: strategies.filter(s => s.status === 'active').length,
    avgReturn: strategies.reduce((sum, s) => sum + parseFloat(s.total_return || '0'), 0) / (strategies.length || 1),
    avgWinRate: strategies.reduce((sum, s) => sum + parseFloat(s.win_rate || '0'), 0) / (strategies.length || 1),
    topStrategy: strategies[0],
  };

  // 策略表现对比数据
  const strategyCompareData = strategies.slice(0, 8).map(s => ({
    name: s.name.slice(0, 8),
    return: parseFloat(s.total_return || '0') * 100,
    winRate: parseFloat(s.win_rate || '0'),
    sharpe: parseFloat(s.sharpe_ratio || '0'),
    score: parseFloat(s.score || '0') * 10,
  }));

  // 雷达图数据（用于策略详情）
  const getRadarData = (strategy: Strategy) => [
    { metric: '收益率', value: Math.min(100, parseFloat(strategy.total_return || '0') * 100 + 50), fullMark: 100 },
    { metric: '胜率', value: parseFloat(strategy.win_rate || '0'), fullMark: 100 },
    { metric: '夏普比率', value: Math.min(100, (parseFloat(strategy.sharpe_ratio || '0') + 2) * 20), fullMark: 100 },
    { metric: '使用频率', value: Math.min(100, (strategy.usage_count / 100) * 100), fullMark: 100 },
    { metric: '成功次数', value: Math.min(100, (strategy.success_count / (strategy.usage_count || 1)) * 100), fullMark: 100 },
    { metric: '评分', value: parseFloat(strategy.score || '0') * 10, fullMark: 100 },
  ];

  // 状态配置
  const statusConfig: Record<string, { text: string; color: string }> = {
    active: { text: '活跃', color: 'success' },
    testing: { text: '测试中', color: 'processing' },
    paused: { text: '已暂停', color: 'warning' },
    retired: { text: '已退役', color: 'default' },
  };

  // 表格列定义
  const columns = [
    {
      title: '策略名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => <strong>{name}</strong>,
      fixed: 'left' as const,
      width: 150,
    },
    {
      title: '类型',
      dataIndex: 'strategy_type',
      key: 'strategy_type',
      render: (type: string) => <Tag>{type}</Tag>,
      width: 120,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const config = statusConfig[status] || statusConfig.paused;
        return <Tag color={config.color}>{config.text}</Tag>;
      },
      width: 100,
      filters: [
        { text: '活跃', value: 'active' },
        { text: '测试中', value: 'testing' },
        { text: '已暂停', value: 'paused' },
        { text: '已退役', value: 'retired' },
      ],
      onFilter: (value: any, record: Strategy) => record.status === value,
    },
    {
      title: '代数',
      dataIndex: 'generation',
      key: 'generation',
      width: 80,
      sorter: (a: Strategy, b: Strategy) => a.generation - b.generation,
    },
    {
      title: '总收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      render: (ret: string | null) => {
        const value = parseFloat(ret || '0') * 100;
        return (
          <span style={{ color: value >= 0 ? '#3f8600' : '#cf1322', fontWeight: 'bold' }}>
            {value >= 0 ? '+' : ''}{value.toFixed(2)}%
          </span>
        );
      },
      width: 120,
      sorter: (a: Strategy, b: Strategy) => parseFloat(a.total_return || '0') - parseFloat(b.total_return || '0'),
    },
    {
      title: '胜率',
      dataIndex: 'win_rate',
      key: 'win_rate',
      render: (rate: string | null) => {
        const value = parseFloat(rate || '0');
        return (
          <Progress
            percent={value}
            size="small"
            status={value > 60 ? 'success' : value > 40 ? 'normal' : 'exception'}
            format={(percent) => `${percent?.toFixed(1)}%`}
          />
        );
      },
      width: 150,
      sorter: (a: Strategy, b: Strategy) => parseFloat(a.win_rate || '0') - parseFloat(b.win_rate || '0'),
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      render: (ratio: string | null) => parseFloat(ratio || '0').toFixed(2),
      width: 100,
      sorter: (a: Strategy, b: Strategy) => parseFloat(a.sharpe_ratio || '0') - parseFloat(b.sharpe_ratio || '0'),
    },
    {
      title: '最大回撤',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      render: (dd: string | null) => {
        const value = parseFloat(dd || '0') * 100;
        return <span style={{ color: '#ff4d4f' }}>{value.toFixed(2)}%</span>;
      },
      width: 100,
    },
    {
      title: '使用次数',
      dataIndex: 'usage_count',
      key: 'usage_count',
      width: 100,
      sorter: (a: Strategy, b: Strategy) => a.usage_count - b.usage_count,
    },
    {
      title: '成功/失败',
      key: 'success_fail',
      render: (_: any, record: Strategy) => (
        <div>
          <span style={{ color: '#52c41a' }}>{record.success_count}</span>
          {' / '}
          <span style={{ color: '#ff4d4f' }}>{record.fail_count}</span>
        </div>
      ),
      width: 100,
    },
    {
      title: '评分',
      dataIndex: 'score',
      key: 'score',
      render: (score: string | null) => {
        const value = parseFloat(score || '0') * 100;
        return (
          <div>
            <Progress
              percent={value}
              size="small"
              strokeColor={value > 70 ? '#52c41a' : value > 50 ? '#1890ff' : '#faad14'}
              showInfo={false}
            />
            <span style={{ fontSize: 12, color: '#999' }}>{value.toFixed(0)}</span>
          </div>
        );
      },
      width: 120,
      sorter: (a: Strategy, b: Strategy) => parseFloat(a.score || '0') - parseFloat(b.score || '0'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Strategy) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => showDetail(record)}>
          详情
        </Button>
      ),
      fixed: 'right' as const,
      width: 100,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <h2><ThunderboltOutlined /> 策略管理</h2>
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
            options={[
              { label: '全部状态', value: 'all' },
              { label: '活跃', value: 'active' },
              { label: '测试中', value: 'testing' },
              { label: '已暂停', value: 'paused' },
              { label: '已退役', value: 'retired' },
            ]}
          />
        </Space>
        <Button icon={<SyncOutlined />} onClick={loadStrategies} loading={loading}>
          刷新
        </Button>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="策略总数"
              value={stats.total}
              suffix="个"
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃策略"
              value={stats.active}
              suffix="个"
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均收益率"
              value={stats.avgReturn * 100}
              precision={2}
              suffix="%"
              prefix={<RiseOutlined />}
              valueStyle={{ color: stats.avgReturn >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="平均胜率"
              value={stats.avgWinRate}
              precision={2}
              suffix="%"
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 策略表现对比 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={16}>
          <Card title="策略表现对比 (TOP 8)">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={strategyCompareData}>
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
        <Col xs={24} lg={8}>
          <Card title="最佳策略" extra={<Tag color="gold">⭐ TOP 1</Tag>}>
            {stats.topStrategy ? (
              <div>
                <h3 style={{ marginBottom: 16 }}>{stats.topStrategy.name}</h3>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <span style={{ color: '#999' }}>收益率：</span>
                    <span style={{ color: '#3f8600', fontWeight: 'bold', fontSize: 18 }}>
                      +{(parseFloat(stats.topStrategy.total_return || '0') * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#999' }}>胜率：</span>
                    <span style={{ fontWeight: 'bold', fontSize: 18 }}>
                      {parseFloat(stats.topStrategy.win_rate || '0').toFixed(2)}%
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#999' }}>夏普比率：</span>
                    <span style={{ fontWeight: 'bold' }}>
                      {parseFloat(stats.topStrategy.sharpe_ratio || '0').toFixed(2)}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#999' }}>使用次数：</span>
                    <span>{stats.topStrategy.usage_count}</span>
                  </div>
                  <Button type="primary" block onClick={() => showDetail(stats.topStrategy)} style={{ marginTop: 16 }}>
                    查看详情
                  </Button>
                </Space>
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#999' }}>暂无策略</div>
            )}
          </Card>
        </Col>
      </Row>

      {/* 策略列表 */}
      <Card title={`策略列表 (${strategies.length}个)`} style={{ marginTop: 16 }}>
        <Table
          dataSource={strategies}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 个策略`,
          }}
          scroll={{ x: 1600 }}
        />
      </Card>

      {/* 详情模态框 */}
      <Modal
        title={`策略详情 - ${selectedStrategy?.name}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={900}
      >
        {selectedStrategy && (
          <div>
            <Descriptions bordered column={2} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="策略ID">{selectedStrategy.id}</Descriptions.Item>
              <Descriptions.Item label="策略类型">{selectedStrategy.strategy_type}</Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={statusConfig[selectedStrategy.status]?.color}>
                  {statusConfig[selectedStrategy.status]?.text}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="代数">{selectedStrategy.generation}</Descriptions.Item>
              <Descriptions.Item label="总收益率">
                <span style={{ color: parseFloat(selectedStrategy.total_return || '0') >= 0 ? '#3f8600' : '#cf1322' }}>
                  {(parseFloat(selectedStrategy.total_return || '0') * 100).toFixed(2)}%
                </span>
              </Descriptions.Item>
              <Descriptions.Item label="胜率">{parseFloat(selectedStrategy.win_rate || '0').toFixed(2)}%</Descriptions.Item>
              <Descriptions.Item label="盈亏比">{parseFloat(selectedStrategy.profit_loss_ratio || '0').toFixed(2)}</Descriptions.Item>
              <Descriptions.Item label="夏普比率">{parseFloat(selectedStrategy.sharpe_ratio || '0').toFixed(2)}</Descriptions.Item>
              <Descriptions.Item label="最大回撤">
                {(parseFloat(selectedStrategy.max_drawdown || '0') * 100).toFixed(2)}%
              </Descriptions.Item>
              <Descriptions.Item label="使用次数">{selectedStrategy.usage_count}</Descriptions.Item>
              <Descriptions.Item label="成功次数">{selectedStrategy.success_count}</Descriptions.Item>
              <Descriptions.Item label="失败次数">{selectedStrategy.fail_count}</Descriptions.Item>
              <Descriptions.Item label="评分">
                {(parseFloat(selectedStrategy.score || '0') * 100).toFixed(0)}分
              </Descriptions.Item>
              <Descriptions.Item label="创建时间" span={2}>
                {dayjs(selectedStrategy.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {selectedStrategy.description || '无'}
              </Descriptions.Item>
            </Descriptions>

            {/* 策略性能雷达图 */}
            <Card title="策略性能分析" size="small">
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={getRadarData(selectedStrategy)}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar name="性能指标" dataKey="value" stroke="#1890ff" fill="#1890ff" fillOpacity={0.6} />
                  <Tooltip />
                </RadarChart>
              </ResponsiveContainer>
            </Card>

            {/* 策略基因 */}
            <Card title="策略基因" size="small" style={{ marginTop: 16 }}>
              <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto', maxHeight: 200 }}>
                {JSON.stringify(selectedStrategy.gene_code, null, 2)}
              </pre>
            </Card>

            {/* 策略参数 */}
            <Card title="策略参数" size="small" style={{ marginTop: 16 }}>
              <pre style={{ background: '#f5f5f5', padding: 16, borderRadius: 4, overflow: 'auto', maxHeight: 200 }}>
                {JSON.stringify(selectedStrategy.parameters, null, 2)}
              </pre>
            </Card>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Strategies;
