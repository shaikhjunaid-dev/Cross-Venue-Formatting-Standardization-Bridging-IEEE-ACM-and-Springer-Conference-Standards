"""
Independent Evaluation Harness for Cross-Venue Formatting Standardization System.

Loads ground-truth benchmark test set, runs the rule mapping engine,
evaluates performance metrics, generates confusion matrix and charts,
and exports all results to results/ directory.
"""

import os
import sys
import json
import csv

# Ensure project root is in python search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

from src.rule_engine import RuleMappingEngine
from src.validator import VenueValidator
from src.schema import CanonicalSection


def run_evaluation():
    test_set_path = os.path.join("data", "ground_truth", "test_set.json")
    with open(test_set_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    engine = RuleMappingEngine()
    
    y_true = []
    y_pred = []
    y_ambig_true = []
    y_ambig_pred = []
    venue_results = {"IEEE": {"correct": 0, "total": 0}, 
                     "ACM": {"correct": 0, "total": 0}, 
                     "SPRINGER": {"correct": 0, "total": 0}}
    
    detailed_rows = []
    
    for sample in test_samples:
        raw = sample["raw"]
        exp_sec = sample["expected_canonical"]
        exp_ambig = sample.get("expected_ambiguous", False)
        venue = sample.get("venue", "IEEE")
        
        pred_dict = engine.map_heading(raw, source_venue=venue)
        pred_sec = pred_dict["canonical_section"]
        pred_ambig = pred_dict["is_ambiguous"]
        
        is_correct = (pred_sec == exp_sec)
        
        y_true.append(exp_sec)
        y_pred.append(pred_sec)
        y_ambig_true.append(exp_ambig)
        y_ambig_pred.append(pred_ambig)
        
        venue_results[venue]["total"] += 1
        if is_correct:
            venue_results[venue]["correct"] += 1
            
        detailed_rows.append({
            "id": sample["id"],
            "venue": venue,
            "raw_heading": raw,
            "expected_canonical": exp_sec,
            "predicted_canonical": pred_sec,
            "is_correct": is_correct,
            "expected_ambiguous": exp_ambig,
            "predicted_ambiguous": pred_ambig,
            "confidence": pred_dict["confidence"],
            "explanation": pred_dict["explanation"],
            "notes": sample.get("notes", "")
        })

    # Metrics computation
    acc = accuracy_score(y_true, y_pred)
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)
    prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    
    # Ambiguity detection metrics
    ambig_acc = accuracy_score(y_ambig_true, y_ambig_pred)
    amb_prec, amb_rec, amb_f1, _ = precision_recall_fscore_support(y_ambig_true, y_ambig_pred, average="binary", zero_division=0)

    # Missing section validation test
    validator_ieee = VenueValidator("IEEE")
    sample_full_ieee = [
        "Abstract", "Index Terms", "I. INTRODUCTION", "II. RELATED WORK",
        "III. METHODOLOGY", "IV. EVALUATION", "V. CONCLUSION", "ACKNOWLEDGMENT", "REFERENCES"
    ]
    sample_missing_ieee = [
        "Abstract", "I. INTRODUCTION", "II. METHODOLOGY", "III. EVALUATION"
    ]
    mapped_full = [engine.map_heading(h) for h in sample_full_ieee]
    mapped_missing = [engine.map_heading(h) for h in sample_missing_ieee]
    
    val_full = validator_ieee.validate_document(mapped_full)
    val_missing = validator_ieee.validate_document(mapped_missing)
    
    missing_detection_successful = (
        len(val_full["missing_mandatory"]) == 0 and 
        len(val_missing["missing_mandatory"]) == 3  # Missing KEYWORDS, CONCLUSION, REFERENCES
    )

    # Unique labels present in evaluation
    labels = sorted(list(set(y_true + y_pred)))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    clf_report = classification_report(y_true, y_pred, labels=labels, output_dict=True, zero_division=0)

    # Venue breakdown
    venue_metrics = {}
    for v, stats in venue_results.items():
        v_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
        venue_metrics[v] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": round(v_acc, 4)
        }

    # Summary dictionary
    summary_results = {
        "dataset": "Independent Ground-Truth Benchmark (45 headings)",
        "total_test_samples": len(test_samples),
        "overall_accuracy": round(acc, 4),
        "macro_precision": round(prec_macro, 4),
        "macro_recall": round(rec_macro, 4),
        "macro_f1": round(f1_macro, 4),
        "weighted_precision": round(prec_weighted, 4),
        "weighted_recall": round(rec_weighted, 4),
        "weighted_f1": round(f1_weighted, 4),
        "ambiguity_detection": {
            "accuracy": round(ambig_acc, 4),
            "precision": round(amb_prec, 4),
            "recall": round(amb_rec, 4),
            "f1_score": round(amb_f1, 4)
        },
        "venue_performance": venue_metrics,
        "missing_section_detection_test_passed": missing_detection_successful,
        "classification_report_per_class": clf_report
    }

    # Save detailed evaluation CSV
    os.makedirs(os.path.join("results", "reports"), exist_ok=True)
    os.makedirs(os.path.join("results", "figures"), exist_ok=True)

    csv_path = os.path.join("results", "reports", "evaluation_table.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(detailed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(detailed_rows)

    # Save metrics JSON
    metrics_path = os.path.join("results", "reports", "evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(summary_results, f, indent=2)

    # Save confusion matrix CSV
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_csv_path = os.path.join("results", "reports", "confusion_matrix.csv")
    cm_df.to_csv(cm_csv_path)

    # Plot Confusion Matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=labels, yticklabels=labels)
    plt.title("Semantic Section Mapping Confusion Matrix (Test Benchmark)", fontsize=13, pad=15)
    plt.xlabel("Predicted Canonical Section", fontsize=11)
    plt.ylabel("Ground-Truth Canonical Section", fontsize=11)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    cm_fig_path = os.path.join("results", "figures", "confusion_matrix.png")
    plt.savefig(cm_fig_path, dpi=300)
    plt.close()

    # Plot Venue Accuracy Comparison Bar Chart
    plt.figure(figsize=(7, 5))
    venues = list(venue_metrics.keys())
    accuracies = [venue_metrics[v]["accuracy"] * 100 for v in venues]
    colors = ["#2b5c8f", "#d95f02", "#7570b3"]
    
    bars = plt.bar(venues, accuracies, color=colors, width=0.55, edgecolor="black", linewidth=1)
    plt.title("Mapping Accuracy Across Publisher Formats", fontsize=13, pad=15)
    plt.ylabel("Accuracy (%)", fontsize=11)
    plt.ylim(0, 110)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{yval:.1f}%", ha="center", va="bottom", fontweight="bold")
        
    plt.tight_layout()
    venue_fig_path = os.path.join("results", "figures", "accuracy_by_venue.png")
    plt.savefig(venue_fig_path, dpi=300)
    plt.close()

    print("\n" + "=" * 70)
    print(" EVALUATION RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total Test Samples Evaluated: {len(test_samples)}")
    print(f"Overall Mapping Accuracy:    {acc * 100:.2f}%")
    print(f"Macro F1-Score:              {f1_macro:.4f}")
    print(f"Weighted F1-Score:           {f1_weighted:.4f}")
    print(f"Ambiguity Detection F1:      {amb_f1:.4f}")
    print("-" * 70)
    print("Publisher Venue Breakdown:")
    for v, stats in venue_metrics.items():
        print(f"  * {v:<10}: {stats['correct']}/{stats['total']} ({stats['accuracy']*100:.1f}%)")
    print("-" * 70)
    print(f"[+] Detailed test table saved to: {csv_path}")
    print(f"[+] Metrics JSON saved to:        {metrics_path}")
    print(f"[+] Confusion matrix plot saved:  {cm_fig_path}")
    print(f"[+] Venue accuracy chart saved:   {venue_fig_path}")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()
