import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';

const ChatInterface = ({ messages, onSendMessage, isLoading }) => {
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isLoading]);

    return (
        <div style={{
            display: 'flex', flexDirection: 'column', height: '100vh',
            maxWidth: '900px', margin: '0 auto', width: '100%',
            position: 'relative'
        }}>
            {/* Header */}
            <header style={{
                padding: '1.25rem',
                background: 'rgba(255, 255, 255, 0.85)',
                backdropFilter: 'blur(20px)',
                position: 'sticky', top: 0, zIndex: 10,
                boxShadow: '0 1px 0px rgba(0,0,0,0.05)' // Subtle separator
            }}>
                <h1 style={{
                    fontSize: '1.25rem', fontWeight: '700',
                    color: '#000000',
                    letterSpacing: '-0.01em',
                    margin: 0,
                    display: 'flex', alignItems: 'center', gap: '0.5rem'
                }}>
                    <span style={{ fontSize: '1.5rem' }}>😊</span> Senyum Chat
                </h1>
            </header>

            {/* Messages Area */}
            <div style={{
                flex: 1, overflowY: 'auto', padding: '1rem',
                display: 'flex', flexDirection: 'column'
            }}>
                {messages.length === 0 ? (
                    <div style={{
                        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: 'var(--text-secondary)', flexDirection: 'column', gap: '1rem', opacity: 0.7
                    }}>
                        <p>Halo! Mulai percakapan dengan Senyum Chat! 😊</p>
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <MessageBubble key={idx} message={msg} />
                    ))
                )}

                {/* Loading Indicator for Model */}
                {isLoading && (
                    <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                        <div style={{
                            width: '36px', height: '36px', borderRadius: '50%',
                            background: 'var(--accent-primary)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            color: 'white'
                        }}>
                            <div className="dot-flashing" />
                        </div>
                    </div>
                )}

                <div ref={scrollRef} />
            </div>

            {/* Input Area */}
            <div style={{ padding: '1rem', paddingBottom: '2rem' }}>
                <MessageInput onSend={onSendMessage} isLoading={isLoading} />
            </div>

            {/* CSS for dot animation */}
            <style>{`
        .dot-flashing {
          position: relative;
          width: 6px;
          height: 6px;
          border-radius: 5px;
          background-color: white;
          color: white;
          animation: dot-flashing 1s infinite linear alternate;
          animation-delay: 0.5s;
        }
        .dot-flashing::before, .dot-flashing::after {
          content: '';
          display: inline-block;
          position: absolute;
          top: 0;
        }
        .dot-flashing::before {
          left: -10px;
          width: 6px; height: 6px; border-radius: 5px; background-color: white;
          animation: dot-flashing 1s infinite alternate;
          animation-delay: 0s;
        }
        .dot-flashing::after {
          left: 10px;
          width: 6px; height: 6px; border-radius: 5px; background-color: white;
          animation: dot-flashing 1s infinite alternate;
          animation-delay: 1s;
        }
        @keyframes dot-flashing {
          0% { background-color: white; }
          50%, 100% { background-color: rgba(255,255,255,0.2); }
        }
      `}</style>
        </div>
    );
};

export default ChatInterface;
