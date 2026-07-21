import { useEffect, useRef, useState } from "react";
import type { ChatMessage, Document } from "../types";
import { CitationList } from "./CitationList";

interface Props {
  document: Document | null;
  messages: ChatMessage[];
  sending: boolean;
  error: string | null;
  onSend: (question: string) => void;
  onClear: () => void;
}

export function ChatPanel({
  document,
  messages,
  sending,
  error,
  onSend,
  onClear,
}: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const canChat = document?.status === "ready";

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || sending || !canChat) return;
    onSend(input);
    setInput("");
  };

  if (!document) {
    return (
      <main className="chat-panel empty">
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h2>Select or upload a document</h2>
          <p>Answers are grounded strictly in your document with page citations.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="chat-panel">
      <header className="chat-header">
        <div>
          <h2>{document.filename}</h2>
          <p className="chat-subtitle">
            {document.status === "ready"
              ? "Ask anything about this document"
              : document.status === "failed"
                ? `Indexing failed: ${document.error_message ?? "unknown error"}`
                : "Indexing in progress — chat unlocks when ready"}
          </p>
        </div>
        {messages.length > 0 && (
          <button type="button" className="btn-ghost" onClick={onClear}>
            Clear chat
          </button>
        )}
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <div className="chat-hint">
            Try: &ldquo;What are the main topics covered?&rdquo; or &ldquo;Summarize section 2.&rdquo;
          </div>
        )}
        {messages.map((msg) => (
          <article key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-role">{msg.role === "user" ? "You" : "DocBot"}</div>
            <div className="message-body">{msg.content}</div>
            {msg.role === "assistant" && msg.citations && (
              <CitationList citations={msg.citations} />
            )}
            {msg.role === "assistant" && msg.cached && (
              <span className="cached-tag">cached</span>
            )}
          </article>
        ))}
        {sending && (
          <article className="message message-assistant">
            <div className="message-role">DocBot</div>
            <div className="typing">
              <span />
              <span />
              <span />
            </div>
          </article>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <div className="banner error chat-error">{error}</div>}

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder={
            canChat ? "Ask a question about this document…" : "Waiting for document to be ready…"
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!canChat || sending}
        />
        <button type="submit" disabled={!canChat || sending || !input.trim()}>
          Send
        </button>
      </form>
    </main>
  );
}
