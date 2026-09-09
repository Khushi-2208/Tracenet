import { useState } from 'react';
import { verifyLink, rejectLink, addNote } from '../services/api';

export default function InvestigatorReview({ evidence, onUpdate }) {
  const [notes, setNotes] = useState(evidence?.review_notes || '');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState('');

  if (!evidence) return null;

  const handleVerify = async () => {
    setSaving(true);
    try {
      await verifyLink(evidence.username_a, evidence.username_b);
      setFeedback('Link verified successfully.');
      onUpdate?.();
    } catch (e) {
      setFeedback('Error: ' + (e.response?.data?.detail || e.message));
    }
    setSaving(false);
  };

  const handleReject = async () => {
    setSaving(true);
    try {
      await rejectLink(evidence.username_a, evidence.username_b);
      setFeedback('Link rejected/dismissed.');
      onUpdate?.();
    } catch (e) {
      setFeedback('Error: ' + (e.response?.data?.detail || e.message));
    }
    setSaving(false);
  };

  const handleAddNote = async () => {
    if (!notes.trim()) return;
    setSaving(true);
    try {
      await addNote(evidence.username_a, evidence.username_b, notes);
      setFeedback('Notes saved successfully.');
      onUpdate?.();
    } catch (e) {
      setFeedback('Error: ' + (e.response?.data?.detail || e.message));
    }
    setSaving(false);
  };

  return (
    <div className="glass-card fade-in">
      <h3 className="text-lg font-bold text-gray-200 mb-1">⚖️ Investigator Review</h3>
      <p className="text-xs text-gray-500 mb-4">
        AI Assessment: <span className="text-gray-300">{evidence.ai_assessment}</span> — Requires human verification
      </p>

      {/* Status */}
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xs text-gray-500">Current Status:</span>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
          evidence.investigator_review_status === 'Marked as Verified Link' ? 'bg-green-500/15 text-green-400 border border-green-500/30' :
          evidence.investigator_review_status === 'Dismissed / Unrelated' ? 'bg-red-500/15 text-red-400 border border-red-500/30' :
          'bg-amber-500/15 text-amber-400 border border-amber-500/30'
        }`}>
          {evidence.investigator_review_status}
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-4">
        <button className="btn-success px-4 py-2 rounded-lg font-semibold text-sm" onClick={handleVerify} disabled={saving}>
          ✓ VERIFY LINK
        </button>
        <button className="btn-danger px-4 py-2 rounded-lg font-semibold text-sm" onClick={handleReject} disabled={saving}>
          ✗ REJECT LINK
        </button>
      </div>

      {/* Notes */}
      <div className="mb-3">
        <label className="text-xs text-gray-500 uppercase tracking-wider font-semibold mb-1 block">
          Investigator Notes
        </label>
        <textarea
          className="w-full bg-navy-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-300 focus:border-cyber-blue focus:outline-none resize-none"
          rows={3}
          placeholder="Enter analytical observation or verification reference..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
      <button className="btn-outline text-sm" onClick={handleAddNote} disabled={saving || !notes.trim()}>
        💾 ADD NOTE
      </button>

      {/* Feedback */}
      {feedback && (
        <div className="mt-3 text-xs text-cyber-blue bg-cyber-blue/10 px-3 py-2 rounded">
          {feedback}
        </div>
      )}
    </div>
  );
}
