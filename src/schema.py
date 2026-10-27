"""
Canonical Semantic Schema and Publisher Venue Specifications.

Defines the universal cross-venue semantic section taxonomy and 
publisher-specific structural expectations for IEEE, ACM, and Springer LNCS.
"""

from enum import Enum
from typing import Dict, List, Set, Any


class CanonicalSection(str, Enum):
    """Universal Canonical Semantic Categories for Scientific Papers."""
    TITLE = "TITLE"
    AUTHORS = "AUTHORS"
    ABSTRACT = "ABSTRACT"
    KEYWORDS = "KEYWORDS"
    INTRODUCTION = "INTRODUCTION"
    RELATED_WORK = "RELATED_WORK"
    METHODOLOGY = "METHODOLOGY"
    EVALUATION = "EVALUATION"
    DISCUSSION = "DISCUSSION"
    CONCLUSION = "CONCLUSION"
    ACKNOWLEDGMENTS = "ACKNOWLEDGMENTS"
    REFERENCES = "REFERENCES"
    APPENDIX = "APPENDIX"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def all_sections(cls) -> List[str]:
        return [sec.value for sec in cls if sec != cls.UNKNOWN]


# Canonical display names and descriptions
SCHEMA_DESCRIPTIONS: Dict[str, str] = {
    CanonicalSection.TITLE.value: "Document Title and Subtitle",
    CanonicalSection.AUTHORS.value: "Author names, affiliations, and contact emails",
    CanonicalSection.ABSTRACT.value: "Concise summary of research motivation, methods, and key findings",
    CanonicalSection.KEYWORDS.value: "Subject descriptors, index terms, or classification concepts",
    CanonicalSection.INTRODUCTION.value: "Research background, motivation, problem statement, and contributions",
    CanonicalSection.RELATED_WORK.value: "Literature review, state of the art, and theoretical background",
    CanonicalSection.METHODOLOGY.value: "Proposed system architecture, algorithm design, formal model, or methodology",
    CanonicalSection.EVALUATION.value: "Experimental setup, empirical results, performance benchmarks, and ablation studies",
    CanonicalSection.DISCUSSION.value: "Analytical interpretation, implications, practical insights, and limitations",
    CanonicalSection.CONCLUSION.value: "Summary of achievements, concluding remarks, and future research directions",
    CanonicalSection.ACKNOWLEDGMENTS.value: "Recognition of funding bodies, institutional support, and collaborator assistance",
    CanonicalSection.REFERENCES.value: "Bibliographic citations and references cited in the body",
    CanonicalSection.APPENDIX.value: "Supplementary proofs, data tables, or extended implementation details",
    CanonicalSection.UNKNOWN.value: "Unrecognized or domain-specific heading that requires manual author resolution",
}


# Venue-specific rules and structural constraints
VENUE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "IEEE": {
        "full_name": "IEEE Conference Template (2-Column Format)",
        "heading_numbering_style": "ROMAN_NUMERALS",  # e.g., I. INTRODUCTION
        "keywords_label": "Index Terms",
        "acknowledgments_heading": "ACKNOWLEDGMENT",  # Singular in IEEE style
        "acknowledgments_plural_allowed": False,
        "references_heading": "REFERENCES",
        "abstract_heading": "Abstract",
        "mandatory_sections": [
            CanonicalSection.ABSTRACT.value,
            CanonicalSection.KEYWORDS.value,
            CanonicalSection.INTRODUCTION.value,
            CanonicalSection.METHODOLOGY.value,
            CanonicalSection.EVALUATION.value,
            CanonicalSection.CONCLUSION.value,
            CanonicalSection.REFERENCES.value,
        ],
        "recommended_sections": [
            CanonicalSection.RELATED_WORK.value,
            CanonicalSection.ACKNOWLEDGMENTS.value,
        ],
        "special_requirements": [
            "Section headings must use uppercase Roman numerals (e.g., 'I. INTRODUCTION').",
            "Acknowledgment must be titled 'ACKNOWLEDGMENT' (strictly singular, not plural).",
            "References must be unnumbered and follow IEEE numeric citation style [1].",
            "Keywords are labeled 'Index Terms---' and listed in alphabetical order.",
            "Abstract should be bold italic and titled 'Abstract---'."
        ]
    },
    "ACM": {
        "full_name": "ACM Primary Article Template (sigconf)",
        "heading_numbering_style": "ARABIC_NUMERALS",  # e.g., 1 INTRODUCTION
        "keywords_label": "Keywords",
        "requires_ccs_concepts": True,
        "acknowledgments_heading": "ACKNOWLEDGMENTS",  # Plural in ACM style
        "acknowledgments_plural_allowed": True,
        "references_heading": "REFERENCES",
        "abstract_heading": "ABSTRACT",
        "mandatory_sections": [
            CanonicalSection.ABSTRACT.value,
            CanonicalSection.KEYWORDS.value,
            CanonicalSection.INTRODUCTION.value,
            CanonicalSection.METHODOLOGY.value,
            CanonicalSection.EVALUATION.value,
            CanonicalSection.CONCLUSION.value,
            CanonicalSection.REFERENCES.value,
        ],
        "recommended_sections": [
            CanonicalSection.RELATED_WORK.value,
            CanonicalSection.DISCUSSION.value,
            CanonicalSection.ACKNOWLEDGMENTS.value,
        ],
        "special_requirements": [
            "Section headings are numbered using Arabic numerals (e.g., '1 INTRODUCTION').",
            "ACM Computing Classification System (CCS) Concepts block is mandatory.",
            "Acknowledgments block is placed using \\begin{acks} ... \\end{acks} in LaTeX.",
            "References must use ACM-Reference-Format.",
            "Title and author metadata include email and ORCID."
        ]
    },
    "SPRINGER": {
        "full_name": "Springer LNCS (Lecture Notes in Computer Science)",
        "heading_numbering_style": "ARABIC_NUMERALS",  # e.g., 1 Introduction
        "keywords_label": "Keywords",
        "requires_ccs_concepts": False,
        "acknowledgments_heading": "Acknowledgements",  # British spelling commonly accepted
        "acknowledgments_plural_allowed": True,
        "references_heading": "References",
        "abstract_heading": "Abstract",
        "mandatory_sections": [
            CanonicalSection.ABSTRACT.value,
            CanonicalSection.KEYWORDS.value,
            CanonicalSection.INTRODUCTION.value,
            CanonicalSection.METHODOLOGY.value,
            CanonicalSection.EVALUATION.value,
            CanonicalSection.CONCLUSION.value,
            CanonicalSection.REFERENCES.value,
        ],
        "recommended_sections": [
            CanonicalSection.RELATED_WORK.value,
            CanonicalSection.DISCUSSION.value,
            CanonicalSection.ACKNOWLEDGMENTS.value,
        ],
        "special_requirements": [
            "Single column layout (122 mm x 193 mm text area).",
            "Headings use title capitalization and Arabic numerals (e.g., '1 Introduction').",
            "Abstract should typically be 150-250 words.",
            "Keywords should be between 3 and 6 terms separated by commas.",
            "Acknowledgements section is unnumbered and placed immediately prior to References."
        ]
    }
}
