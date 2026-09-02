import { useState, useEffect } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import InvestigatePage from './pages/InvestigatePage';
import GraphPage from './pages/GraphPage';
import EvidencePage from './pages/EvidencePage';
import TimelinePage from './pages/TimelinePage';
import ReportsPage from './pages/ReportsPage';
import { getDatasetStats, healthCheck } from './services/api';

function App() {
  const [stats, setStats] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const location = useLocation();

  // Load stats on mount
  useEffect(() => {
    fetchStats();
    checkHealth();
    // Poll health check every 10s
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const data = await getDatasetStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const checkHealth = async () => {
    try {
      const data = await healthCheck();
      setSystemStatus(data);
    } catch (err) {
      setSystemStatus({ status: 'offline' });
    }
  };

  return (
    <div className="app-layout">
      <Sidebar systemStatus={systemStatus} />
      <div className="main-content flex flex-col">
        <Header systemStatus={systemStatus} />
        <main className="flex-1 overflow-auto bg-navy-900">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<DashboardPage stats={stats} setStats={setStats} onDataLoaded={fetchStats} />} />
            <Route path="/investigate" element={<InvestigatePage stats={stats} />} />
            <Route path="/graph" element={<GraphPage stats={stats} />} />
            <Route path="/evidence" element={<EvidencePage stats={stats} />} />
            <Route path="/timeline" element={<TimelinePage />} />
            <Route path="/reports" element={<ReportsPage stats={stats} />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
