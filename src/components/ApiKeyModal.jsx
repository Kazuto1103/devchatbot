import React, { useState } from 'react';
import { Key } from 'lucide-react';

const ApiKeyModal = ({ onSave }) => {
  const [key, setKey] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!key.trim()) {
      setError('API Key is required');
      return;
    }
    // Simple validation (starts with AI usually, but not strictly enforced to avoid breaking changes)
    onSave(key.trim());
  };

  return (
    <div className="modal-overlay" style={{
      position: 'fixed', inset: 0, background: 'rgba(0, 0, 0, 0.4)', // Neutral dim
      backdropFilter: 'blur(5px)', display: 'flex', alignItems: 'center',
      justifyContent: 'center', zIndex: 1000
    }}>
      <div className="glass-panel" style={{ padding: '2rem', width: '100%', maxWidth: '400px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            background: 'rgba(0, 0, 0, 0.05)', padding: '1rem', borderRadius: '50%',
            marginBottom: '1rem', color: '#000000'
          }}>
            <Key size={32} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Enter API Key</h2>
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '0.5rem' }}>
            To use this chatbot, please enter your Google Gemini API Key.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <input
              type="password"
              className="input-field"
              placeholder="AIzaSy..."
              value={key}
              onChange={(e) => {
                setKey(e.target.value);
                setError('');
              }}
            />
            {error && <p style={{ color: 'var(--error)', fontSize: '0.875rem', marginTop: '0.5rem' }}>{error}</p>}
          </div>
          <button type="submit" className="btn-primary" style={{ width: '100%' }}>
            Start Chatting
          </button>
        </form>

        <p style={{ marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
          Don't have a key? <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-primary)' }}>Get one from Google AI Studio</a>
        </p>
      </div>
    </div>
  );
};

export default ApiKeyModal;
