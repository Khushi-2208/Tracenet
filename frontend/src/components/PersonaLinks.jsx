export default function PersonaLinks({ relationships, onSelect, selectedPair }) {
  if (!relationships || !relationships.length) return null;

  return (
    <div className="glass-card fade-in">
      <h3 className="text-lg font-bold text-gray-200 mb-4">Potential Persona Links</h3>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Username A</th>
              <th>Username B</th>
              <th>Confidence</th>
              <th>PGP</th>
              <th>Wallet</th>
              <th>Domain</th>
              <th>Writing</th>
              <th>Assessment</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {relationships.map((r, i) => {
              const isSelected = selectedPair &&
                ((selectedPair[0] === r.username_a && selectedPair[1] === r.username_b) ||
                 (selectedPair[0] === r.username_b && selectedPair[1] === r.username_a));

              return (
                <tr
                  key={i}
                  className={`cursor-pointer transition-colors ${isSelected ? 'bg-cyber-blue/5' : ''}`}
                  onClick={() => onSelect?.(r.username_a, r.username_b)}
                >
                  <td className="font-semibold text-gray-200">{r.username_a}</td>
                  <td className="font-semibold text-gray-200">{r.username_b}</td>
                  <td>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      r.confidence_score >= 0.75 ? 'badge-high' :
                      r.confidence_score >= 0.50 ? 'badge-medium' : 'badge-low'
                    }`}>
                      {r.confidence_percentage}
                    </span>
                  </td>
                  <td className="font-mono text-sm">{r.pgp_match_pct}</td>
                  <td className="font-mono text-sm">{r.wallet_match_pct}</td>
                  <td className="font-mono text-sm">{r.domain_match_pct}</td>
                  <td className="font-mono text-sm">{r.writing_match_pct}</td>
                  <td>
                    <span className="text-xs text-gray-400">{r.ai_assessment}</span>
                  </td>
                  <td>
                    <span className={`text-xs ${
                      r.investigator_review_status === 'Marked as Verified Link' ? 'text-green-400' :
                      r.investigator_review_status === 'Dismissed / Unrelated' ? 'text-red-400' : 'text-gray-500'
                    }`}>
                      {r.investigator_review_status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
