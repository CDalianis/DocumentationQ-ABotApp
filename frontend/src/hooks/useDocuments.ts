import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";
import type { Document } from "../types";

const POLL_MS = 2500;

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const hasPending = documents.some(
      (d) => d.status === "pending" || d.status === "processing"
    );
    if (!hasPending) return;
    const timer = setInterval(refresh, POLL_MS);
    return () => clearInterval(timer);
  }, [documents, refresh]);

  const upload = async (file: File) => {
    const result = await api.uploadDocument(file);
    await refresh();
    return result.id;
  };

  const remove = async (id: string) => {
    await api.deleteDocument(id);
    await refresh();
  };

  return { documents, loading, error, refresh, upload, remove };
}
