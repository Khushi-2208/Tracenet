import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import SearchBar from '../components/SearchBar';
import ActorProfile from '../components/ActorProfile';
import ForceGraph from '../components/ForceGraph';
import { searchEntities, getActorProfile, getActorGraph } from '../services/api';

export default function InvestigatePage({ stats }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [searchResults, setSearchResults] = useState(null);
  const [selectedActor, setSelectedActor] = useState(null);
  const [actorProfile, setActorProfile] = useState(null);
  const [actorGraph, setActorGraph] = useState(null);
  const [loading, setLoading] = useState(false);
  const [localQuery, setLocalQuery] = useState(query);

  useEffect(() => {
    setLocalQuery(query);
  }, [query]);

  useEffect(() => {
    if (query) {
      handleSearch(query);
    }
  }, [query]);

  const handleSearch = async (q) => {
    if (!q) return;
    setLoading(true);
    try {
      const res = await searchEntities(q);
      setSearchResults(res);
      // If we find an exact username match, load profile
      const exactMatch = res.results.find(r => r.type === 'Username' && r.name.toLowerCase() === q.toLowerCase());
      if (exactMatch) {
        loadActorProfile(exactMatch.name);
      } else {
        setSelectedActor(null);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const loadActorProfile = async (username) => {
    setLoading(true);
    try {
      const profile = await getActorProfile(username);
      const graph = await getActorGraph(username);
      setActorProfile(profile);
      setActorGraph(graph);
      setSelectedActor(username);
      setSearchResults(null);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  if (!stats?.is_processed) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-full text-gray-500">
        <div className="text-4xl mb-4">📂</div>
        <p>No dataset processed. Please upload a CSV from the Overview page.</p>
      </div>
    );
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6 flex gap-4">
        <div className="flex-1">
          <SearchBar
            value={localQuery}
            onChange={setLocalQuery}
            onSearch={() => setSearchParams(localQuery ? { q: localQuery } : {})}
          />
        </div>
      </div>

      <div className="flex-1 overflow-hidden grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 overflow-y-auto pr-2">
          {loading && <div className="text-cyber-blue">Loading...</div>}
          
          {searchResults && searchResults.results.length > 0 && !selectedActor && (
            <div className="glass-card fade-in">
              <h3 className="text-lg font-bold text-gray-200 mb-4">Search Results</h3>
              <div className="space-y-2">
                {searchResults.results.map((r, i) => (
                  <div key={i} className="bg-navy-800 p-3 rounded border border-gray-800 flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-gray-200">{r.name}</div>
                      <div className="text-xs text-gray-500">{r.type}</div>
                    </div>
                    {r.type === 'Username' && (
                      <button className="btn-outline text-xs py-1" onClick={() => loadActorProfile(r.name)}>
                        Investigate
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {searchResults && searchResults.results.length === 0 && !selectedActor && (
            <div className="text-gray-500">No results found for "{query}"</div>
          )}

          {selectedActor && actorProfile && (
            <ActorProfile profile={actorProfile} />
          )}
        </div>

        <div className="lg:col-span-2 bg-navy-800 border border-gray-800 rounded-xl overflow-hidden flex flex-col relative">
          {selectedActor && actorGraph ? (
            <>
              <div className="absolute top-4 left-4 z-10 bg-navy-900/80 backdrop-blur px-3 py-1.5 rounded-lg border border-gray-700 text-sm font-semibold text-gray-200">
                2-Hop Subgraph: {selectedActor}
              </div>
              <ForceGraph data={actorGraph} height={600} onNodeClick={loadActorProfile} />
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-600">
              <div className="text-4xl mb-4">🕸️</div>
              <p>Select an actor to view their entity graph</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
