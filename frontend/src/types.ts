export interface Document {
  id: string;
  filename: string;
  status: "pending" | "processing" | "ready" | "failed";
  node_count: number | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  page_number: number;
  source: string;
  excerpt: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  cached: boolean;
  document_id: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  cached?: boolean;
}

export interface HealthInfo {
  status: string;
  llm_provider: string;
  embedding_provider: string;
}
