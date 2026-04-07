"""
Human review queue service.

Routes uncertain, flagged, or boundary-score submissions to a persistent
queue that teachers can review and override.

Trigger conditions:
- LLM verdict is UNCERTAIN
- flag_score > 0.7  (integrity concern)
- Final score within 5 points of a grade boundary (25, 50, 75)
"""

import json
from typing import Any, Dict, List, Optional

from backend.core.services.database import get_db


# ---------------------------------------------------------------------------
# Trigger logic
# ---------------------------------------------------------------------------

GRADE_BOUNDARIES = [25, 50, 75]  # Configurable grade boundaries
BOUNDARY_MARGIN = 5              # Points within boundary to trigger review


def _should_queue(result: Dict[str, Any]) -> List[str]:
    """
    Determine if a submission should be queued for review.

    Returns:
        List of trigger reasons (empty if no review needed).
    """
    triggers = []

    # Trigger 1: LLM was uncertain
    llm_verdict = result.get("llm_verdict", "")
    if llm_verdict == "UNCERTAIN":
        triggers.append("UNCERTAIN")

    # Trigger 2: Integrity flag
    flag_score = result.get("flag_score", 0)
    if flag_score > 0.7:
        triggers.append("FLAG")

    # Trigger 3: Score near grade boundary
    final_score = result.get("final_score", 0)
    for boundary in GRADE_BOUNDARIES:
        if abs(final_score - boundary) < BOUNDARY_MARGIN:
            triggers.append("BOUNDARY")
            break

    return triggers


# ---------------------------------------------------------------------------
# Queue operations
# ---------------------------------------------------------------------------

def maybe_queue_for_review(
    submission_id: str,
    student_id: str,
    assignment_id: str,
    result: Dict[str, Any],
) -> Optional[str]:
    """
    Check if submission should be reviewed and insert if so.

    Args:
        submission_id: Unique submission identifier.
        student_id: Student identifier.
        assignment_id: Assignment identifier.
        result: Full evaluation result dict.

    Returns:
        The review queue entry ID if queued, None otherwise.
    """
    db = get_db()
    if not db.available:
        return None

    triggers = _should_queue(result)
    if not triggers:
        return None

    flag_reasons = result.get("flag_reasons", [])
    if isinstance(flag_reasons, list):
        flag_reasons_json = json.dumps(flag_reasons)
    else:
        flag_reasons_json = json.dumps([])

    row = db.execute_one(
        """
        INSERT INTO review_queue
            (submission_id, student_id, assignment_id, trigger, auto_score, flag_reasons)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        [
            submission_id,
            student_id,
            assignment_id,
            triggers[0],  # Primary trigger
            result.get("final_score", 0),
            flag_reasons_json,
        ],
    )
    return str(row["id"]) if row else None


def get_pending_reviews(
    assignment_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict]:
    """Get pending review items, optionally filtered by assignment."""
    db = get_db()
    if not db.available:
        return []

    if assignment_id:
        rows = db.execute(
            """
            SELECT * FROM review_queue
            WHERE status = 'pending' AND assignment_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            [assignment_id, limit],
        )
    else:
        rows = db.execute(
            """
            SELECT * FROM review_queue
            WHERE status = 'pending'
            ORDER BY created_at DESC
            LIMIT %s
            """,
            [limit],
        )
    return _serialize_rows(rows or [])


def get_review_by_id(review_id: str) -> Optional[Dict]:
    """Get a single review item by ID."""
    db = get_db()
    if not db.available:
        return None

    row = db.execute_one(
        "SELECT * FROM review_queue WHERE id = %s",
        [review_id],
    )
    return _serialize_row(row) if row else None


def set_teacher_override(
    review_id: str,
    teacher_score: float,
    teacher_notes: str = "",
) -> Optional[Dict]:
    """
    Teacher overrides the auto-generated score.

    The original auto_score is preserved for tracking system accuracy.
    """
    db = get_db()
    if not db.available:
        return None

    row = db.execute_one(
        """
        UPDATE review_queue
        SET status = 'reviewed',
            teacher_score = %s,
            teacher_notes = %s
        WHERE id = %s
        RETURNING *
        """,
        [teacher_score, teacher_notes, review_id],
    )
    return _serialize_row(row) if row else None


def get_queue_stats() -> Dict:
    """Summary statistics for the review queue."""
    db = get_db()
    if not db.available:
        return {"available": False}

    row = db.execute_one(
        """
        SELECT
            COUNT(*) FILTER (WHERE status = 'pending')  AS pending,
            COUNT(*) FILTER (WHERE status = 'reviewed') AS reviewed,
            COUNT(*) AS total,
            AVG(ABS(auto_score - teacher_score))
                FILTER (WHERE teacher_score IS NOT NULL) AS avg_override_delta
        FROM review_queue
        """,
    )
    return {
        "available": True,
        "pending": row["pending"] if row else 0,
        "reviewed": row["reviewed"] if row else 0,
        "total": row["total"] if row else 0,
        "avg_override_delta": round(float(row["avg_override_delta"]), 2)
            if row and row["avg_override_delta"] is not None else None,
    }


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------

def _serialize_row(row: Dict) -> Dict:
    """Convert a DB row to a JSON-safe dict."""
    if not row:
        return {}
    result = dict(row)
    # Convert UUID to string
    for key in ["id"]:
        if key in result and result[key] is not None:
            result[key] = str(result[key])
    # Convert datetime
    for key in ["created_at"]:
        if key in result and result[key] is not None:
            result[key] = result[key].isoformat()
    return result


def _serialize_rows(rows: List[Dict]) -> List[Dict]:
    return [_serialize_row(r) for r in rows]
