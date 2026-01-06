import React, { useState, useEffect } from 'react';
import { GoogleGenerativeAI } from '@google/generative-ai';
import ApiKeyModal from './components/ApiKeyModal';
import ChatInterface from './components/ChatInterface';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [genAI, setGenAI] = useState(null);
  const [chatContext, setChatContext] = useState(null);

  // Load chat context from database
  useEffect(() => {
    fetch('/api/chat-context')
      .then(res => res.json())
      .then(data => {
        setChatContext(data);
      })
      .catch(err => console.error("Failed to load chat context:", err));
  }, []);

  useEffect(() => {
    if (apiKey) {
      const ai = new GoogleGenerativeAI(apiKey);
      setGenAI(ai);
    }
  }, [apiKey]);

  const handleSaveKey = (key) => {
    setApiKey(key);
  };

  const handleSendMessage = async (text) => {
    if (!genAI) return;

    // Add user message
    const userMsg = { role: 'user', text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      if (!chatContext) {
        setMessages(prev => [...prev, {
          role: 'model',
          text: 'Maaf, sistem sedang memuat data. Silakan coba lagi sebentar.'
        }]);
        setIsLoading(false);
        return;
      }

      // Format FAQ context
      const faqContext = chatContext.faq.map(faq =>
        `Q: ${faq.pertanyaan}\nA: ${faq.jawaban}`
      ).join('\n\n');

      // Format fasilitas context - ALL DATA with compact format
      const fasilitasContext = chatContext.fasilitas.map(f =>
        `${f.nama_fasilitas}|${f.alamat}|${f.kelurahan}|${f.kecamatan}${f.telp ? `|${f.telp}` : ''}`
      ).join('\n');

      // Debug: Log the data being sent to AI
      console.log('=== DEBUG: Data loaded ===');
      console.log('Total FAQ:', chatContext.faq.length);
      console.log('Total Fasilitas:', chatContext.fasilitas.length);
      console.log('ALL fasilitas included in AI context');
      console.log('Sample fasilitas (first 3):');
      chatContext.fasilitas.slice(0, 3).forEach(f => {
        console.log(`- ${f.nama_fasilitas}`);
      });

      const systemInstruction = `Anda adalah asisten customer service virtual untuk Website Kota Pangkal Pinang. 
Tugas Anda adalah membantu pengunjung dengan ramah, sopan, dan profesional.

DATA YANG TERSEDIA:

=== FREQUENTLY ASKED QUESTIONS (FAQ) ===
${faqContext}

=== FASILITAS DI PANGKAL PINANG ===
Format: Nama|Alamat|Kelurahan|Kecamatan|Telp
Total: ${chatContext.fasilitas.length} fasilitas (SEMUA DATA)

${fasilitasContext}

PEDOMAN MENJAWAB:
1. Gunakan nada yang RAMAH, SOPAN, dan HANGAT
2. Jika pertanyaan ada di FAQ atau data fasilitas, berikan jawaban lengkap dan informatif
3. Jika diminta informasi fasilitas tertentu (masjid, gereja, sekolah, rumah sakit, dll), cari di data fasilitas
4. Jika pertanyaan di luar data yang tersedia, jawab dengan sopan: 
   "Maaf, saya belum memiliki informasi tersebut. Silakan hubungi kantor pelayanan Kota Pangkal Pinang untuk informasi lebih lanjut."
5. Selalu akhiri jawaban dengan ramah
6. Gunakan Bahasa Indonesia yang baik dan benar

Ingat: Anda adalah perwakilan resmi Kota Pangkal Pinang, selalu profesional dan membantu!`;

      const model = genAI.getGenerativeModel({
        model: "gemini-2.5-flash",
        systemInstruction: systemInstruction
      });

      // Construct history for the chat model
      const history = messages.map(m => ({
        role: m.role,
        parts: [{ text: m.text }]
      }));

      const chat = model.startChat({
        history: history,
        generationConfig: {
          maxOutputTokens: 1000,
        },
      });

      const result = await chat.sendMessage(text);
      const response = await result.response;
      const textResponse = response.text();

      setMessages(prev => [...prev, { role: 'model', text: textResponse }]);
    } catch (error) {
      console.error("Error generating response:", error);
      setMessages(prev => [...prev, {
        role: 'model',
        text: `Error: ${error.message || "Something went wrong. Please check your API key."}`
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
