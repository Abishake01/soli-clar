import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const Tutor = () => {
  const [clarityCode, setClarityCode] = useState('');
  const [explanation, setExplanation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleExplain = async () => {
    if (!clarityCode.trim()) return;
    setIsLoading(true);
    setError('');
    setExplanation('');
    try {
      const res = await axios.post(`${API_BASE_URL}/api/explain`, { clarityCode });
      setExplanation(res.data.explanation || '');
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to explain');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <header className="App-header">
        <h1>AI Tutor</h1>
        <p>Paste Clarity code to get an explanation and guidance.</p>
      </header>
      <main>
        <div style={{ display: 'grid', gap: 12 }}>
          <textarea
            placeholder="Paste Clarity code here..."
            value={clarityCode}
            onChange={(e) => setClarityCode(e.target.value)}
            rows={10}
            style={{ fontFamily: 'monospace', padding: 12 }}
          />
          <button className="convert-button" onClick={handleExplain} disabled={isLoading || !clarityCode.trim()}>
            {isLoading ? 'Explaining...' : 'Explain Code'}
          </button>
          {error && <div className="error-message">{error}</div>}
          {explanation && (
            <div style={{ textAlign: 'left', whiteSpace: 'pre-wrap', background: '#f9fafb', padding: 12, borderRadius: 8 }}>
              {explanation}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Tutor;

