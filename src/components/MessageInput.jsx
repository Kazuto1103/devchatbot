import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

const MessageInput = ({ onSend, isLoading }) => {
    const [text, setText] = useState('');

    const handleSend = () => {
        if (text.trim() && !isLoading) {
            onSend(text.trim());
            setText('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="glass-panel" style={{ padding: '1rem', marginTop: '1rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-end' }}>
                <textarea
                    className="input-field"
                    placeholder="Type your message..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                    style={{
                        resize: 'none',
                        minHeight: '24px',
                        maxHeight: '150px',
                        height: 'auto',
                        overflowY: 'hidden',
                        fieldSizing: 'content' // Modern CSS for auto-grow (might need fallback for older browsers but fine here)
                    }}
                    rows={1}
                />
                <button
                    className="btn-primary"
                    onClick={handleSend}
                    disabled={isLoading || !text.trim()}
                    style={{
                        height: '46px', width: '46px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        padding: 0, opacity: (isLoading || !text.trim()) ? 0.5 : 1
                    }}
                >
                    {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
                </button>
            </div>
            <style>{`
        .animate-spin {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
};

export default MessageInput;
