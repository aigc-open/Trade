// 智能体状态
export interface AgentStatus {
  id: number;
  agent_type: 'perception' | 'memory' | 'planning' | 'decision' | 'execution' | 'reflection';
  status: 'running' | 'stopped' | 'error' | 'paused';
  current_task: string | null;
  last_action: string | null;
  last_heartbeat: string | null;
  metrics: {
    tasks_completed?: number;
    success_rate?: number;
    avg_response_time?: number;
    uptime_hours?: number;
  };
  error_count: number;
  last_error: string | null;
  created_at: string;
  updated_at: string;
}

// 投资组合
export interface Portfolio {
  id: number;
  account_name: string;
  account_type: 'real' | 'simulation';
  initial_capital: string;
  total_asset: string;
  cash: string;
  market_value: string;
  available_cash: string;
  frozen_cash: string;
  total_pnl: string;
  total_return: string;
  today_pnl: string;
  today_return: string;
  total_trades: number;
  win_trades: number;
  lose_trades: number;
  win_rate: string | null;
  max_drawdown: string;
  sharpe_ratio: string | null;
  volatility: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// 策略
export interface Strategy {
  id: number;
  name: string;
  strategy_type: string;
  status: 'active' | 'testing' | 'paused' | 'retired';
  gene_code: Record<string, any>;
  parameters: Record<string, any>;
  description: string;
  logic: string;
  generation: number;
  performance_metrics: Record<string, any>;
  win_rate: string | null;
  profit_loss_ratio: string | null;
  sharpe_ratio: string | null;
  max_drawdown: string | null;
  total_return: string | null;
  usage_count: number;
  success_count: number;
  fail_count: number;
  score: string | null;
  created_at: string;
  updated_at: string;
}

// 交易记录
export interface Trade {
  id: number;
  trade_id: string;
  symbol: string;
  action: 'BUY' | 'SELL';
  account_type: 'real' | 'simulation';
  account_name: string;
  order_price: string;
  order_quantity: number;
  filled_price: string | null;
  filled_quantity: number;
  status: 'pending' | 'submitted' | 'partial_filled' | 'filled' | 'cancelled' | 'failed';
  order_time: string;
  filled_time: string | null;
  commission: string;
  slippage: string;
  total_amount: string;
  strategy: number | null;
  decision: number | null;
  decision_process: Record<string, any>;
  reason: string;
  stop_loss: string | null;
  take_profit: string | null;
  execution_quality: Record<string, any>;
  pnl: string | null;
  pnl_pct: string | null;
  created_at: string;
  updated_at: string;
}

// 持仓
export interface Position {
  id: number;
  symbol: string;
  account_type: 'real' | 'simulation';
  account_name: string;
  quantity: number;
  available_quantity: number;
  frozen_quantity: number;
  avg_cost: string;
  total_cost: string;
  current_price: string | null;
  market_value: string | null;
  unrealized_pnl: string | null;
  unrealized_pnl_pct: string | null;
  realized_pnl: string;
  strategy: number | null;
  stop_loss: string | null;
  take_profit: string | null;
  opened_at: string;
  holding_days: number;
  is_closed: boolean;
  closed_at: string | null;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// 决策记录
export interface Decision {
  id: number;
  symbol: string;
  decision_type: string;
  final_decision: string;
  confidence_score: string;
  decision_time: string;
  target_position_pct: string | null;
  stop_loss: string | null;
  take_profit: string | null;
  holding_period: number | null;
  proposal: Record<string, any>;
  debate_summary: Record<string, any>;
  risk_assessment: Record<string, any>;
  is_executed: boolean;
  execution_time: string | null;
  execution_result: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

// 市场数据
export interface MarketData {
  id: number;
  symbol: string;
  market: string;
  timestamp: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number;
  amount: string | null;
  change_pct: string | null;
  turnover_rate: string | null;
  data_source: string;
  raw_data: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// 复盘报告
export interface ReviewReport {
  id: number;
  report_type: 'daily' | 'weekly' | 'monthly';
  report_date: string;
  title: string;
  summary: string;
  report_data: Record<string, any>;
  performance_overview: Record<string, any>;
  total_return: string | null;
  win_rate: string | null;
  sharpe_ratio: string | null;
  max_drawdown: string | null;
  trade_count: number;
  win_count: number;
  lose_count: number;
  best_trades: Array<Record<string, any>>;
  worst_trades: Array<Record<string, any>>;
  lessons_learned: Array<Record<string, any>>;
  success_cases: Array<Record<string, any>>;
  failure_cases: Array<Record<string, any>>;
  strategy_analysis: Record<string, any>;
  best_strategies: Array<Record<string, any>>;
  worst_strategies: Array<Record<string, any>>;
  market_insights: Record<string, any>;
  improvement_suggestions: string[];
  action_items: Array<Record<string, any>>;
  evolution_summary: Record<string, any>;
  cognitive_bias_analysis: Record<string, any>;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

// 用户
export interface User {
  id: number;
  username: string;
  email: string;
  real_name: string;
  role: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
}

// API响应
export interface ApiResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
  data?: T;
}

// 登录请求
export interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应
export interface LoginResponse {
  token: string;
  user: User;
}

