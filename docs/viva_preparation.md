# Comprehensive Viva & Oral Defense Preparation Guide

**Project Title:** Cross-Venue Formatting Standardization: Bridging IEEE, ACM, and Springer Conference Standards  
**Degree Level:** B.Sc. Computer Science (Beginner / Intermediate)  
**Subject:** Research Methodology  

---

## 1. Simple Project Explanation in Hinglish (Samjhein Apni Bhasha Mein)

### Yeh project aakhir karta kya hai?
> "Sir/Ma'am, jab hum koi research paper likhte hain, toh har conference ya publisher ka apna format aur rules hote hain. Jaise IEEE bolta hai 2-column layout mein likho, Roman numerals use karo (`I. INTRODUCTION`), keywords ko `Index Terms` bolo, aur acknowledgment ko strictly singular `ACKNOWLEDGMENT` likho. Wahi ACM bolta hai Arabic numerals use karo (`1 INTRODUCTION`), CCS Concepts XML lagao, aur `ACKNOWLEDGMENTS` (plural) likho. Springer LNCS single column mangta hai.
>
> Jab ek student ka paper ek conference se reject hota hai ya dusri conference mein submit karna hota hai, toh usko manually poora paper restructure karna padta hai. Is formatting mein researchers ka average 14 ghante kharab hote hain (Jiang et al., 2019 PLOS ONE study). 
>
> Humne ek **Python-based Cross-Venue Formatting Standardization System** banaya hai. Yeh tool manuscript ke section headings ko extract karta hai, unko hamare banaye hue universal **Canonical Schema** (11 standard categories) se map karta hai, check karta hai ki koi mandatory section missing toh nahi hai, aur IEEE vs ACM vs Springer ke specific rules check karke warnings aur migration roadmap deta hai.
>
> Humne 45 real headings ke independent test set par isko evaluate kiya, jisme hamari overall mapping accuracy **95.56%** aayi aur IEEE/ACM par 100% aayi."

---

## 2. Two-Minute Elevator Pitch (Opening Statement in English)

> "Good morning, respected examiners. My Research Methodology project is titled **'Cross-Venue Formatting Standardization: Bridging IEEE, ACM, and Springer Conference Standards'**.
>
> In scholarly computer science publishing, manuscripts must adhere to strict publisher guidelines. However, requirements across leading publishers like IEEE, ACM, and Springer differ significantly—not just in visual styling, but in rhetorical section naming, numbering styles, mandatory frontmatter, and acknowledgment conventions. Studies show that formatting and reformatting cost researchers an average of 14 hours per paper, totaling over $1.1 billion in lost productivity globally each year.
>
> To solve this problem for novice researchers and students, I have engineered an explainable, rule-based standardization system. It maps disparate paper headings to an 11-category canonical semantic schema, validates document completeness against target publisher profiles, and detects subtle compliance violations—such as IEEE's strict singular 'ACKNOWLEDGMENT' mandate or ACM's Arabic numbering.
>
> When tested against a manually verified benchmark of 45 diverse headings, my system achieved a **95.56% overall accuracy** and a **macro F1-score of 0.9619**, with a 100% detection rate for missing mandatory sections. I have implemented both a command-line interface and an interactive Streamlit dashboard for real-time author assistance. Thank you, and I look forward to your questions."

---

## 3. Codebase File-by-File Explanation

