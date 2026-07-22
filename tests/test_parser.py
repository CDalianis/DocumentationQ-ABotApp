from pathlib import Path

from app.services.parser import parse_document


def test_parse_docx_preserves_page_metadata(sample_docx: Path):
    docs = parse_document(sample_docx)
    assert len(docs) >= 1
    assert all(d.metadata["page_number"] >= 1 for d in docs)
    assert all(d.metadata["source"] == "manual.docx" for d in docs)
    combined = " ".join(d.text for d in docs)
    assert "warranty period is 2 years" in combined


def test_parse_docx_page_numbers_start_at_one(sample_docx: Path):
    docs = parse_document(sample_docx)
    assert docs[0].metadata["page_number"] == 1
