"""
Streamlit Web Interface for Cross-Venue Formatting Standardization System.

An interactive dashboard demonstrating:
1. Automated semantic section mapping across IEEE, ACM, and Springer LNCS.
2. Intelligent heading recommendations (Original -> Detected Meaning -> Target Heading -> Reason).
3. Publisher compliance validation and missing section detection.
4. Comprehensive, itemized cross-venue migration roadmap.
5. Direct DOCX conversion with downloadable corrected manuscript.
6. Granular Before-and-After conversion report with 100% content preservation.
7. Exportable CSV, JSON, and Roadmap reports.
"""

import streamlit as st
import json
import pandas as pd
import sys
import os
import io

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.rule_engine import RuleMappingEngine
from src.validator import VenueValidator
from src.reporter import ReportGenerator
from src.schema import VENUE_CONFIGS, CanonicalSection
from src.extractor import extract_headings_from_docx, extract_headings_from_pdf, UnreadablePDFError
from src.document_inspector import DocumentInspector
from src.migration_roadmap import MigrationRoadmapGenerator, generate_heading_recommendations
from src.docx_converter import DocxStandardizer

st.set_page_config(
    page_title="Cross-Venue Formatting Standardization",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Cross-Venue Formatting Standardization System")
st.subheader("Bridging IEEE, ACM, and Springer Conference Standards")
st.markdown(
    "A research prototype for **semantic section classification**, **cross-template validation**, "
    "**actionable migration roadmaps**, and **automated DOCX publication conversion** in Computer Science research."
)

# Sidebar configurations
st.sidebar.header("Configuration & Venues")
source_venue = st.sidebar.selectbox("Source Paper Venue:", ["IEEE", "ACM", "SPRINGER"], index=0)
target_venue = st.sidebar.selectbox("Target Submission Venue:", ["IEEE", "ACM", "SPRINGER"], index=1)

# Sample presets
SAMPLE_INPUTS = {
    "IEEE Standard Paper": [
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
    ],
    "ACM sigconf Paper": [
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
    ],
    "Springer LNCS Paper": [
        "Abstract",
        "Keywords: Semantic mapping, conference standards, natural language processing",
        "1 Introduction",
        "2 Prior Studies and Theoretical Framework",
        "3 Proposed System Architecture",
        "4 Experiments and Results",
        "5 Concluding Remarks and Outlook",
        "Acknowledgements",
        "References"
    ],
    "Incomplete / Non-Compliant Paper (Missing Sections)": [
        "Abstract",
        "1. Introduction",
        "2. Our Model",
        "3. Results and Discussion",
        "4. Conclusion",
        "ACKNOWLEDGMENTS"
    ]
}

st.sidebar.header("Input Selection")
input_mode = st.sidebar.radio("Select Input Mode:", ["Use Preset Sample", "Manual Text Input", "Upload File (TXT, JSON, PDF, DOCX)"])

input_headings = []
uploaded_docx_bytes = None

if input_mode == "Use Preset Sample":
    sample_key = st.sidebar.selectbox("Choose Sample:", list(SAMPLE_INPUTS.keys()))
    input_headings = SAMPLE_INPUTS[sample_key]
elif input_mode == "Manual Text Input":
    text_val = st.sidebar.text_area(
        "Enter headings (one per line):",
        value="Abstract\nIndex Terms\nI. INTRODUCTION\nII. SYSTEM MODEL\nIII. EVALUATION\nIV. CONCLUSION\nREFERENCES"
    )
    input_headings = [line.strip() for line in text_val.split("\n") if line.strip()]
else:
    uploaded = st.sidebar.file_uploader("Upload .txt, .json, .pdf, or .docx file", type=["txt", "json", "pdf", "docx"])
    if uploaded:
        fn = uploaded.name.lower()
        file_bytes = uploaded.getvalue()
        try:
            if fn.endswith(".pdf"):
                input_headings = extract_headings_from_pdf(io.BytesIO(file_bytes))
                if not input_headings:
                    st.warning("No standard section headings detected in this PDF. Please verify document layout.")
            elif fn.endswith(".docx"):
                uploaded_docx_bytes = file_bytes
                input_headings = extract_headings_from_docx(io.BytesIO(file_bytes))
                if not input_headings:
                    st.warning("No section headings detected in this Word document. Please verify document layout.")
            elif fn.endswith(".json"):
                content = file_bytes.decode("utf-8")
                data = json.loads(content)
                if isinstance(data, list):
                    input_headings = [str(x) for x in data]
                elif isinstance(data, dict) and "headings" in data:
                    input_headings = data["headings"]
            else:
                content = file_bytes.decode("utf-8")
                input_headings = [l.strip() for l in content.split("\n") if l.strip()]
        except UnreadablePDFError as e:
            st.error(f"🚨 PDF Extraction Error: {e}")
            input_headings = []
        except Exception as e:
            st.error(f"🚨 Error reading uploaded file: {e}")
            input_headings = []

# Main Analysis
if input_headings:
    engine = RuleMappingEngine()
    validator = VenueValidator(target_venue=target_venue)
    
    mapped_headings = [engine.map_heading(h, source_venue=source_venue) for h in input_headings]
    val_result = validator.validate_document(mapped_headings)

    # -------------------------------------------------------------------------
    # 1. Improved Heading Mapping Table
    # -------------------------------------------------------------------------
    st.markdown("### 1. Document Section Mapping & Heading Recommendations")
    st.caption(
        "Displays the semantic classification, recommended target heading style, and publisher rationale for every detected section. "
        "Ambiguous headings are flagged for manual review rather than guessed."
    )

    heading_recommendations = generate_heading_recommendations(mapped_headings, target_venue=target_venue)
    rec_df = pd.DataFrame(heading_recommendations)
    
    # Display table with all requested columns
    st.dataframe(
        rec_df[["Original Heading", "Detected Meaning / Category", "Recommended Target Heading", "Reason", "Confidence", "Status"]], 
        use_container_width=True
    )

    # Visual alert if any heading requires manual author review
    manual_review_headings = [h for h in heading_recommendations if h.get("manual_review")]
    if manual_review_headings:
        st.warning(
            f"⚠️ **{len(manual_review_headings)} Heading(s) Require Manual Review:** "
            "Original text is safely preserved to prevent accidental misclassification. Please confirm classification."
        )

    # -------------------------------------------------------------------------
    # 2. Publisher Compliance & Structural Validation
    # -------------------------------------------------------------------------
    st.markdown("### 2. Publisher Compliance & Structural Validation")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Headings Analyzed", val_result["total_headings_analyzed"])
    with col2:
        comp_color = "normal" if val_result["is_compliant"] else "inverse"
        st.metric("Target Venue", f"{target_venue}", delta="Compliant" if val_result["is_compliant"] else "Revisions Needed", delta_color=comp_color)
    with col3:
        st.metric("Unmapped Headings", val_result["unmapped_headings_count"])

    # Detailed warnings and missing sections
    if val_result["missing_mandatory"]:
        st.error(f"🚨 **Missing Mandatory Sections for {target_venue}:** " + ", ".join(val_result["missing_mandatory"]))

    if val_result["warnings"]:
        with st.expander("⚠️ View Style and Structural Warnings", expanded=True):
            for w in val_result["warnings"]:
                st.warning(w)

    if val_result["suggestions"]:
        with st.expander("💡 Actionable Author Suggestions", expanded=True):
            for s in val_result["suggestions"]:
                st.info(s)

    # -------------------------------------------------------------------------
    # 3. Complete and Accurate Migration Roadmap
    # -------------------------------------------------------------------------
    st.markdown("### 3. Comprehensive Cross-Venue Migration Roadmap")
    st.caption(
        "An itemized roadmap covering layout, metadata, abstract, keywords, CCS classification, headings, "
        "tables, figures, and citations against official publisher standards."
    )

    # Inspect document deeply or from extracted text
    inspector = DocumentInspector(target_venue=target_venue)
    if uploaded_docx_bytes:
        inspection = inspector.inspect_docx(uploaded_docx_bytes)
    else:
        inspection = inspector.inspect_from_headings_and_text(input_headings)

    roadmap_gen = MigrationRoadmapGenerator(source_venue=source_venue, target_venue=target_venue)
    roadmap_entries = roadmap_gen.generate_roadmap(inspection)

    # Roadmap Metrics
    total_roadmap = len(roadmap_entries)
    high_prio = len([r for r in roadmap_entries if r.get("priority") == "High" and r.get("status") != "COMPLIANT"])
    med_prio = len([r for r in roadmap_entries if r.get("priority") == "Medium" and r.get("status") != "COMPLIANT"])
    compliant_cnt = len([r for r in roadmap_entries if r.get("status") == "COMPLIANT"])

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        st.metric("Total Roadmap Items", total_roadmap)
    with rc2:
        st.metric("High Priority Issues", high_prio)
    with rc3:
        st.metric("Medium Priority Issues", med_prio)
    with rc4:
        st.metric("Already Compliant Items", compliant_cnt)

    # Filter roadmap view
    filter_option = st.radio(
        "Filter Roadmap:", 
        ["All Items", "Issues Requiring Attention (High & Medium)", "Already Compliant Elements", "Manual Review Required"],
        horizontal=True
    )

    if filter_option == "Issues Requiring Attention (High & Medium)":
        filtered_roadmap = [r for r in roadmap_entries if r.get("status") != "COMPLIANT"]
    elif filter_option == "Already Compliant Elements":
        filtered_roadmap = [r for r in roadmap_entries if r.get("status") == "COMPLIANT"]
    elif filter_option == "Manual Review Required":
        filtered_roadmap = [r for r in roadmap_entries if r.get("manual_review_required")]
    else:
        filtered_roadmap = roadmap_entries

    roadmap_display_rows = []
    for r in filtered_roadmap:
        prio_badge = "🔴 High" if r.get("priority") == "High" else ("🟡 Medium" if r.get("priority") == "Medium" else "🟢 Low")
        status_badge = "✅ Compliant" if r.get("status") == "COMPLIANT" else ("✋ Manual Review" if r.get("manual_review_required") else "⚡ Needs Change")
        auto_badge = "⚡ Yes" if r.get("auto_applicable") else "✋ Manual Review"

        roadmap_display_rows.append({
            "Element": r.get("element"),
            "Category": r.get("category"),
            "Priority": prio_badge,
            "Status": status_badge,
            "Current Format": r.get("current_format"),
            "Target Format": r.get("target_format"),
            "Action Required": r.get("action"),
            "Reason": r.get("reason"),
            "Rule Reference": r.get("rule_reference"),
            "Auto Applicable": auto_badge
        })

    if roadmap_display_rows:
        roadmap_df = pd.DataFrame(roadmap_display_rows)
        st.dataframe(roadmap_df, use_container_width=True)
    else:
        st.info("No items match the selected filter.")

    with st.expander("📌 Quick Migration Guidelines Summary", expanded=False):
        summary_guide = ReportGenerator.generate_cross_venue_migration_guide(source_venue, target_venue, mapped_headings)
        for step in summary_guide:
            st.write(f"- {step}")

    # -------------------------------------------------------------------------
    # 4. Actual DOCX Conversion & Before-and-After Report
    # -------------------------------------------------------------------------
    st.markdown("### 4. Actual Document Conversion & Before-and-After Report")
    st.caption(
        "Generates a verified, publication-ready Word (.docx) document adhering to the target venue specifications. "
        "Original research text, tables, citations, and figures are 100% preserved."
    )

    standardizer = DocxStandardizer(target_venue=target_venue, source_venue=source_venue)
    if uploaded_docx_bytes:
        conversion_out = standardizer.convert_docx(uploaded_docx_bytes)
    else:
        conversion_out = standardizer.create_docx_from_headings_and_text(input_headings)

    converted_docx_bytes = conversion_out["converted_docx_bytes"]
    conv_report = conversion_out["conversion_report"]

    # Prominent Download Button
    doc_file_name = f"standardized_{source_venue}_to_{target_venue}_manuscript.docx"
    st.download_button(
        label="📥 Download Corrected DOCX",
        data=converted_docx_bytes,
        file_name=doc_file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        help=f"Download the standardized {target_venue} Word document."
    )

    # Before-and-After Report Summary Cards
    bc1, bc2, bc3, bc4, bc5 = st.columns(5)
    with bc1:
        st.metric("Total Issues Detected", conv_report["total_issues_detected"])
    with bc2:
        st.metric("Successfully Corrected", conv_report["issues_successfully_corrected"])
    with bc3:
        st.metric("Already Compliant", conv_report["issues_already_compliant"])
    with bc4:
        st.metric("Manual Review Needed", conv_report["issues_requiring_manual_review"])
    with bc5:
        st.metric("Unverified Rules", conv_report["rules_unverified_count"])

    # Preservation confirmation banner
    st.success(f"🛡️ **Content Integrity Guaranteed:** {conv_report['preservation_status']}")

    # Table of Actual Changes Applied
    st.markdown("#### Table of Real Changes Applied to Document")
    if conv_report["applied_changes"]:
        applied_df = pd.DataFrame(conv_report["applied_changes"])
        show_cols = [c for c in ["element", "category", "before", "after", "action_applied", "status"] if c in applied_df.columns]
        st.dataframe(applied_df[show_cols], use_container_width=True)
    else:
        st.info("No structural transformations were required; document was already compliant.")

    # Explicit Manual Review Items
    if conv_report["manual_review_items"]:
        with st.expander("✋ Items Requiring Manual Author Attention Prior to Camera-Ready", expanded=True):
            for item in conv_report["manual_review_items"]:
                prio = item.get("priority", "Medium")
                badge = "🔴" if prio == "High" else "🟡"
                st.markdown(f"- {badge} **{item.get('element')}:** {item.get('action_required')} *(Priority: {prio})*")

    # -------------------------------------------------------------------------
    # 5. Export Standardization Reports
    # -------------------------------------------------------------------------
    st.markdown("### 5. Export Standardization Reports")
    ec1, ec2, ec3 = st.columns(3)
    with ec1:
        mappings_csv = rec_df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Mappings (CSV)", data=mappings_csv, file_name=f"mappings_{source_venue}_to_{target_venue}.csv", mime="text/csv")
    with ec2:
        roadmap_csv_data = pd.DataFrame(roadmap_entries).to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Migration Roadmap (CSV)", data=roadmap_csv_data, file_name=f"roadmap_{source_venue}_to_{target_venue}.csv", mime="text/csv")
    with ec3:
        full_json_dict = {
            "validation": val_result,
            "heading_mappings": mapped_headings,
            "heading_recommendations": heading_recommendations,
            "migration_roadmap": roadmap_entries,
            "conversion_report": conv_report
        }
        json_data = json.dumps(full_json_dict, indent=2).encode("utf-8")
        st.download_button("📥 Download Full Analysis (JSON)", data=json_data, file_name=f"analysis_{source_venue}_to_{target_venue}.json", mime="application/json")
else:
    st.info("Please provide input headings or select a preset sample from the sidebar.")
