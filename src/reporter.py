"""
Report Generator for Cross-Venue Mapping and Validation.

Generates structured JSON, tabular CSV, and human-readable text summaries
of section mappings, validation results, and cross-venue conversion steps.
"""

import os
import json
import csv
from typing import Dict, List, Any


class ReportGenerator:
    """Produces exportable reports and cross-venue adaptation recommendations."""

    @staticmethod
    def to_json(mapped_headings: List[Dict[str, Any]], validation: Dict[str, Any], filepath: str) -> None:
        """Saves mapping and validation results to structured JSON."""
        data = {
            "validation_summary": validation,
            "section_mappings": mapped_headings
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def to_csv(mapped_headings: List[Dict[str, Any]], filepath: str) -> None:
        """Saves mapping results to CSV for spreadsheet inspection."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fieldnames = [
            "raw_heading", "cleaned_heading", "numbering_type", "level",
            "canonical_section", "secondary_section", "confidence",
            "is_ambiguous", "is_compound", "match_type", "explanation"
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in mapped_headings:
                filtered_row = {k: row.get(k, "") for k in fieldnames}
                writer.writerow(filtered_row)

    @staticmethod
    def roadmap_to_csv(roadmap_entries: List[Dict[str, Any]], filepath: str) -> None:
        """Saves actionable migration roadmap to CSV for author task tracking."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        fieldnames = [
            "element", "category", "current_format", "target_format", "action",
            "reason", "rule_reference", "priority", "auto_applicable",
            "manual_review_required", "status", "is_verified_rule"
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for entry in roadmap_entries:
                writer.writerow(entry)

    @staticmethod
    def generate_console_summary(mapped_headings: List[Dict[str, Any]], validation: Dict[str, Any]) -> str:
        """Generates clear, formatted terminal text for viva and demonstration."""
        lines = []
        lines.append("=" * 80)
        lines.append(" CROSS-VENUE FORMATTING STANDARDIZATION SYSTEM: ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"Target Venue: {validation['full_venue_name']} ({validation['venue']})")
        lines.append(f"Status: {'[COMPLIANT]' if validation['is_compliant'] else '[NON-COMPLIANT / REVISIONS NEEDED]'}")
        lines.append(f"Total Headings: {validation['total_headings_analyzed']} | Unmapped: {validation['unmapped_headings_count']}")
        lines.append("-" * 80)
        lines.append(f"{'RAW HEADING':<35} | {'CANONICAL MAPPING':<20} | {'CONF':<6} | {'STATUS'}")
        lines.append("-" * 80)
        
        for m in mapped_headings:
            flag = "OK"
            if m["canonical_section"] == "UNKNOWN":
                flag = "[UNMAPPED]"
            elif m["is_ambiguous"]:
                flag = "[AMBIGUOUS]"
            elif m["is_compound"]:
                flag = "[COMPOUND]"
            
            raw_disp = (m["raw_heading"][:32] + "...") if len(m["raw_heading"]) > 32 else m["raw_heading"]
            lines.append(f"{raw_disp:<35} | {m['canonical_section']:<20} | {m['confidence']:<6.2f} | {flag}")

        lines.append("-" * 80)
        
        if validation["missing_mandatory"]:
            lines.append(f"CRITICAL: Missing Mandatory Sections ({len(validation['missing_mandatory'])}):")
            for m_sec in validation["missing_mandatory"]:
                lines.append(f"  * {m_sec}")
        
        if validation["warnings"]:
            lines.append(f"\nFormatting & Convention Warnings ({len(validation['warnings'])}):")
            for w in validation["warnings"]:
                lines.append(f"  ! {w}")

        if validation["suggestions"]:
            lines.append(f"\nActionable Suggestions ({len(validation['suggestions'])}):")
            for s in validation["suggestions"]:
                lines.append(f"  -> {s}")

        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def generate_cross_venue_migration_guide(source_venue: str, target_venue: str, 
                                             mapped_headings: List[Dict[str, Any]]) -> List[str]:
        """Provides direct migration advice when converting between venues."""
        s = source_venue.upper()
        t = target_venue.upper()
        guide = []
        
        if s == t:
            return ["Source and target venues are identical. No cross-venue restructuring required."]
            
        guide.append(f"Migration Roadmap: Converting from {s} to {t}:")
        
        if s == "IEEE" and t == "ACM":
            guide.append("1. Numbering: Convert Roman numerals (I, II, III) to Arabic numerals (1, 2, 3).")
            guide.append("2. Keywords: Rename 'Index Terms' to 'Keywords'.")
            guide.append("3. CCS Concepts: Generate and insert ACM Computing Classification System (CCS) XML block.")
            guide.append("4. Acknowledgments: Rename singular 'ACKNOWLEDGMENT' to plural 'ACKNOWLEDGMENTS' (use \\begin{acks}).")
            guide.append("5. Layout: Ensure transition from IEEE 2-column 10pt to ACM Libertine 9pt 2-column or review single-column.")

        elif s == "IEEE" and t == "SPRINGER":
            guide.append("1. Numbering: Convert Roman numerals (I, II, III) to Arabic numerals (1, 2, 3).")
            guide.append("2. Layout: Transition from IEEE 2-column layout to Springer LNCS single-column layout (122x193 mm).")
            guide.append("3. Keywords: Change 'Index Terms' to 'Keywords' (3-6 terms separated by commas).")
            guide.append("4. Acknowledgements: Rename 'ACKNOWLEDGMENT' to 'Acknowledgements' (unnumbered section before References).")

        elif s == "ACM" and t == "IEEE":
            guide.append("1. Numbering: Convert Arabic numerals (1, 2, 3) to uppercase Roman numerals (I., II., III.).")
            guide.append("2. Keywords: Change 'Keywords' to 'Index Terms---' and sort terms alphabetically.")
            guide.append("3. Acknowledgments: Change 'ACKNOWLEDGMENTS' to strictly singular 'ACKNOWLEDGMENT'.")
            guide.append("4. Remove ACM-specific metadata: Remove CCS Concepts block and conference rights text.")
            guide.append("5. References: Format citations in IEEE numeric style [1] with author initials first.")

        elif s == "SPRINGER" and t == "IEEE":
            guide.append("1. Numbering: Convert Arabic numerals to uppercase Roman numerals (I., II., III.).")
            guide.append("2. Layout: Transition from single-column LNCS to 2-column IEEE format.")
            guide.append("3. Keywords: Change 'Keywords' to 'Index Terms---'.")
            guide.append("4. Acknowledgments: Ensure singular title 'ACKNOWLEDGMENT'.")

        elif s == "SPRINGER" and t == "ACM":
            guide.append("1. Metadata: Add mandatory ACM Computing Classification System (CCS) block.")
            guide.append("2. Layout: Convert single-column to ACM sigconf format.")
            guide.append("3. Acknowledgments: Ensure \\begin{acks} environment is used.")

        return guide
