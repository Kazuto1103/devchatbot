import React from 'react';
import { Bot, User } from 'lucide-react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    const formatMessage = (text) => {
        if (!text) return null;

        // Split text into lines to handle bullet points and blocks
        const lines = text.split('\n');

        return lines.map((line, index) => {
            let processedLine = line;

            // Handle bullet points: "* " at the start of a line
            const isBullet = processedLine.trim().startsWith('* ');
            if (isBullet) {
                processedLine = processedLine.replace(/^\s*\*\s+/, '');
            }

            // Handle bold: **text**
            const parts = processedLine.split(/(\*\*.*?\*\*)/g);
            const content = parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={i}>{part.slice(2, -2)}</strong>;
                }
                return part;
            });

            return (
                <div key={index} style={{
                    display: isBullet ? 'list-item' : 'block',
                    marginLeft: isBullet ? '1.5rem' : '0',
                    marginBottom: index === lines.length - 1 ? '0' : '0.5rem'
                }}>
                    {content}
                </div>
            );
        });
    };

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
                borderRadius: '20px',
                borderTopRightRadius: isUser ? '4px' : '20px',
                borderTopLeftRadius: !isUser ? '4px' : '20px',
                background: isUser ? '#000000' : '#ffffff',
                border: !isUser ? '1px solid rgba(0,0,0,0.05)' : 'none',
                lineHeight: '1.6',
                whiteSpace: 'pre-wrap',
                color: isUser ? '#ffffff' : '#1d1d1f',
                boxShadow: isUser ? '0 2px 4px rgba(0,0,0,0.1)' : '0 2px 8px rgba(0,0,0,0.04)'
            }}>
                {formatMessage(message.text)}
            </div>
        </div>
    );
};

export default MessageBubble;
