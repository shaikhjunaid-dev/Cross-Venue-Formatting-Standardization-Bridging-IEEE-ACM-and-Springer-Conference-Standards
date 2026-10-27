"""
Command-Line Interface (CLI) for Cross-Venue Formatting Standardization.

Usage:
    python -m src.cli --input data/samples/ieee_sample.json --target IEEE
    python -m src.cli --headings "I. INTRODUCTION" "II. RELATED WORK" "III. SYSTEM MODEL" --target ACM
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any
from .rule_engine import RuleMappingEngine
from .validator import VenueValidator
from .reporter import ReportGenerator
from .extractor import extract_headings_from_file, UnreadablePDFError
from .document_inspector import DocumentInspector
from .migration_roadmap import MigrationRoadmapGenerator, generate_heading_recommendations
from .docx_converter import DocxStandardizer


def load_input_headings(input_path: str) -> List[str]:
    """Loads heading strings from JSON, plain text, DOCX, or PDF file."""
    if input_path.lower().endswith((".pdf", ".docx")):
        return extract_headings_from_file(input_path, input_path)
    elif input_path.lower().endswith(".json"):
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # could be list of strings or list of dicts with 'heading'
                if len(data) > 0 and isinstance(data[0], dict):
                    return [d.get("heading") or d.get("raw_heading") for d in data if d.get("heading") or d.get("raw_heading")]
                return [str(item) for item in data]
            elif isinstance(data, dict) and "headings" in data:
                return data["headings"]
            else:
                raise ValueError("JSON file must be a list of headings or a dict with 'headings' key.")
    else:
        with open(input_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Venue Formatting Standardization System - Semantic Section Mapper"
    )
    parser.add_argument("--input", "-i", type=str, help="Path to input text file or JSON containing headings")
    parser.add_argument("--headings", "-H", nargs="+", help="Direct list of headings to analyze")
    parser.add_argument("--source", "-s", type=str, default="IEEE", choices=["IEEE", "ACM", "SPRINGER"],
                        help="Source venue format of the paper (default: IEEE)")
    parser.add_argument("--target", "-t", type=str, default="IEEE", choices=["IEEE", "ACM", "SPRINGER"],
                        help="Target venue format for validation (default: IEEE)")
    parser.add_argument("--output-json", "-oj", type=str, default=None, help="Path to save output JSON report")
    parser.add_argument("--output-csv", "-oc", type=str, default=None, help="Path to save output CSV report")
    parser.add_argument("--convert-docx", "-cd", type=str, default=None, help="Path to save converted/standardized DOCX manuscript")
    parser.add_argument("--output-roadmap-csv", type=str, default=None, help="Path to save actionable migration roadmap CSV")
    
    args = parser.parse_args()
    
    headings: List[str] = []
    if args.input:
        try:
            headings = load_input_headings(args.input)
        except UnreadablePDFError as e:
            print(f"[!] PDF Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[!] Error loading input file '{args.input}': {e}")
            sys.exit(1)
    elif args.headings:
        headings = args.headings
    else:
        print("[!] No input provided. Using default IEEE sample headings...")
        headings = [
            "Abstract",
            "Index Terms---Semantic mapping, IEEE templates, standardization",
            "I. INTRODUCTION",
            "II. RELATED WORK",
            "III. PROPOSED METHODOLOGY AND ARCHITECTURE",
            "IV. EXPERIMENTAL EVALUATION AND RESULTS",
            "V. DISCUSSION",
            "VI. CONCLUSION AND FUTURE WORK",
            "ACKNOWLEDGMENT",
            "REFERENCES"
        ]

    engine = RuleMappingEngine()
    validator = VenueValidator(target_venue=args.target)
    
    mapped_headings = [engine.map_heading(h, source_venue=args.source) for h in headings]
    val_result = validator.validate_document(mapped_headings)
    
    # Print console summary
    summary_text = ReportGenerator.generate_console_summary(mapped_headings, val_result)
    print(summary_text)
    
    # Cross-venue migration guide
    if args.source.upper() != args.target.upper():
        print("\n" + "=" * 80)
        migration_guide = ReportGenerator.generate_cross_venue_migration_guide(args.source, args.target, mapped_headings)
        for step in migration_guide:
            print(f"  {step}")
        print("=" * 80)

    # Detailed Cross-venue Migration Roadmap
    inspector = DocumentInspector(target_venue=args.target)
    if args.input and args.input.lower().endswith(".docx"):
        inspection = inspector.inspect_docx(args.input)
    else:
        inspection = inspector.inspect_from_headings_and_text(headings)
    
    roadmap_gen = MigrationRoadmapGenerator(source_venue=args.source, target_venue=args.target)
    roadmap_entries = roadmap_gen.generate_roadmap(inspection)

    # Save outputs if specified
    if args.output_json:
        ReportGenerator.to_json(mapped_headings, val_result, args.output_json)
        print(f"[+] Saved JSON report to: {args.output_json}")
    if args.output_csv:
        ReportGenerator.to_csv(mapped_headings, args.output_csv)
        print(f"[+] Saved CSV report to: {args.output_csv}")
    if args.output_roadmap_csv:
        ReportGenerator.roadmap_to_csv(roadmap_entries, args.output_roadmap_csv)
        print(f"[+] Saved Migration Roadmap CSV to: {args.output_roadmap_csv}")

    # DOCX Conversion
    if args.convert_docx:
        standardizer = DocxStandardizer(target_venue=args.target, source_venue=args.source)
        if args.input and args.input.lower().endswith(".docx"):
            result = standardizer.convert_docx(args.input)
        else:
            result = standardizer.create_docx_from_headings_and_text(headings)
        
        os.makedirs(os.path.dirname(os.path.abspath(args.convert_docx)), exist_ok=True)
        with open(args.convert_docx, "wb") as f_out:
            f_out.write(result["converted_docx_bytes"])
        
        rep = result["conversion_report"]
        print("\n" + "=" * 80)
        print(" BEFORE-AND-AFTER DOCX CONVERSION REPORT")
        print("=" * 80)
        print(f"  Source Venue: {rep['source_venue']} -> Target Venue: {rep['target_venue']} ({rep['target_full_name']})")
        print(f"  Official Template: {rep['official_template_source']}")
        print(f"  Issues Detected:   {rep['total_issues_detected']}")
        print(f"  Issues Corrected:  {rep['issues_successfully_corrected']}")
        print(f"  Already Compliant: {rep['issues_already_compliant']}")
        print(f"  Manual Review:     {rep['issues_requiring_manual_review']}")
        print(f"  Content Status:    {rep['preservation_status']}")
        print("-" * 80)
        print(f"  Applied Changes ({len(rep['applied_changes'])}):")
        for ch in rep['applied_changes']:
            print(f"    * [{ch.get('category', 'General')}] {ch.get('element')}: '{ch.get('before')}' -> '{ch.get('after')}' ({ch.get('action_applied')})")
        if rep['manual_review_items']:
            print(f"  Items Requiring Manual Author Attention ({len(rep['manual_review_items'])}):")
            for mi in rep['manual_review_items']:
                print(f"    ! {mi.get('element')}: {mi.get('action_required')} [Priority: {mi.get('priority')}]")
        print("=" * 80)
        print(f"[+] Saved standardized DOCX manuscript to: {args.convert_docx}")


if __name__ == "__main__":
    main()
