export default function EvidenceBreakdown({ evidence }) {
  if (!evidence) return null;

  const scoreColor = (score) => {
    if (score >= 0.75) return '#ef4444';
    if (score >= 0.50) return '#f59e0b';
    return '#3b82f6';
  };

  const signals = [
    { label: 'PGP Key Match', weight: '30%', score: evidence.pgp_score, pct: evidence.pgp_match_pct, color: '#9d4edd' },
    { label: 'Wallet Match', weight: '25%', score: evidence.wallet_score, pct: evidence.wallet_match_pct, color: '#00f5d4' },
    { label: 'Domain Match', weight: '20%', score: evidence.domain_score, pct: evidence.domain_match_pct, color: '#3a86ff' },
    { label: 'Writing Style', weight: '25%', score: evidence.writing_style_score, pct: evidence.writing_match_pct, color: '#ffb703' },
  ];

  return (
    <div className="glass-card fade-in">
      {/* Confidence Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider">Evidence Confidence</div>
          <div className="text-sm text-gray-400 mt-1">
            {evidence.username_a} ↔ {evidence.username_b}
          </div>
        </div>
        <div className="text-right">
          <div className="text-4xl font-black font-mono" style={{ color: scoreColor(evidence.confidence_score) }}>
            {evidence.confidence_percentage}
          </div>
          <div className={`text-xs mt-1 px-2 py-0.5 rounded inline-block font-semibold ${
            evidence.confidence_score >= 0.75 ? 'badge-high' :
            evidence.confidence_score >= 0.50 ? 'badge-medium' : 'badge-low'
          }`}>
            {evidence.ai_assessment}
          </div>
        </div>
      </div>

      {/* Signal Breakdown */}
      <div className="space-y-4">
        {signals.map((s, i) => (
          <div key={i}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-300">{s.label} <span className="text-gray-600">({s.weight})</span></span>
              <span className="text-sm font-semibold font-mono" style={{ color: s.color }}>{s.pct}</span>
            </div>
            <div className="score-bar">
              <div className="score-bar-fill" style={{ width: `${s.score * 100}%`, background: s.color }}></div>
            </div>
          </div>
        ))}
      </div>

      {/* Evidence Explanation */}
      {evidence.evidence_explanation && (
        <div className="mt-6 pt-4 border-t border-gray-800">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">Evidence Reasoning</div>
          <div className="space-y-1.5">
            {evidence.evidence_explanation.map((exp, i) => (
              <div key={i} className={`text-sm px-3 py-1.5 rounded ${
                exp.includes('✓') ? 'bg-green-500/10 text-green-400' : 'bg-gray-800 text-gray-500'
              }`}>
                {exp}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Shared Artifacts */}
      <div className="mt-4 grid grid-cols-3 gap-3">
        <div>
          <div className="text-xs text-gray-600">Shared PGPs</div>
          <div className="text-sm text-gray-300 font-mono mt-1">{evidence.shared_pgps?.join(', ') || 'None'}</div>
        </div>
        <div>
          <div className="text-xs text-gray-600">Shared Wallets</div>
          <div className="text-sm text-gray-300 font-mono mt-1">{evidence.shared_wallets?.join(', ') || 'None'}</div>
        </div>
        <div>
          <div className="text-xs text-gray-600">Shared Domains</div>
          <div className="text-sm text-gray-300 font-mono mt-1">{evidence.shared_domains?.join(', ') || 'None'}</div>
        </div>
      </div>
    </div>
  );
}
