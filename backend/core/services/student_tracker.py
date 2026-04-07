"""
Student profile tracker + cohort normalizer.

Provides:
- Per-student score history with improvement deltas
- Class-wide percentile ranking
- Trend analysis ("improving", "stable", "declining")
"""

from typing import Any, Dict, List, Optional

import numpy as np

from backend.core.services.database import get_db


# ---------------------------------------------------------------------------
# Score recording
# ---------------------------------------------------------------------------

def record_score(
    student_id: str,
    assignment_id: str,
    score: float,
    topic_tag: str = "",
) -> bool:
    """
    Record a student's score for an assignment.

    Returns True if recorded successfully, False if DB unavailable.
    """
    db = get_db()
    if not db.available:
        return False

    db.execute(
        """
        INSERT INTO student_scores (student_id, assignment_id, topic_tag, score)
        VALUES (%s, %s, %s, %s)
        """,
        [student_id, assignment_id, topic_tag or "", score],
    )
    return True


# ---------------------------------------------------------------------------
# Improvement delta
# ---------------------------------------------------------------------------

def get_improvement_delta(
    student_id: str,
    topic_tag: str,
    current_score: float,
) -> Dict[str, Any]:
    """
    Compute improvement delta vs. the student's recent history.

    Compares current score against the average of the student's last 5
    submissions on the same topic.

    Returns:
        {
            "delta": float | None,
            "trend": "improving" | "declining" | "stable" | "first submission",
            "prev_avg": float | None
        }
    """
    db = get_db()
    if not db.available:
        return {"delta": None, "trend": "first submission", "prev_avg": None}

    rows = db.execute(
        """
        SELECT score FROM student_scores
        WHERE student_id = %s AND topic_tag = %s
        ORDER BY submitted_at DESC
        LIMIT 5
        """,
        [student_id, topic_tag or ""],
    )

    if not rows:
        return {"delta": None, "trend": "first submission", "prev_avg": None}

    prev_avg = sum(r["score"] for r in rows) / len(rows)
    delta = current_score - prev_avg

    if delta > 5:
        trend = "improving"
    elif delta < -5:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "delta": round(delta, 1),
        "trend": trend,
        "prev_avg": round(prev_avg, 1),
    }


# ---------------------------------------------------------------------------
# Cohort percentile
# ---------------------------------------------------------------------------

def compute_percentile(student_score: float, all_scores: List[float]) -> int:
    """
    Compute a student's percentile rank within the class.

    Args:
        student_score: The student's score.
        all_scores: List of all student scores for the same assignment.

    Returns:
        Percentile rank (0–100).
    """
    if not all_scores:
        return 0

    arr = np.array(all_scores)
    return int(np.sum(arr <= student_score) / len(arr) * 100)


def compute_percentiles_for_cohort(
    results: Dict[str, float],
) -> Dict[str, int]:
    """
    Compute percentile ranks for all students in a cohort.

    Args:
        results: Dict mapping student_id → score.

    Returns:
        Dict mapping student_id → percentile rank.
    """
    all_scores = list(results.values())
    return {
        student_id: compute_percentile(score, all_scores)
        for student_id, score in results.items()
    }


# ---------------------------------------------------------------------------
# Score history
# ---------------------------------------------------------------------------

def get_score_history(
    student_id: str,
    topic_tag: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    """
    Get a student's score history.

    Args:
        student_id: Student identifier.
        topic_tag: Optional filter by topic.
        limit: Maximum number of records.

    Returns:
        List of score records, newest first.
    """
    db = get_db()
    if not db.available:
        return []

    if topic_tag:
        rows = db.execute(
            """
            SELECT assignment_id, topic_tag, score, submitted_at
            FROM student_scores
            WHERE student_id = %s AND topic_tag = %s
            ORDER BY submitted_at DESC
            LIMIT %s
            """,
            [student_id, topic_tag, limit],
        )
    else:
        rows = db.execute(
            """
            SELECT assignment_id, topic_tag, score, submitted_at
            FROM student_scores
            WHERE student_id = %s
            ORDER BY submitted_at DESC
            LIMIT %s
            """,
            [student_id, limit],
        )

    result = []
    for r in (rows or []):
        entry = dict(r)
        if entry.get("submitted_at"):
            entry["submitted_at"] = entry["submitted_at"].isoformat()
        result.append(entry)
    return result


def format_report_card(
    student_id: str,
    score: float,
    percentile: int,
    delta: Optional[float],
) -> str:
    """
    Format a human-readable report card line.

    Example: "Score: 74/100 · Top 32% of class · +11 points vs your last 3 submissions"
    """
    parts = [f"Score: {score:.0f}/100"]

    top_pct = 100 - percentile
    parts.append(f"Top {top_pct}% of class")

    if delta is not None:
        sign = "+" if delta >= 0 else ""
        parts.append(f"{sign}{delta:.0f} points vs recent average")

    return " · ".join(parts)
