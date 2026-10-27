"""
Heading Normalization and Preprocessing Module.

Preprocesses raw section headings extracted from scientific papers:
- Strips numbering prefixes (Roman, Arabic, alphabetic, decimal).
- Cleans punctuation, trailing separators, and excessive whitespace.
- Detects structural heading level and numbering convention.
"""

import re
from typing import Dict, Any, Tuple


# Regex patterns for numbering detection
ROMAN_PATTERN = re.compile(r"^(?:[IVXLCDM]+)[\.\:\-\s]+", re.IGNORECASE)
ARABIC_MULTI_PATTERN = re.compile(r"^(?:\d+\.)+\d*[\.\:\-\s]*")
ARABIC_SINGLE_PATTERN = re.compile(r"^\d+[\.\:\-\s]+")
ALPHA_PATTERN = re.compile(r"^[A-Z]\.[\s]+")


def normalize_heading(raw_text: str) -> Dict[str, Any]:
    """
    Cleans raw heading string and extracts structural metadata.
    
    Returns:
        Dict containing:
        - raw: original text
        - cleaned: lowercased, punctuation-stripped text for rule matching
        - numbering_type: 'ROMAN', 'ARABIC_HIERARCHICAL', 'ARABIC_SINGLE', 'ALPHA', or 'NONE'
        - level: estimated hierarchical heading level (1 for main section, 2 for subsection, etc.)
    """
    text = (raw_text or "").strip()
    original = text
    
    # Remove leading common prefixes like "Section", "Sec."
    text = re.sub(r"^(?:Section|Sec\.)\s*", "", text, flags=re.IGNORECASE).strip()
    
    numbering_type = "NONE"
    level = 1
    
    # Check for hierarchical Arabic (e.g., "1.2.3 Methodology" or "3.1 Results")
    hier_match = ARABIC_MULTI_PATTERN.match(text)
    if hier_match:
        prefix = hier_match.group(0)
        digits = [d for d in prefix.split(".") if d.strip().isdigit()]
        level = max(1, len(digits))
        numbering_type = "ARABIC_HIERARCHICAL"
        text = text[len(prefix):].strip()
    else:
        # Check for single Arabic (e.g., "1. Introduction" or "1 Introduction")
        single_match = ARABIC_SINGLE_PATTERN.match(text)
        if single_match:
            numbering_type = "ARABIC_SINGLE"
            level = 1
            text = text[len(single_match.group(0)):].strip()
        else:
            # Check for Roman (e.g., "I. INTRODUCTION", "IV. RESULTS")
            roman_match = ROMAN_PATTERN.match(text)
            if roman_match:
                # Disqualify single letter "I" if followed immediately by letter word (e.g. "I love")
                # Roman pattern with dot or dash is very reliable
                numbering_type = "ROMAN"
                level = 1
                text = text[len(roman_match.group(0)):].strip()
            else:
                # Check for Alphabetic subsection (e.g. "A. Data Preprocessing")
                alpha_match = ALPHA_PATTERN.match(text)
                if alpha_match:
                    numbering_type = "ALPHA"
                    level = 2
                    text = text[len(alpha_match.group(0)):].strip()
    
    # Clean special publisher artifacts (e.g., "---", ":", trailing dots)
    text = re.sub(r"^[\-\—\:\.\s]+", "", text)
    text = re.sub(r"[\-\—\:\.\s]+$", "", text)
    cleaned = text.strip().lower()
    
    return {
        "raw": original,
        "cleaned": cleaned,
        "numbering_type": numbering_type,
        "level": level
    }
