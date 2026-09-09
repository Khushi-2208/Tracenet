export default function ActorProfile({ profile }) {
  if (!profile) return null;

  return (
    <div className="glass-card fade-in">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider">Investigated Entity</div>
          <h2 className="text-2xl font-black text-gray-100 mt-1">{profile.username}</h2>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20">
          ACTIVE ENTITY
        </span>
      </div>

      <div className="space-y-4 mt-4">
        {/* PGP Keys */}
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">🔑 PGP Keys</div>
          {profile.pgp_keys?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {profile.pgp_keys.map((k, i) => (
                <div key={i} className="bg-purple-500/10 text-purple-400 border border-purple-500/20 rounded px-3 py-1.5 text-sm font-mono" style={{ wordBreak: 'break-all' }}>{k}</div>
              ))}
            </div>
          ) : <div className="text-gray-600 text-sm">None detected</div>}
        </div>

        {/* Wallets */}
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">💳 Crypto Wallets</div>
          {profile.wallets?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {profile.wallets.map((w, i) => (
                <div key={i} className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 rounded px-3 py-1.5 text-sm font-mono" style={{ wordBreak: 'break-all' }}>{w}</div>
              ))}
            </div>
          ) : <div className="text-gray-600 text-sm">None detected</div>}
        </div>

        {/* Domains */}
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">🌐 Domains</div>
          {profile.domains?.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {profile.domains.map((d, i) => (
                <div key={i} className="bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded px-3 py-1.5 text-sm font-mono" style={{ wordBreak: 'break-all' }}>{d}</div>
              ))}
            </div>
          ) : <div className="text-gray-600 text-sm">None detected</div>}
        </div>
      </div>

      {/* Posts & Related */}
      <div className="space-y-4 mt-4 pt-4 border-t border-gray-800">
        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">
            📝 Forum Posts ({profile.post_count ?? 0})
          </div>
          <div className="max-h-48 overflow-y-auto space-y-2">
            {profile.posts?.map((post, i) => (
              <div key={i} className="bg-navy-800 rounded p-3 text-sm text-gray-400 border border-gray-800">
                {post}
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">
            👥 Potential Persona Links
          </div>
          {profile.potential_links?.length > 0 ? (
            <div className="space-y-2">
              {profile.potential_links.map((link, i) => (
                <div key={i} className="flex items-center justify-between bg-navy-800 rounded p-3 border border-gray-800">
                  <span className="font-semibold text-gray-200">{link.related_username}</span>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                      link.confidence_score >= 0.75 ? 'badge-high' :
                      link.confidence_score >= 0.50 ? 'badge-medium' : 'badge-low'
                    }`}>
                      {link.confidence_percentage}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 text-sm">No direct entity graph overlap found</div>
          )}

          {/* Related Usernames from graph */}
          {profile.related_usernames?.length > 0 && !profile.potential_links?.length && (
            <div className="space-y-2">
              {profile.related_usernames.map((u, i) => (
                <div key={i} className="flex items-center gap-2 text-sm text-gray-300 bg-navy-800 rounded p-2 border border-gray-800">
                  <span className="text-cyber-blue">→</span> {u} <span className="text-gray-600 text-xs">(Shared Infrastructure)</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
