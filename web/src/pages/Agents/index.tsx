import { useEffect, useState } from 'react';
import { Card, Row, Col, Descriptions, Tag, Table, Tabs, Progress, Space, Button, Statistic, Badge, message } from 'antd';
import {
  RobotOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '@/services/api';
import type { AgentStatus } from '@/types';
import dayjs from 'dayjs';
import './index.css';

const Agents = () => {
  const [loading, setLoading] = useState(true);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<AgentStatus | null>(null);

  // 加载智能体数据
  const loadAgents = async () => {
    setLoading(true);
    try {
      const response: any = await apiService.getAgentStatus();
      const agentList = response.results || response || [];
      setAgents(agentList);
      if (agentList.length > 0 && !selectedAgent) {
        setSelectedAgent(agentList[0]);
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      message.error('加载智能体数据失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
    // 每10秒刷新
    const interval = setInterval(loadAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  // 智能体类型映射
  const agentTypeNames: Record<string, { name: string; icon: string; color: string }> = {
    perception: { name: '感知层', icon: '👁️', color: '#1890ff' },
    memory: { name: '记忆层', icon: '🧠', color: '#722ed1' },
    planning: { name: '规划层', icon: '📋', color: '#13c2c2' },
    decision: { name: '决策层', icon: '💭', color: '#52c41a' },
    execution: { name: '执行层', icon: '⚡', color: '#faad14' },
    reflection: { name: '反思层', icon: '🔄', color: '#f5222d' },
  };

  // 状态映射
  const statusConfig: Record<string, { text: string; color: string; icon: any }> = {
    running: { text: '运行中', color: 'success', icon: <CheckCircleOutlined /> },
    stopped: { text: '已停止', color: 'default', icon: <CloseCircleOutlined /> },
    error: { text: '错误', color: 'error', icon: <CloseCircleOutlined /> },
    paused: { text: '已暂停', color: 'warning', icon: <PauseCircleOutlined /> },
  };

  // 模拟性能历史数据
  const generatePerformanceData = (agent: AgentStatus) => {
    const data = [];
    const now = Date.now();
    for (let i = 11; i >= 0; i--) {
      data.push({
        time: dayjs(now - i * 5 * 60 * 1000).format('HH:mm'),
        success_rate: Math.max(0, Math.min(100, (agent.metrics?.success_rate || 0) + Math.random() * 10 - 5)),
        response_time: Math.max(0, (agent.metrics?.avg_response_time || 100) + Math.random() * 50 - 25),
      });
    }
    return data;
  };

  // 智能体列表列
  const columns = [
    {
      title: '智能体',
      dataIndex: 'agent_type',
      key: 'agent_type',
      render: (type: string) => (
        <Space>
          <span style={{ fontSize: 20 }}>{agentTypeNames[type]?.icon}</span>
          <span style={{ fontWeight: 'bold' }}>{agentTypeNames[type]?.name || type}</span>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const config = statusConfig[status] || statusConfig.stopped;
        return (
          <Badge status={config.color as any} text={config.text} />
        );
      },
    },
    {
      title: '当前任务',
      dataIndex: 'current_task',
      key: 'current_task',
      render: (task: string | null) => task || '-',
    },
    {
      title: '成功率',
      dataIndex: 'metrics',
      key: 'success_rate',
      render: (metrics: any) => (
        <Progress
          percent={Math.round(metrics?.success_rate || 0)}
          size="small"
          status={metrics?.success_rate > 80 ? 'success' : metrics?.success_rate > 60 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '最后心跳',
      dataIndex: 'last_heartbeat',
      key: 'last_heartbeat',
      render: (time: string | null) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: AgentStatus) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => setSelectedAgent(record)}
          >
            详情
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="agents-page">
      <div style={{ marginBottom: 16 }}>
        <Space>
          <h2><RobotOutlined /> 智能体管理</h2>
          <Button icon={<SyncOutlined />} onClick={loadAgents} loading={loading}>
            刷新
          </Button>
        </Space>
      </div>

      {/* 智能体概览卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        {agents.map((agent) => {
          const info = agentTypeNames[agent.agent_type];
          const statusConf = statusConfig[agent.status];
          return (
            <Col key={agent.id} xs={24} sm={12} lg={8} xl={4}>
              <Card
                hoverable
                className={selectedAgent?.id === agent.id ? 'agent-card-selected' : ''}
                onClick={() => setSelectedAgent(agent)}
                style={{ borderLeft: `4px solid ${info?.color}` }}
              >
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>
                    {info?.icon}
                  </div>
                  <div style={{ fontWeight: 'bold', marginBottom: 8 }}>
                    {info?.name}
                  </div>
                  <Tag color={statusConf?.color}>
                    {statusConf?.icon} {statusConf?.text}
                  </Tag>
                  {agent.metrics?.success_rate !== undefined && (
                    <div style={{ marginTop: 8, fontSize: 12, color: '#999' }}>
                      成功率: {agent.metrics.success_rate.toFixed(1)}%
                    </div>
                  )}
                </div>
              </Card>
            </Col>
          );
        })}
      </Row>

      {/* 智能体详情 */}
      {selectedAgent && (
        <Card title={`${agentTypeNames[selectedAgent.agent_type]?.name} - 详细信息`}>
          <Tabs
            items={[
              {
                key: 'overview',
                label: '概览',
                children: (
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      <Descriptions bordered column={2}>
                        <Descriptions.Item label="智能体ID">{selectedAgent.id}</Descriptions.Item>
                        <Descriptions.Item label="类型">
                          {agentTypeNames[selectedAgent.agent_type]?.name}
                        </Descriptions.Item>
                        <Descriptions.Item label="状态">
                          <Tag color={statusConfig[selectedAgent.status]?.color}>
                            {statusConfig[selectedAgent.status]?.text}
                          </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="当前任务">
                          {selectedAgent.current_task || '无'}
                        </Descriptions.Item>
                        <Descriptions.Item label="最后操作">
                          {selectedAgent.last_action || '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="最后心跳">
                          {selectedAgent.last_heartbeat
                            ? dayjs(selectedAgent.last_heartbeat).format('YYYY-MM-DD HH:mm:ss')
                            : '-'}
                        </Descriptions.Item>
                        <Descriptions.Item label="错误次数">
                          <Badge count={selectedAgent.error_count} showZero />
                        </Descriptions.Item>
                        <Descriptions.Item label="最后错误">
                          {selectedAgent.last_error || '无'}
                        </Descriptions.Item>
                      </Descriptions>
                    </Col>

                    {/* 性能指标 */}
                    <Col span={24}>
                      <Card title="性能指标" size="small">
                        <Row gutter={16}>
                          <Col span={6}>
                            <Statistic
                              title="任务完成数"
                              value={selectedAgent.metrics?.tasks_completed || 0}
                              suffix="个"
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="成功率"
                              value={selectedAgent.metrics?.success_rate || 0}
                              precision={2}
                              suffix="%"
                              valueStyle={{
                                color:
                                  (selectedAgent.metrics?.success_rate || 0) > 80
                                    ? '#3f8600'
                                    : '#cf1322',
                              }}
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="平均响应时间"
                              value={selectedAgent.metrics?.avg_response_time || 0}
                              suffix="ms"
                            />
                          </Col>
                          <Col span={6}>
                            <Statistic
                              title="运行时长"
                              value={selectedAgent.metrics?.uptime_hours || 0}
                              precision={1}
                              suffix="小时"
                            />
                          </Col>
                        </Row>
                      </Card>
                    </Col>
                  </Row>
                ),
              },
              {
                key: 'performance',
                label: '性能趋势',
                children: (
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      <Card title="成功率趋势" size="small">
                        <ResponsiveContainer width="100%" height={250}>
                          <AreaChart data={generatePerformanceData(selectedAgent)}>
                            <defs>
                              <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#52c41a" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#52c41a" stopOpacity={0} />
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis domain={[0, 100]} />
                            <Tooltip />
                            <Area
                              type="monotone"
                              dataKey="success_rate"
                              stroke="#52c41a"
                              fillOpacity={1}
                              fill="url(#colorSuccess)"
                              name="成功率 (%)"
                            />
                          </AreaChart>
                        </ResponsiveContainer>
                      </Card>
                    </Col>
                    <Col span={24}>
                      <Card title="响应时间趋势" size="small">
                        <ResponsiveContainer width="100%" height={250}>
                          <LineChart data={generatePerformanceData(selectedAgent)}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line
                              type="monotone"
                              dataKey="response_time"
                              stroke="#1890ff"
                              name="响应时间 (ms)"
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      </Card>
                    </Col>
                  </Row>
                ),
              },
              {
                key: 'logs',
                label: '运行日志',
                children: (
                  <div style={{ background: '#000', color: '#0f0', padding: 16, borderRadius: 4, fontFamily: 'monospace' }}>
                    <div>[{dayjs().format('YYYY-MM-DD HH:mm:ss')}] INFO: Agent {selectedAgent.agent_type} initialized</div>
                    <div>[{dayjs().subtract(1, 'minute').format('YYYY-MM-DD HH:mm:ss')}] INFO: Starting task execution...</div>
                    <div>[{dayjs().subtract(2, 'minute').format('YYYY-MM-DD HH:mm:ss')}] SUCCESS: Task completed successfully</div>
                    <div>[{dayjs().subtract(5, 'minute').format('YYYY-MM-DD HH:mm:ss')}] INFO: Metrics updated</div>
                    <div>[{dayjs().subtract(10, 'minute').format('YYYY-MM-DD HH:mm:ss')}] INFO: Heartbeat sent</div>
                    <div style={{ color: '#999', marginTop: 8 }}>日志功能开发中，将从后端实时获取...</div>
                  </div>
                ),
              },
            ]}
          />
        </Card>
      )}

      {/* 智能体列表 */}
      <Card title="智能体列表" style={{ marginTop: 16 }}>
        <Table
          dataSource={agents}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={false}
        />
      </Card>
    </div>
  );
};

export default Agents;
