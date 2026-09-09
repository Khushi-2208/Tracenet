export default function Header({ systemStatus }) {
  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-navy-800/50 backdrop-blur-sm">
      <div>
        <h1 className="text-lg font-bold text-gray-200">
          TRACENET <span className="text-gray-500 font-normal text-sm">• Cyber Intelligence Platform</span>
        </h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-gray-400 bg-navy-700 px-3 py-1.5 rounded-full">
          <span className={`status-dot ${systemStatus?.status === 'online' ? 'status-online' : 'status-offline'}`}></span>
          <span>SYSTEM {systemStatus?.status === 'online' ? 'ONLINE' : 'OFFLINE'}</span>
        </div>
      </div>
    </div>
  );
}
