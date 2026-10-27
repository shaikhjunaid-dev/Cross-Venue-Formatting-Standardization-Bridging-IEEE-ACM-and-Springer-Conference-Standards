"""
Unit Tests for DOCX Conversion Engine, Target Template Formatting, and Content Preservation.
"""

import io
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import docx
from docx.shared import Inches, Pt

from src.docx_converter import DocxStandardizer


SAMPLE_MANUSCRIPT_PATH = os.path.join("data", "samples", "sample_manuscript.docx")


def create_mock_docx(source_venue="IEEE") -> bytes:
    """Helper to build a pristine mock DOCX in memory with paragraphs and tables."""
    doc = docx.Document()
    
    # Title & Authors
    doc.add_paragraph("Cross-Venue Standardization in Academic Systems")
    doc.add_paragraph("Author One, Author Two\nUniversity of Computing\ncontact@university.edu")
    
    if source_venue == "IEEE":
        doc.add_paragraph("Abstract---This paper presents an automated cross-venue standardizer.")
        doc.add_paragraph("Index Terms---standardization, meta-templates, conference formatting")
        doc.add_paragraph("I. INTRODUCTION")
        doc.add_paragraph("Research paper formatting consumes an average of 52 hours per accepted manuscript [1].")
        doc.add_paragraph("II. RELATED WORK")
        doc.add_paragraph("Ahmed and Afzal [2] proposed section mapping methods using heuristic regex.")
        doc.add_paragraph("III. PROPOSED ARCHITECTURE")
        doc.add_paragraph("Our system uses rule engines to bridge IEEE, ACM, and Springer formats.")
        doc.add_paragraph("ACKNOWLEDGMENT")
        doc.add_paragraph("The authors thank the research supervisors for guidance.")
        doc.add_paragraph("REFERENCES")
        doc.add_paragraph("[1] Y. Jiang et al., PLOS ONE 2019.")
    elif source_venue == "ACM":
        doc.add_paragraph("ABSTRACT\nThis paper presents an automated cross-venue standardizer.")
        doc.add_paragraph("Keywords: standardization, meta-templates, conference formatting")
        doc.add_paragraph("1 INTRODUCTION")
        doc.add_paragraph("Research paper formatting consumes an average of 52 hours per accepted manuscript [1].")
        doc.add_paragraph("2 RELATED WORK")
        doc.add_paragraph("Ahmed and Afzal [2] proposed section mapping methods.")
        doc.add_paragraph("ACKNOWLEDGMENTS")
        doc.add_paragraph("The authors thank the supervisors.")
        doc.add_paragraph("REFERENCES")
        doc.add_paragraph("[1] Y. Jiang et al., PLOS ONE 2019.")
    
    # Add a sample data table
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Metric"
    table.cell(0, 1).text = "Value"
    table.cell(1, 0).text = "Accuracy"
    table.cell(1, 1).text = "95.5%"

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_convert_docx_ieee_to_acm():
    """Tests converting IEEE Word document to ACM sigconf format."""
    input_bytes = create_mock_docx(source_venue="IEEE")
    initial_doc = docx.Document(io.BytesIO(input_bytes))
    orig_p_count = len(initial_doc.paragraphs)
    orig_tbl_count = len(initial_doc.tables)
    
    standardizer = DocxStandardizer(target_venue="ACM", source_venue="IEEE")
    res = standardizer.convert_docx(input_bytes)
    
    assert "converted_docx_bytes" in res
    assert "conversion_report" in res
    
    rep = res["conversion_report"]
    assert rep["source_venue"] == "IEEE"
    assert rep["target_venue"] == "ACM"
    assert rep["issues_successfully_corrected"] >= 4
    
    # Reopen converted DOCX and verify elements
    converted_doc = docx.Document(io.BytesIO(res["converted_docx_bytes"]))
    converted_texts = [p.text.strip() for p in converted_doc.paragraphs if p.text.strip()]
    
    # Verify headings converted to ACM Arabic ALL CAPS
    assert any("1 INTRODUCTION" in t for t in converted_texts)
    assert any("2 RELATED WORK" in t for t in converted_texts)
    assert any("3 PROPOSED ARCHITECTURE" in t for t in converted_texts)
    
    # Verify ACKNOWLEDGMENTS plural
    assert any("ACKNOWLEDGMENTS" in t for t in converted_texts)
    
    # Verify Keywords label
    assert any(t.startswith("Keywords:") for t in converted_texts)
    
    # Verify ACM CCS notice was inserted
    assert any("ACM CCS CONCEPTS" in t for t in converted_texts)
    
    # Verify table preserved
    assert len(converted_doc.tables) == orig_tbl_count
    assert converted_doc.tables[0].cell(1, 1).text == "95.5%"
    
    # Verify content preservation (original research text still present)
    assert any("52 hours per accepted manuscript" in t for t in converted_texts)


