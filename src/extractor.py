"""
Document Text and Heading Extractor for PDF and Word (DOCX) Files.

Provides robust heading extraction for academic papers in PDF and DOCX formats:
- Uses python-docx for Word document paragraph analysis and style inspection.
- Uses pypdf for digital PDF text stream parsing.
- Detects Roman, Arabic, alphabetic, and unnumbered canonical section headings.
- Handles lead-in headers (e.g., 'Abstract---...', 'Index Terms---...').
- Raises UnreadablePDFError for scanned or image-only PDFs with no extractable text.
"""

import io
import os
import re
from typing import List, Union, BinaryIO

import docx
import pypdf

from .rule_engine import RuleMappingEngine


class DocumentExtractionError(Exception):
    """Base exception for document extraction errors."""
    pass


class UnreadablePDFError(DocumentExtractionError):
    """Raised when a PDF is scanned, image-only, or contains no extractable text layer."""
    pass


# Compiled regex patterns for heading detection
ROMAN_HEADING = re.compile(r"^(?:[IVXLCDM]+)[\.\:\-\s]+[A-Za-z]", re.IGNORECASE)
ARABIC_HEADING = re.compile(r"^\d+(?:\.\d+)*[\.\:\-\s]+[A-Za-z]")
ALPHA_HEADING = re.compile(r"^[A-Z]\.[\s]+[A-Za-z]")
STANDARD_KEYWORDS = re.compile(
    r"^(?:Abstract|Index\s+Terms|Keywords|CCS\s+Concepts|Acknowledgment|Acknowledgments|Acknowledgements|References|Bibliography|Works\s+Cited|Appendix|Discussion|Conclusion)",
    re.IGNORECASE
)
CAPTION_FILTER = re.compile(r"^(?:TABLE\s+[IVXLCDM\d]+|Fig(?:ure)?\.?\s+\d+)", re.IGNORECASE)


def _clean_and_filter_heading(text: str, engine: RuleMappingEngine) -> Union[str, None]:
    """
    Evaluates whether a candidate text line is a valid academic heading.
    Returns cleaned heading string if valid, otherwise None.
    """
    line = text.strip()
    if not line:
        return None

    # Filter out table or figure captions
    if CAPTION_FILTER.match(line):
        return None

    # Handle lead-in headings like 'Abstract---...' or 'Index Terms---...' or 'Abstract—...'
    if line.startswith("Abstract") or line.startswith("ABSTRACT") or "Index Terms" in line[:15] or "Keywords" in line[:12]:
        if "---" in line or "—" in line or "--" in line:
            parts = re.split(r"[\—\-\-]{1,3}", line, maxsplit=1)
            lead = parts[0].strip()
            if lead:
                # Include the marker so that Index Terms or Abstract are properly identified
                return f"{lead}---" if "---" in line or "—" in line else lead
        elif len(line) <= 100:
            return line

    # Check numbered patterns (Roman, Arabic, Alpha)
    if ROMAN_HEADING.match(line) and len(line) <= 120:
        return line
    if ARABIC_HEADING.match(line) and len(line) <= 120:
        return line
    if ALPHA_HEADING.match(line) and len(line) <= 120:
        return line

    # Check unnumbered standard section names
    if STANDARD_KEYWORDS.match(line) and len(line) <= 80:
        # Check if line does not end like a standard sentence
        if not line.endswith((".", ",", ";")):
            return line

    # Check if short standalone line matches canonical rule engine
    if len(line) <= 60 and not line.endswith((".", ",", ";")):
        mapped = engine.map_heading(line)
        if mapped["canonical_section"] != "UNKNOWN" and mapped["confidence"] >= 0.90:
            return line

    return None


