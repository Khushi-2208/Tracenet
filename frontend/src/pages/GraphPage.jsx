import { useState, useEffect } from 'react';
import ForceGraph from '../components/ForceGraph';
import { getFullGraph } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function GraphPage({ stats }) {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (stats?.is_processed) {
      loadGraph();
    }
  }, [stats]);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const data = await getFullGraph();
      setGraphData(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleNodeClick = (username) => {
    navigate(`/investigate?q=${encodeURIComponent(username)}`);
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
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">Global Characteristic Graph</h2>
          <p className="text-sm text-gray-400 mt-1">Multi-entity relationship visualization</p>
        </div>
        <div className="text-sm text-gray-500 bg-navy-800 px-3 py-1.5 rounded-lg border border-gray-700">
          Nodes: {graphData?.nodes?.length || 0} | Edges: {graphData?.links?.length || 0}
        </div>
      </div>

      <div className="flex-1 glass-card p-1">
        {loading ? (
          <div className="flex items-center justify-center h-full text-cyber-blue">Loading global graph...</div>
        ) : graphData ? (
          <ForceGraph data={graphData} height={typeof window !== 'undefined' ? window.innerHeight - 200 : 700} onNodeClick={handleNodeClick} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">Failed to load graph</div>
        )}
      </div>
    </div>
  );
}
