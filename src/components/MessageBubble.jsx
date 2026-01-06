import React from 'react';
import { Bot, User } from 'lucide-react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div style={{
            display: 'flex',
            gap: '1rem',
            marginBottom: '1.5rem',
            flexDirection: isUser ? 'row-reverse' : 'row'
        }}>
            <div style={{
                width: '36px', height: '36px', borderRadius: '50%',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
                background: isUser ? 'var(--accent-secondary)' : 'var(--accent-primary)',
                color: 'white'
            }}>
                {isUser ? <User size={20} /> : <Bot size={20} />}
            </div>

            <div style={{
                maxWidth: '80%',
                padding: '1rem',
                borderRadius: '20px', // More rounded
                borderTopRightRadius: isUser ? '4px' : '20px',
                borderTopLeftRadius: !isUser ? '4px' : '20px',
                background: isUser ? '#000000' : '#ffffff', // User: Black, AI: White
                border: !isUser ? '1px solid rgba(0,0,0,0.05)' : 'none',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap', // Preserve formatting
                color: isUser ? '#ffffff' : '#1d1d1f',
                boxShadow: isUser ? '0 2px 4px rgba(0,0,0,0.1)' : '0 2px 8px rgba(0,0,0,0.04)'
            }}>
                {message.text}
            </div>
        </div>
    );
};

export default MessageBubble;
