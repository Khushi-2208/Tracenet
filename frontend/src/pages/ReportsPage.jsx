import { useState, useEffect } from 'react';
import { getExportCSVUrl, getExportPDFUrl, getExportJSONUrl, getPersonaLinks } from '../services/api';

export default function ReportsPage({ stats }) {
  const [links, setLinks] = useState([]);
  const [selectedPair, setSelectedPair] = useState('');

  useEffect(() => {
    if (stats?.is_processed) {
      getPersonaLinks(0.0).then(res => {
        setLinks(res.relationships || []);
        if (res.relationships?.length) {
          setSelectedPair(`${res.relationships[0].username_a}|${res.relationships[0].username_b}`);
        }
      }).catch(console.error);
    }
  }, [stats]);

  if (!stats?.is_processed) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-full text-gray-500">
        <div className="text-4xl mb-4">📂</div>
        <p>No dataset processed. Please upload a CSV from the Overview page.</p>
      </div>
    );
  }

  return (
    <div className="p-6 h-full flex flex-col max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-100">Intelligence Export & Reports</h2>
        <p className="text-sm text-gray-400 mt-1">Generate professional investigation artifacts for law enforcement or further analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* PDF Export */}
        <div className="glass-card flex flex-col">
          <div className="text-4xl mb-3">📄</div>
          <h3 className="text-lg font-bold text-gray-200 mb-2">PDF Intelligence Brief</h3>
          <p className="text-sm text-gray-400 mb-4 flex-1">
            Generate a formatted, professional PDF report for a specific persona link containing confidence scores, shared evidence, and investigator notes.
          </p>
          
          <div className="mb-4">
            <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1 block">
              Target Persona Link
            </label>
            <select 
              className="search-input w-full"
              value={selectedPair}
              onChange={(e) => setSelectedPair(e.target.value)}
            >
              {links.map((l, i) => (
                <option key={i} value={`${l.username_a}|${l.username_b}`}>
                  {l.username_a} ↔ {l.username_b} ({l.confidence_percentage})
                </option>
              ))}
            </select>
          </div>

          <a 
            href={selectedPair ? getExportPDFUrl(...selectedPair.split('|')) : '#'}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-cyber text-center flex items-center justify-center gap-2"
          >
            <span>⬇️</span> EXPORT PDF REPORT
          </a>
        </div>

        {/* CSV Export */}
        <div className="glass-card flex flex-col">
          <div className="text-4xl mb-3">📊</div>
          <h3 className="text-lg font-bold text-gray-200 mb-2">CSV Data Dump</h3>
          <p className="text-sm text-gray-400 mb-4 flex-1">
            Export the complete table of calculated persona links, including raw confidence scores and stylometric breakdown percentages.
          </p>
          <a 
            href={getExportCSVUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline text-center flex items-center justify-center gap-2 mt-auto"
          >
            <span>⬇️</span> DOWNLOAD CSV
          </a>
        </div>

        {/* JSON Export */}
        <div className="glass-card flex flex-col md:col-span-2">
          <div className="text-4xl mb-3">⚙️</div>
          <h3 className="text-lg font-bold text-gray-200 mb-2">Machine-Readable JSON</h3>
          <p className="text-sm text-gray-400 mb-4">
            Complete dataset export for ingestion into external tools (e.g., Maltego, Palantir). Includes all dataset statistics, processed text metrics, and graph topology.
          </p>
          <a 
            href={getExportJSONUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline text-center flex items-center justify-center gap-2"
          >
            <span>⬇️</span> DOWNLOAD JSON ARCHIVE
          </a>
        </div>

      </div>
    </div>
  );
}
