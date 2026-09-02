import { useState } from 'react';

export default function TimelineView({ events, filters = true }) {
  const [filterType, setFilterType] = useState('All');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  if (!events || !events.length) return <div className="text-gray-600 text-sm">No timeline data available.</div>;

  let filtered = [...events];

  // Filter by type
  if (filterType !== 'All') {
    const typeMap = {
      'Posts': (e) => true,
      'PGP': (e) => e.pgp_key && e.pgp_key !== 'UNKNOWN_PGP',
      'Wallet': (e) => e.wallet_id && e.wallet_id !== 'UNKNOWN_WALLET',
      'Domain': (e) => e.domain && e.domain !== 'unknown.onion',
    };
    if (typeMap[filterType]) filtered = filtered.filter(typeMap[filterType]);
  }

  // Date range filter
  if (dateFrom) filtered = filtered.filter(e => e.timestamp >= dateFrom);
  if (dateTo) filtered = filtered.filter(e => e.timestamp <= dateTo + 'T23:59:59');

  // Group by date
  const grouped = {};
  filtered.forEach(e => {
    const date = e.timestamp.split('T')[0];
    if (!grouped[date]) grouped[date] = [];
    grouped[date].push(e);
  });

  const sortedDates = Object.keys(grouped).sort().reverse();

  return (
    <div className="fade-in">
      {/* Filters */}
      {filters && (
        <div className="flex flex-wrap gap-3 mb-6">
          {['All', 'Posts', 'PGP', 'Wallet', 'Domain'].map(type => (
            <button
              key={type}
              className={`btn-outline text-xs ${filterType === type ? 'border-cyber-blue text-cyber-blue' : ''}`}
              onClick={() => setFilterType(type)}
            >
              {type}
            </button>
          ))}
          <div className="flex items-center gap-2 ml-auto">
            <input
              type="date"
              className="search-input text-xs py-1 px-2"
              style={{ paddingLeft: '8px', width: '140px' }}
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              placeholder="From"
            />
            <span className="text-gray-600">to</span>
            <input
              type="date"
              className="search-input text-xs py-1 px-2"
              style={{ paddingLeft: '8px', width: '140px' }}
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              placeholder="To"
            />
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="space-y-6">
        {sortedDates.map(date => (
          <div key={date}>
            <div className="text-sm font-bold text-cyber-blue mb-3 uppercase tracking-wider">
              {new Date(date + 'T00:00:00').toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })}
            </div>
            <div className="relative pl-8">
              <div className="timeline-line"></div>
              {grouped[date].map((event, i) => (
                <div key={i} className="relative pb-4 slide-in" style={{ animationDelay: `${i * 50}ms` }}>
                  <div className="timeline-dot" style={{ top: '6px' }}></div>
                  <div className="bg-navy-700/50 border border-gray-800 rounded-lg p-3 ml-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-sm text-gray-200">{event.username}</span>
                      <span className="text-xs text-gray-600">•</span>
                      <span className="text-xs text-gray-500">{event.source}</span>
                      <span className="text-xs text-gray-600 ml-auto">
                        {event.timestamp.split('T')[1]?.slice(0, 5)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-400 mb-2">{event.text}</div>
                    <div className="flex flex-wrap gap-2">
                      {event.pgp_key && event.pgp_key !== 'UNKNOWN_PGP' && (
                        <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded">🔑 {event.pgp_key}</span>
                      )}
                      {event.wallet_id && event.wallet_id !== 'UNKNOWN_WALLET' && (
                        <span className="text-xs bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded">💳 {event.wallet_id}</span>
                      )}
                      {event.domain && (
                        <span className="text-xs bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded">🌐 {event.domain}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-gray-600 text-center py-8">No events match the current filters.</div>
      )}
    </div>
  );
}
