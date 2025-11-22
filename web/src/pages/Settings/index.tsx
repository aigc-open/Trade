import { useState } from 'react';
import { Card, Form, Input, Button, Switch, Select, InputNumber, Space, message, Tabs, Descriptions, Avatar } from 'antd';
import {
  SettingOutlined,
  UserOutlined,
  LockOutlined,
  BellOutlined,
  SafetyOutlined,
  ApiOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import useStore from '@/store/useStore';
import { apiService } from '@/services/api';

const Settings = () => {
  const { user, setUser } = useStore();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();

  // 保存个人信息
  const handleSaveProfile = async (values: any) => {
    setLoading(true);
    try {
      const response: any = await apiService.updateUserProfile(values);
      setUser(response);
      message.success('个人信息更新成功！');
    } catch (error: any) {
      message.error(error.response?.data?.error || '更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 修改密码
  const handleChangePassword = async (values: any) => {
    setLoading(true);
    try {
      await apiService.changePassword(values);
      message.success('密码修改成功！');
      passwordForm.resetFields();
    } catch (error: any) {
      message.error(error.response?.data?.error || '密码修改失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 保存系统配置
  const handleSaveSystemConfig = async (values: any) => {
    setLoading(true);
    try {
      // TODO: 调用API更新系统配置
      await new Promise(resolve => setTimeout(resolve, 1000));
      message.success('系统配置更新成功！');
    } catch (error) {
      message.error('更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 保存风控配置
  const handleSaveRiskConfig = async (values: any) => {
    setLoading(true);
    try {
      // TODO: 调用API更新风控配置
      await new Promise(resolve => setTimeout(resolve, 1000));
      message.success('风控配置更新成功！');
    } catch (error) {
      message.error('更新失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const tabItems = [
    {
      key: 'profile',
      label: <span><UserOutlined />个人资料</span>,
      children: (
        <Card>
          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <Avatar size={80} icon={<UserOutlined />} />
            <h3 style={{ marginTop: 16 }}>{user?.username || 'Admin'}</h3>
            <p style={{ color: '#999' }}>{user?.email || 'admin@example.com'}</p>
          </div>

          <Descriptions bordered column={1} style={{ marginBottom: 24 }}>
            <Descriptions.Item label="用户名">{user?.username || 'admin'}</Descriptions.Item>
            <Descriptions.Item label="邮箱">{user?.email || '-'}</Descriptions.Item>
            <Descriptions.Item label="真实姓名">{user?.real_name || '-'}</Descriptions.Item>
            <Descriptions.Item label="角色">{user?.role || '管理员'}</Descriptions.Item>
            <Descriptions.Item label="账号状态">
              <span style={{ color: user?.is_active ? '#52c41a' : '#ff4d4f' }}>
                {user?.is_active ? '激活' : '未激活'}
              </span>
            </Descriptions.Item>
            <Descriptions.Item label="注册时间">
              {user?.date_joined ? new Date(user.date_joined).toLocaleString('zh-CN') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="最后登录">
              {user?.last_login ? new Date(user.last_login).toLocaleString('zh-CN') : '-'}
            </Descriptions.Item>
          </Descriptions>

          <Form
            form={form}
            layout="vertical"
            initialValues={{
              username: user?.username,
              email: user?.email,
              real_name: user?.real_name,
            }}
            onFinish={handleSaveProfile}
          >
            <Form.Item label="用户名" name="username" rules={[{ required: true }]}>
              <Input disabled prefix={<UserOutlined />} />
            </Form.Item>
            <Form.Item label="邮箱" name="email" rules={[{ type: 'email' }]}>
              <Input prefix="@" placeholder="your@email.com" />
            </Form.Item>
            <Form.Item label="真实姓名" name="real_name">
              <Input placeholder="请输入真实姓名" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存修改
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'security',
      label: <span><LockOutlined />安全设置</span>,
      children: (
        <Card title="修改密码">
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handleChangePassword}
          >
            <Form.Item
              label="当前密码"
              name="old_password"
              rules={[{ required: true, message: '请输入当前密码' }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入当前密码" />
            </Form.Item>
            <Form.Item
              label="新密码"
              name="new_password"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 6, message: '密码至少6位' },
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请输入新密码" />
            </Form.Item>
            <Form.Item
              label="确认新密码"
              name="confirm_password"
              dependencies={['new_password']}
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="请再次输入新密码" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                修改密码
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'notification',
      label: <span><BellOutlined />通知设置</span>,
      children: (
        <Card>
          <Form
            layout="vertical"
            initialValues={{
              email_notification: true,
              trade_notification: true,
              risk_alert: true,
              daily_report: true,
              weekly_report: false,
            }}
            onFinish={handleSaveSystemConfig}
          >
            <Form.Item label="邮件通知" name="email_notification" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="交易提醒" name="trade_notification" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="风险警报" name="risk_alert" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="每日报告" name="daily_report" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="每周报告" name="weekly_report" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存设置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'risk',
      label: <span><SafetyOutlined />风控设置</span>,
      children: (
        <Card title="风险控制参数">
          <Form
            layout="vertical"
            initialValues={{
              max_position_ratio: 20,
              max_single_loss: 5,
              max_daily_loss: 10,
              max_drawdown: 15,
              position_size_method: 'kelly',
              stop_loss_type: 'trailing',
            }}
            onFinish={handleSaveRiskConfig}
          >
            <Form.Item
              label="单个持仓最大占比 (%)"
              name="max_position_ratio"
              tooltip="单个股票持仓不能超过总资产的百分比"
            >
              <InputNumber min={1} max={100} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item
              label="单笔最大亏损 (%)"
              name="max_single_loss"
              tooltip="单笔交易允许的最大亏损百分比"
            >
              <InputNumber min={1} max={20} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item
              label="单日最大亏损 (%)"
              name="max_daily_loss"
              tooltip="单日累计亏损达到此阈值时停止交易"
            >
              <InputNumber min={1} max={30} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item
              label="最大回撤限制 (%)"
              name="max_drawdown"
              tooltip="账户回撤超过此值时触发风控"
            >
              <InputNumber min={1} max={50} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="仓位管理方法" name="position_size_method">
              <Select
                options={[
                  { label: 'Kelly公式', value: 'kelly' },
                  { label: '固定比例', value: 'fixed_ratio' },
                  { label: '等权重', value: 'equal_weight' },
                  { label: 'ATR法', value: 'atr' },
                ]}
              />
            </Form.Item>
            <Form.Item label="止损类型" name="stop_loss_type">
              <Select
                options={[
                  { label: '移动止损', value: 'trailing' },
                  { label: '固定止损', value: 'fixed' },
                  { label: 'ATR止损', value: 'atr' },
                  { label: '百分比止损', value: 'percentage' },
                ]}
              />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存风控配置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'system',
      label: <span><SettingOutlined />系统配置</span>,
      children: (
        <Card>
          <Form
            layout="vertical"
            initialValues={{
              account_type: 'simulation',
              data_refresh_interval: 30,
              chart_theme: 'light',
              auto_refresh: true,
              show_notifications: true,
            }}
            onFinish={handleSaveSystemConfig}
          >
            <Form.Item label="默认账户类型" name="account_type">
              <Select
                options={[
                  { label: '模拟账户', value: 'simulation' },
                  { label: '实盘账户', value: 'real' },
                ]}
              />
            </Form.Item>
            <Form.Item label="数据刷新间隔(秒)" name="data_refresh_interval">
              <InputNumber min={5} max={300} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label="图表主题" name="chart_theme">
              <Select
                options={[
                  { label: '亮色', value: 'light' },
                  { label: '暗色', value: 'dark' },
                ]}
              />
            </Form.Item>
            <Form.Item label="自动刷新" name="auto_refresh" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item label="显示通知" name="show_notifications" valuePropName="checked">
              <Switch />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存系统配置
              </Button>
            </Form.Item>
          </Form>
        </Card>
      ),
    },
    {
      key: 'api',
      label: <span><ApiOutlined />API配置</span>,
      children: (
        <Card title="API密钥配置">
          <Form
            layout="vertical"
            initialValues={{
              openai_api_key: '**********************',
              tushare_token: '**********************',
              alphavantage_key: '**********************',
            }}
            onFinish={handleSaveSystemConfig}
          >
            <Form.Item
              label="OpenAI API Key"
              name="openai_api_key"
              tooltip="用于AI决策分析"
            >
              <Input.Password placeholder="sk-..." />
            </Form.Item>
            <Form.Item
              label="Tushare Token"
              name="tushare_token"
              tooltip="用于获取A股数据"
            >
              <Input.Password placeholder="请输入Tushare Token" />
            </Form.Item>
            <Form.Item
              label="Alpha Vantage Key"
              name="alphavantage_key"
              tooltip="用于获取美股数据"
            >
              <Input.Password placeholder="请输入Alpha Vantage Key" />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<SaveOutlined />}>
                保存API配置
              </Button>
            </Form.Item>
          </Form>

          <Card title="API文档" size="small" style={{ marginTop: 16 }}>
            <Space direction="vertical">
              <a href="http://localhost:8000/api/schema/swagger-ui/" target="_blank" rel="noopener noreferrer">
                📖 Swagger UI文档
              </a>
              <a href="http://localhost:8000/api/schema/redoc/" target="_blank" rel="noopener noreferrer">
                📖 ReDoc文档
              </a>
              <a href="http://localhost:8000/admin" target="_blank" rel="noopener noreferrer">
                🔧 Django Admin后台
              </a>
            </Space>
          </Card>
        </Card>
      ),
    },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 16 }}><SettingOutlined /> 系统设置</h2>
      <Tabs items={tabItems} />
    </div>
  );
};

export default Settings;
