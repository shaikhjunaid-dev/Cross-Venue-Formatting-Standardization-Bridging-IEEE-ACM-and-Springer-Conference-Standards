"""
Comprehensive Venue Specifications and Official Guidelines Registry.

Codifies the verified requirements for IEEE Conference, ACM sigconf (acmart), 
and Springer LNCS proceedings across all structural and typographical dimensions.
"""

from typing import Dict, Any, List


VENUE_SPECIFICATIONS: Dict[str, Dict[str, Any]] = {
    "IEEE": {
        "id": "IEEE",
        "full_name": "IEEE Conference Proceedings Template",
        "doc_type": "Conference Proceedings (2-Column)",
        "official_guideline_source": "IEEE Author Center - Conference Template (2024)",
        "is_verified": True,
        
        # Typography & Page Layout
        "layout": {
            "columns": 2,
            "column_width_in": 3.5,
            "column_gutter_in": 0.25,
            "margin_top_in": 0.75,
            "margin_bottom_in": 1.0,
            "margin_left_in": 0.625,
            "margin_right_in": 0.625,
            "font_family": "Times New Roman",
            "body_font_size_pt": 10.0,
            "body_line_spacing": 1.0,
            "text_alignment": "JUSTIFY",
        },
        
        # Title and Authors
        "title": {
            "font_family": "Times New Roman",
            "font_size_pt": 20.0,
            "bold": True,
            "alignment": "CENTER",
            "casing": "TITLE_CASE",
            "rule": "Title centered, 20-24pt bold Times New Roman in title case across both columns."
        },
        "authors": {
            "font_family": "Times New Roman",
            "name_font_size_pt": 11.0,
            "name_bold": True,
            "affiliation_font_size_pt": 9.0,
            "layout": "MULTI_COLUMN_BLOCKS",
            "rule": "Author names centered in 11pt bold, affiliations in 9-10pt regular italic/normal."
        },
        
        # Frontmatter
        "abstract": {
            "lead_in": "Abstract---",
            "lead_in_format": "BOLD_ITALIC",
            "body_font_size_pt": 9.0,
            "body_bold": True,
            "max_words": 250,
            "rule": "Abstract heading must be 'Abstract---' in 9pt bold italic, followed immediately by text without line break."
        },
        "keywords": {
            "label": "Index Terms---",
            "lead_in_format": "BOLD_ITALIC",
            "body_font_size_pt": 9.0,
            "alphabetical_order_required": True,
            "separator": ", ",
            "rule": "Keywords must be labeled 'Index Terms---' in 9pt bold italic, listed in alphabetical order."
        },
        "ccs_concepts": {
            "required": False,
            "rule": "CCS Concepts are specific to ACM and are not used in IEEE conference templates."
        },
        
        # Headings Hierarchy
        "headings": {
            "level1": {
                "numbering": "ROMAN",
                "casing": "ALL_CAPS",
                "font_size_pt": 10.0,
                "bold": True,
                "alignment": "CENTER",
                "format_example": "I. INTRODUCTION",
                "rule": "Primary headings use uppercase Roman numerals (e.g. 'I. INTRODUCTION'), 10pt bold centered."
            },
            "level2": {
                "numbering": "ALPHA",
                "casing": "TITLE_CASE",
                "font_size_pt": 10.0,
                "italic": True,
                "bold": False,
                "alignment": "LEFT",
                "format_example": "A. Heading Normalization Layer",
                "rule": "Secondary headings use capital Latin letters (e.g. 'A. Subsection Title'), 10pt italic left-aligned."
            },
            "level3": {
                "numbering": "ARABIC_PAREN",
                "casing": "TITLE_CASE",
                "font_size_pt": 10.0,
                "italic": True,
                "bold": False,
                "alignment": "LEFT",
                "format_example": "1) Sub-subsection Title:",
                "rule": "Tertiary headings use Arabic numerals with closing parenthesis (e.g. '1) Title:'), run-in italic."
            }
        },
        
        # Special Sections
        "acknowledgments": {
            "exact_heading": "ACKNOWLEDGMENT",
            "casing": "ALL_CAPS",
            "numbering": False,
            "plural_allowed": False,
            "rule": "IEEE style strictly requires the singular form 'ACKNOWLEDGMENT', unnumbered, placed before References."
        },
        "references": {
            "exact_heading": "REFERENCES",
            "casing": "ALL_CAPS",
            "numbering": False,
            "citation_style": "NUMERIC_SQUARE_BRACKETS", # e.g. [1]
            "format_example": "[1] J. K. Author, \"Title of paper,\" Abbrev. Journal, vol. x, no. x, pp. xxx, year.",
            "rule": "References heading is unnumbered 'REFERENCES'. Citations use numeric brackets [1] in appearance order."
        },
        
        # Figures and Tables
        "tables": {
            "caption_position": "ABOVE",
            "caption_label": "TABLE I",
            "numbering": "ROMAN",
            "alignment": "CENTER",
            "rule": "Table caption appears above table, centered, labeled 'TABLE I' in uppercase Roman numerals."
        },
        "figures": {
            "caption_position": "BELOW",
            "caption_label": "Fig. 1.",
            "numbering": "ARABIC",
            "alignment": "LEFT_OR_CENTER",
            "rule": "Figure caption appears below figure, labeled 'Fig. 1.' with abbreviated prefix."
        }
    },
    
    "ACM": {
        "id": "ACM",
        "full_name": "ACM Primary Article Template (acmart sigconf)",
        "doc_type": "Conference Proceedings (2-Column)",
        "official_guideline_source": "ACM Primary Article Template & Publication Workflow (2024)",
        "is_verified": True,
        
        # Typography & Page Layout
        "layout": {
            "columns": 2,
            "column_width_in": 3.33,
            "column_gutter_in": 0.33,
            "margin_top_in": 0.75,
            "margin_bottom_in": 1.0,
            "margin_left_in": 0.75,
            "margin_right_in": 0.75,
            "font_family": "Linux Libertine", # In Word: Calibri or Times New Roman accepted
            "fallback_font": "Times New Roman",
            "body_font_size_pt": 9.0,
            "body_line_spacing": 1.1,
            "text_alignment": "JUSTIFY",
        },
        
        # Title and Authors
        "title": {
            "font_family": "Linux Libertine",
            "font_size_pt": 18.0,
            "bold": True,
            "alignment": "CENTER",
            "casing": "TITLE_CASE",
            "rule": "Title centered, 18pt bold in title case across both columns."
        },
        "authors": {
            "font_family": "Linux Libertine",
            "name_font_size_pt": 10.0,
            "name_bold": True,
            "affiliation_font_size_pt": 8.5,
            "layout": "AUTHOR_BLOCKS",
            "rule": "Author names 10pt bold, affiliation 8.5pt with city, country, email, and ORCID identifier."
        },
        
        # Frontmatter
        "abstract": {
            "lead_in": "ABSTRACT",
            "lead_in_format": "BOLD_UPPERCASE",
            "body_font_size_pt": 9.0,
            "body_bold": False,
            "max_words": 300,
            "rule": "Abstract heading is 'ABSTRACT' in bold uppercase, followed by standard 9pt abstract text."
        },
        "keywords": {
            "label": "Keywords",
            "lead_in_format": "BOLD",
            "body_font_size_pt": 9.0,
            "alphabetical_order_required": False,
            "separator": ", ",
            "rule": "Keywords labeled as 'Keywords:' or 'Keywords', comma separated."
        },
        "ccs_concepts": {
            "required": True,
            "rule": "ACM Computing Classification System (CCS) concepts block is mandatory for ACM proceedings (2012 taxonomy)."
        },
        
        # Headings Hierarchy
        "headings": {
            "level1": {
                "numbering": "ARABIC",
                "casing": "ALL_CAPS",
                "font_size_pt": 10.0,
                "bold": True,
                "alignment": "LEFT",
                "format_example": "1 INTRODUCTION",
                "rule": "Primary headings use Arabic numerals without trailing dot (e.g. '1 INTRODUCTION'), 10pt bold uppercase left-aligned."
            },
            "level2": {
                "numbering": "ARABIC_DECIMAL",
                "casing": "TITLE_CASE",
                "font_size_pt": 9.5,
                "italic": False,
                "bold": True,
                "alignment": "LEFT",
                "format_example": "1.1 Subsection Title",
                "rule": "Secondary headings use hierarchical Arabic numerals (e.g. '1.1 Subsection Title'), 9.5pt bold."
            },
            "level3": {
                "numbering": "ARABIC_DECIMAL",
                "casing": "TITLE_CASE",
                "font_size_pt": 9.0,
                "italic": True,
                "bold": True,
                "alignment": "LEFT",
                "format_example": "1.1.1 Sub-subsection Title",
                "rule": "Tertiary headings use 3-tier Arabic numerals (e.g. '1.1.1 Title'), 9pt bold italic."
            }
        },
        
        # Special Sections
        "acknowledgments": {
            "exact_heading": "ACKNOWLEDGMENTS",
            "casing": "ALL_CAPS",
            "numbering": False,
            "plural_allowed": True,
            "rule": "ACM style uses plural 'ACKNOWLEDGMENTS' (or \\begin{acks} in LaTeX), unnumbered, placed before References."
        },
        "references": {
            "exact_heading": "REFERENCES",
            "casing": "ALL_CAPS",
            "numbering": False,
            "citation_style": "NUMERIC_SQUARE_BRACKETS", # or author-year
            "format_example": "[1] First Author et al. 2024. Article Title. Journal Vol, No (2024), 1-10.",
            "rule": "References heading is unnumbered 'REFERENCES' adhering to ACM-Reference-Format."
        },
        
        # Figures and Tables
        "tables": {
            "caption_position": "ABOVE",
            "caption_label": "Table 1:",
            "numbering": "ARABIC",
            "alignment": "CENTER",
            "rule": "Table caption placed above table, labeled 'Table 1:' using Arabic numerals with colon."
        },
        "figures": {
            "caption_position": "BELOW",
            "caption_label": "Figure 1:",
            "numbering": "ARABIC",
            "alignment": "CENTER",
            "rule": "Figure caption placed below figure, labeled 'Figure 1:' with full word 'Figure'."
        }
    },
    
    "SPRINGER": {
        "id": "SPRINGER",
        "full_name": "Springer LNCS (Lecture Notes in Computer Science)",
        "doc_type": "Proceedings Series (Single-Column)",
        "official_guideline_source": "Springer Information for Authors of Computer Science Proceedings (LNCS 2024)",
        "is_verified": True,
        
        # Typography & Page Layout
        "layout": {
            "columns": 1,
            "column_width_in": 4.8, # 122 mm text width
            "margin_top_in": 1.25,
            "margin_bottom_in": 1.25,
            "margin_left_in": 1.22, # 122mm width on 210mm A4 gives approx 44mm margins (1.73 in) or centered
            "margin_right_in": 1.22,
            "font_family": "Times New Roman",
            "fallback_font": "Times New Roman",
            "body_font_size_pt": 10.0,
            "body_line_spacing": 1.15,
            "text_alignment": "JUSTIFY",
        },
        
        # Title and Authors
        "title": {
            "font_family": "Times New Roman",
            "font_size_pt": 14.0,
            "bold": True,
            "alignment": "CENTER",
            "casing": "TITLE_CASE",
            "rule": "Title centered, 14pt bold Times New Roman in title case (single column)."
        },
        "authors": {
            "font_family": "Times New Roman",
            "name_font_size_pt": 10.0,
            "name_bold": False,
            "affiliation_font_size_pt": 9.0,
            "layout": "CENTERED_STACK",
            "rule": "Author names 10pt centered, affiliations 9pt with institution and email."
        },
        
        # Frontmatter
        "abstract": {
            "lead_in": "Abstract.",
            "lead_in_format": "BOLD_TITLE_CASE",
            "body_font_size_pt": 9.0,
            "body_bold": False,
            "max_words": 250,
            "min_words": 150,
            "rule": "Abstract starts with 'Abstract.' in bold run-in, typically 150 to 250 words."
        },
        "keywords": {
            "label": "Keywords:",
            "lead_in_format": "BOLD",
            "body_font_size_pt": 9.0,
            "min_terms": 3,
            "max_terms": 6,
            "separator": " · ", # Springer uses middot or comma
            "rule": "Keywords labeled 'Keywords:' in bold, containing 3 to 6 terms separated by commas or middots."
        },
        "ccs_concepts": {
            "required": False,
            "rule": "CCS Concepts are not required for Springer LNCS."
        },
        
        # Headings Hierarchy
        "headings": {
            "level1": {
                "numbering": "ARABIC",
                "casing": "TITLE_CASE",
                "font_size_pt": 12.0,
                "bold": True,
                "alignment": "LEFT",
                "format_example": "1 Introduction",
                "rule": "Primary headings use Arabic numerals with space (e.g. '1 Introduction'), 12pt bold in title case (not ALL CAPS)."
            },
            "level2": {
                "numbering": "ARABIC_DECIMAL",
                "casing": "TITLE_CASE",
                "font_size_pt": 10.0,
                "italic": False,
                "bold": True,
                "alignment": "LEFT",
                "format_example": "1.1 Subsection Title",
                "rule": "Secondary headings use hierarchical Arabic numerals (e.g. '1.1 Subsection Title'), 10pt bold."
            },
            "level3": {
                "numbering": "ARABIC_DECIMAL",
                "casing": "TITLE_CASE",
                "font_size_pt": 10.0,
                "italic": True,
                "bold": False,
                "alignment": "LEFT",
                "format_example": "1.1.1 Sub-subsection Title",
                "rule": "Tertiary headings use 3-tier Arabic numerals (e.g. '1.1.1 Title'), 10pt italic."
            }
        },
        
        # Special Sections
        "acknowledgments": {
            "exact_heading": "Acknowledgements",
            "casing": "TITLE_CASE",
            "numbering": False,
            "plural_allowed": True,
            "rule": "Springer LNCS accepts British 'Acknowledgements', unnumbered, placed immediately prior to References."
        },
        "references": {
            "exact_heading": "References",
            "casing": "TITLE_CASE",
            "numbering": False,
            "citation_style": "NUMERIC_SQUARE_BRACKETS",
            "format_example": "1. Author, A.: Title of paper. Journal Vol, pp-pp (year)",
            "rule": "References heading is unnumbered 'References' in Title Case, citations in square brackets [1]."
        },
        
        # Figures and Tables
        "tables": {
            "caption_position": "ABOVE",
            "caption_label": "Table 1.",
            "numbering": "ARABIC",
            "alignment": "CENTER",
            "rule": "Table caption placed above table, labeled 'Table 1.' with dot."
        },
        "figures": {
            "caption_position": "BELOW",
            "caption_label": "Fig. 1.",
            "numbering": "ARABIC",
            "alignment": "CENTER",
            "rule": "Figure caption placed below figure, labeled 'Fig. 1.' with dot."
        }
    }
}
