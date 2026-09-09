import { useState, useRef } from 'react';

export default function CSVUpload({ onUpload, onLoadSample, isProcessing }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file);
    }
  };

  const handleSelect = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedFile(file);
  };

  const handleProcess = () => {
    if (selectedFile) onUpload(selectedFile);
  };

  return (
    <div className="glass-card fade-in">
      <h3 className="text-lg font-bold text-gray-200 mb-4 flex items-center gap-2">
        <span>📂</span> Upload CSV Dataset
      </h3>

      <div
        className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          className="hidden"
          onChange={handleSelect}
        />
        <div className="text-3xl mb-3">📁</div>
        {selectedFile ? (
          <>
            <div className="text-cyber-blue font-semibold">{selectedFile.name}</div>
            <div className="text-xs text-gray-500 mt-1">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </div>
          </>
        ) : (
          <>
            <div className="text-gray-400 font-medium">Drop CSV file here or click to browse</div>
            <div className="text-xs text-gray-600 mt-2">
              Required columns: username, pgp_key, wallet_id, domain, text, timestamp, source
            </div>
          </>
        )}
      </div>

      <div className="flex gap-3 mt-4">
        <button
          className="btn-cyber flex-1"
          onClick={handleProcess}
          disabled={!selectedFile || isProcessing}
        >
          {isProcessing ? '⟳ Processing...' : '▶ PROCESS DATA'}
        </button>
        <button
          className="btn-outline"
          onClick={onLoadSample}
          disabled={isProcessing}
        >
          🚀 Load Sample
        </button>
      </div>
    </div>
  );
}
