import { NavLink } from 'react-router-dom';

const navItems = [
  { path: '/', label: 'Overview', icon: '📊' },
  { path: '/investigate', label: 'Investigate', icon: '🔍' },
  { path: '/graph', label: 'Actor Graph', icon: '🕸️' },
  { path: '/evidence', label: 'Evidence', icon: '🔗' },
  { path: '/timeline', label: 'Timeline', icon: '📅' },
  { path: '/reports', label: 'Reports', icon: '📄' },
];

export default function Sidebar({ systemStatus }) {
  return (
    <div className="sidebar">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800">
        <div className="font-black text-xl tracking-wide" style={{
          background: 'linear-gradient(90deg, #38bdf8, #818cf8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          TRACENET
        </div>
        <div className="text-xs text-gray-500 mt-1">Threat Actor Intelligence</div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        <div className="px-4 mb-2 text-xs text-gray-600 uppercase tracking-wider font-semibold">
          Investigation
        </div>
        {navItems.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-semibold">System Status</div>
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
          <span className={`status-dot ${systemStatus?.data_loaded ? 'status-online' : 'status-offline'}`}></span>
          <span>{systemStatus?.data_loaded ? 'Data Loaded' : 'No Dataset'}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
          <span className={`status-dot ${systemStatus?.neo4j ? 'status-online' : 'status-offline'}`}></span>
          <span>Neo4j {systemStatus?.neo4j ? 'Connected' : 'Offline'}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <span className="status-dot status-online"></span>
          <span>AI Engine</span>
        </div>
        <div className="mt-3 text-xs text-gray-600">SIH 2026 Prototype</div>
      </div>
    </div>
  );
}
