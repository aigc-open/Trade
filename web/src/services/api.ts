import axios, { AxiosInstance } from 'axios';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，清除token并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// API方法
export const apiService = {
  // 认证
  login: (username: string, password: string) =>
    api.post('/user/login/', { username, password }),
  
  logout: () => api.post('/user/logout/'),
  
  // 用户管理
  getUserProfile: () => api.get('/user/profile/'),
  updateUserProfile: (data: any) => api.patch('/user/update_profile/', data),
  changePassword: (data: any) => api.post('/user/change_password/', data),
  
  // 智能体状态
  getAgentStatus: (params?: any) => api.get('/agents/status/', { params }),
  
  // 投资组合
  getPortfolios: (params?: any) => api.get('/trades/portfolio/', { params }),
  getPortfolio: (id: number) => api.get(`/trades/portfolio/${id}/`),
  
  // 策略
  getStrategies: (params?: any) => api.get('/strategies/', { params }),
  getStrategy: (id: number) => api.get(`/strategies/${id}/`),
  
  // 交易
  getTrades: (params?: any) => api.get('/trades/trades/', { params }),
  getTrade: (id: number) => api.get(`/trades/trades/${id}/`),
  
  // 持仓
  getPositions: (params?: any) => api.get('/trades/positions/', { params }),
  getPosition: (id: number) => api.get(`/trades/positions/${id}/`),
  
  // 决策
  getDecisions: (params?: any) => api.get('/agents/decisions/', { params }),
  getDecision: (id: number) => api.get(`/agents/decisions/${id}/`),
  
  // 市场数据
  getMarketData: (params?: any) => api.get('/market-data/data/', { params }),
  
  // 复盘报告
  getReviewReports: (params?: any) => api.get('/reports/reviews/', { params }),
  getReviewReport: (id: number) => api.get(`/reports/reviews/${id}/`),
  
  // 系统文档
  getSystemDoc: () => api.get('/docs/system-guide/'),
};

