"""
AI Study Coach — Streaming chat endpoint for students.

Uses Ollama Phi-3 (local) or Gemini (cloud) to provide personalized
improvement guidance based on the student's evaluation history.
Streams responses token-by-token via Server-Sent Events (SSE).
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.app.middleware.auth import require_student, TokenPayload
from backend.core.services.database import get_db
from backend.core.services.student_tracker import (
    get_score_history,
    get_skill_breakdown,
    get_class_percentile,
    get_student_summary,
)

router = APIRouter(prefix="/api/portal", tags=["student-coach"])

OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "phi3:mini"


# ---------------------------------------------------------------------------
# Request / helpers
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    conversation_history: list = []


def _resolve_db_student_id(login_id: str) -> str:
    """Resolve login username to DB student_id (handles _Result suffix)."""
    db = get_db()
    if not db.available:
        return login_id
    for candidate in [login_id, f"{login_id}_Result"]:
        row = db.execute_one(
            "SELECT student_id FROM student_scores WHERE student_id = %s LIMIT 1",
            [candidate],
        )
        if row:
            return row["student_id"]
    row = db.execute_one(
        "SELECT student_id FROM student_scores WHERE student_id LIKE %s LIMIT 1",
        [f"{login_id}%"],
    )
    return row["student_id"] if row else login_id


def _build_student_context(login_id: str) -> str:
    """Build a rich context string from the student's evaluation data."""
    db_id = _resolve_db_student_id(login_id)
    summary = get_student_summary(db_id)
    history = get_score_history(db_id, limit=5)
    skills = get_skill_breakdown(db_id)
    rank = get_class_percentile(db_id)

    lines = [f"Student: {login_id}"]

    if summary.get("total_submissions", 0) > 0:
        lines.append(f"Total submissions: {summary['total_submissions']}")
        lines.append(f"Average score: {summary['average_score']:.1f}/100")
        lines.append(f"Best: {summary['best_score']:.1f}, Worst: {summary['worst_score']:.1f}")
        lines.append(f"Grade: {summary['cumulative_grade']} (GPA {summary['gpa']:.2f})")

    if rank.get("percentile"):
        lines.append(f"Class percentile: {rank['percentile']}th out of {rank.get('class_size', '?')} students")

    if skills:
        strong = sorted(skills, key=lambda s: s.get("avg_score", 0), reverse=True)
        lines.append("Topic scores: " + ", ".join(
            f"{s['topic_tag']}: {s['avg_score']:.0f}" for s in strong[:5]
        ))

    if history:
        lines.append("Recent submissions:")
        for h in history[:3]:
            lines.append(f"  - {h.get('assignment_id', 'assignment')} ({h.get('topic_tag', 'general')}): {h['score']:.1f}/100")

    # Pull recent feedback from evaluation_results
    db = get_db()
    if db.available:
        all_ids = [login_id, f"{login_id}_Result", db_id]
        placeholders = ", ".join(["%s"] * len(set(all_ids)))
        rows = db.execute(
            f"""SELECT feedback, final_score, file
               FROM evaluation_results
               WHERE submission_id IN ({placeholders})
               ORDER BY evaluated_at DESC LIMIT 2""",
            list(set(all_ids)),
        )
        if rows:
            lines.append("Recent AI feedback on submissions:")
            for r in rows:
                fb = r.get("feedback", "")
                if isinstance(fb, str):
                    try:
                        fb = json.loads(fb)
                    except Exception:
                        pass
                if isinstance(fb, list):
                    fb = " ".join(fb)
                if fb:
                    lines.append(f"  [{r.get('file', '?')} — {r.get('final_score', '?')}/100]: {str(fb)[:300]}")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an AI Study Coach for a student in an academic evaluation platform called Evaluator 2.0. You run locally on the student's machine using Phi-3 Mini.

Your role:
- Answer ANY question the student asks — academic, coding, career, study strategies, or general knowledge
- Provide personalized, actionable improvement advice based on the student's actual scores and feedback when relevant
- Create detailed, structured study plans with day-by-day breakdowns when asked
- Explain evaluation feedback in simple, encouraging terms
- Identify weak areas and suggest specific exercises with concrete examples
- Give coding tips with actual code snippets when helpful
- Be encouraging but honest about areas needing improvement

Rules:
- You can answer ANY question — you are a general-purpose study assistant, not limited to specific topics
- Use markdown formatting: **bold** for emphasis, bullet points for lists, `code` for code references
- Reference the student's actual data when the question is about their performance
- When creating study plans, use a clear day-by-day structure with checkboxes
- Never reveal other students' data
- Keep responses focused and practical (2-4 paragraphs for general questions, longer for study plans)

