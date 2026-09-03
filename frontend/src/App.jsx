import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000/chat";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: trimmedMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedMessage,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
      }

      const data = await response.json();

      setConversationId(data.conversation_id);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I couldn't process your request.",
        },
      ]);
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
    <div className="app">
      <div className="chat-card">
        <header className="chat-header">
          <div>
            <h1>AI Customer Support</h1>
            <p>How can we help you today?</p>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            Online
          </div>
        </header>

        <main className="chat-container">
          {messages.length === 0 && (
            <div className="welcome">
              <h2>Welcome 👋</h2>
              <p>
                Ask me anything and I'll do my best to help.
              </p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-row ${msg.role}`}
            >
              <div className={`message ${msg.role}`}>
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-row assistant">
              <div className="message assistant typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </main>

        <div className="input-area">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            rows="1"
            disabled={loading}
          />

          <button
            onClick={handleSend}
            disabled={!message.trim() || loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;