def test_convert_docx_acm_to_ieee():
    """Tests converting ACM Word document to IEEE format."""
    input_bytes = create_mock_docx(source_venue="ACM")
    
    standardizer = DocxStandardizer(target_venue="IEEE", source_venue="ACM")
    res = standardizer.convert_docx(input_bytes)
    
    converted_doc = docx.Document(io.BytesIO(res["converted_docx_bytes"]))
    converted_texts = [p.text.strip() for p in converted_doc.paragraphs if p.text.strip()]
    
    # Verify headings converted to IEEE Roman numerals
    assert any("I. INTRODUCTION" in t for t in converted_texts)
    assert any("II. RELATED WORK" in t for t in converted_texts)
    
    # Verify singular ACKNOWLEDGMENT
    assert any(t == "ACKNOWLEDGMENT" for t in converted_texts)
    
    # Verify Index Terms prefix
    assert any(t.startswith("Index Terms---") for t in converted_texts)


def test_convert_docx_ieee_to_springer():
    """Tests converting IEEE Word document to Springer LNCS format."""
    input_bytes = create_mock_docx(source_venue="IEEE")
    
    standardizer = DocxStandardizer(target_venue="SPRINGER", source_venue="IEEE")
    res = standardizer.convert_docx(input_bytes)
    
    converted_doc = docx.Document(io.BytesIO(res["converted_docx_bytes"]))
    converted_texts = [p.text.strip() for p in converted_doc.paragraphs if p.text.strip()]
    
    # Verify Title Case headings
    assert any("1 Introduction" in t for t in converted_texts)
    assert any("2 Related Work" in t for t in converted_texts)
    
    # Verify British spelling Acknowledgements
    assert any("Acknowledgements" in t for t in converted_texts)
    
    # Verify single column across sections
    for sec in converted_doc.sections:
        cols_elem = sec._sectPr.xpath('./w:cols')
        if cols_elem:
            assert cols_elem[0].get(docx.oxml.ns.qn('w:num')) in [None, "1"]


def test_create_docx_from_headings_and_text():
    """Tests generating a new Word document from a list of headings and presets."""
    headings = [
        "Abstract",
        "Index Terms---Semantic classification, document engineering",
        "I. INTRODUCTION",
        "II. RELATED WORK",
        "III. METHODOLOGY",
        "ACKNOWLEDGMENT",
        "REFERENCES"
    ]
    standardizer = DocxStandardizer(target_venue="ACM", source_venue="IEEE")
    res = standardizer.create_docx_from_headings_and_text(headings)
    
    assert "converted_docx_bytes" in res
    doc = docx.Document(io.BytesIO(res["converted_docx_bytes"]))
    
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    assert any("1 INTRODUCTION" in t for t in texts)
    assert any("2 RELATED WORK" in t for t in texts)
    assert any("3 METHODOLOGY" in t for t in texts)
    assert any("ACKNOWLEDGMENTS" in t for t in texts)
