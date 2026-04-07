"""
Orchestrator v2.0 — coordinates evaluation, integrity, and tracking.

Wires together:
- Code/Content evaluation agents
- Aggregator agent
- Integrity check (plagiarism detection)
- Student profile tracking (score history + percentile)
- Review queue (flags uncertain/suspicious submissions)
"""

import hashlib
from typing import Any, Dict, List, Optional

from ..agents.aggregator_agent import AggregatorAgent
from ..agents.code_agent import CodeEvaluationAgent
from ..agents.content_agent import ContentEvaluationAgent
from ..utils.file_parser import (
    get_student_name_from_filename,
    read_folder,
    read_submissions_by_type,
)
from ..utils.rubric import Rubric


class Orchestrator:
    """Orchestrates evaluation workflow across student submissions."""

    ASSIGNMENT_TYPES = {"code", "content", "mixed"}

    def __init__(self, rubric: Optional[Rubric] = None):
        self.rubric = rubric or Rubric()
        self.code_agent = CodeEvaluationAgent()
        self.content_agent = ContentEvaluationAgent()
        self.aggregator_agent = AggregatorAgent()

    def evaluate_submissions(
        self,
        assignment_type: str,
        folder_path: str,
        problem_statement: Optional[str] = None,
        ideal_reference: Optional[str] = None,
        assignment_id: Optional[str] = None,
        topic_tag: Optional[str] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evaluate all submissions in a folder.

        Args:
            assignment_type: 'code', 'content', or 'mixed'
            folder_path: Path to folder containing student submissions
            problem_statement: For code assignments
            ideal_reference: For content assignments
            assignment_id: Unique assignment ID (for integrity + tracking)
            topic_tag: Topic tag for student progress tracking

        Returns:
            Dictionary mapping student names to final evaluation results
        """
        if assignment_type not in self.ASSIGNMENT_TYPES:
            raise ValueError(
                f"Invalid assignment type. Must be one of: {self.ASSIGNMENT_TYPES}"
            )

        # Generate assignment_id if not provided
        if not assignment_id:
            seed = f"{assignment_type}:{problem_statement or ''}:{ideal_reference or ''}"
            assignment_id = hashlib.md5(seed.encode()).hexdigest()[:16]

        # Read submissions
        if assignment_type == "mixed":
            submissions = read_submissions_by_type(folder_path)
        else:
            submissions = read_folder(folder_path)

        # Get test cases from rubric
        test_cases = self.rubric.get_test_cases() if hasattr(self.rubric, 'get_test_cases') else []

        # Evaluate each submission
        results = {}

        if assignment_type == "code":
            results = self._evaluate_code_submissions(
                submissions, problem_statement, assignment_id, test_cases
            )
        elif assignment_type == "content":
            results = self._evaluate_content_submissions(
                submissions, ideal_reference, problem_statement, assignment_id
            )
        elif assignment_type == "mixed":
            results = self._evaluate_mixed_submissions(
                submissions, problem_statement, ideal_reference, assignment_id, test_cases
            )

        # ── Post-evaluation: student tracking + percentiles ──
        self._run_student_tracking(results, assignment_id, topic_tag or "")

        return results

    # ======================================================================
    # CODE SUBMISSIONS
    # ======================================================================

    def _evaluate_code_submissions(
        self,
        submissions: Dict[str, str],
        problem_statement: Optional[str] = None,
        assignment_id: str = "",
        test_cases: List[dict] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate code-only submissions with integrity checks."""
        results = {}
        test_cases = test_cases or []

        for filename, code in submissions.items():
            student_name = get_student_name_from_filename(filename)

            # Prepare input for code agent
            code_criteria = self.rubric.get_criteria("code")
            code_weights = {k: v.get("weight", 0.25) for k, v in code_criteria.items()}
            agent_input = {
                "problem_statement": problem_statement or "",
                "rubric": {"weights": code_weights},
                "student_code": code,
                "filename": filename,
                "test_cases": test_cases,
            }

            # Evaluate with code agent
            code_output = self.code_agent.evaluate(agent_input)

            # Aggregate
            aggregator_input = {
                "agent_outputs": [code_output],
                "rubric": {"weights": [1.0]},
            }
            final_result = self.aggregator_agent.evaluate(aggregator_input)

            result_entry = {
                "file": filename,
                "assignment_type": "code",
                **final_result,
            }

            # ── Integrity check ──
            integrity = self._run_integrity_check(
                code, assignment_id, student_name, text_content=""
            )
            if integrity:
                result_entry["flag_score"] = integrity["flag_score"]
                result_entry["flag_reasons"] = integrity["reasons"]

            # ── Review queue ──
            self._maybe_queue(student_name, assignment_id, result_entry)

            results[student_name] = result_entry

        return results

    # ======================================================================
    # CONTENT SUBMISSIONS
    # ======================================================================

    def _evaluate_content_submissions(
        self,
        submissions: Dict[str, str],
        ideal_reference: Optional[str] = None,
        problem_statement: Optional[str] = None,
        assignment_id: str = "",
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate content-only submissions."""

        # Precompute ideal reference embedding (once, not per student)
        self._precompute_embedding(ideal_reference, assignment_id)

        results = {}

        for filename, content in submissions.items():
            student_name = get_student_name_from_filename(filename)

            content_criteria = self.rubric.get_criteria("content")
            content_weights = {k: v.get("weight", 0.25) for k, v in content_criteria.items()}
            agent_input = {
                "student_content": content,
                "rubric": {"weights": content_weights},
                "ideal_reference": ideal_reference or "",
                "problem_statement": problem_statement or "",
                "rubric_id": assignment_id,
            }

            content_output = self.content_agent.evaluate(agent_input)

            aggregator_input = {
                "agent_outputs": [content_output],
                "rubric": {"weights": [1.0]},
            }
            final_result = self.aggregator_agent.evaluate(aggregator_input)

            result_entry = {
                "file": filename,
                "assignment_type": "content",
                **final_result,
            }

            # ── Integrity check ──
            integrity = self._run_integrity_check(
                "", assignment_id, student_name, text_content=content
            )
            if integrity:
                result_entry["flag_score"] = integrity["flag_score"]
                result_entry["flag_reasons"] = integrity["reasons"]

            # ── Review queue ──
            self._maybe_queue(student_name, assignment_id, result_entry)

            results[student_name] = result_entry

        return results

    # ======================================================================
    # MIXED SUBMISSIONS
    # ======================================================================

    def _evaluate_mixed_submissions(
        self,
        submissions: Dict[str, Dict[str, str]],
        problem_statement: Optional[str] = None,
        ideal_reference: Optional[str] = None,
        assignment_id: str = "",
        test_cases: List[dict] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """Evaluate mixed submissions (both code and content)."""
        test_cases = test_cases or []

        # Precompute embedding
        self._precompute_embedding(ideal_reference, assignment_id)

        results = {}
        code_submissions = submissions.get("code", {})
        content_submissions = submissions.get("text", {})

        all_students = set(
            get_student_name_from_filename(f)
            for f in list(code_submissions.keys()) + list(content_submissions.keys())
        )

        for student_name in all_students:
            agent_outputs = []

            # Evaluate code if available
            student_code = None
            for filename, code in code_submissions.items():
                if get_student_name_from_filename(filename) == student_name:
                    student_code = code
                    code_criteria = self.rubric.get_criteria("code")
                    code_weights = {k: v.get("weight", 0.25) for k, v in code_criteria.items()}
                    agent_input = {
                        "problem_statement": problem_statement or "",
                        "rubric": {"weights": code_weights},
                        "student_code": code,
                        "filename": filename,
                        "test_cases": test_cases,
                    }
                    code_output = self.code_agent.evaluate(agent_input)
                    agent_outputs.append(code_output)
                    break

            # Evaluate content if available
            for filename, content in content_submissions.items():
                if get_student_name_from_filename(filename) == student_name:
                    content_criteria = self.rubric.get_criteria("content")
                    content_weights = {k: v.get("weight", 0.25) for k, v in content_criteria.items()}
                    agent_input = {
                        "student_content": content,
                        "rubric": {"weights": content_weights},
                        "ideal_reference": ideal_reference or "",
                        "problem_statement": problem_statement or "",
                        "rubric_id": assignment_id,
                    }
                    content_output = self.content_agent.evaluate(agent_input)
                    agent_outputs.append(content_output)
                    break

            # Aggregate results
            if agent_outputs:
                weights = self.rubric.get_weights()
                aggregator_input = {
                    "agent_outputs": agent_outputs,
                    "rubric": {"weights": list(weights.values())},
                }
                final_result = self.aggregator_agent.evaluate(aggregator_input)

                result_entry = {
                    "assignment_type": "mixed",
                    "agent_count": len(agent_outputs),
                    **final_result,
                }

                # Integrity check on code + content
                integrity = self._run_integrity_check(
                    student_code or "", assignment_id, student_name, 
                    text_content=submissions.get("text", {}).get(student_name, "")
                )
                if integrity:
                    result_entry["flag_score"] = integrity["flag_score"]
                    result_entry["flag_reasons"] = integrity["reasons"]

                # Review queue
                self._maybe_queue(student_name, assignment_id, result_entry)

                results[student_name] = result_entry

        return results

    # ======================================================================
    # HELPER METHODS
    # ======================================================================

    def _run_integrity_check(
        self, code: str, assignment_id: str, student_id: str, text_content: str = ""
    ) -> Optional[Dict]:
        """Run plagiarism + AI detection. Returns None if DB unavailable."""
        try:
            from backend.core.services.integrity_service import integrity_flag
            return integrity_flag(code, assignment_id, student_id, text_content=text_content)
        except Exception as e:
            print(f"Integrity check failed (non-fatal): {e}")
            return None

    def _maybe_queue(
        self, student_id: str, assignment_id: str, result: Dict
    ):
        """Queue submission for review if trigger conditions are met."""
        try:
            from backend.core.services.review_queue import maybe_queue_for_review
            maybe_queue_for_review(
                submission_id=f"{student_id}_{assignment_id}",
                student_id=student_id,
                assignment_id=assignment_id,
                result=result,
            )
        except Exception as e:
            print(f"Review queue insert failed (non-fatal): {e}")

    def _precompute_embedding(
        self, ideal_reference: Optional[str], rubric_id: str
    ):
        """Precompute ideal answer embedding for semantic scoring."""
        if not ideal_reference:
            return
        try:
            from backend.core.services.embedding_service import (
                is_available,
                precompute_rubric_embedding,
            )
            if is_available():
                precompute_rubric_embedding(ideal_reference, rubric_id)
        except Exception:
            pass  # Embedding is optional

    def _run_student_tracking(
        self,
        results: Dict[str, Dict],
        assignment_id: str,
        topic_tag: str,
    ):
        """Record scores, compute improvement deltas, and percentile ranks."""
        try:
            from backend.core.services.student_tracker import (
                record_score,
                get_improvement_delta,
                compute_percentiles_for_cohort,
            )

            # Record scores
            score_map = {}
            for student_name, result in results.items():
                score = result.get("final_score", 0)
                record_score(student_name, assignment_id, score, topic_tag)
                score_map[student_name] = score

            # Compute percentiles across the cohort
            percentiles = compute_percentiles_for_cohort(score_map)

            # Compute deltas and attach to results
            for student_name, result in results.items():
                delta_info = get_improvement_delta(
                    student_name, topic_tag, result.get("final_score", 0)
                )
                result["percentile"] = percentiles.get(student_name)
                result["improvement_delta"] = delta_info.get("delta")
                result["trend"] = delta_info.get("trend")

        except Exception as e:
            print(f"Student tracking failed (non-fatal): {e}")

    def get_rubric(self) -> Rubric:
        return self.rubric

    def set_rubric(self, rubric: Rubric) -> None:
        self.rubric = rubric
