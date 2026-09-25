import io
import re
import fitz  # PyMuPDF

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class PDFExtractionError(Exception):
    """Custom exception raised when PDF extraction fails or text is unreadable."""
    pass

def clean_extracted_text(raw_text: str) -> str:
    """
    Cleans raw PDF text by:
    - Normalizing unicode whitespace & quotes
    - Replacing tabs and repeated spaces with a single space
    - Preserving useful section layout while eliminating excess empty lines
    - Trimming trailing/leading whitespace
    """
    if not raw_text:
        return ""

    # Replace common unicode artifacts
    cleaned = raw_text.replace("\xa0", " ").replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    cleaned = cleaned.replace("–", "-").replace("—", "-").replace("•", " ")

    # Process line by line to strip excessive whitespace
    lines = []
    for line in cleaned.split("\n"):
        stripped = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(stripped)

    # Rejoin lines
    joined = "\n".join(lines)

    # Collapse more than 2 consecutive newlines into 2
    joined = re.sub(r"\n{3,}", "\n\n", joined)

    return joined.strip()

def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extracts text from PDF bytes using PyMuPDF (fitz).
    Returns a dict with:
      - 'text': cleaned full text
      - 'page_count': total pages
      - 'char_count': total characters
      - 'preview': first 400 characters preview
    """
    if len(pdf_bytes) > MAX_FILE_SIZE_BYTES:
        raise PDFExtractionError(
            f"File size exceeds the 10 MB limit (got {len(pdf_bytes) / (1024 * 1024):.1f} MB)."
        )

    # Validate PDF magic header
    if not pdf_bytes.startswith(b"%PDF-"):
        raise PDFExtractionError("Invalid file format. The uploaded file is not a valid PDF.")

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as e:
        raise PDFExtractionError(f"Failed to open PDF document: {str(e)}")

    page_count = len(doc)
    if page_count == 0:
        doc.close()
        raise PDFExtractionError("The uploaded PDF has no pages.")

    pages_text = []
    for page_num in range(page_count):
        try:
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                pages_text.append(page_text)
        except Exception as e:
            # Continue reading other pages if one fails
            continue

    doc.close()

    raw_combined = "\n\n".join(pages_text)
    cleaned_text = clean_extracted_text(raw_combined)

    # If the PDF is scanned or contains only images/vector art with no text layer
    if len(cleaned_text.strip()) < 30:
        raise PDFExtractionError(
            "We couldn't extract readable text from this PDF. Please upload a text-based PDF resume."
        )

    return {
        "text": cleaned_text,
        "page_count": page_count,
        "char_count": len(cleaned_text),
        "preview": cleaned_text[:400] + ("..." if len(cleaned_text) > 400 else "")
    }