| File Path | What it Does (Simple Explanation) | Why It Is Important |
| :--- | :--- | :--- |
| `src/schema.py` | Defines `CanonicalSection` enum (11 categories) and `VENUE_CONFIGS` dictionary containing official rules for IEEE, ACM, and Springer LNCS. | Acts as the "single source of truth" for publisher rules and canonical vocabulary. |
| `src/normalizer.py` | Cleans heading strings using regex: strips Roman numbers (`I.`), Arabic numbers (`1.`, `3.2.1`), removes punctuation (`---`), and case-folds text. | Ensures that "I. INTRODUCTION" and "1. Introduction" both become "introduction" for reliable pattern matching. |
| `src/rule_engine.py` | Contains regex patterns and keyword dictionaries with priority weights. Detects compound phrases ("Results and Discussion") and assigns confidence scores with explanations. | The core brain of the system. Provides explainability instead of black-box prediction. |
| `src/validator.py` | Audits mapped headings against target venue. Detects missing mandatory sections, singular/plural acknowledgment mismatches, and sequence errors. | Ensures the paper actually complies with the publisher's author guidelines. |
| `src/reporter.py` | Formats output into terminal summaries, CSV files, structured JSON, and generates cross-venue migration roadmaps. | Exports clean data and actionable checklists for authors. |
| `src/cli.py` | Command-line interface allowing users to analyze papers via command prompt or pass JSON files. | Enables batch processing and automation. |
| `src/app.py` | Interactive Streamlit web interface with interactive dropdowns, presets, real-time tables, metrics, and download buttons. | Provides a beginner-friendly visual dashboard for demonstration. |
| `tests/evaluate.py` | Independent evaluation harness. Runs 45 benchmark samples, computes accuracy, F1-scores, generates confusion matrix and charts. | Proves that results are genuine and reproducible without data fabrication. |

---

## 4. Methodology and Metrics Breakdown

### How the system works (Step-by-Step Data Flow):
1. **Input:** The user provides section headings (via text, JSON, or UI preset).
2. **Normalization:** `normalize_heading()` detects numbering style (Roman vs Arabic) and cleans the string.
3. **Compound Splitting:** Checks if the heading joins two sections (e.g. "Results and Discussion"). If so, flags it as compound/ambiguous, sets primary = `EVALUATION`, secondary = `DISCUSSION`.
4. **Pattern Matching:** Matches against exact keywords and regex patterns. Assigns confidence score (e.g., 1.0 for exact, 0.95 for regex).
5. **Venue Validation:** `VenueValidator` checks if any mandatory sections (e.g., Abstract, Keywords, References) are missing and flags style violations (e.g., Arabic in IEEE).
6. **Reporting:** Outputs clean table, compliance alerts, and conversion roadmap.

### Evaluation Metrics Explained Simply:
- **Accuracy (95.56%):** Out of 45 test headings, 43 were mapped to their exact ground-truth canonical class.
- **Precision (0.9630 Macro):** When the system predicts a section as "METHODOLOGY", how often is it truly "METHODOLOGY"? (Nearly 100% precision; no false positive mappings).
- **Recall (0.9644 Macro):** Out of all true "RELATED_WORK" sections in the test set, how many did the system successfully find?
- **Macro F1-Score (0.9619):** Balanced harmonic mean of Precision and Recall across all classes equally.
- **Ambiguity Detection F1 (0.8571):** Measures how accurately the system identifies compound/ambiguous headings.

---

## 5. 25 Likely Viva Questions & Model Answers

### Category 1: Project Motivation & Conceptual Understanding
**Q1: What is the main problem your project addresses?**  
*Answer:* "Publishers like IEEE, ACM, and Springer use different section names, numbering styles, and mandatory rules for conference papers. Students and researchers waste an average of 14 hours reformatting papers when switching venues. My project provides an automated, explainable system to map headings to a universal schema and validate compliance against publisher rules."

**Q2: What is the difference between 'visual formatting' and 'semantic section mapping'?**  
*Answer:* "Visual formatting deals with presentation appearance—such as margins, font size (10pt vs 9pt), and two-column vs single-column layout. Semantic section mapping deals with the rhetorical purpose of the text—identifying that 'Proposed System', 'Methodology', and 'Materials and Methods' all serve the same functional purpose in the scientific argument."

**Q3: Why did you choose IEEE, ACM, and Springer?**  
*Answer:* "IEEE, ACM, and Springer (LNCS) are the three primary archival publishing bodies in Computer Science. Almost all major CS conferences are sponsored by or indexed under these three publishers, making them the most representative."

**Q4: Can you give a specific example of where IEEE and ACM rules conflict?**  
*Answer:* "Yes. IEEE conference templates strictly require Roman numeral section numbering (`I. INTRODUCTION`), while ACM requires Arabic numbering (`1 INTRODUCTION`). IEEE strictly requires singular 'ACKNOWLEDGMENT', whereas ACM uses plural 'ACKNOWLEDGMENTS'. Furthermore, ACM requires a CCS Concepts XML block, while IEEE uses 'Index Terms'."

