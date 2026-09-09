import { useState, useEffect, useCallback } from 'react';
import CSVUpload from '../components/CSVUpload';
import ProcessingStatus from '../components/ProcessingStatus';
import StatsCards from '../components/StatsCards';
import SearchBar from '../components/SearchBar';
import { uploadCSV, loadSampleData, getDatasetStats } from '../services/api';
import { useNavigate } from 'react-router-dom';

const PROCESSING_STEPS = [
  'Reading CSV',
  'Validating records',
  'Extracting entities',
  'Creating Neo4j graph',
  'Running AI writing analysis',
  'Calculating confidence scores',
];

export default function DashboardPage({ stats, setStats, onDataLoaded }) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStep, setProcessingStep] = useState(-1);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const simulateSteps = useCallback((callback) => {
    setIsProcessing(true);
    setProcessingStep(0);
    setError('');

    // Simulate step progression while backend processes
    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step < PROCESSING_STEPS.length - 1) {
        setProcessingStep(step);
      }
    }, 800);

    callback()
      .then((result) => {
        clearInterval(interval);
        setProcessingStep(PROCESSING_STEPS.length); // All done
        setStats(result);
        onDataLoaded?.();
        setTimeout(() => {
          setIsProcessing(false);
          setProcessingStep(-1);
        }, 1000);
      })
      .catch((err) => {
        clearInterval(interval);
        setIsProcessing(false);
        setProcessingStep(-1);
        setError(err.response?.data?.detail || err.message || 'Processing failed');
      });
  }, [setStats, onDataLoaded]);

  const handleUpload = (file) => {
    simulateSteps(() => uploadCSV(file));
  };

  const handleLoadSample = () => {
    simulateSteps(() => loadSampleData());
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      navigate(`/investigate?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Hero Banner */}
      <div className="glass-card text-center py-8">
        <h1 className="text-3xl font-black tracking-wide" style={{
          background: 'linear-gradient(90deg, #38bdf8, #818cf8)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          TRACENET
        </h1>
        <p className="text-gray-400 mt-2">Threat Actor Intelligence Platform</p>
        <p className="text-xs text-gray-600 mt-1 max-w-xl mx-auto">
          Multi-Source Persona Correlation & Stylometric Intelligence Fusion Engine for Cyber Investigations
        </p>
      </div>

      {/* Human-in-the-loop Notice */}
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg px-4 py-3 text-sm text-amber-400 flex items-start gap-2">
        <span>⚠️</span>
        <span>
          <strong>Human-in-the-Loop Decision Support:</strong> TRACENET correlates PGP keys, wallet IDs, domains, and
          stylometric similarity signals to assist human investigators. It does NOT automatically label individuals or guarantee real-world identity.
        </span>
      </div>

      {/* Stats Cards */}
      {stats?.is_processed && <StatsCards stats={stats} />}

      {/* Main Grid: Upload + Search */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload */}
        <div>
          {isProcessing ? (
            <ProcessingStatus currentStep={processingStep} steps={PROCESSING_STEPS} />
          ) : (
            <CSVUpload onUpload={handleUpload} onLoadSample={handleLoadSample} isProcessing={isProcessing} />
          )}

          {error && (
            <div className="mt-3 bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-3 text-sm text-red-400">
              ❌ {error}
            </div>
          )}

          {/* Processing Result */}
          {stats?.is_processed && !isProcessing && (
            <div className="glass-card mt-4 fade-in">
              <div className="text-sm text-green-400 font-semibold mb-2">✓ Investigation Dataset Processed</div>
              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <div>Records Processed: <span className="text-gray-200 font-mono">{stats.records_processed}</span></div>
                <div>Unique Handles: <span className="text-gray-200 font-mono">{stats.unique_usernames}</span></div>
                <div>PGP Keys: <span className="text-gray-200 font-mono">{stats.unique_pgp_keys}</span></div>
                <div>Wallets: <span className="text-gray-200 font-mono">{stats.unique_wallets}</span></div>
                <div>Domains: <span className="text-gray-200 font-mono">{stats.unique_domains}</span></div>
                <div>Potential Links: <span className="text-gray-200 font-mono">{stats.high_confidence_links}</span></div>
              </div>
            </div>
          )}
        </div>

        {/* Search */}
        <div className="glass-card">
          <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
            <span>🔍</span> Investigation Search
          </h3>
          <SearchBar
            value={searchQuery}
            onChange={setSearchQuery}
            onSearch={handleSearch}
          />
          <p className="text-xs text-gray-600 mt-3">
            Search by username, PGP key, wallet address, or domain to begin investigation.
          </p>

          {stats?.is_processed && (
            <div className="mt-4 pt-4 border-t border-gray-800">
              <div className="text-xs text-gray-500 uppercase tracking-wider mb-2 font-semibold">Quick Access</div>
              <div className="flex flex-wrap gap-2">
                {['ShadowX', 'DarkWolf', 'CipherGhost', 'RedFox'].map(name => (
                  <button
                    key={name}
                    className="btn-outline text-xs"
                    onClick={() => navigate(`/investigate?q=${name}`)}
                  >
                    {name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
