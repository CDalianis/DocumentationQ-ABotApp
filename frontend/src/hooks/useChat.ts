import { useCallback, useState } from "react";
import { api } from "../api/client";
import type { ChatMessage } from "../types";

export function useChat(documentId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async (question: string) => {
    if (!documentId || !question.trim()) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: question.trim(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setSending(true);
    setError(null);

    try {
      const res = await api.askQuestion(documentId, question.trim());
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.answer,
        citations: res.citations,
        cached: res.cached,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Query failed");
    } finally {
      setSending(false);
    }
  };

  const clear = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, sending, error, send, clear };
}
