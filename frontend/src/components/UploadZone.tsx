import type { Document } from "../types";

interface Props {
  onUpload: (file: File) => Promise<string>;
  uploading: boolean;
}

export function UploadZone({ onUpload, uploading }: Props) {
  const handleFiles = async (files: FileList | null) => {
    if (!files?.length || uploading) return;
    await onUpload(files[0]);
  };

  return (
    <label className={`upload-zone ${uploading ? "uploading" : ""}`}>
      <input
        type="file"
        accept=".pdf,.doc,.docx"
        disabled={uploading}
        onChange={(e) => {
          handleFiles(e.target.files);
          e.target.value = "";
        }}
      />
      <span className="upload-icon">↑</span>
      <span className="upload-label">
        {uploading ? "Uploading…" : "Drop PDF or Word doc"}
      </span>
      <span className="upload-hint">.pdf · .docx · max 50 MB</span>
    </label>
  );
}

export function statusBadge(status: Document["status"]) {
  const labels: Record<Document["status"], string> = {
    pending: "Queued",
    processing: "Indexing",
    ready: "Ready",
    failed: "Failed",
  };
  return <span className={`badge badge-${status}`}>{labels[status]}</span>;
}
