"""
Unit tests for RuleMappingEngine and Normalizer using Python unittest.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.normalizer import normalize_heading
from src.rule_engine import RuleMappingEngine
from src.schema import CanonicalSection


class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.engine = RuleMappingEngine()

    def test_normalizer_roman(self):
        res = normalize_heading("I. INTRODUCTION")
        self.assertEqual(res["cleaned"], "introduction")
        self.assertEqual(res["numbering_type"], "ROMAN")
        self.assertEqual(res["level"], 1)

    def test_normalizer_arabic(self):
        res = normalize_heading("3.2.1 Empirical Results:")
        self.assertEqual(res["cleaned"], "empirical results")
        self.assertEqual(res["numbering_type"], "ARABIC_HIERARCHICAL")
        self.assertEqual(res["level"], 3)

    def test_normalizer_clean_punctuation(self):
        res = normalize_heading("Index Terms---")
        self.assertEqual(res["cleaned"], "index terms")

    def test_rule_mapping_standard_sections(self):
        m_intro = self.engine.map_heading("I. INTRODUCTION")
        self.assertEqual(m_intro["canonical_section"], CanonicalSection.INTRODUCTION.value)
        self.assertGreaterEqual(m_intro["confidence"], 0.95)
        self.assertFalse(m_intro["is_ambiguous"])

        m_eval = self.engine.map_heading("IV. EXPERIMENTAL EVALUATION")
        self.assertEqual(m_eval["canonical_section"], CanonicalSection.EVALUATION.value)

        m_ack = self.engine.map_heading("ACKNOWLEDGMENT")
        self.assertEqual(m_ack["canonical_section"], CanonicalSection.ACKNOWLEDGMENTS.value)

    def test_compound_section_handling(self):
        m_compound = self.engine.map_heading("IV. Results and Discussion")
        self.assertEqual(m_compound["canonical_section"], CanonicalSection.EVALUATION.value)
        self.assertEqual(m_compound["secondary_section"], CanonicalSection.DISCUSSION.value)
        self.assertTrue(m_compound["is_ambiguous"])
        self.assertTrue(m_compound["is_compound"])

    def test_unmapped_section_handling(self):
        m_unknown = self.engine.map_heading("Smart Grid Deployment in Metropolitan Cities")
        self.assertEqual(m_unknown["canonical_section"], CanonicalSection.UNKNOWN.value)
        self.assertEqual(m_unknown["confidence"], 0.0)
        self.assertFalse(m_unknown["is_ambiguous"])


if __name__ == "__main__":
    unittest.main()
