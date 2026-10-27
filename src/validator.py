"""
Venue-Specific Structural and Compliance Validator.

Validates extracted section mappings against target conference requirements 
(IEEE, ACM, Springer LNCS) and checks:
- Missing mandatory and recommended sections.
- Structural sequencing anomalies (e.g., Results before Methodology).
- Venue-specific formatting conventions (singular vs plural Acknowledgment, Roman vs Arabic numerals).
"""

from typing import Dict, List, Any, Optional
from .schema import CanonicalSection, VENUE_CONFIGS


class VenueValidator:
    """Validates mapped document sections against publisher specifications."""

    def __init__(self, target_venue: str = "IEEE"):
        self.venue = target_venue.upper()
        if self.venue not in VENUE_CONFIGS:
            raise ValueError(f"Unsupported venue '{target_venue}'. Choose from {list(VENUE_CONFIGS.keys())}")
        self.config = VENUE_CONFIGS[self.venue]

    def validate_document(self, mapped_headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates full document structure against selected venue.
        
        Args:
            mapped_headings: List of mapping output dicts from RuleMappingEngine.
            
        Returns:
            Dict containing:
            - is_compliant: bool
            - missing_mandatory: List of missing canonical sections
            - missing_recommended: List of missing recommended sections
            - warnings: List of warning strings
            - suggestions: List of actionable suggestions for the author
            - sequence_issues: List of detected out-of-order section pairs
        """
        present_canonical: List[str] = [m["canonical_section"] for m in mapped_headings]
        present_set = set(present_canonical)
        
        # 1. Check Missing Sections
        missing_mandatory = [
            sec for sec in self.config["mandatory_sections"] 
            if sec not in present_set
        ]
        
        missing_recommended = [
            sec for sec in self.config.get("recommended_sections", [])
            if sec not in present_set
        ]
        
        warnings: List[str] = []
        suggestions: List[str] = []
        
        # 2. Check Numbering and Formatting Conventions
        for item in mapped_headings:
            raw = item["raw_heading"]
            num_type = item.get("numbering_type", "NONE")
            sec = item["canonical_section"]
            
            # IEEE-specific checks
            if self.venue == "IEEE":
                if sec in [CanonicalSection.INTRODUCTION.value, CanonicalSection.METHODOLOGY.value, 
                           CanonicalSection.EVALUATION.value, CanonicalSection.CONCLUSION.value]:
                    if num_type == "ARABIC_SINGLE":
                        warnings.append(
                            f"IEEE style violation in heading '{raw}': IEEE requires uppercase Roman numerals "
                            f"(e.g., 'I. INTRODUCTION'), but Arabic numeral was detected."
                        )
                # Check singular Acknowledgment
                if sec == CanonicalSection.ACKNOWLEDGMENTS.value:
                    if "acknowledgments" in raw.lower() or "acknowledgements" in raw.lower():
                        warnings.append(
                            f"IEEE convention alert: Heading '{raw}' uses plural form. "
                            f"IEEE style explicitly requires singular 'ACKNOWLEDGMENT'."
                        )
                        suggestions.append("Change 'ACKNOWLEDGMENTS' to singular 'ACKNOWLEDGMENT' for IEEE submission.")
                # Check Index Terms
                if sec == CanonicalSection.KEYWORDS.value and "keywords" in raw.lower():
                    suggestions.append("IEEE preferred term for keywords is 'Index Terms---'.")
            
            # ACM-specific checks
            elif self.venue == "ACM":
                if num_type == "ROMAN":
                    warnings.append(
                        f"ACM style violation in heading '{raw}': ACM templates use Arabic numerals "
                        f"(e.g., '1 Introduction'), but Roman numeral was detected."
                    )
                if sec == CanonicalSection.KEYWORDS.value and "index terms" in raw.lower():
                    suggestions.append("ACM uses 'Keywords' instead of IEEE's 'Index Terms'.")
            
            # Springer-specific checks
            elif self.venue == "SPRINGER":
                if num_type == "ROMAN":
                    warnings.append(
                        f"Springer LNCS violation in heading '{raw}': Springer requires Arabic numerals "
                        f"(e.g., '1 Introduction')."
                    )

        # 3. Check Mandatory Section Completeness
        if missing_mandatory:
            warnings.append(
                f"Missing {len(missing_mandatory)} mandatory section(s) for {self.venue}: {missing_mandatory}"
            )
            for m_sec in missing_mandatory:
                suggestions.append(f"Add required section: '{m_sec}' before submission.")

        # 4. Check Sequence Order
        sequence_issues = self._check_sequence(present_canonical)
        for issue in sequence_issues:
            warnings.append(f"Structural sequence anomaly: {issue}")

        is_compliant = (len(missing_mandatory) == 0 and len(sequence_issues) == 0)

        return {
            "venue": self.venue,
            "full_venue_name": self.config["full_name"],
            "is_compliant": is_compliant,
            "missing_mandatory": missing_mandatory,
            "missing_recommended": missing_recommended,
            "warnings": warnings,
            "suggestions": suggestions,
            "sequence_issues": sequence_issues,
            "total_headings_analyzed": len(mapped_headings),
            "unmapped_headings_count": sum(1 for m in mapped_headings if m["canonical_section"] == CanonicalSection.UNKNOWN.value)
        }

    def _check_sequence(self, sections: List[str]) -> List[str]:
        """Detects illogical discourse ordering."""
        issues = []
        
        # Abstract must appear before Introduction
        if CanonicalSection.ABSTRACT.value in sections and CanonicalSection.INTRODUCTION.value in sections:
            abs_idx = sections.index(CanonicalSection.ABSTRACT.value)
            intro_idx = sections.index(CanonicalSection.INTRODUCTION.value)
            if abs_idx > intro_idx:
                issues.append("Abstract appears after Introduction.")

        # Introduction must appear before Methodology
        if CanonicalSection.INTRODUCTION.value in sections and CanonicalSection.METHODOLOGY.value in sections:
            intro_idx = sections.index(CanonicalSection.INTRODUCTION.value)
            meth_idx = sections.index(CanonicalSection.METHODOLOGY.value)
            if intro_idx > meth_idx:
                issues.append("Introduction appears after Methodology.")

        # Methodology before Evaluation
        if CanonicalSection.METHODOLOGY.value in sections and CanonicalSection.EVALUATION.value in sections:
            meth_idx = sections.index(CanonicalSection.METHODOLOGY.value)
            eval_idx = sections.index(CanonicalSection.EVALUATION.value)
            if meth_idx > eval_idx:
                issues.append("Methodology appears after Results/Evaluation.")

        # Conclusion before References
        if CanonicalSection.CONCLUSION.value in sections and CanonicalSection.REFERENCES.value in sections:
            conc_idx = sections.index(CanonicalSection.CONCLUSION.value)
            ref_idx = sections.index(CanonicalSection.REFERENCES.value)
            if conc_idx > ref_idx:
                issues.append("Conclusion appears after References. References should be at the document end.")

        return issues
