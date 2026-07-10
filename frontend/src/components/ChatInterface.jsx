import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { submitChatMessage, submitTranscription } from '../store/interactionSlice';

export default function ChatInterface() {
  const dispatch = useDispatch();
  const { chat, currentForm } = useSelector((state) => state.interactions);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (chatMessagesRef.current && messagesEndRef.current) {
      chatMessagesRef.current.scrollTop = messagesEndRef.current.offsetTop - chatMessagesRef.current.offsetTop;
    }
  }, [chat.messages]);

  const handleSend = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed) return;
    dispatch({ type: 'interactions/addChatMessage', payload: { role: 'user', text: trimmed } });
    dispatch(submitChatMessage(trimmed));
    setInput('');
  };

  // ─── File Upload ────────────────────────────────────────────────────

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/ogg', 'audio/webm', 'audio/flac',
      'audio/mpeg', 'audio/x-wav', 'audio/x-m4a'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a|ogg|webm|flac)$/i)) {
      alert('Unsupported format. Use mp3, wav, m4a, ogg, webm, or flac.');
      return;
    }

    console.log('[File] Uploading:', file.name, file.type, file.size, 'bytes');
    dispatch(submitTranscription(file));
    fileInputRef.current.value = '';
  };

  return (
    <div className="chat-interface">
      <h2 className="form-title">Chat with AI Assistant</h2>

      <div className="chat-messages" ref={chatMessagesRef}>
        {chat.messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble chat-bubble--${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {chat.loading && (
          <div className="chat-bubble chat-bubble--bot chat-bubble--typing">
            <span className="typing-dot">•</span>
            <span className="typing-dot">•</span>
            <span className="typing-dot">•</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input
          type="text"
          className="chat-input"
          placeholder="Describe your interaction…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={chat.loading}
        />

        <input
          type="file"
          accept="audio/*,.mp3,.wav,.m4a,.ogg,.webm,.flac"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />

        <button
          type="button"
          className="btn btn-file"
          onClick={() => fileInputRef.current?.click()}
          disabled={chat.loading}
          title="Upload audio file"
        >
          📁
        </button>

        <button
          type="submit"
          className="btn btn-primary btn-send"
          disabled={chat.loading || !input.trim()}
        >
          Send
        </button>
      </form>

      {currentForm.hcpName && (
        <div className="chat-status">
          ✦ Form auto-populated — review and submit above.
        </div>
      )}
    </div>
  );
}
