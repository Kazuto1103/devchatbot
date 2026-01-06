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
                borderRadius: '12px',
                borderTopRightRadius: isUser ? '4px' : '12px',
                borderTopLeftRadius: !isUser ? '4px' : '12px',
                background: isUser ? 'rgba(255, 140, 66, 0.15)' : 'rgba(96, 165, 250, 0.15)',
                border: `1px solid ${isUser ? 'rgba(255, 140, 66, 0.3)' : 'rgba(96, 165, 250, 0.3)'}`,
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap', // Preserve formatting
                color: 'var(--text-primary)'
            }}>
                {message.text}
            </div>
        </div>
    );
};

export default MessageBubble;
