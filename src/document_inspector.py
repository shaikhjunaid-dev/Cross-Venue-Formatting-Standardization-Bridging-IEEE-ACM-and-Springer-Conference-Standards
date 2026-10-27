"""
Comprehensive Document Element Inspector.

Inspects academic manuscripts (DOCX, PDF, or structured headings/text) across all
supported publication dimensions:
- Title and author information
- Abstract structure and word count
- Keywords, Index Terms, and ACM CCS Concepts
- Section headings, hierarchy, numbering styles, and casing
- Tables and figures (captions, labels, numbering)
- In-text citations and reference list formatting
- Acknowledgments and funding disclosures
- Page layout, columns, margins, and typography
"""

import io
import re
from typing import Dict, List, Any, Optional, Union, BinaryIO

import docx
from docx.shared import Inches, Pt

from .rule_engine import RuleMappingEngine
from .normalizer import normalize_heading
from .schema import CanonicalSection
from .venue_specs import VENUE_SPECIFICATIONS


# Helper Regex Patterns
CITATION_NUMERIC = re.compile(r"\[\s*\d+(?:\s*[\,\-–]\s*\d+)*\s*\]")
CITATION_AUTHOR_YEAR = re.compile(r"\((?:[A-Z][a-zA-Z\s]+(?:\s+et\s+al\.)?\,\s*(?:19|20)\d{2}[a-z]?)\)")
TABLE_CAPTION_PATTERN = re.compile(r"^(TABLE|Table)\s+([IVXLCDM\d]+)[\.\:\-\s]*(.*)", re.IGNORECASE)
FIGURE_CAPTION_PATTERN = re.compile(r"^(Fig(?:ure)?\.?)\s*(\d+)[\.\:\-\s]*(.*)", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
ORCID_PATTERN = re.compile(r"\b0000-000[1-3]-\d{4}-\d{3}[\dX]\b")


def detect_casing(text: str) -> str:
    """Detects text casing convention."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "UNKNOWN"
    if all(c.isupper() for c in letters):
        return "ALL_CAPS"
    words = text.strip().split()
    if all(w[0].isupper() for w in words if w and w[0].isalpha()):
        return "TITLE_CASE"
    return "MIXED"


class DocumentInspector:
    """Inspects all detectable structural elements of a research paper."""

    def __init__(self, target_venue: str = "ACM"):
        self.target_venue = target_venue.upper()
        self.target_spec = VENUE_SPECIFICATIONS.get(self.target_venue, VENUE_SPECIFICATIONS["ACM"])
        self.engine = RuleMappingEngine()

    def inspect_docx(self, docx_source: Union[str, bytes, BinaryIO, docx.Document]) -> Dict[str, Any]:
        """Deep inspection of a Word (.docx) document."""
        if hasattr(docx_source, "paragraphs") and hasattr(docx_source, "sections"):
            doc = docx_source
        elif isinstance(docx_source, bytes):
            doc = docx.Document(io.BytesIO(docx_source))
        elif hasattr(docx_source, "read"):
            doc = docx.Document(docx_source)
        else:
            doc = docx.Document(docx_source)

        report: Dict[str, Any] = {
            "source_type": "DOCX",
            "title": self._inspect_title(doc),
            "authors": self._inspect_authors(doc),
            "abstract": self._inspect_abstract(doc),
            "keywords": self._inspect_keywords(doc),
            "ccs_concepts": self._inspect_ccs_concepts(doc),
            "headings": self._inspect_headings_docx(doc),
            "tables": self._inspect_tables(doc),
            "figures": self._inspect_figures(doc),
            "citations": self._inspect_citations(doc),
            "references": self._inspect_references(doc),
            "acknowledgments": self._inspect_acknowledgments(doc),
            "layout": self._inspect_layout(doc)
        }
        return report

    def inspect_from_headings_and_text(self, headings: List[str], full_text: Optional[str] = None) -> Dict[str, Any]:
        """Inspects when only extracted headings (or plain text) are available."""
        full_text = full_text or "\n".join(headings)
        report: Dict[str, Any] = {
            "source_type": "HEADINGS_LIST",
            "title": {"text": headings[0] if headings and not any(k in headings[0].lower() for k in ["abstract", "intro"]) else "Untitled Document", "casing": "UNKNOWN"},
            "authors": {"author_count": 0, "has_emails": bool(EMAIL_PATTERN.search(full_text)), "has_orcid": bool(ORCID_PATTERN.search(full_text))},
            "abstract": self._inspect_abstract_text(full_text),
            "keywords": self._inspect_keywords_text(full_text, headings),
            "ccs_concepts": {"present": "ccs concepts" in full_text.lower() or "computing classification" in full_text.lower(), "text": ""},
            "headings": self._inspect_headings_list(headings),
            "tables": self._inspect_tables_text(full_text),
            "figures": self._inspect_figures_text(full_text),
            "citations": self._inspect_citations_text(full_text),
            "references": self._inspect_references_text(full_text, headings),
            "acknowledgments": self._inspect_acknowledgments_text(headings),
            "layout": {"columns": 2 if any(h.startswith("I.") for h in headings) else 1, "is_estimated": True}
        }
        return report

    # -------------------------------------------------------------------------
    # Internal DOCX Inspection Helpers
    # -------------------------------------------------------------------------

    def _inspect_title(self, doc: docx.Document) -> Dict[str, Any]:
        """Detects paper title, font size, bold, alignment, and casing."""
        for p in doc.paragraphs[:5]:
            text = p.text.strip()
            if not text:
                continue
            is_title_style = "title" in (p.style.name or "").lower()
            runs = [r for r in p.runs if r.text.strip()]
            font_size = runs[0].font.size.pt if runs and runs[0].font.size else None
            is_bold = any(r.bold for r in runs)
            if is_title_style or (font_size and font_size >= 14) or is_bold and len(text) > 15:
                # Exclude if it's 'Abstract' or 'Introduction'
                if not any(k in text.lower() for k in ["abstract", "introduction", "author"]):
                    return {
                        "text": text,
                        "font_size_pt": font_size,
                        "bold": is_bold,
                        "casing": detect_casing(text),
                        "alignment": str(p.alignment)
                    }
        return {"text": "", "font_size_pt": None, "bold": False, "casing": "UNKNOWN", "alignment": "UNKNOWN"}

    def _inspect_authors(self, doc: docx.Document) -> Dict[str, Any]:
        """Detects author information, emails, and ORCID."""
        text_chunk = "\n".join(p.text for p in doc.paragraphs[:12])
        emails = EMAIL_PATTERN.findall(text_chunk)
        orcids = ORCID_PATTERN.findall(text_chunk)
        return {
            "has_emails": len(emails) > 0,
            "emails_found": emails,
            "has_orcid": len(orcids) > 0,
            "orcids_found": orcids,
            "author_block_detected": len(emails) > 0 or "department" in text_chunk.lower() or "university" in text_chunk.lower()
        }

    def _inspect_abstract(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects abstract paragraph, lead-in, and word count."""
        for p in doc.paragraphs[:15]:
            text = p.text.strip()
            if text.lower().startswith("abstract") or "abstract---" in text.lower() or "abstract—" in text.lower() or "abstract." in text.lower():
                words = text.split()
                # Check lead-in
                lead_in = "Abstract"
                if "---" in text[:15] or "—" in text[:15]:
                    lead_in = "Abstract---"
                elif text.startswith("ABSTRACT"):
                    lead_in = "ABSTRACT"
                elif text.startswith("Abstract."):
                    lead_in = "Abstract."
                return {
                    "present": True,
                    "lead_in": lead_in,
                    "word_count": len(words),
                    "full_text": text[:300] + "..." if len(text) > 300 else text,
                    "is_bold_lead": any(r.bold for r in p.runs[:2]) if p.runs else False,
                    "is_italic_lead": any(r.italic for r in p.runs[:2]) if p.runs else False
                }
        return {"present": False, "lead_in": "", "word_count": 0, "full_text": ""}

    def _inspect_keywords(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects keywords / Index Terms."""
        for p in doc.paragraphs[:18]:
            text = p.text.strip()
            low = text.lower()
            if low.startswith("index terms") or low.startswith("keywords") or low.startswith("key words"):
                # Determine label
                label = "Keywords"
                if "index terms" in low:
                    label = "Index Terms---" if ("---" in text or "—" in text) else "Index Terms"
                elif "keywords:" in low:
                    label = "Keywords:"
                
                # Extract terms
                clean_terms = re.sub(r"^(?:index\s+terms|keywords)[\-\—\:\s]*", "", text, flags=re.IGNORECASE)
                terms = [t.strip() for t in re.split(r"[\,\;·]", clean_terms) if t.strip()]
                is_alphabetical = (terms == sorted(terms, key=lambda s: s.lower())) if len(terms) > 1 else True
                return {
                    "present": True,
                    "label": label,
                    "terms": terms,
                    "term_count": len(terms),
                    "is_alphabetical": is_alphabetical,
                    "raw_text": text
                }
        return {"present": False, "label": "", "terms": [], "term_count": 0, "is_alphabetical": False, "raw_text": ""}

    def _inspect_ccs_concepts(self, doc: docx.Document) -> Dict[str, Any]:
        """Checks for ACM CCS Concepts block."""
        full_text = "\n".join(p.text for p in doc.paragraphs[:25])
        low = full_text.lower()
        present = "ccs concepts" in low or "computing classification system" in low or "<ccs2012>" in low
        return {"present": present, "details": "Found in frontmatter" if present else "Missing"}

    def _inspect_headings_docx(self, doc: docx.Document) -> List[Dict[str, Any]]:
        """Extracts and evaluates all headings in the DOCX."""
        headings = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            # Use normalizer
            norm = normalize_heading(text)
            cleaned = norm["cleaned"]
            is_heading_style = "heading" in (p.style.name or "").lower()
            
            # Check if it matches heading patterns
            is_pattern_heading = (
                norm["numbering_type"] != "NONE" or 
                any(text.lower().startswith(k) for k in ["abstract", "index terms", "keywords", "acknowledgment", "acknowledgements", "references", "bibliography", "appendix"]) or
                (len(text) <= 60 and not text.endswith((".", ",", ";")) and is_heading_style)
            )
            
            if is_pattern_heading and not TABLE_CAPTION_PATTERN.match(text) and not FIGURE_CAPTION_PATTERN.match(text):
                heading_info = self._analyze_single_heading(text, norm)
                headings.append(heading_info)
        return headings

    def _inspect_tables(self, doc: docx.Document) -> List[Dict[str, Any]]:
        """Inspects table captions and numbering."""
        tables_found = []
        for p in doc.paragraphs:
            text = p.text.strip()
            m = TABLE_CAPTION_PATTERN.match(text)
            if m:
                label_prefix = m.group(1)
                num = m.group(2)
                is_roman = bool(re.match(r"^[IVXLCDM]+$", num, re.IGNORECASE))
                tables_found.append({
                    "raw_caption": text,
                    "label_prefix": label_prefix,
                    "number_str": num,
                    "numbering_style": "ROMAN" if is_roman else "ARABIC",
                    "casing": detect_casing(text)
                })
        return tables_found

    def _inspect_figures(self, doc: docx.Document) -> List[Dict[str, Any]]:
        """Inspects figure captions and numbering."""
        figures_found = []
        for p in doc.paragraphs:
            text = p.text.strip()
            m = FIGURE_CAPTION_PATTERN.match(text)
            if m:
                label_prefix = m.group(1)
                num = m.group(2)
                figures_found.append({
                    "raw_caption": text,
                    "label_prefix": label_prefix,
                    "number_str": num,
                    "casing": detect_casing(text)
                })
        return figures_found

    def _inspect_citations(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects in-text citations."""
        full_text = "\n".join(p.text for p in doc.paragraphs)
        numeric = CITATION_NUMERIC.findall(full_text)
        author_year = CITATION_AUTHOR_YEAR.findall(full_text)
        return {
            "style": "NUMERIC_SQUARE_BRACKETS" if len(numeric) >= len(author_year) else "AUTHOR_YEAR",
            "numeric_citations_count": len(numeric),
            "author_year_citations_count": len(author_year),
            "samples": (numeric[:3] if numeric else author_year[:3])
        }

    def _inspect_references(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects reference list heading and formatting."""
        for p in doc.paragraphs[-35:]:
            text = p.text.strip()
            if text.lower() in ["references", "bibliography", "works cited"]:
                return {
                    "present": True,
                    "raw_heading": text,
                    "casing": detect_casing(text)
                }
        return {"present": False, "raw_heading": "", "casing": "UNKNOWN"}

    def _inspect_acknowledgments(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects acknowledgment heading for singular vs plural."""
        for p in doc.paragraphs:
            text = p.text.strip()
            norm = normalize_heading(text)
            if norm["cleaned"] in ["acknowledgment", "acknowledgments", "acknowledgements"]:
                return {
                    "present": True,
                    "raw_heading": text,
                    "is_singular": "acknowledgment" == text.lower().strip(".:- "),
                    "is_plural": "acknowledgments" in text.lower() or "acknowledgements" in text.lower(),
                    "casing": detect_casing(text)
                }
        return {"present": False, "raw_heading": "", "is_singular": False, "is_plural": False, "casing": "UNKNOWN"}

    def _inspect_layout(self, doc: docx.Document) -> Dict[str, Any]:
        """Inspects DOCX page layout, margins, and column settings."""
        if not doc.sections:
            return {"columns": 1, "margins": {}}
        sec = doc.sections[0]
        # Inspect columns XML
        cols_val = 1
        cols_elem = sec._sectPr.xpath('./w:cols')
        if cols_elem and cols_elem[0].get(docx.oxml.ns.qn('w:num')):
            cols_val = int(cols_elem[0].get(docx.oxml.ns.qn('w:num')))
        
        # Check second section if present (often body is section 2)
        if len(doc.sections) > 1:
            sec2 = doc.sections[1]
            cols_elem2 = sec2._sectPr.xpath('./w:cols')
            if cols_elem2 and cols_elem2[0].get(docx.oxml.ns.qn('w:num')):
                cols_val = int(cols_elem2[0].get(docx.oxml.ns.qn('w:num')))

        return {
            "columns": cols_val,
            "margin_top_in": round(sec.top_margin.inches, 3) if sec.top_margin else 1.0,
            "margin_bottom_in": round(sec.bottom_margin.inches, 3) if sec.bottom_margin else 1.0,
            "margin_left_in": round(sec.left_margin.inches, 3) if sec.left_margin else 1.0,
            "margin_right_in": round(sec.right_margin.inches, 3) if sec.right_margin else 1.0,
            "primary_font": "Times New Roman"
        }

    # -------------------------------------------------------------------------
    # Text-Based Inspection Fallbacks
    # -------------------------------------------------------------------------

    def _inspect_abstract_text(self, text: str) -> Dict[str, Any]:
        for line in text.splitlines():
            low = line.lower().strip()
            if low.startswith("abstract"):
                return {"present": True, "lead_in": line[:20], "word_count": len(line.split())}
        return {"present": False, "lead_in": "", "word_count": 0}

    def _inspect_keywords_text(self, text: str, headings: List[str]) -> Dict[str, Any]:
        for line in text.splitlines():
            low = line.lower().strip()
            if low.startswith("index terms") or low.startswith("keywords"):
                label = "Index Terms---" if "index terms" in low else "Keywords"
                return {"present": True, "label": label, "raw_text": line}
        return {"present": False, "label": "", "raw_text": ""}

    def _inspect_headings_list(self, headings: List[str]) -> List[Dict[str, Any]]:
        return [self._analyze_single_heading(h, normalize_heading(h)) for h in headings]

    def _inspect_tables_text(self, text: str) -> List[Dict[str, Any]]:
        matches = TABLE_CAPTION_PATTERN.findall(text)
        return [{"raw_caption": m[0] + " " + m[1], "numbering_style": "ROMAN" if re.match(r"^[IVXLCDM]+$", m[1]) else "ARABIC"} for m in matches]

    def _inspect_figures_text(self, text: str) -> List[Dict[str, Any]]:
        matches = FIGURE_CAPTION_PATTERN.findall(text)
        return [{"raw_caption": m[0] + " " + m[1], "label_prefix": m[0]} for m in matches]

    def _inspect_citations_text(self, text: str) -> Dict[str, Any]:
        numeric = CITATION_NUMERIC.findall(text)
        return {"style": "NUMERIC_SQUARE_BRACKETS" if numeric else "UNKNOWN", "numeric_citations_count": len(numeric)}

    def _inspect_references_text(self, text: str, headings: List[str]) -> Dict[str, Any]:
        for h in headings:
            if h.lower().strip(".:- ") in ["references", "bibliography", "works cited"]:
                return {"present": True, "raw_heading": h, "casing": detect_casing(h)}
        return {"present": False, "raw_heading": "", "casing": "UNKNOWN"}

    def _inspect_acknowledgments_text(self, headings: List[str]) -> Dict[str, Any]:
        for h in headings:
            clean = h.lower().strip(".:- ")
            if clean in ["acknowledgment", "acknowledgments", "acknowledgements"]:
                return {
                    "present": True,
                    "raw_heading": h,
                    "is_singular": clean == "acknowledgment",
                    "is_plural": "acknowledgments" in clean or "acknowledgements" in clean
                }
        return {"present": False, "raw_heading": "", "is_singular": False, "is_plural": False}

    # -------------------------------------------------------------------------
    # Core Heading Analyzer with Context & Recommendations
    # -------------------------------------------------------------------------

    def _analyze_single_heading(self, raw_heading: str, norm: Dict[str, Any]) -> Dict[str, Any]:
        """Maps heading and computes target format and reasoning."""
        mapped = self.engine.map_heading(raw_heading)
        canonical = mapped["canonical_section"]
        casing = detect_casing(norm["cleaned"])
        num_type = norm["numbering_type"]
        level = norm["level"]

        # Compute recommended target heading format
        rec_heading, rec_reason = self._compute_target_heading(raw_heading, canonical, level, num_type, norm["cleaned"])

        return {
            "raw_heading": raw_heading,
            "cleaned_heading": norm["cleaned"],
            "level": level,
            "numbering_type": num_type,
            "casing": casing,
            "canonical_section": canonical,
            "secondary_section": mapped["secondary_section"],
            "confidence": mapped["confidence"],
            "is_ambiguous": mapped["is_ambiguous"],
            "is_compound": mapped["is_compound"],
            "explanation": mapped["explanation"],
            "recommended_heading": rec_heading,
            "recommendation_reason": rec_reason
        }

    def _compute_target_heading(self, raw: str, canonical: str, level: int, num_type: str, cleaned: str) -> (str, str):
        """Calculates exact target heading recommendation according to target venue."""
        target_v = self.target_venue
        title_core = cleaned.title()

        # Special Sections Handling
        if canonical == CanonicalSection.ABSTRACT.value:
            if target_v == "IEEE":
                return "Abstract---", "IEEE style requires 'Abstract---' in bold italic."
            elif target_v == "ACM":
                return "ABSTRACT", "ACM sigconf style uses uppercase bold 'ABSTRACT'."
            else:
                return "Abstract.", "Springer LNCS style uses 'Abstract.' with bold run-in dot."

        if canonical == CanonicalSection.KEYWORDS.value:
            if target_v == "IEEE":
                return "Index Terms---", "IEEE style requires 'Index Terms---' in bold italic."
            elif target_v == "ACM":
                return "Keywords", "ACM style labels this section 'Keywords' (comma separated)."
            else:
                return "Keywords:", "Springer LNCS style uses 'Keywords:' in bold."

        if canonical == CanonicalSection.ACKNOWLEDGMENTS.value:
            if target_v == "IEEE":
                return "ACKNOWLEDGMENT", "IEEE style strictly requires the singular form 'ACKNOWLEDGMENT'."
            elif target_v == "ACM":
                return "ACKNOWLEDGMENTS", "ACM style requires the plural form 'ACKNOWLEDGMENTS'."
            else:
                return "Acknowledgements", "Springer LNCS standard accepts 'Acknowledgements'."

        if canonical == CanonicalSection.REFERENCES.value:
            if target_v in ["IEEE", "ACM"]:
                return "REFERENCES", f"{target_v} requires unnumbered uppercase 'REFERENCES'."
            else:
                return "References", "Springer LNCS requires unnumbered title case 'References'."

        # Level 1 Main Sections
        if level == 1:
            if target_v == "IEEE":
                # Convert to Roman uppercase
                roman_prefix = "I." # Default fallback
                if num_type == "ARABIC_SINGLE":
                    digits = re.findall(r"^\d+", raw.strip())
                    if digits:
                        num = int(digits[0])
                        roman_map = ["I.", "II.", "III.", "IV.", "V.", "VI.", "VII.", "VIII.", "IX.", "X."]
                        roman_prefix = roman_map[num - 1] if 1 <= num <= len(roman_map) else f"{num}."
                return f"{roman_prefix} {cleaned.upper()}", "IEEE Level 1 headings must use Roman numerals and uppercase."
            
            elif target_v == "ACM":
                # Convert to Arabic uppercase
                arabic_prefix = "1"
                if num_type == "ROMAN":
                    roman_str = re.findall(r"^[IVXLCDM]+", raw.strip(), re.IGNORECASE)
                    if roman_str:
                        roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
                        num = roman_to_int.get(roman_str[0].upper(), 1)
                        arabic_prefix = str(num)
                elif num_type == "ARABIC_SINGLE":
                    digits = re.findall(r"^\d+", raw.strip())
                    arabic_prefix = digits[0] if digits else "1"
                return f"{arabic_prefix} {cleaned.upper()}", "ACM Level 1 headings must use Arabic numerals without dot and uppercase."

            elif target_v == "SPRINGER":
                # Convert to Arabic Title Case
                arabic_prefix = "1"
                if num_type == "ROMAN":
                    roman_str = re.findall(r"^[IVXLCDM]+", raw.strip(), re.IGNORECASE)
                    if roman_str:
                        roman_to_int = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10}
                        num = roman_to_int.get(roman_str[0].upper(), 1)
                        arabic_prefix = str(num)
                elif num_type == "ARABIC_SINGLE":
                    digits = re.findall(r"^\d+", raw.strip())
                    arabic_prefix = digits[0] if digits else "1"
                return f"{arabic_prefix} {title_core}", "Springer LNCS Level 1 headings use Arabic numerals and Title Case (not ALL CAPS)."

        # Level 2 Subsections
        if level == 2:
            if target_v == "IEEE":
                return f"A. {title_core}", "IEEE subsections use Latin capital letters (e.g. 'A. Title') and Title Case."
            elif target_v in ["ACM", "SPRINGER"]:
                return f"1.1 {title_core}", f"{target_v} subsections use hierarchical decimal Arabic numerals (e.g. '1.1 Title')."

        # Fallback
        return raw, "Preserved original heading; manual author confirmation recommended."
