import type { Document, HealthInfo, QueryResponse } from "../types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthInfo>("/health"),

  listDocuments: () => request<Document[]>("/api/v1/documents/"),

  getDocument: (id: string) => request<Document>(`/api/v1/documents/${id}`),

  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ id: string; filename: string; status: string; message: string }>(
      "/api/v1/documents/upload",
      { method: "POST", body: form }
    );
  },

  deleteDocument: (id: string) =>
    request<void>(`/api/v1/documents/${id}`, { method: "DELETE" }),

  askQuestion: (documentId: string, question: string) =>
    request<QueryResponse>(`/api/v1/query/${documentId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
};