def extract_headings_from_docx(file_source: Union[str, bytes, BinaryIO]) -> List[str]:
    """
    Extracts section headings from a Word (.docx) document.
    
    Args:
        file_source: File path string, raw bytes, or file-like binary stream.
        
    Returns:
        List of extracted section heading strings.
    """
    if isinstance(file_source, bytes):
        file_source = io.BytesIO(file_source)

    try:
        doc = docx.Document(file_source)
    except Exception as e:
        raise DocumentExtractionError(f"Failed to parse Word (.docx) document: {e}")

    engine = RuleMappingEngine()
    headings: List[str] = []

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style_name = (p.style.name or "").lower()
        is_heading_style = any(h in style_name for h in ["heading", "title"])

        # If explicitly formatted with a Word Heading style
        if is_heading_style and len(text) <= 120 and not CAPTION_FILTER.match(text):
            if text not in headings:
                headings.append(text)
            continue

        # Check candidate patterns
        candidate = _clean_and_filter_heading(text, engine)
        if candidate and candidate not in headings:
            headings.append(candidate)

    return headings


def extract_headings_from_pdf(file_source: Union[str, bytes, BinaryIO]) -> List[str]:
    """
    Extracts section headings from a PDF document.
    
    Args:
        file_source: File path string, raw bytes, or file-like binary stream.
        
    Returns:
        List of extracted section heading strings.
        
    Raises:
        UnreadablePDFError: If the PDF contains no extractable text (e.g., scanned/image-only).
        DocumentExtractionError: If the PDF file is corrupted or cannot be read.
    """
    if isinstance(file_source, bytes):
        file_source = io.BytesIO(file_source)

    try:
        reader = pypdf.PdfReader(file_source)
    except Exception as e:
        raise DocumentExtractionError(f"Failed to parse PDF document: {e}")

    if not reader.pages:
        raise UnreadablePDFError("The uploaded PDF has no pages.")

    total_text = []
    for page_idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            total_text.append(page_text)
        except Exception:
            continue

    full_content = "\n".join(total_text)
    
    # Check if text is virtually empty (scanned or image-only PDF)
    non_ws_chars = len(re.sub(r"\s+", "", full_content))
    if non_ws_chars < 30:
        raise UnreadablePDFError(
            "The uploaded PDF appears to be a scanned document or image-only file with no extractable text. "
            "Please upload a searchable text PDF or a Word (.docx) / JSON / TXT file."
        )

    engine = RuleMappingEngine()
    headings: List[str] = []

    for raw_line in full_content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        candidate = _clean_and_filter_heading(line, engine)
        if candidate:
            # Prevent adjacent duplicate running headers
            if not headings or headings[-1] != candidate:
                headings.append(candidate)

    return headings


def extract_headings_from_file(file_source: Union[str, bytes, BinaryIO], filename: str) -> List[str]:
    """
    Universal dispatcher that extracts headings from PDF, DOCX, TXT, or JSON.
    """
    fn = filename.lower()
    if fn.endswith(".docx"):
        return extract_headings_from_docx(file_source)
    elif fn.endswith(".pdf"):
        return extract_headings_from_pdf(file_source)
    elif fn.endswith(".json"):
        import json
        if isinstance(file_source, (bytes, io.BytesIO)):
            content = file_source.read() if hasattr(file_source, "read") else file_source
            data = json.loads(content.decode("utf-8") if isinstance(content, bytes) else content)
        else:
            with open(file_source, "r", encoding="utf-8") as f:
                data = json.load(f)
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                return [d.get("heading") or d.get("raw_heading") for d in data if d.get("heading") or d.get("raw_heading")]
            return [str(x) for x in data]
        elif isinstance(data, dict) and "headings" in data:
            return data["headings"]
        else:
            raise DocumentExtractionError("JSON must contain a list of headings or a dict with 'headings' key.")
    else:
        # Default text format
        if hasattr(file_source, "read"):
            content = file_source.read()
            text_str = content.decode("utf-8") if isinstance(content, bytes) else str(content)
        elif isinstance(file_source, bytes):
            text_str = file_source.decode("utf-8")
        else:
            with open(file_source, "r", encoding="utf-8") as f:
                text_str = f.read()
        return [l.strip() for l in text_str.splitlines() if l.strip() and not l.strip().startswith("#")]
