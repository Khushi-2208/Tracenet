export default function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    { label: 'Records', value: stats.records_processed, color: '#38bdf8' },
    { label: 'Unique Handles', value: stats.unique_usernames, color: '#e63946' },
    { label: 'PGP Keys', value: stats.unique_pgp_keys, color: '#9d4edd' },
    { label: 'Wallets', value: stats.unique_wallets, color: '#00f5d4' },
    { label: 'Domains', value: stats.unique_domains, color: '#3a86ff' },
    { label: 'Potential Links', value: stats.high_confidence_links ?? stats.potential_links ?? 0, color: '#ffb703' },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 fade-in">
      {cards.map((card, i) => (
        <div key={i} className="metric-card" style={{ '--accent-color': card.color }}>
          <div className="metric-val" style={{ color: card.color }}>
            {card.value ?? 0}
          </div>
          <div className="metric-lbl">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
