import React, { useState, useEffect } from 'react';

import ApiKeyModal from './components/ApiKeyModal';
import ChatInterface from './components/ChatInterface';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSaveKey = (key) => {
    setApiKey(key);
  };

  const handleSendMessage = async (text) => {
    // Add user message to UI immediately
    const userMsg = { role: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          apiKey: apiKey,
          message: text,
          history: messages // Send previous conversation history
        }),
      });


      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Server error: ${response.status}`);
      }

      if (data.error) {
        throw new Error(data.error);
      }

      setMessages(prev => [...prev, { role: 'model', text: data.text }]);
    } catch (error) {
      console.error("Error generating response:", error);
      setMessages(prev => [...prev, {
        role: 'model',
        text: `Error: ${error.message || "Failed to connect to the server."}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      {!apiKey ? (
        <ApiKeyModal onSave={handleSaveKey} />
      ) : (
        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}

export default App;
