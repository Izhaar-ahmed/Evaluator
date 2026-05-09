import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


def export_results_to_csv(
    results: Dict[str, Dict[str, Any]],
    output_folder: str = "./outputs",
    filename: Optional[str] = None,
) -> str:
    """
    Export evaluation results to CSV file.

    Format:
    - Score out of 10
    - No word_count, max_score, assignment_type, or file columns
    - Includes student summary text
    - Clean, actionable feedback

    Args:
        results: Dictionary of student name to evaluation results
        output_folder: Folder to save CSV file
        filename: CSV filename. If None, uses 'results.csv'

    Returns:
        Path to the created CSV file
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_filename = filename or "results.csv"
    csv_file_path = output_path / csv_filename

    if not results:
        raise ValueError("No results to export")

    # Prepare rows
    rows = []
    for student_name, evaluation in results.items():
        clean_name = student_name.replace("_Result", "")

        # Score is already /10 from backend
        score_10 = evaluation.get("final_score", 0)

        concept_coverage = evaluation.get("concept_coverage", 0)
        matched = evaluation.get("matched_concepts", 0)
        total = evaluation.get("total_concepts", 0)

        # Get summary text
        summary = evaluation.get("summary_text", "")
        if summary:
            summary = " ".join(summary.split())

        # Build clean feedback
        feedback = _build_clean_feedback(evaluation)

        row = {
            "student_name": clean_name,
            "score": score_10,
            "concept_coverage": f"{round(concept_coverage)}%",
            "concepts_matched": f"{matched}/{total}" if total else "N/A",
            "feedback": feedback,
            "summary_text": summary,
        }
        rows.append(row)

    # Sort by student name
    rows.sort(key=lambda r: r["student_name"])

    fieldnames = [
        "student_name",
        "score",
        "concept_coverage",
        "concepts_matched",
        "feedback",
        "summary_text",
    ]

    with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(csv_file_path)


def _build_clean_feedback(evaluation: Dict[str, Any]) -> str:
    """
    Build clean, actionable feedback from evaluation data.
    No markdown, no emojis — just clear teacher-style comments.
    """
    parts = []
    score = evaluation.get("final_score", 0)
    coverage = evaluation.get("concept_coverage", 0)
    word_count = evaluation.get("word_count", 0)

    # Extract matched/missing topics from combined_feedback
    matched_topics = ""
    missing_topics = ""
    for fb in evaluation.get("combined_feedback", []):
        if "Topics covered:" in fb:
            matched_topics = fb.split("Topics covered:")[-1].strip()
        if "Missing topics:" in fb:
            missing_topics = fb.split("Missing topics:")[-1].strip()

    # Overall assessment
    if score >= 8:
        parts.append("Excellent summary — demonstrates strong understanding of the lecture content.")
    elif score >= 6.5:
        parts.append("Good summary — covers key topics well.")
    elif score >= 5:
        parts.append("Adequate summary — some important topics are covered but several key concepts are missing.")
    elif score >= 3:
        parts.append("Below average — the summary lacks coverage of most lecture topics.")
    else:
        parts.append("Poor submission — does not reflect the lecture content.")

    # Coverage detail
    if coverage >= 70:
        parts.append(f"Strong topic coverage ({round(coverage)}%).")
    elif coverage >= 40:
        parts.append(f"Moderate topic coverage ({round(coverage)}%).")
    else:
        parts.append(f"Low topic coverage ({round(coverage)}%). Review the key lecture topics.")

    # What they covered well
    if matched_topics:
        parts.append(f"Covered: {matched_topics}.")

    # What they missed
    if missing_topics:
        parts.append(f"Missing: {missing_topics}.")

    # Length feedback
    if word_count < 30:
        parts.append("Summary is too short — aim for at least 80-100 words.")
    elif word_count > 200:
        parts.append("Summary is too long — keep it concise at 100-120 words.")

    # Depth advice
    depth_score = 0
    for fb in evaluation.get("combined_feedback", []):
        if "surface-level" in fb.lower():
            parts.append("Try to explain why topics are important, not just list them.")
            break
        elif "explain *why*" in fb.lower():
            parts.append("Include brief explanations of how concepts connect.")
            break

    return " | ".join(parts)


def _format_feedback_for_csv(feedback_list: List[str]) -> str:
    """Format feedback list into a single CSV-safe string."""
    if not feedback_list:
        return ""
    return " | ".join(feedback_list)


def export_results_to_detailed_csv(
    results: Dict[str, Dict[str, Any]],
    output_folder: str = "./outputs",
    filename: Optional[str] = None,
) -> str:
    """
    Export evaluation results to a detailed CSV.

    Args:
        results: Dictionary of student name to evaluation results
        output_folder: Folder to save CSV file
        filename: CSV filename

    Returns:
        Path to the created CSV file
    """
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_filename = filename or "results_detailed.csv"
    csv_file_path = output_path / csv_filename

    if not results:
        raise ValueError("No results to export")

    rows = []
    for student_name, evaluation in results.items():
        clean_name = student_name.replace("_Result", "")
        score_10 = evaluation.get("final_score", 0)
        concept_coverage = evaluation.get("concept_coverage", 0)
        matched = evaluation.get("matched_concepts", 0)
        total = evaluation.get("total_concepts", 0)

        matched_topics = ""
        missing_topics = ""
        for fb in evaluation.get("combined_feedback", []):
            if "Topics covered:" in fb:
                matched_topics = fb.split("Topics covered:")[-1].strip()
            if "Missing topics:" in fb:
                missing_topics = fb.split("Missing topics:")[-1].strip()

        summary = evaluation.get("summary_text", "")
        if summary:
            summary = " ".join(summary.split())

        row = {
            "student_name": clean_name,
            "score": score_10,
            "concept_coverage": f"{round(concept_coverage)}%",
            "concepts_matched": f"{matched}/{total}" if total else "N/A",
            "topics_covered": matched_topics,
            "topics_missing": missing_topics,
            "feedback": _build_clean_feedback(evaluation),
            "summary_text": summary,
        }
        rows.append(row)

    rows.sort(key=lambda r: r["student_name"])

    fieldnames = [
        "student_name",
        "score",
        "concept_coverage",
        "concepts_matched",
        "topics_covered",
        "topics_missing",
        "feedback",
        "summary_text",
    ]

    with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(csv_file_path)
