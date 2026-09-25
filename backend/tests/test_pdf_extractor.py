import fitz
import pytest
from app.services.pdf_extractor import (
    extract_text_from_pdf,
    clean_extracted_text,
    PDFExtractionError
)

def create_in_memory_pdf(text_content: str) -> bytes:
    """Helper to generate a valid PDF in memory with PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), text_content)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_clean_extracted_text():
    """Test whitespace reduction, tab replacement, and newline collapsing."""
    raw = "   John   Doe   \n\n\n\n   Software    Engineer   \t\twith   Python   \n\n\n"
    cleaned = clean_extracted_text(raw)
    assert "John Doe" in cleaned
    assert "Software Engineer with Python" in cleaned
    assert "\n\n\n" not in cleaned

def test_extract_text_from_valid_pdf():
    """Test extracting text from a genuine multi-line PDF document."""
    sample_text = (
        "Alice Smith\n"
        "Full Stack Developer\n"
        "Proficient in Python, React, TypeScript, and PostgreSQL.\n"
        "Built cloud applications deployed with Docker and Kubernetes on AWS."
    )
    pdf_bytes = create_in_memory_pdf(sample_text)
    result = extract_text_from_pdf(pdf_bytes)

    assert result["page_count"] == 1
    assert "Alice Smith" in result["text"]
    assert "Python" in result["text"]
    assert "React" in result["text"]
    assert result["char_count"] > 50

def test_invalid_pdf_bytes_rejected():
    """Test that non-PDF content triggers a PDFExtractionError."""
    fake_content = b"This is just plain text, not a PDF header."
    with pytest.raises(PDFExtractionError) as exc_info:
        extract_text_from_pdf(fake_content)
    assert "not a valid PDF" in str(exc_info.value)

def test_empty_or_too_short_pdf_rejected():
    """Test that a blank PDF triggers an informative extraction error."""
    blank_pdf = create_in_memory_pdf("   ")
    with pytest.raises(PDFExtractionError) as exc_info:
        extract_text_from_pdf(blank_pdf)
    assert "readable text" in str(exc_info.value)