**Q5: What is the canonical schema, and how did you decide on its sections?**  
*Answer:* "Our canonical schema consists of 11 universal academic discourse categories: Title, Authors, Abstract, Keywords, Introduction, Related Work, Methodology, Evaluation, Discussion, Conclusion, Acknowledgments, References (plus Appendix). This was derived from the classic IMRaD framework (Sollaci & Pereira, 2004) and the recent SASC taxonomy (Duran-Silva et al., 2024)."

---

### Category 2: Technical Design & Implementation
**Q6: Why did you choose a rule-based engine instead of a deep learning model like BERT or LLM?**  
*Answer:* "Three reasons: First, rule-based systems are deterministic and 100% explainable—they provide the exact rule rationale to the user. Second, deep learning models require heavy GPU hardware, large training datasets, and can suffer from hallucinations or unpredictable black-box errors. Third, for academic section headings, the lexical vocabulary is relatively structured, making regex rules fast, lightweight, and effective (achieving 95.56% accuracy)."

**Q7: How does your system handle compound headings like 'Results and Discussion'?**  
*Answer:* "In `src/rule_engine.py`, we have an explicit compound dictionary `COMPOUND_SECTIONS`. When 'Results and Discussion' is encountered, it identifies both `EVALUATION` and `DISCUSSION`. It assigns `EVALUATION` as the primary section, `DISCUSSION` as the secondary section, and sets `is_ambiguous=True` so the author is transparently informed."

**Q8: What happens when an author enters a completely unknown or domain-specific heading?**  
*Answer:* "The system maps it to `UNKNOWN` with a confidence score of 0.00 and an explanation stating that no canonical rule matched. It does not hallucinate an incorrect guess, but flags it for manual author review."

**Q9: How does the normalization module work?**  
*Answer:* "In `src/normalizer.py`, we use compiled regular expressions to strip Roman numeral prefixes (`^[IVXLCDM]+\.`), hierarchical Arabic numbers (`^(\d+\.)+`), and trailing punctuation or dashes (`---`). It also returns the detected numbering style and heading level."

**Q10: How does the validator check section sequencing?**  
*Answer:* "In `src/validator.py`, the `_check_sequence` method checks the relative index positions of mapped sections. For example, if `INTRODUCTION` appears after `METHODOLOGY`, or if `CONCLUSION` appears after `REFERENCES`, it flags a structural sequencing anomaly."

---

### Category 3: Experimental Evaluation & Results
**Q11: What were your exact evaluation results?**  
*Answer:* "On an independent benchmark of 45 headings, the system achieved 95.56% overall accuracy, a macro F1-score of 0.9619, and a weighted F1-score of 0.9560. On IEEE and ACM samples, accuracy was 100%, and on Springer samples it was 85.7%."

**Q12: Why was accuracy lower (85.7%) on Springer? What were the two errors?**  
*Answer:* "Exactly two headings were not mapped (flagged as `UNKNOWN`): 
1. '2 Survey of Existing Literature': The rule had 'literature review' and 'related work', but missed the phrase 'survey of existing literature'.
2. '3 The Proposed Standardization Engine': The author used the custom phrase 'Standardization Engine' instead of 'system' or 'framework'.
Importantly, the system did not make a false positive error; it safely marked them as `UNKNOWN`."

**Q13: Did you use the same dataset to create the rules and test the system?**  
*Answer:* "No. We strictly maintained dataset separation: a 30-sample development set (`development_set.json`) was used to formulate the rules, and a completely separate 45-sample test set (`test_set.json`) was used exclusively for independent evaluation."

**Q14: How did you test missing section detection?**  
*Answer:* "We passed both complete papers and incomplete papers (missing Keywords, Methodology, or References). The validator successfully identified 100% of the missing mandatory sections in the incomplete test drafts."

---

