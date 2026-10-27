"""
Unit tests for PDF and DOCX Document Extractor.
"""

import io
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.extractor import (
    extract_headings_from_docx,
    extract_headings_from_pdf,
    extract_headings_from_file,
    UnreadablePDFError,
    DocumentExtractionError,
)
import pypdf


class TestDocumentExtractor(unittest.TestCase):

    def setUp(self):
        self.sample_docx = os.path.join(PROJECT_ROOT, "data", "samples", "sample_manuscript.docx")
        self.sample_pdf = os.path.join(PROJECT_ROOT, "data", "samples", "sample_manuscript.pdf")
        self.scanned_pdf = os.path.join(PROJECT_ROOT, "data", "samples", "scanned_sample.pdf")

    def test_extract_headings_docx(self):
        headings = extract_headings_from_docx(self.sample_docx)
        self.assertIsInstance(headings, list)
        self.assertGreater(len(headings), 5)
        
        # Verify key canonical sections are extracted
        joined = " ".join(headings)
        self.assertIn("INTRODUCTION", joined)
        self.assertIn("METHODOLOGY", joined)
        self.assertIn("EVALUATION", joined)
        self.assertIn("REFERENCES", joined)

    def test_extract_headings_pdf(self):
        headings = extract_headings_from_pdf(self.sample_pdf)
        self.assertIsInstance(headings, list)
        self.assertGreater(len(headings), 5)
        
        joined = " ".join(headings)
        self.assertIn("Abstract", joined)
        self.assertIn("INTRODUCTION", joined)
        self.assertIn("CONCLUSION", joined)
        self.assertIn("REFERENCES", joined)

    def test_unreadable_scanned_pdf_error(self):
        with self.assertRaises(UnreadablePDFError) as ctx:
            extract_headings_from_pdf(self.scanned_pdf)
        self.assertIn("scanned document or image-only", str(ctx.exception))

    def test_blank_stream_pdf_error(self):
        # Create an in-memory blank PDF with 0 characters
        writer = pypdf.PdfWriter()
        writer.add_blank_page(width=612, height=792)
        buf = io.BytesIO()
        writer.write(buf)
        buf.seek(0)

        with self.assertRaises(UnreadablePDFError):
            extract_headings_from_pdf(buf)

    def test_universal_dispatcher_json_and_txt(self):
        # Test JSON sample
        ieee_json = os.path.join(PROJECT_ROOT, "data", "samples", "ieee_sample.json")
        h_json = extract_headings_from_file(ieee_json, "ieee_sample.json")
        self.assertGreater(len(h_json), 5)
        self.assertTrue(any("INTRODUCTION" in h for h in h_json))

        # Test DOCX sample
        h_docx = extract_headings_from_file(self.sample_docx, "sample.docx")
        self.assertGreater(len(h_docx), 5)

        # Test PDF sample
        h_pdf = extract_headings_from_file(self.sample_pdf, "sample.pdf")
        self.assertGreater(len(h_pdf), 5)

    def test_corrupted_file_handling(self):
        corrupted_bytes = io.BytesIO(b"Not a valid PDF or DOCX file content")
        with self.assertRaises(DocumentExtractionError):
            extract_headings_from_pdf(corrupted_bytes)
        with self.assertRaises(DocumentExtractionError):
            extract_headings_from_docx(corrupted_bytes)


if __name__ == "__main__":
    unittest.main()
