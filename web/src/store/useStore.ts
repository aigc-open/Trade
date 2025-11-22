import { create } from 'zustand';
import { User, AgentStatus, Portfolio } from '../types';

interface StoreState {
  // 用户相关
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  
  // 智能体状态
  agentStatus: AgentStatus[];
  setAgentStatus: (status: AgentStatus[]) => void;
  
  // 投资组合
  currentPortfolio: Portfolio | null;
  setCurrentPortfolio: (portfolio: Portfolio | null) => void;
  
  // 全局loading
  loading: boolean;
  setLoading: (loading: boolean) => void;
  
  // 侧边栏折叠状态
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

const useStore = create<StoreState>((set) => ({
  // 初始状态
  user: null,
  token: localStorage.getItem('token'),
  agentStatus: [],
  currentPortfolio: null,
  loading: false,
  collapsed: false,
  
  // Actions
  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
    set({ token });
  },
  setAgentStatus: (agentStatus) => set({ agentStatus }),
  setCurrentPortfolio: (currentPortfolio) => set({ currentPortfolio }),
  setLoading: (loading) => set({ loading }),
  setCollapsed: (collapsed) => set({ collapsed }),
}));

export default useStore;

