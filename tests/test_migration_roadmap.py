"""
Unit Tests for Cross-Venue Migration Roadmap Generator & Heading Recommendations.
"""

import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.schema import CanonicalSection
from src.document_inspector import DocumentInspector
from src.migration_roadmap import MigrationRoadmapGenerator, generate_heading_recommendations
from src.rule_engine import RuleMappingEngine


SAMPLE_IEEE_HEADINGS = [
    "Abstract",
    "Index Terms---Deep learning, document parsing, conference templates",
    "I. INTRODUCTION",
    "II. RELATED WORK AND BACKGROUND",
    "III. PROPOSED ARCHITECTURE AND SYSTEM DESIGN",
    "IV. EXPERIMENTAL SETUP AND EMPIRICAL EVALUATION",
    "V. DISCUSSION AND LIMITATIONS",
    "VI. CONCLUSION AND FUTURE WORK",
    "ACKNOWLEDGMENT",
    "REFERENCES"
]

SAMPLE_ACM_HEADINGS = [
    "ABSTRACT",
    "CCS CONCEPTS",
    "Keywords",
    "1 INTRODUCTION",
    "2 RELATED WORK",
    "3 METHODOLOGY AND FORMULATION",
    "4 EXPERIMENTAL RESULTS",
    "5 DISCUSSION",
    "6 CONCLUSION",
    "ACKNOWLEDGMENTS",
    "REFERENCES"
]


def test_roadmap_ieee_to_acm_structure_and_fields():
    """Verifies all 9 mandatory fields are present in every roadmap entry for IEEE -> ACM."""
    inspector = DocumentInspector(target_venue="ACM")
    inspection = inspector.inspect_from_headings_and_text(SAMPLE_IEEE_HEADINGS)
    
    generator = MigrationRoadmapGenerator(source_venue="IEEE", target_venue="ACM")
    roadmap = generator.generate_roadmap(inspection)
    
    assert len(roadmap) > 0
    mandatory_fields = [
        "element", "current_format", "target_format", "action",
        "reason", "rule_reference", "priority", "auto_applicable",
        "manual_review_required"
    ]
    
    for entry in roadmap:
        for field in mandatory_fields:
            assert field in entry, f"Missing field '{field}' in roadmap entry: {entry}"
            assert entry[field] is not None, f"Field '{field}' is None in entry: {entry}"
        assert entry["priority"] in ["High", "Medium", "Low"]
        assert isinstance(entry["auto_applicable"], bool)
        assert isinstance(entry["manual_review_required"], bool)
        assert entry["status"] in ["COMPLIANT", "NEEDS_CHANGE", "MANUAL_REVIEW"]


def test_roadmap_detects_acm_ccs_requirement():
    """Verifies that missing ACM CCS concepts block is flagged as High Priority Manual Review."""
    inspector = DocumentInspector(target_venue="ACM")
    # Sample paper without CCS block
    inspection = inspector.inspect_from_headings_and_text(SAMPLE_IEEE_HEADINGS)
    
    generator = MigrationRoadmapGenerator(source_venue="IEEE", target_venue="ACM")
    roadmap = generator.generate_roadmap(inspection)
    
    ccs_entries = [r for r in roadmap if "CCS" in r["element"] or "Computing Classification" in r["element"]]
    assert len(ccs_entries) >= 1
    ccs_item = ccs_entries[0]
    assert ccs_item["priority"] == "High"
    assert ccs_item["manual_review_required"] is True
    assert ccs_item["auto_applicable"] is False


def test_roadmap_springer_lncs_single_column_requirement():
    """Verifies IEEE -> Springer LNCS roadmap mandates 1-column layout transition."""
    inspector = DocumentInspector(target_venue="SPRINGER")
    inspection = inspector.inspect_from_headings_and_text(SAMPLE_IEEE_HEADINGS)
    # Simulate source was 2-column IEEE
    inspection["layout"]["columns"] = 2
    
    generator = MigrationRoadmapGenerator(source_venue="IEEE", target_venue="SPRINGER")
    roadmap = generator.generate_roadmap(inspection)
    
    col_entries = [r for r in roadmap if "Column" in r["element"]]
    assert len(col_entries) >= 1
    col_item = col_entries[0]
    assert "1-Column" in col_item["target_format"]
    assert col_item["priority"] == "High"
    assert col_item["status"] == "NEEDS_CHANGE"


def test_heading_recommendations_ieee_to_acm():
    """Verifies heading recommendation formats Roman numerals to unpunctuated Arabic numerals in ALL CAPS."""
    engine = RuleMappingEngine()
    mapped = [engine.map_heading(h, source_venue="IEEE") for h in SAMPLE_IEEE_HEADINGS]
    recs = generate_heading_recommendations(mapped, target_venue="ACM")
    
    rec_dict = {r["Original Heading"]: r for r in recs}
    
    # Check Introduction
    intro_rec = rec_dict["I. INTRODUCTION"]
    assert intro_rec["Recommended Target Heading"] == "1 INTRODUCTION"
    assert "Arabic" in intro_rec["Reason"]
    assert intro_rec["manual_review"] is False

    # Check Keywords
    kw_rec = [r for r in recs if "Index Terms" in r["Original Heading"]][0]
    assert kw_rec["Recommended Target Heading"] == "Keywords: "
    
    # Check Acknowledgment
    ack_rec = rec_dict["ACKNOWLEDGMENT"]
    assert ack_rec["Recommended Target Heading"] == "ACKNOWLEDGMENTS"


def test_heading_recommendations_acm_to_ieee():
    """Verifies heading recommendation formats Arabic numerals to Roman numerals."""
    engine = RuleMappingEngine()
    mapped = [engine.map_heading(h, source_venue="ACM") for h in SAMPLE_ACM_HEADINGS]
    recs = generate_heading_recommendations(mapped, target_venue="IEEE")
    
    rec_dict = {r["Original Heading"]: r for r in recs}
    
    assert rec_dict["1 INTRODUCTION"]["Recommended Target Heading"] == "I. INTRODUCTION"
    assert rec_dict["2 RELATED WORK"]["Recommended Target Heading"] == "II. RELATED WORK"
    assert rec_dict["ACKNOWLEDGMENTS"]["Recommended Target Heading"] == "ACKNOWLEDGMENT"


def test_heading_recommendations_ambiguous_and_unknown():
    """Verifies ambiguous headings are preserved and marked for manual review."""
    engine = RuleMappingEngine()
    
    # Ambiguous heading spanning two sections
    ambig_raw = "III. RESULTS AND DISCUSSION OF BENCHMARKS"
    mapped_ambig = engine.map_heading(ambig_raw, source_venue="IEEE")
    recs = generate_heading_recommendations([mapped_ambig], target_venue="ACM")
    
    assert len(recs) == 1
    rec = recs[0]
    assert rec["manual_review"] is True
    assert "Manual Review" in rec["Status"]
    assert ambig_raw in rec["Recommended Target Heading"]

    # Unknown custom domain heading with numbering
    custom_raw = "4. CASE STUDY ON AUTONOMOUS VEHICLES"
    mapped_custom = engine.map_heading(custom_raw, source_venue="ACM")
    recs_custom = generate_heading_recommendations([mapped_custom], target_venue="IEEE")
    
    assert len(recs_custom) == 1
    rec_c = recs_custom[0]
    assert "CASE STUDY ON AUTONOMOUS VEHICLES" in rec_c["Recommended Target Heading"]
    assert rec_c["manual_review"] is False  # formatting standardized without altering words
