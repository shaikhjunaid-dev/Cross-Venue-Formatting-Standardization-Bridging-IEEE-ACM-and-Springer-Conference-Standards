"""
Comprehensive Migration Roadmap Generator.

Generates complete, actionable, itemized migration roadmap entries comparing
all detected document elements against verified target publisher specifications
(IEEE, ACM, Springer LNCS).
"""

from typing import Dict, List, Any
from .venue_specs import VENUE_SPECIFICATIONS
from .schema import CanonicalSection


class MigrationRoadmapGenerator:
    """Produces fine-grained, element-by-element cross-venue migration roadmaps."""

    def __init__(self, source_venue: str, target_venue: str):
        self.source_venue = source_venue.upper()
        self.target_venue = target_venue.upper()
        self.source_spec = VENUE_SPECIFICATIONS.get(self.source_venue, VENUE_SPECIFICATIONS["IEEE"])
        self.target_spec = VENUE_SPECIFICATIONS.get(self.target_venue, VENUE_SPECIFICATIONS["ACM"])

    def generate_roadmap(self, inspection: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes document inspection report and outputs a complete list of 
        actionable roadmap entries across all academic paper dimensions.
        """
        roadmap: List[Dict[str, Any]] = []

        # 1. Page Layout & Columns
        self._check_layout(inspection, roadmap)

        # 2. Paper Title & Authors
        self._check_title_and_authors(inspection, roadmap)

        # 3. Abstract Section
        self._check_abstract(inspection, roadmap)

        # 4. Keywords and ACM CCS Concepts
        self._check_keywords_and_ccs(inspection, roadmap)

        # 5. Section Headings & Hierarchy
        self._check_headings(inspection, roadmap)

        # 6. Acknowledgments
        self._check_acknowledgments(inspection, roadmap)

        # 7. Tables and Figures
        self._check_tables_and_figures(inspection, roadmap)

        # 8. Citations and References
        self._check_citations_and_references(inspection, roadmap)

        return roadmap

    # -------------------------------------------------------------------------
    # Dimension Checkers
    # -------------------------------------------------------------------------

    def _check_layout(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        layout = insp.get("layout", {})
        cur_cols = layout.get("columns", 1)
        tgt_cols = self.target_spec["layout"]["columns"]
        tgt_font = self.target_spec["layout"]["font_family"]
        tgt_size = self.target_spec["layout"]["body_font_size_pt"]

        if cur_cols != tgt_cols:
            roadmap.append({
                "element": "Document Page Layout (Columns)",
                "category": "Layout & Typography",
                "current_format": f"{cur_cols}-Column Layout",
                "target_format": f"{tgt_cols}-Column Layout ({self.target_venue} standard)",
                "action": f"Switch document body section from {cur_cols} column(s) to {tgt_cols} column(s) with {self.target_spec['layout'].get('column_gutter_in', 0.25)}in gutter.",
                "reason": f"{self.target_venue} conference standard explicitly mandates a {tgt_cols}-column layout for proceedings publication.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Page Layout",
                "priority": "High",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
        else:
            roadmap.append({
                "element": "Document Page Layout (Columns)",
                "category": "Layout & Typography",
                "current_format": f"{cur_cols}-Column Layout",
                "target_format": f"{tgt_cols}-Column Layout",
                "action": "Maintain existing column layout.",
                "reason": f"Document already complies with {self.target_venue}'s {tgt_cols}-column specification.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Page Layout",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })

        # Margins & Base Typography
        cur_top = layout.get("margin_top_in", 1.0)
        tgt_top = self.target_spec["layout"]["margin_top_in"]
        tgt_side = self.target_spec["layout"]["margin_left_in"]
        if abs(cur_top - tgt_top) > 0.1:
            roadmap.append({
                "element": "Page Margins & Text Area",
                "category": "Layout & Typography",
                "current_format": f"Top margin: {cur_top}in, Sides: {layout.get('margin_left_in', 1.0)}in",
                "target_format": f"Top: {tgt_top}in, Sides: {tgt_side}in (Text Width: {self.target_spec['layout'].get('column_width_in', 3.5)}in)",
                "action": f"Adjust page setup margins to Top={tgt_top}in, Bottom={self.target_spec['layout']['margin_bottom_in']}in, Left/Right={tgt_side}in.",
                "reason": f"Ensures manuscript stays strictly within {self.target_venue}'s printable boundary area.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Margins",
                "priority": "Medium",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
        else:
            roadmap.append({
                "element": "Page Margins & Text Area",
                "category": "Layout & Typography",
                "current_format": f"Top: {cur_top}in, Sides: {layout.get('margin_left_in', 1.0)}in",
                "target_format": f"Top: {tgt_top}in, Sides: {tgt_side}in",
                "action": "Maintain current page margins.",
                "reason": f"Margins match {self.target_venue} allowable boundaries.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Margins",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })

    def _check_title_and_authors(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        title = insp.get("title", {})
        authors = insp.get("authors", {})
        
        # Title size
        tgt_title_size = self.target_spec["title"]["font_size_pt"]
        cur_title_size = title.get("font_size_pt")
        if cur_title_size and abs(cur_title_size - tgt_title_size) > 1.5:
            roadmap.append({
                "element": "Paper Title Typography",
                "category": "Metadata & Frontmatter",
                "current_format": f"{cur_title_size}pt Title",
                "target_format": f"{tgt_title_size}pt Bold {self.target_spec['title']['font_family']}",
                "action": f"Set title font size to {tgt_title_size}pt bold centered.",
                "reason": f"{self.target_venue} specifies {tgt_title_size}pt for paper titles.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Title Specifications",
                "priority": "Medium",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })

        # Author Metadata & ORCID
        if self.target_venue == "ACM" and not authors.get("has_orcid", False):
            roadmap.append({
                "element": "Author Information & ORCID IDs",
                "category": "Metadata & Frontmatter",
                "current_format": "Author block without verified ORCID identifier",
                "target_format": "Author block including 16-digit ORCID URI for corresponding authors",
                "action": "Author must add valid ORCID iD (e.g., https://orcid.org/0000-0002-XXXX-XXXX) in author block.",
                "reason": "ACM Open Access model strongly requires or mandates ORCID identifiers for all published authors.",
                "rule_reference": "ACM Publications Policy on Author Identification (2024)",
                "priority": "High",
                "auto_applicable": False,
                "manual_review_required": True,
                "status": "MANUAL_REVIEW",
                "is_verified_rule": True
            })
        elif self.target_venue == "IEEE":
            roadmap.append({
                "element": "Author Affiliation Structure",
                "category": "Metadata & Frontmatter",
                "current_format": "Standard author block",
                "target_format": "Centered columns with Name, Dept, University, City, Country, Email",
                "action": "Format author entries into parallel centered columns across top of page 1.",
                "reason": "IEEE 2-column conference format requires side-by-side author blocks under title.",
                "rule_reference": "IEEE Author Center - Author Information Layout",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT" if authors.get("author_block_detected") else "NEEDS_CHANGE",
                "is_verified_rule": True
            })

    def _check_abstract(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        abstract = insp.get("abstract", {})
        if not abstract.get("present", False):
            roadmap.append({
                "element": "Abstract Section",
                "category": "Metadata & Frontmatter",
                "current_format": "Missing",
                "target_format": self.target_spec["abstract"]["lead_in"],
                "action": "Author must insert an Abstract summarizing background, methods, results, and conclusion.",
                "reason": f"{self.target_venue} proceedings strictly require an abstract on page 1.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Abstract Requirements",
                "priority": "High",
                "auto_applicable": False,
                "manual_review_required": True,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
            return

        cur_lead = abstract.get("lead_in", "")
        tgt_lead = self.target_spec["abstract"]["lead_in"]
        
        if cur_lead != tgt_lead:
            roadmap.append({
                "element": "Abstract Heading Lead-in Style",
                "category": "Metadata & Frontmatter",
                "current_format": f"Heading formatted as '{cur_lead}'",
                "target_format": f"Heading formatted as '{tgt_lead}' ({self.target_spec['abstract']['lead_in_format']})",
                "action": f"Rename lead-in heading to '{tgt_lead}' and apply target font style.",
                "reason": f"{self.target_venue} guidelines require '{tgt_lead}' lead-in format.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Abstract Style",
                "priority": "Medium",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
        else:
            roadmap.append({
                "element": "Abstract Heading Lead-in Style",
                "category": "Metadata & Frontmatter",
                "current_format": f"'{cur_lead}'",
                "target_format": f"'{tgt_lead}'",
                "action": "Maintain existing abstract heading.",
                "reason": f"Abstract heading complies with {self.target_venue} formatting.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Abstract Style",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })

        # Check word count
        words = abstract.get("word_count", 0)
        max_words = self.target_spec["abstract"].get("max_words", 250)
        min_words = self.target_spec["abstract"].get("min_words", 0)
        if words > max_words:
            roadmap.append({
                "element": "Abstract Word Count",
                "category": "Metadata & Frontmatter",
                "current_format": f"{words} words",
                "target_format": f"Maximum {max_words} words",
                "action": f"Condense abstract text by approx {words - max_words} words.",
                "reason": f"{self.target_venue} guidelines recommend or enforce an abstract length under {max_words} words.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Abstract Limits",
                "priority": "Medium",
                "auto_applicable": False,
                "manual_review_required": True,
                "status": "MANUAL_REVIEW",
                "is_verified_rule": True
            })

    def _check_keywords_and_ccs(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        keywords = insp.get("keywords", {})
        tgt_label = self.target_spec["keywords"]["label"]
        cur_label = keywords.get("label", "")

        if not keywords.get("present", False):
            roadmap.append({
                "element": "Keywords / Index Terms Section",
                "category": "Metadata & Frontmatter",
                "current_format": "Missing",
                "target_format": tgt_label,
                "action": f"Author must supply 3 to 6 subject keywords labeled as '{tgt_label}'.",
                "reason": f"Mandatory for {self.target_venue} indexing in digital libraries.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Keywords",
                "priority": "High",
                "auto_applicable": False,
                "manual_review_required": True,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
        else:
            if cur_label != tgt_label:
                roadmap.append({
                    "element": "Keywords Marker Label",
                    "category": "Metadata & Frontmatter",
                    "current_format": f"Labeled as '{cur_label}'",
                    "target_format": f"Labeled as '{tgt_label}'",
                    "action": f"Rename keyword prefix from '{cur_label}' to '{tgt_label}'.",
                    "reason": f"{self.target_venue} author kit specifically specifies '{tgt_label}' as standard marker.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Keywords Labeling",
                    "priority": "Medium",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })
            else:
                roadmap.append({
                    "element": "Keywords Marker Label",
                    "category": "Metadata & Frontmatter",
                    "current_format": f"'{cur_label}'",
                    "target_format": f"'{tgt_label}'",
                    "action": "Maintain existing keyword label.",
                    "reason": f"Keyword label conforms to {self.target_venue} format.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Keywords",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "COMPLIANT",
                    "is_verified_rule": True
                })

            # Alphabetical check for IEEE
            if self.target_venue == "IEEE" and not keywords.get("is_alphabetical", True):
                roadmap.append({
                    "element": "Keywords Alphabetical Ordering",
                    "category": "Metadata & Frontmatter",
                    "current_format": "Terms not in alphabetical order",
                    "target_format": "Alphabetically sorted Index Terms",
                    "action": "Sort the comma-separated terms in alphabetical order.",
                    "reason": "IEEE style explicitly requires Index Terms to be listed in alphabetical order.",
                    "rule_reference": "IEEE Author Center - Index Terms Guidelines",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })

        # ACM CCS Concepts Check
        if self.target_venue == "ACM":
            ccs = insp.get("ccs_concepts", {})
            if not ccs.get("present", False):
                roadmap.append({
                    "element": "ACM CCS Concepts Block",
                    "category": "Metadata & Frontmatter",
                    "current_format": "Missing CCS Concepts block",
                    "target_format": "2012 ACM Computing Classification System concepts XML block",
                    "action": "Generate and insert 2012 ACM CCS XML concepts block from https://dl.acm.org/ccs prior to Keywords.",
                    "reason": "ACM conference publications strictly mandate CCS classification concepts for cataloging.",
                    "rule_reference": "ACM Primary Article Template Specifications (Sec. 2.4)",
                    "priority": "High",
                    "auto_applicable": False,
                    "manual_review_required": True,
                    "status": "MANUAL_REVIEW",
                    "is_verified_rule": True
                })
            else:
                roadmap.append({
                    "element": "ACM CCS Concepts Block",
                    "category": "Metadata & Frontmatter",
                    "current_format": "Present",
                    "target_format": "Present",
                    "action": "Maintain existing ACM CCS Concepts block.",
                    "reason": "Complies with ACM taxonomy requirement.",
                    "rule_reference": "ACM Primary Article Template Specifications",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "COMPLIANT",
                    "is_verified_rule": True
                })
        elif self.source_venue == "ACM" and self.target_venue in ["IEEE", "SPRINGER"]:
            ccs = insp.get("ccs_concepts", {})
            if ccs.get("present", False):
                roadmap.append({
                    "element": "Redundant ACM CCS Concepts Block",
                    "category": "Metadata & Frontmatter",
                    "current_format": "ACM CCS Concepts present",
                    "target_format": "Remove CCS block for target venue",
                    "action": f"Remove ACM-specific CCS XML concepts when submitting to {self.target_venue}.",
                    "reason": f"{self.target_venue} does not use or publish ACM CCS XML syntax.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Metadata",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })

    def _check_headings(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        headings = insp.get("headings", [])
        tgt_level1 = self.target_spec["headings"]["level1"]
        tgt_level2 = self.target_spec["headings"]["level2"]

        for h in headings:
            raw = h["raw_heading"]
            sec = h["canonical_section"]
            level = h["level"]
            rec = h.get("recommended_heading", raw)
            reason = h.get("recommendation_reason", "")
            
            # Skip Abstract, Keywords, Acknowledgment, References here (handled separately)
            if sec in [CanonicalSection.ABSTRACT.value, CanonicalSection.KEYWORDS.value, 
                       CanonicalSection.ACKNOWLEDGMENTS.value, CanonicalSection.REFERENCES.value]:
                continue

            if raw != rec:
                roadmap.append({
                    "element": f"Section Heading: '{raw}'",
                    "category": "Headings & Structure",
                    "current_format": raw,
                    "target_format": rec,
                    "action": f"Update heading to '{rec}'",
                    "reason": reason,
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Heading Style",
                    "priority": "High" if level == 1 else "Medium",
                    "auto_applicable": True,
                    "manual_review_required": h.get("is_ambiguous", False),
                    "status": "MANUAL_REVIEW" if h.get("is_ambiguous") else "NEEDS_CHANGE",
                    "is_verified_rule": True
                })
            else:
                roadmap.append({
                    "element": f"Section Heading: '{raw}'",
                    "category": "Headings & Structure",
                    "current_format": raw,
                    "target_format": rec,
                    "action": "Maintain existing heading format.",
                    "reason": f"Complies with {self.target_venue} style.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Heading Style",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "COMPLIANT",
                    "is_verified_rule": True
                })

    def _check_acknowledgments(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        ack = insp.get("acknowledgments", {})
        if not ack.get("present", False):
            # Optional in most venues, but recommended
            roadmap.append({
                "element": "Acknowledgment Section",
                "category": "Headings & Structure",
                "current_format": "Not present in document",
                "target_format": f"Optional section: '{self.target_spec['acknowledgments']['exact_heading']}'",
                "action": f"If recognizing grant or institutional funding, place '{self.target_spec['acknowledgments']['exact_heading']}' before References.",
                "reason": f"{self.target_venue} requires specific unnumbered placement for acknowledgments.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Acknowledgments",
                "priority": "Low",
                "auto_applicable": False,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })
            return

        cur_heading = ack.get("raw_heading", "")
        tgt_heading = self.target_spec["acknowledgments"]["exact_heading"]

        if cur_heading.strip(".:- ") != tgt_heading:
            roadmap.append({
                "element": "Acknowledgment Section Title",
                "category": "Headings & Structure",
                "current_format": f"'{cur_heading}'",
                "target_format": f"'{tgt_heading}'",
                "action": f"Rename heading to strictly '{tgt_heading}'.",
                "reason": self.target_spec["acknowledgments"]["rule"],
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Acknowledgments",
                "priority": "High" if self.target_venue == "IEEE" else "Medium",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "NEEDS_CHANGE",
                "is_verified_rule": True
            })
        else:
            roadmap.append({
                "element": "Acknowledgment Section Title",
                "category": "Headings & Structure",
                "current_format": f"'{cur_heading}'",
                "target_format": f"'{tgt_heading}'",
                "action": "Maintain existing heading.",
                "reason": f"Heading correctly matches {self.target_venue} requirements.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Acknowledgments",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })

    def _check_tables_and_figures(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        tables = insp.get("tables", [])
        tgt_tbl_lbl = self.target_spec["tables"]["caption_label"] # e.g. 'TABLE I' or 'Table 1:'
        
        for t in tables:
            raw_cap = t.get("raw_caption", "")
            cur_num = t.get("numbering_style", "ARABIC")
            tgt_num = self.target_spec["tables"]["numbering"]
            
            if cur_num != tgt_num:
                roadmap.append({
                    "element": f"Table Caption Label: '{raw_cap[:30]}...'",
                    "category": "Figures & Tables",
                    "current_format": f"Using {cur_num} table numbering",
                    "target_format": f"{self.target_venue} style: {tgt_num} numbering (e.g. '{tgt_tbl_lbl}')",
                    "action": f"Convert table numbering from {cur_num} to {tgt_num} and place caption above table.",
                    "reason": self.target_spec["tables"]["rule"],
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Tables",
                    "priority": "Medium",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })

        figures = insp.get("figures", [])
        tgt_fig_lbl = self.target_spec["figures"]["caption_label"] # e.g. 'Fig. 1.' or 'Figure 1:'
        for f in figures:
            raw_cap = f.get("raw_caption", "")
            pfx = f.get("label_prefix", "")
            
            # Check if prefix matches
            needs_fig_change = (self.target_venue == "ACM" and "fig." in pfx.lower()) or (self.target_venue in ["IEEE", "SPRINGER"] and "figure" in pfx.lower())
            if needs_fig_change:
                roadmap.append({
                    "element": f"Figure Caption Prefix: '{raw_cap[:30]}...'",
                    "category": "Figures & Tables",
                    "current_format": f"Prefix '{pfx}'",
                    "target_format": f"Prefix '{tgt_fig_lbl}'",
                    "action": f"Change caption prefix to '{tgt_fig_lbl}' below figure.",
                    "reason": self.target_spec["figures"]["rule"],
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - Figures",
                    "priority": "Medium",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })

    def _check_citations_and_references(self, insp: Dict[str, Any], roadmap: List[Dict[str, Any]]) -> None:
        citations = insp.get("citations", {})
        references = insp.get("references", {})
        tgt_ref_heading = self.target_spec["references"]["exact_heading"] # REFERENCES vs References

        # Reference Section Heading
        if references.get("present", False):
            cur_ref = references.get("raw_heading", "")
            if cur_ref.strip(".:- ") != tgt_ref_heading:
                roadmap.append({
                    "element": "References Section Heading",
                    "category": "Citations & References",
                    "current_format": f"'{cur_ref}'",
                    "target_format": f"'{tgt_ref_heading}'",
                    "action": f"Update reference heading to '{tgt_ref_heading}'.",
                    "reason": f"{self.target_venue} requires '{tgt_ref_heading}' in {self.target_spec['references']['casing']}.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - References",
                    "priority": "Medium",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "NEEDS_CHANGE",
                    "is_verified_rule": True
                })
            else:
                roadmap.append({
                    "element": "References Section Heading",
                    "category": "Citations & References",
                    "current_format": f"'{cur_ref}'",
                    "target_format": f"'{tgt_ref_heading}'",
                    "action": "Maintain existing references heading.",
                    "reason": f"Heading conforms to {self.target_venue} style.",
                    "rule_reference": f"{self.target_spec['official_guideline_source']} - References",
                    "priority": "Low",
                    "auto_applicable": True,
                    "manual_review_required": False,
                    "status": "COMPLIANT",
                    "is_verified_rule": True
                })

        # In-text Citation Style Check
        cur_cite_style = citations.get("style", "NUMERIC_SQUARE_BRACKETS")
        tgt_cite_style = self.target_spec["references"]["citation_style"]
        if cur_cite_style != tgt_cite_style and cur_cite_style != "UNKNOWN":
            roadmap.append({
                "element": "In-text Citation Style",
                "category": "Citations & References",
                "current_format": f"Found {cur_cite_style} (e.g. {citations.get('samples', [''])[0]})",
                "target_format": f"{tgt_cite_style} (e.g. [1])",
                "action": f"Convert citations from {cur_cite_style} to {tgt_cite_style}.",
                "reason": f"{self.target_venue} author kit specifies {tgt_cite_style}.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Citations",
                "priority": "High",
                "auto_applicable": False,
                "manual_review_required": True,
                "status": "MANUAL_REVIEW",
                "is_verified_rule": True
            })
        else:
            roadmap.append({
                "element": "In-text Citation Style",
                "category": "Citations & References",
                "current_format": "Square bracket numeric citations [1]",
                "target_format": "Square bracket numeric citations [1]",
                "action": "Maintain numeric citation style.",
                "reason": f"Complies with {self.target_venue} numeric reference convention.",
                "rule_reference": f"{self.target_spec['official_guideline_source']} - Citations",
                "priority": "Low",
                "auto_applicable": True,
                "manual_review_required": False,
                "status": "COMPLIANT",
                "is_verified_rule": True
            })


# Helper Roman and Alphabet lists for recommendations
ROMAN_NUMS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI"]
ALPHA_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


def generate_heading_recommendations(mapped_headings: List[Dict[str, Any]], target_venue: str) -> List[Dict[str, Any]]:
    """
    Generates intelligent, venue-specific heading recommendations for each heading.
    
    Returns list of dicts with:
    - raw_heading: Original heading text
    - detected_meaning: Semantic category or ambiguity flag
    - recommended_target: Recommended target heading string or style
    - reason: Detailed rationale citing target publisher guidelines
    - confidence: Confidence score
    - status: Visual status flag
    - manual_review: Whether manual review is required
    """
    tgt = target_venue.upper()
    target_spec = VENUE_SPECIFICATIONS.get(tgt, VENUE_SPECIFICATIONS["ACM"])
    
    results: List[Dict[str, Any]] = []
    l1_idx = 0
    l2_idx = 0

    for m in mapped_headings:
        raw = m.get("raw_heading", "")
        cleaned = m.get("cleaned_heading", raw)
        canonical = m.get("canonical_section", "UNKNOWN")
        level = m.get("level", 1)
        is_ambiguous = m.get("is_ambiguous", False)
        secondary = m.get("secondary_section")
        confidence = m.get("confidence", 0.0)

        # 1. Ambiguous Headings -> Require Manual Review
        if is_ambiguous:
            detected = f"⚠️ Ambiguous ({canonical} / {secondary})"
            rec_target = f"⚠️ Manual Review (Preserve: '{raw}')"
            reason = (
                f"Heading matches multiple semantic categories ({canonical} and {secondary}). "
                f"Preserved original heading verbatim to avoid misrepresenting research scope until author confirms classification."
            )
            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": detected,
                "Recommended Target Heading": rec_target,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "⚠️ Ambiguous (Manual Review)",
                "manual_review": True
            })
            continue

        # 2. Abstract
        if canonical == CanonicalSection.ABSTRACT.value:
            lead = target_spec["abstract"]["lead_in"]
            if tgt == "IEEE":
                rec_target = "Abstract---"
                reason = "IEEE conference standard mandates bold italic lead-in 'Abstract---' followed directly by abstract body."
            elif tgt == "ACM":
                rec_target = "ABSTRACT"
                reason = "ACM acmart sigconf standard requires bold uppercase standalone heading 'ABSTRACT'."
            else:
                rec_target = "Abstract."
                reason = "Springer LNCS standard mandates bold lead-in 'Abstract.' run into the paragraph."
            
            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": "ABSTRACT",
                "Recommended Target Heading": rec_target,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "✅ Auto-Mapped",
                "manual_review": False
            })
            continue

        # 3. Keywords / Index Terms
        if canonical == CanonicalSection.KEYWORDS.value:
            lbl = target_spec["keywords"]["label"]
            if tgt == "IEEE":
                rec_target = "Index Terms---"
                reason = "IEEE mandates bold italic 'Index Terms---' prefix followed by alphabetical keywords."
            elif tgt == "ACM":
                rec_target = "Keywords: "
                reason = "ACM requires 'Keywords: ' prefix followed by lowercase comma-separated keywords."
            else:
                rec_target = "Keywords:"
                reason = "Springer LNCS requires bold 'Keywords:' prefix followed by 3-6 keywords separated by commas."

            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": "KEYWORDS / INDEX TERMS",
                "Recommended Target Heading": rec_target,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "✅ Auto-Mapped",
                "manual_review": False
            })
            continue

        # 4. Acknowledgments
        if canonical == CanonicalSection.ACKNOWLEDGMENTS.value:
            tgt_ack = target_spec["acknowledgments"]["exact_heading"]
            if tgt == "IEEE":
                reason = "IEEE strictly requires singular 'ACKNOWLEDGMENT' (not plural), centered and unnumbered."
            elif tgt == "ACM":
                reason = "ACM requires plural 'ACKNOWLEDGMENTS' using the \\begin{acks} environment."
            else:
                reason = "Springer LNCS requires British spelling 'Acknowledgements' as an unnumbered section before References."

            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": "ACKNOWLEDGMENTS",
                "Recommended Target Heading": tgt_ack,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "✅ Auto-Mapped",
                "manual_review": False
            })
            continue

        # 5. References
        if canonical == CanonicalSection.REFERENCES.value:
            tgt_ref = target_spec["references"]["exact_heading"]
            if tgt == "IEEE":
                reason = "IEEE mandates uppercase centered 'REFERENCES' without numbering."
            elif tgt == "ACM":
                reason = "ACM sigconf mandates uppercase bold 'REFERENCES' without numbering."
            else:
                reason = "Springer LNCS mandates Title Case bold 'References' without numbering."

            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": "REFERENCES",
                "Recommended Target Heading": tgt_ref,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "✅ Auto-Mapped",
                "manual_review": False
            })
            continue

        # 6. Known Canonical Section (Level 1 vs Level 2)
        if canonical != CanonicalSection.UNKNOWN.value:
            if level == 1:
                l1_idx += 1
                l2_idx = 0
                if tgt == "IEEE":
                    r_pfx = ROMAN_NUMS[l1_idx - 1] if 1 <= l1_idx <= len(ROMAN_NUMS) else str(l1_idx)
                    rec_target = f"{r_pfx}. {cleaned.upper()}"
                    reason = f"IEEE Level 1 standard: uppercase Roman numeral followed by ALL CAPS text."
                elif tgt == "ACM":
                    rec_target = f"{l1_idx} {cleaned.upper()}"
                    reason = f"ACM sigconf Level 1 standard: unpunctuated Arabic numeral followed by ALL CAPS text."
                else:
                    rec_target = f"{l1_idx} {cleaned.title()}"
                    reason = f"Springer LNCS Level 1 standard: Arabic numeral followed by Title Case text."

                results.append({
                    "Original Heading": raw,
                    "Detected Meaning / Category": canonical,
                    "Recommended Target Heading": rec_target,
                    "Reason": reason,
                    "Confidence": f"{confidence:.2f}",
                    "Status": "✅ Auto-Mapped",
                    "manual_review": False
                })
            else:
                l2_idx += 1
                if tgt == "IEEE":
                    a_pfx = ALPHA_LETTERS[l2_idx - 1] if 1 <= l2_idx <= len(ALPHA_LETTERS) else f"S{l2_idx}"
                    rec_target = f"{a_pfx}. {cleaned.title()}"
                    reason = f"IEEE Level 2 standard: capital letter in italics followed by Title Case text."
                else:
                    curr_l1 = max(1, l1_idx)
                    rec_target = f"{curr_l1}.{l2_idx} {cleaned.title()}"
                    reason = f"{tgt} Level 2 standard: decimal Arabic numbering followed by Title Case bold text."

                results.append({
                    "Original Heading": raw,
                    "Detected Meaning / Category": f"{canonical} (Subsection)",
                    "Recommended Target Heading": rec_target,
                    "Reason": reason,
                    "Confidence": f"{confidence:.2f}",
                    "Status": "✅ Auto-Mapped",
                    "manual_review": False
                })
            continue

        # 7. Unknown / Domain-Specific Section
        # Handle intelligently: if structural numbering or hierarchy is detected, standardize formatting while preserving author wording!
        if m.get("numbering_type") != "NONE" or (cleaned and len(cleaned.split()) <= 8):
            if level == 1:
                l1_idx += 1
                l2_idx = 0
                if tgt == "IEEE":
                    r_pfx = ROMAN_NUMS[l1_idx - 1] if 1 <= l1_idx <= len(ROMAN_NUMS) else str(l1_idx)
                    rec_target = f"{r_pfx}. {cleaned.upper()}"
                    reason = f"Preserve author domain-specific title; apply IEEE Level 1 Roman uppercase style."
                elif tgt == "ACM":
                    rec_target = f"{l1_idx} {cleaned.upper()}"
                    reason = f"Preserve author domain-specific title; apply ACM sigconf Level 1 unpunctuated Arabic style."
                else:
                    rec_target = f"{l1_idx} {cleaned.title()}"
                    reason = f"Preserve author domain-specific title; apply Springer LNCS Level 1 Title Case style."

                results.append({
                    "Original Heading": raw,
                    "Detected Meaning / Category": "Custom Domain Technical Section",
                    "Recommended Target Heading": rec_target,
                    "Reason": reason,
                    "Confidence": f"{confidence:.2f}",
                    "Status": "🔄 Format Standardized",
                    "manual_review": False
                })
            else:
                l2_idx += 1
                if tgt == "IEEE":
                    a_pfx = ALPHA_LETTERS[l2_idx - 1] if 1 <= l2_idx <= len(ALPHA_LETTERS) else f"S{l2_idx}"
                    rec_target = f"{a_pfx}. {cleaned.title()}"
                    reason = f"Preserve author domain-specific title; apply IEEE Level 2 alphabetic italic style."
                else:
                    curr_l1 = max(1, l1_idx)
                    rec_target = f"{curr_l1}.{l2_idx} {cleaned.title()}"
                    reason = f"Preserve author domain-specific title; apply {tgt} Level 2 decimal Arabic style."

                results.append({
                    "Original Heading": raw,
                    "Detected Meaning / Category": "Custom Domain Subsection",
                    "Recommended Target Heading": rec_target,
                    "Reason": reason,
                    "Confidence": f"{confidence:.2f}",
                    "Status": "🔄 Format Standardized",
                    "manual_review": False
                })
        else:
            # Completely unparseable or ambiguous -> Mark for manual review, preserve original
            rec_target = f"⚠️ Preserve: '{raw}'"
            reason = "No matching canonical section or structural numbering detected. Preserved original heading verbatim to avoid altering research meaning."
            results.append({
                "Original Heading": raw,
                "Detected Meaning / Category": "Unclassified Custom Element",
                "Recommended Target Heading": rec_target,
                "Reason": reason,
                "Confidence": f"{confidence:.2f}",
                "Status": "⚠️ Manual Review Required",
                "manual_review": True
            })

    return results

