import type { Document } from "../types";
import { statusBadge, UploadZone } from "./UploadZone";

interface Props {
  documents: Document[];
  selectedId: string | null;
  loading: boolean;
  uploading: boolean;
  error: string | null;
  onSelect: (id: string) => void;
  onUpload: (file: File) => Promise<string>;
  onDelete: (id: string) => void;
}

export function DocumentSidebar({
  documents,
  selectedId,
  loading,
  uploading,
  error,
  onSelect,
  onUpload,
  onDelete,
}: Props) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>DocBot</h1>
        <p>Context-aware Q&A with citations</p>
      </div>

      <UploadZone onUpload={onUpload} uploading={uploading} />

      {error && <div className="banner error">{error}</div>}

      <div className="doc-list-header">
        <span>Documents</span>
        <span className="count">{documents.length}</span>
      </div>

      <ul className="doc-list">
        {loading && documents.length === 0 && (
          <li className="doc-item muted">Loading…</li>
        )}
        {!loading && documents.length === 0 && (
          <li className="doc-item muted">No documents yet</li>
        )}
        {documents.map((doc) => (
          <li key={doc.id}>
            <button
              type="button"
              className={`doc-item ${selectedId === doc.id ? "active" : ""}`}
              onClick={() => onSelect(doc.id)}
            >
              <span className="doc-name" title={doc.filename}>
                {doc.filename}
              </span>
              <span className="doc-meta">
                {statusBadge(doc.status)}
                {doc.node_count != null && (
                  <span className="node-count">{doc.node_count} chunks</span>
                )}
              </span>
            </button>
            <button
              type="button"
              className="doc-delete"
              title="Delete document"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(doc.id);
              }}
            >
              ×
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
