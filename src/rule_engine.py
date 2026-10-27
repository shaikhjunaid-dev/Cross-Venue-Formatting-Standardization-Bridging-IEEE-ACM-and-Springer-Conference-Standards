"""
Rule-Based Cross-Venue Semantic Mapping Engine.

Maps normalized section headings from IEEE, ACM, or Springer papers to the 
universal CanonicalSection schema. Evaluates explicit keyword rules, regex 
patterns, compound section splitting, and ambiguity detection with explainability.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from .schema import CanonicalSection
from .normalizer import normalize_heading


# Canonical section mapping rule definitions with priority weights
MAPPING_RULES: Dict[str, Dict[str, Any]] = {
    CanonicalSection.TITLE.value: {
        "exact": ["title", "paper title", "manuscript title"],
        "regex": [r"\btitle\b"],
        "weight": 1.0
    },
    CanonicalSection.AUTHORS.value: {
        "exact": ["authors", "author", "authors and affiliations", "author information"],
        "regex": [r"\bauthors?\b", r"\baffiliations?\b"],
        "weight": 0.95
    },
    CanonicalSection.ABSTRACT.value: {
        "exact": ["abstract", "executive summary", "overview"],
        "regex": [r"^abstract\b", r"\babstract\b"],
        "weight": 1.0
    },
    CanonicalSection.KEYWORDS.value: {
        "exact": [
            "keywords", "key words", "index terms", "ccs concepts", 
            "computing classification system", "subject descriptors", 
            "index terms---", "key-words"
        ],
        "regex": [r"\bindex\s+terms\b", r"\bccs\s+concepts\b", r"\bkeywords?\b"],
        "weight": 1.0
    },
    CanonicalSection.INTRODUCTION.value: {
        "exact": [
            "introduction", "motivation", "background and motivation",
            "context and motivation", "problem statement", "preliminaries and introduction"
        ],
        "regex": [r"^introduction\b", r"\bmotivation\b", r"\bproblem\s+formulation\b"],
        "weight": 1.0
    },
    CanonicalSection.RELATED_WORK.value: {
        "exact": [
            "related work", "related works", "literature review", 
            "state of the art", "prior work", "background and related work",
            "previous work", "survey of literature", "theoretical background"
        ],
        "regex": [
            r"\brelated\s+works?\b", r"\bliterature\s+review\b", 
            r"\bstate\s+of\s+the\s+art\b", r"\bprior\s+art\b",
            r"\bbackground\s+and\s+related\b"
        ],
        "weight": 0.98
    },
    CanonicalSection.METHODOLOGY.value: {
        "exact": [
            "methodology", "methods", "method", "proposed method", 
            "proposed methodology", "proposed system", "system architecture", 
            "proposed framework", "materials and methods", "system design", 
            "design and implementation", "model architecture", "algorithm",
            "proposed approach", "technical approach", "formal model"
        ],
        "regex": [
            r"\bmethodolog(?:y|ies)\b", r"\bproposed\s+(?:method|system|framework|approach|model|architecture)\b",
            r"\bsystem\s+(?:design|architecture|model)\b", r"\bmaterials\s+and\s+methods\b",
            r"\bdesign\s+and\s+implementation\b"
        ],
        "weight": 0.95
    },
    CanonicalSection.EVALUATION.value: {
        "exact": [
            "results", "evaluation", "experiments", "experimental evaluation", 
            "experimental results", "performance evaluation", "empirical analysis", 
            "benchmarking", "validation", "experiments and results", "case study evaluation",
            "simulation results", "performance analysis", "experimental setup",
            "ablation study", "ablation analysis", "sensitivity analysis"
        ],
        "regex": [
            r"\bexperiment(?:s|al)?\b", r"\bevaluation\b", r"\bperformance\s+(?:evaluation|analysis)\b",
            r"\bempirical\s+(?:study|results|analysis)\b", r"\bsimulation\s+results\b",
            r"\bbenchmarks?\b", r"\bablation\b", r"\bsensitivity\s+analysis\b"
        ],
        "weight": 0.95
    },
    CanonicalSection.DISCUSSION.value: {
        "exact": [
            "discussion", "findings and discussion", "analysis and discussion", 
            "practical implications", "comparative discussion", "threats to validity",
            "limitations", "discussion and limitations"
        ],
        "regex": [
            r"^discussion\b", r"\banalysis\s+and\s+discussion\b",
            r"\bthreats\s+to\s+validity\b", r"\blimitations?\b"
        ],
        "weight": 0.92
    },
    CanonicalSection.CONCLUSION.value: {
        "exact": [
            "conclusion", "conclusions", "concluding remarks", 
            "conclusion and future work", "conclusions and future directions", 
            "summary and conclusion", "summary and outlook", "concluding observations"
        ],
        "regex": [
            r"\bconclusions?\b", r"\bconcluding\b", r"\bfuture\s+works?\b",
            r"\bsummary\s+and\s+outlook\b"
        ],
        "weight": 1.0
    },
    CanonicalSection.ACKNOWLEDGMENTS.value: {
        "exact": [
            "acknowledgment", "acknowledgments", "acknowledgements", 
            "financial disclosure", "funding", "acknowledgement",
            "grant support", "conflict of interest"
        ],
        "regex": [r"\backnowledg(?:e)?ments?\b", r"\bfunding\b", r"\bgrant\s+support\b"],
        "weight": 1.0
    },
    CanonicalSection.REFERENCES.value: {
        "exact": [
            "references", "bibliography", "works cited", 
            "literature cited", "reference list"
        ],
        "regex": [r"^references?\b", r"^bibliography\b", r"^works\s+cited\b"],
        "weight": 1.0
    },
    CanonicalSection.APPENDIX.value: {
        "exact": [
            "appendix", "appendices", "supplementary material", 
            "supplemental data", "supplementary proof"
        ],
        "regex": [r"\bappendix\b", r"\bappendices\b", r"\bsupplementary\b"],
        "weight": 0.95
    }
}


# Known compound multi-section phrases
COMPOUND_SECTIONS: Dict[str, Tuple[str, str]] = {
    "results and discussion": (CanonicalSection.EVALUATION.value, CanonicalSection.DISCUSSION.value),
    "discussion and conclusion": (CanonicalSection.DISCUSSION.value, CanonicalSection.CONCLUSION.value),
    "conclusion and future work": (CanonicalSection.CONCLUSION.value, CanonicalSection.CONCLUSION.value),
    "background and related work": (CanonicalSection.RELATED_WORK.value, CanonicalSection.RELATED_WORK.value),
    "experiments and results": (CanonicalSection.EVALUATION.value, CanonicalSection.EVALUATION.value),
    "design and implementation": (CanonicalSection.METHODOLOGY.value, CanonicalSection.METHODOLOGY.value),
    "implementation and evaluation": (CanonicalSection.METHODOLOGY.value, CanonicalSection.EVALUATION.value),
}


class RuleMappingEngine:
    """Deterministic, explainable rule-based mapping engine."""

    def __init__(self):
        self.rules = MAPPING_RULES
        self.compounds = COMPOUND_SECTIONS

    def map_heading(self, raw_heading: str, source_venue: Optional[str] = None) -> Dict[str, Any]:
        """
        Maps a raw heading to a canonical section with full rationale and ambiguity check.
        """
        norm = normalize_heading(raw_heading)
        cleaned = norm["cleaned"]
        
        # Check compound sections first
        for compound_key, (primary, secondary) in self.compounds.items():
            if compound_key in cleaned:
                is_compound = primary != secondary
                explanation = (
                    f"Compound heading detected: matches both '{primary}' and '{secondary}'. "
                    f"Primary classification assigned to '{primary}'."
                    if is_compound else
                    f"Standard compound phrase matched '{compound_key}' -> mapped to '{primary}'."
                )
                return {
                    "raw_heading": raw_heading,
                    "cleaned_heading": cleaned,
                    "numbering_type": norm["numbering_type"],
                    "level": norm["level"],
                    "canonical_section": primary,
                    "secondary_section": secondary if is_compound else None,
                    "confidence": 0.95 if is_compound else 1.0,
                    "is_ambiguous": is_compound,
                    "is_compound": is_compound,
                    "explanation": explanation,
                    "match_type": "COMPOUND_PHRASE"
                }

        # Check exact matches across all canonical sections
        matches = []
        for sec, rule in self.rules.items():
            if cleaned in rule["exact"]:
                matches.append((sec, 1.0, f"Exact dictionary match for term '{cleaned}'."))

        # If no exact match, check regex patterns
        if not matches:
            for sec, rule in self.rules.items():
                for pat in rule["regex"]:
                    if re.search(pat, cleaned, re.IGNORECASE):
                        matches.append((sec, rule["weight"], f"Regex pattern '{pat}' matched in '{cleaned}'."))
                        break

        # Decision handling
        if not matches:
            return {
                "raw_heading": raw_heading,
                "cleaned_heading": cleaned,
                "numbering_type": norm["numbering_type"],
                "level": norm["level"],
                "canonical_section": CanonicalSection.UNKNOWN.value,
                "secondary_section": None,
                "confidence": 0.0,
                "is_ambiguous": False,
                "is_compound": False,
                "explanation": f"No canonical rule matched for heading '{raw_heading}'. Author domain-specific section.",
                "match_type": "NONE"
            }

        if len(matches) == 1:
            best_sec, conf, exp = matches[0]
            return {
                "raw_heading": raw_heading,
                "cleaned_heading": cleaned,
                "numbering_type": norm["numbering_type"],
                "level": norm["level"],
                "canonical_section": best_sec,
                "secondary_section": None,
                "confidence": conf,
                "is_ambiguous": False,
                "is_compound": False,
                "explanation": exp,
                "match_type": "RULE_MATCH"
            }

        # Multiple matches -> Ambiguity detected
        # Sort by confidence descending
        matches.sort(key=lambda x: x[1], reverse=True)
        primary = matches[0]
        alternatives = [m[0] for m in matches[1:] if m[0] != primary[0]]
        
        is_ambiguous = len(alternatives) > 0 and (primary[1] - matches[1][1] < 0.1)
        exp = (
            f"Multiple candidate matches detected: {[m[0] for m in matches]}. "
            f"Selected '{primary[0]}' with highest rule weight ({primary[1]:.2f})."
        )
        
        return {
            "raw_heading": raw_heading,
            "cleaned_heading": cleaned,
            "numbering_type": norm["numbering_type"],
            "level": norm["level"],
            "canonical_section": primary[0],
            "secondary_section": alternatives[0] if alternatives else None,
            "confidence": round(primary[1] * (0.85 if is_ambiguous else 1.0), 2),
            "is_ambiguous": is_ambiguous,
            "is_compound": False,
            "explanation": exp,
            "match_type": "AMBIGUOUS_MULTI_RULE" if is_ambiguous else "RULE_MATCH"
        }
