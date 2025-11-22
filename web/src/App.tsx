import { Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Portfolio from './pages/Portfolio';
import Strategies from './pages/Strategies';
import Trades from './pages/Trades';
import Positions from './pages/Positions';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import Login from './pages/Login';
import useStore from './store/useStore';
import './App.css';

function App() {
  const { token } = useStore();

  // 未登录跳转登录页
  if (!token) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/strategies" element={<Strategies />} />
        <Route path="/trades" element={<Trades />} />
        <Route path="/positions" element={<Positions />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </MainLayout>
  );
}

export default App;
