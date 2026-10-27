"""
Unit tests for VenueValidator using Python unittest.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.rule_engine import RuleMappingEngine
from src.validator import VenueValidator
from src.schema import CanonicalSection


class TestVenueValidator(unittest.TestCase):

    def setUp(self):
        self.engine = RuleMappingEngine()

    def test_validator_detects_missing_mandatory(self):
        validator = VenueValidator("IEEE")
        
        # Paper missing Conclusion and References
        headings = ["Abstract", "Index Terms", "I. INTRODUCTION", "II. METHODOLOGY", "III. EVALUATION"]
        mapped = [self.engine.map_heading(h) for h in headings]
        val = validator.validate_document(mapped)
        
        self.assertFalse(val["is_compliant"])
        self.assertIn(CanonicalSection.CONCLUSION.value, val["missing_mandatory"])
        self.assertIn(CanonicalSection.REFERENCES.value, val["missing_mandatory"])

    def test_validator_detects_ieee_plural_acknowledgments(self):
        validator = VenueValidator("IEEE")
        
        headings = [
            "Abstract", "Index Terms", "I. INTRODUCTION", "II. METHODOLOGY",
            "III. EVALUATION", "IV. CONCLUSION", "ACKNOWLEDGMENTS", "REFERENCES"
        ]
        mapped = [self.engine.map_heading(h) for h in headings]
        val = validator.validate_document(mapped)
        
        ack_warnings = [w for w in val["warnings"] if "singular" in w.lower() or "plural" in w.lower()]
        self.assertGreater(len(ack_warnings), 0)

    def test_validator_detects_sequence_issue(self):
        validator = VenueValidator("IEEE")
        
        headings = [
            "Abstract", "Index Terms", "I. METHODOLOGY", "II. INTRODUCTION",
            "III. EVALUATION", "IV. CONCLUSION", "ACKNOWLEDGMENT", "REFERENCES"
        ]
        mapped = [self.engine.map_heading(h) for h in headings]
        val = validator.validate_document(mapped)
        
        self.assertGreater(len(val["sequence_issues"]), 0)
        self.assertTrue(any("Introduction appears after Methodology" in issue for issue in val["sequence_issues"]))


if __name__ == "__main__":
    unittest.main()
