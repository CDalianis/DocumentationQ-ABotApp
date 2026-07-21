import { useEffect, useState } from "react";
import { api } from "./api/client";
import { ChatPanel } from "./components/ChatPanel";
import { DocumentSidebar } from "./components/DocumentSidebar";
import { useChat } from "./hooks/useChat";
import { useDocuments } from "./hooks/useDocuments";
import type { HealthInfo } from "./types";

export default function App() {
  const { documents, loading, error, upload, remove } = useDocuments();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const { messages, sending, error: chatError, send, clear } = useChat(selectedId);

  const selected = documents.find((d) => d.id === selectedId) ?? null;

  useEffect(() => {
    api.health().then(setHealth).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedId && documents.length > 0) {
      const ready = documents.find((d) => d.status === "ready");
      setSelectedId(ready?.id ?? documents[0].id);
    }
  }, [documents, selectedId]);

  useEffect(() => {
    clear();
  }, [selectedId, clear]);

  const handleUpload = async (file: File): Promise<string> => {
    setUploading(true);
    try {
      const id = await upload(file);
      setSelectedId(id);
      return id;
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    await remove(id);
    if (selectedId === id) setSelectedId(null);
  };

  return (
    <div className="app">
      <DocumentSidebar
        documents={documents}
        selectedId={selectedId}
        loading={loading}
        uploading={uploading}
        error={error}
        onSelect={setSelectedId}
        onUpload={handleUpload}
        onDelete={handleDelete}
      />
      <ChatPanel
        document={selected}
        messages={messages}
        sending={sending}
        error={chatError}
        onSend={send}
        onClear={clear}
      />
      {health && (
        <footer className="status-bar">
          LLM: <code>{health.llm_provider}</code> · Embeddings:{" "}
          <code>{health.embedding_provider}</code>
        </footer>
      )}
    </div>
  );
}
