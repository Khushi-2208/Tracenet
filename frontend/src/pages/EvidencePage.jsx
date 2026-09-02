import { useState, useEffect } from 'react';
import PersonaLinks from '../components/PersonaLinks';
import EvidenceBreakdown from '../components/EvidenceBreakdown';
import InvestigatorReview from '../components/InvestigatorReview';
import { getPersonaLinks, getEvidenceBreakdown } from '../services/api';

export default function EvidencePage({ stats }) {
  const [links, setLinks] = useState([]);
  const [selectedPair, setSelectedPair] = useState(null);
  const [evidenceDetails, setEvidenceDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (stats?.is_processed) {
      loadLinks();
    }
  }, [stats]);

  const loadLinks = async () => {
    try {
      const res = await getPersonaLinks();
      setLinks(res.relationships);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectPair = async (uA, uB) => {
    setSelectedPair([uA, uB]);
    setLoading(true);
    try {
      const res = await getEvidenceBreakdown(uA, uB);
      setEvidenceDetails(res.evidence);
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
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-100">Evidence Correlation</h2>
        <p className="text-sm text-gray-400 mt-1">Review AI-generated stylometric and graph-based persona links</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        {/* Left Col: Links Table */}
        <div className="flex flex-col min-h-0 overflow-y-auto pr-2">
          <PersonaLinks 
            relationships={links} 
            onSelect={handleSelectPair} 
            selectedPair={selectedPair} 
          />
        </div>

        {/* Right Col: Evidence Details & Review */}
        <div className="flex flex-col gap-6 overflow-y-auto pr-2">
          {loading && <div className="text-cyber-blue">Loading evidence...</div>}
          
          {!selectedPair && !loading && (
            <div className="glass-card flex-1 flex flex-col items-center justify-center text-gray-500">
              <div className="text-4xl mb-4">🔗</div>
              <p>Select a persona link from the table to view detailed evidence</p>
            </div>
          )}

          {selectedPair && evidenceDetails && !loading && (
            <>
              <EvidenceBreakdown evidence={evidenceDetails} />
              <InvestigatorReview 
                evidence={evidenceDetails} 
                onUpdate={() => {
                  loadLinks(); // Refresh table
                  handleSelectPair(selectedPair[0], selectedPair[1]); // Refresh details
                }} 
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
