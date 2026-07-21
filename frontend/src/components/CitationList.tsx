import type { Citation } from "../types";

export function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  return (
    <div className="citations">
      <span className="citations-label">Sources</span>
      <ul>
        {citations.map((c, i) => (
          <li key={`${c.page_number}-${i}`}>
            <span className="cite-page">Page {c.page_number}</span>
            <span className="cite-source">{c.source}</span>
            <p className="cite-excerpt">{c.excerpt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