### Category 4: Academic Integrity, Target Venue & Funding
**Q15: What is your proposed publication venue, and did you verify its indexing?**  
*Answer:* "Our proposed target is *Computer Applications in Engineering Education* (Wiley). I verified from Scopus and SCImago that it is currently ranked **Q1 in Education** and **Q1 in Engineering (miscellaneous)**, and Q2 in Computer Science, with an Impact Factor of 2.7 and CiteScore of ~6.8."

**Q16: How does this project fit the scope of that journal?**  
*Answer:* "The journal focuses on educational software and instructional technology that enhances engineering education. Our tool serves as an educational scaffold in undergraduate Research Methodology and Technical Writing courses, helping novice students learn scientific paper structure and reduce cognitive overhead."

**Q17: Is this project eligible for direct funding under AICTE RPS?**  
*Answer:* "No, an undergraduate student cannot be the Principal Investigator (PI) under AICTE RPS guidelines. The PI must be a regular, full-time faculty member at an AICTE-approved institution. However, this student project serves as the foundational proof-of-concept and working prototype for a faculty mentor's future RPS grant proposal in Educational Technology."

---

### Category 5: Limitations & Future Scope
**Q18: What are the main limitations of your project?**  
*Answer:* "First, the test benchmark contains 45 headings; while thorough for proof-of-concept, broader cross-disciplinary testing is needed. Second, unique author vocabulary not covered by regex rules defaults to `UNKNOWN`. Third, the system operates on headings and structure, but does not re-compile full PDF typeset documents or format LaTeX equations."

**Q19: How would you improve the system in future work?**  
*Answer:* "In future iterations, we could introduce a hybrid architecture: use rules first for 100% explainability, and use a lightweight local sentence transformer (like SciBERT or MiniLM) as a fallback for `UNKNOWN` headings. We could also develop a browser extension for Overleaf so students get real-time warnings while typing."

**Q20: Why did you not use an off-the-shelf tool like Pandoc instead?**  
*Answer:* "Pandoc converts file syntax—for example, converting Markdown tags into LaTeX commands. However, Pandoc has zero semantic understanding: it does not know if your paper is missing an Abstract, it cannot tell if you used Arabic numerals in an IEEE paper, and it cannot flag plural versus singular Acknowledgment violations."

---

## 6. Live Prototype Demonstration Script

If asked to demonstrate the system live in front of the examiners, follow this exact 3-step walkthrough:

### Step 1: Open Terminal & Run CLI on Standard IEEE Paper
```powershell
Set-Location "C:\Users\Md junaid\.gemini\antigravity\scratch\cross_venue_standardization"
python -m src.cli --input data/samples/ieee_sample.json --source IEEE --target ACM
```
*Examiner Explanation:* "Notice that all 10 sections are mapped with 1.00 confidence. The system immediately alerts us that converting this IEEE paper to ACM violates ACM style because Roman numerals were detected where Arabic numerals are required, and provides a 5-step migration roadmap."

### Step 2: Run CLI on Deficient / Non-Standard Student Draft
```powershell
python -m src.cli --input data/samples/non_standard_sample.json --source IEEE --target IEEE
```
*Examiner Explanation:* "Here the student manuscript missed Keywords, Methodology, and References. The system flags:
- `Status: NON-COMPLIANT`
- `Missing Mandatory Sections: KEYWORDS, METHODOLOGY, REFERENCES`
- `IEEE convention alert: Heading 'ACKNOWLEDGMENTS' is plural; IEEE requires singular 'ACKNOWLEDGMENT'`
- `Unmapped heading: 'Case Study of Campus Network Traffic' flagged as UNKNOWN`."

### Step 3: Run the Evaluation Suite (Showing Real Accuracy)
```powershell
python tests/evaluate.py
```
*Examiner Explanation:* "This runs our 45-sample independent benchmark in real-time, outputting 95.56% overall accuracy, saving the confusion matrix and bar charts into the `results/` folder."

### Step 4 (Optional): Launch Interactive Streamlit GUI
```powershell
streamlit run src/app.py
```
*Examiner Explanation:* "This launches our interactive web interface where any student can choose presets, upload a file, inspect mappings in a responsive table, and download CSV/JSON reports."