Student context:
{context}
"""


def _check_ollama() -> bool:
    """Quick check if Ollama is running."""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=2):
            return True
    except Exception:
        return False


def _stream_ollama(prompt: str, system: str, max_tokens: int = 512):
    """Stream tokens from Ollama's /api/chat endpoint."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": True,
        "options": {
            "num_predict": max_tokens,
            "temperature": 0.6,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        for line in resp:
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token
                if chunk.get("done"):
                    break
            except json.JSONDecodeError:
                continue
        resp.close()
    except Exception as e:
        yield f"\n\n_[Connection error: {e}]_"


# ---------------------------------------------------------------------------
# SSE Streaming endpoint
# ---------------------------------------------------------------------------

@router.post("/chat")
async def student_chat(
    body: ChatRequest,
    user: TokenPayload = Depends(require_student),
):
    """Stream AI study coach response via Server-Sent Events (Ollama only)."""
    login_id = user.student_id
    if not login_id:
        raise HTTPException(400, "Student ID not found in token")

    message = body.message.strip()
    if not message:
        raise HTTPException(400, "Message cannot be empty")

    if not _check_ollama():
        raise HTTPException(
            503,
            "AI Coach requires Ollama to be running locally. "
            "Start it with: ollama serve && ollama pull phi3:mini",
        )

    # Build context from student data
    context = _build_student_context(login_id)
    system = SYSTEM_PROMPT.format(context=context)

    # Include conversation history in the prompt (last 6 messages)
    history = body.conversation_history[-6:]
    history_text = ""
    if history:
        for h in history:
            role = h.get("role", "user")
            content = h.get("content", "")[:300]
            history_text += f"\n{role.capitalize()}: {content}"
        history_text += f"\nUser: {message}"
    else:
        history_text = message

    def event_stream():
        for token in _stream_ollama(history_text, system):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Structured improvement plan (non-streaming)
# ---------------------------------------------------------------------------

IMPROVEMENT_PLAN_PROMPT = """Based on the student's evaluation data below, create a detailed, structured weekly improvement plan.

Format the plan EXACTLY like this:

**Improvement Plan for [Student Name]**
**Current Status:** [Grade] | [GPA] | [Percentile]th percentile

**Priority Areas (weakest → strongest):**
1. [Topic] — current score: [X]/100
2. [Topic] — current score: [X]/100

**Week 1: Foundation Building**

- Day 1-2: [Topic Focus]
  - [ ] [Specific task with concrete example]
  - [ ] [Specific task]
  - [ ] Practice: [exercise description]

- Day 3-4: [Topic Focus]
  - [ ] [Specific task]
  - [ ] [Specific task]

- Day 5: Review & Self-Test
  - [ ] Re-attempt weakest submission
  - [ ] Compare with original feedback

- Day 6-7: Rest + Light Review
  - [ ] Read through corrected code
  - [ ] Note 3 key learnings

**Week 2: Skill Deepening**
[Continue with similar structure]

**Key Resources:**
- [Specific resource/tutorial for weak area 1]
- [Specific resource for weak area 2]

**Target Goals:**
- Raise [weak topic] from [X] to [Y] within 2 weeks
- Achieve overall grade of [target]

Student context:
{context}
"""


@router.post("/improvement-plan")
async def generate_improvement_plan(
    user: TokenPayload = Depends(require_student),
):
    """Generate a structured improvement plan via Ollama (streamed)."""
    login_id = user.student_id
    if not login_id:
        raise HTTPException(400, "Student ID not found in token")

    if not _check_ollama():
        raise HTTPException(503, "Ollama is not running. Start with: ollama serve")

    context = _build_student_context(login_id)
    prompt = IMPROVEMENT_PLAN_PROMPT.format(context=context)
    system = "You are an expert academic coach. Create actionable, specific study plans. Use markdown formatting with checkboxes."

    def event_stream():
        for token in _stream_ollama(
            "Generate my personalized improvement plan based on my data.",
            system + "\n\n" + prompt,
            max_tokens=1024,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/chat/status")
def chat_status(user: TokenPayload = Depends(require_student)):
    """Check if the AI coach backend (Ollama) is available."""
    ollama_ok = _check_ollama()

    return {
        "available": ollama_ok,
        "backend": "ollama" if ollama_ok else "none",
        "model": OLLAMA_MODEL if ollama_ok else "unavailable",
    }
