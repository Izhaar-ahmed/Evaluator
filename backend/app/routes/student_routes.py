"""API routes for student profile and history."""

from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.core.services.student_tracker import (
    get_score_history,
    get_improvement_delta,
    format_report_card,
    compute_percentile,
)


router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/{student_id}/history")
def student_history(
    student_id: str,
    topic_tag: Optional[str] = None,
    limit: int = 20,
):
    """
    Get a student's score history with improvement deltas.

    Query params:
    - topic_tag: Filter by topic (optional)
    - limit: Max records to return (default 20)
    """
    history = get_score_history(student_id, topic_tag=topic_tag, limit=limit)

    # Compute running delta if history exists
    if history:
        scores = [h["score"] for h in history]
        latest = scores[0] if scores else 0
        delta_info = get_improvement_delta(
            student_id,
            topic_tag=topic_tag or "",
            current_score=latest,
        )
    else:
        delta_info = {"delta": None, "trend": "no data", "prev_avg": None}

    return {
        "status": "success",
        "student_id": student_id,
        "history": history,
        "improvement": delta_info,
    }


@router.get("/{student_id}/report")
def student_report(
    student_id: str,
    score: float = 0,
    percentile: int = 50,
    topic_tag: Optional[str] = None,
):
    """
    Generate a formatted report card for a student.

    Query params:
    - score: Current score
    - percentile: Percentile rank in class
    - topic_tag: Topic for improvement delta
    """
    delta_info = get_improvement_delta(
        student_id,
        topic_tag=topic_tag or "",
        current_score=score,
    )

    report = format_report_card(
        student_id=student_id,
        score=score,
        percentile=percentile,
        delta=delta_info["delta"],
    )

    return {
        "status": "success",
        "student_id": student_id,
        "report_card": report,
        "details": {
            "score": score,
            "percentile": percentile,
            "trend": delta_info["trend"],
            "delta": delta_info["delta"],
        },
    }
