"""
File handler — extracts text from PDF and TXT files with size limits.
"""
from __future__ import annotations

import io

# Maximum characters extracted from any single document
MAX_CHARS = 12_000


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from an uploaded file.

    Supports:
      - .pdf  (via PyMuPDF / fitz)
      - .txt  (direct decode)

    Parameters
    ----------
    file_bytes : bytes
        Raw file content.
    filename : str
        Original filename (used to determine file type).

    Returns
    -------
    str
        Extracted text, truncated to MAX_CHARS.

    Raises
    ------
    ValueError
        If the file type is not supported.
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "txt":
        text = file_bytes.decode("utf-8", errors="replace")
    elif ext == "pdf":
        text = _extract_pdf(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type '.{ext}'. Please upload a PDF or TXT file."
        )

    return text[:MAX_CHARS]


def _extract_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        pages = [page.get_text() for page in doc]
        return "\n".join(pages)
    except ImportError as exc:
        raise ImportError(
            "PyMuPDF is required for PDF extraction. "
            "Install it with: pip install PyMuPDF"
        ) from exc
