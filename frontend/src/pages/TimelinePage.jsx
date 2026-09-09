import { useState, useEffect } from 'react';
import TimelineView from '../components/TimelineView';
import { getFullTimeline } from '../services/api';

export default function TimelinePage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    loadTimeline();
  }, []);

  const loadTimeline = async () => {
    setLoading(true);
    try {
      const res = await getFullTimeline();
      setEvents(res.events);
    } catch (err) {
      setError(true);
    }
    setLoading(false);
  };

  if (error) {
    return (
      <div className="p-6 flex flex-col items-center justify-center h-full text-gray-500">
        <div className="text-4xl mb-4">📂</div>
        <p>No dataset processed. Please upload a CSV from the Overview page.</p>
      </div>
    );
  }

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-100">Chronological Activity Timeline</h2>
        <p className="text-sm text-gray-400 mt-1">Track entity actions and posts over time</p>
      </div>

      <div className="flex-1 glass-card overflow-y-auto">
        {loading ? (
          <div className="text-cyber-blue p-4">Loading timeline...</div>
        ) : (
          <TimelineView events={events} />
        )}
      </div>
    </div>
  );
}
