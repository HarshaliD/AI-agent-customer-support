import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed || loading) return;

    const userMessage = trimmed;
    setInput("");
    setError(null);

    setMessages((previousMessages) => [
      ...previousMessages,
      { role: "user", content: userMessage },
    ]);

    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();

      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      setMessages((previousMessages) => [
        ...previousMessages,
        { role: "assistant", content: data.response },
      ]);
    } catch (err) {
      console.error("Error communicating with chat API:", err);
      setError("Failed to get response from support backend. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="chat-app">
      <header className="chat-header">
        <h2>AI Customer Support</h2>
        {conversationId && (
          <span className="session-tag">Session #{conversationId}</span>
        )}
      </header>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>👋 Hello! How can I help you today?</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message-bubble ${msg.role}`}>
            <div className="message-sender">
              {msg.role === "user" ? "You" : "Support Agent"}
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}

        {loading && (
          <div className="message-bubble assistant loading">
            <div className="message-sender">Support Agent</div>
            <div className="message-content">
              <span className="dot">.</span>
              <span className="dot">.</span>
              <span className="dot">.</span>
            </div>
          </div>
        )}

        {error && <div className="error-banner">{error}</div>}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}

export default App;