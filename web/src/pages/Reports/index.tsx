import { useEffect, useState } from 'react';
import { Card, List, Tag, Space, Button, Select, Descriptions, Row, Col, Statistic, Timeline, Empty } from 'antd';
import {
  FileTextOutlined,
  SyncOutlined,
  TrophyOutlined,
  CloseCircleOutlined,
  BulbOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { apiService } from '@/services/api';
import type { ReviewReport } from '@/types';
import dayjs from 'dayjs';

const Reports = () => {
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<ReviewReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReviewReport | null>(null);
  const [reportType, setReportType] = useState<string>('all');

  // 加载报告数据
  const loadReports = async () => {
    setLoading(true);
    try {
      const params: any = { ordering: '-review_period_end' };
      if (reportType !== 'all') {
        params.review_type = reportType;
      }
      const response: any = await apiService.getReviewReports(params);
      const reportList = response.results || response || [];
      setReports(reportList);
      if (reportList.length > 0 && !selectedReport) {
        setSelectedReport(reportList[0]);
      }
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, [reportType]);

  // 报告类型配置
  const reportTypeConfig: Record<string, { text: string; color: string }> = {
    daily: { text: '日报', color: 'blue' },
    weekly: { text: '周报', color: 'green' },
    monthly: { text: '月报', color: 'orange' },
  };

  // 生成趋势数据
  const generateTrendData = () => {
    return reports.slice(0, 10).reverse().map(r => ({
      date: dayjs(r.report_date).format('MM-DD'),
      return: parseFloat(r.total_return || '0') * 100,
      winRate: parseFloat(r.win_rate || '0'),
      profit: parseFloat(r.report_data?.total_pnl || '0'),
    }));
  };

  const trendData = generateTrendData();

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <h2><FileTextOutlined /> 复盘报告</h2>
          <Select
            value={reportType}
            onChange={setReportType}
            style={{ width: 120 }}
            options={[
              { label: '全部报告', value: 'all' },
              { label: '日报', value: 'daily' },
              { label: '周报', value: 'weekly' },
              { label: '月报', value: 'monthly' },
            ]}
          />
        </Space>
        <Button icon={<SyncOutlined />} onClick={loadReports} loading={loading}>
          刷新
        </Button>
      </div>

      <Row gutter={[16, 16]}>
        {/* 左侧：报告列表 */}
        <Col xs={24} lg={8}>
          <Card title="报告列表" bodyStyle={{ padding: 0, maxHeight: 800, overflow: 'auto' }}>
            {reports.length > 0 ? (
              <List
                dataSource={reports}
                renderItem={(report) => (
                  <List.Item
                    key={report.id}
                    style={{
                      cursor: 'pointer',
                      background: selectedReport?.id === report.id ? '#e6f7ff' : 'white',
                      padding: '12px 16px',
                    }}
                    onClick={() => setSelectedReport(report)}
                  >
                    <List.Item.Meta
                      title={
                        <Space>
                          <Tag color={reportTypeConfig[report.report_type]?.color}>
                            {reportTypeConfig[report.report_type]?.text}
                          </Tag>
                          <span>{dayjs(report.report_date).format('YYYY-MM-DD')}</span>
                        </Space>
                      }
                      description={
                        <div>
                          <div>
                            收益率: <span style={{ color: parseFloat(report.total_return || '0') >= 0 ? '#3f8600' : '#cf1322' }}>
                              {(parseFloat(report.total_return || '0') * 100).toFixed(2)}%
                            </span>
                          </div>
                          <div>胜率: {parseFloat(report.win_rate || '0').toFixed(2)}%</div>
                          <div>交易: {report.trade_count}笔</div>
                        </div>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无报告" style={{ padding: 40 }} />
            )}
          </Card>
        </Col>

        {/* 右侧：报告详情 */}
        <Col xs={24} lg={16}>
          {selectedReport ? (
            <div>
              {/* 基本信息 */}
              <Card title="报告概览">
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="报告类型">
                    <Tag color={reportTypeConfig[selectedReport.report_type]?.color}>
                      {reportTypeConfig[selectedReport.report_type]?.text}
                    </Tag>
                  </Descriptions.Item>
                  <Descriptions.Item label="报告日期">
                    {dayjs(selectedReport.report_date).format('YYYY-MM-DD')}
                  </Descriptions.Item>
                  <Descriptions.Item label="交易次数">{selectedReport.trade_count}笔</Descriptions.Item>
                  <Descriptions.Item label="盈利/亏损">
                    <span style={{ color: '#52c41a' }}>{selectedReport.win_count}</span>
                    {' / '}
                    <span style={{ color: '#ff4d4f' }}>{selectedReport.lose_count}</span>
                  </Descriptions.Item>
                  <Descriptions.Item label="胜率">{parseFloat(selectedReport.win_rate || '0').toFixed(2)}%</Descriptions.Item>
                  <Descriptions.Item label="夏普比率">{parseFloat(selectedReport.sharpe_ratio || '0').toFixed(2)}</Descriptions.Item>
                  <Descriptions.Item label="总盈亏">
                    <span style={{ color: parseFloat(selectedReport.report_data?.total_pnl || '0') >= 0 ? '#3f8600' : '#cf1322' }}>
                      ¥{parseFloat(selectedReport.report_data?.total_pnl || '0').toFixed(2)}
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="收益率">
                    <span style={{ color: parseFloat(selectedReport.total_return || '0') >= 0 ? '#3f8600' : '#cf1322' }}>
                      {(parseFloat(selectedReport.total_return || '0') * 100).toFixed(2)}%
                    </span>
                  </Descriptions.Item>
                  <Descriptions.Item label="最大回撤">
                    {parseFloat(selectedReport.max_drawdown || '0').toFixed(2)}%
                  </Descriptions.Item>
                  <Descriptions.Item label="报告标题" span={2}>
                    {selectedReport.title}
                  </Descriptions.Item>
                </Descriptions>
              </Card>

              {/* 成功案例 */}
              <Card
                title={<Space><TrophyOutlined style={{ color: '#52c41a' }} />成功案例</Space>}
                style={{ marginTop: 16 }}
              >
                <Timeline
                  items={selectedReport.success_cases.map((c: any, index: number) => ({
                    color: 'green',
                    children: (
                      <div key={index}>
                        <div style={{ fontWeight: 'bold' }}>{c.symbol || `案例 ${index + 1}`}</div>
                        <div style={{ color: '#999', fontSize: 12 }}>{c.description || c.reason || '成功交易'}</div>
                        {c.profit && <div style={{ color: '#52c41a' }}>盈利: ¥{c.profit}</div>}
                      </div>
                    ),
                  }))}
                />
              </Card>

              {/* 失败案例 */}
              <Card
                title={<Space><CloseCircleOutlined style={{ color: '#ff4d4f' }} />失败案例</Space>}
                style={{ marginTop: 16 }}
              >
                <Timeline
                  items={selectedReport.failure_cases.map((c: any, index: number) => ({
                    color: 'red',
                    children: (
                      <div key={index}>
                        <div style={{ fontWeight: 'bold' }}>{c.symbol || `案例 ${index + 1}`}</div>
                        <div style={{ color: '#999', fontSize: 12 }}>{c.description || c.reason || '失败交易'}</div>
                        {c.loss && <div style={{ color: '#ff4d4f' }}>亏损: ¥{c.loss}</div>}
                      </div>
                    ),
                  }))}
                />
              </Card>

              {/* 关键洞察 */}
              <Card title={<Space><BulbOutlined style={{ color: '#faad14' }} />关键洞察</Space>} style={{ marginTop: 16 }}>
                <List
                  dataSource={selectedReport.key_insights}
                  renderItem={(insight: string, index: number) => (
                    <List.Item key={index}>
                      <List.Item.Meta
                        avatar={<span style={{ fontSize: 20 }}>💡</span>}
                        description={insight}
                      />
                    </List.Item>
                  )}
                />
              </Card>

              {/* 改进建议 */}
              <Card title="改进建议" style={{ marginTop: 16 }}>
                <List
                  dataSource={selectedReport.improvement_suggestions}
                  renderItem={(suggestion: string, index: number) => (
                    <List.Item key={index}>
                      <List.Item.Meta
                        avatar={<span style={{ fontSize: 20 }}>📌</span>}
                        description={suggestion}
                      />
                    </List.Item>
                  )}
                />
              </Card>

              {/* 认知偏差 */}
              {selectedReport.cognitive_bias_analysis && selectedReport.cognitive_bias_analysis.biases && selectedReport.cognitive_bias_analysis.biases.length > 0 && (
                <Card title="认知偏差分析" style={{ marginTop: 16 }}>
                  <Space wrap>
                    {selectedReport.cognitive_bias_analysis.biases.map((bias: string, index: number) => (
                      <Tag key={index} color="warning">{bias}</Tag>
                    ))}
                  </Space>
                  {selectedReport.cognitive_bias_analysis.emotional_state && (
                    <div style={{ marginTop: 12 }}>
                      <span style={{ color: '#999' }}>情绪状态: </span>
                      <strong>{selectedReport.cognitive_bias_analysis.emotional_state}</strong>
                    </div>
                  )}
                </Card>
              )}

              {/* 经验教训 */}
              {selectedReport.lessons_learned && selectedReport.lessons_learned.length > 0 && (
                <Card title="经验教训" style={{ marginTop: 16 }}>
                  <Timeline
                    items={selectedReport.lessons_learned.map((lesson: any, index: number) => ({
                      children: (
                        <div key={index}>
                          <div style={{ fontWeight: 'bold' }}>{lesson.title || lesson.topic}</div>
                          <div style={{ color: '#666' }}>{lesson.description || lesson.lesson}</div>
                        </div>
                      ),
                    }))}
                  />
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <Empty description="请选择一个报告查看详情" />
            </Card>
          )}
        </Col>
      </Row>

      {/* 趋势分析 */}
      {reports.length > 0 && (
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="收益率趋势">
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                  <Line type="monotone" dataKey="return" stroke="#1890ff" name="收益率(%)" />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="胜率趋势">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
                  <Bar dataKey="winRate" fill="#52c41a" name="胜率(%)" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default Reports;
