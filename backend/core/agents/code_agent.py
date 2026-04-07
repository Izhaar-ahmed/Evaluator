"""
Code Evaluation Agent — v2.0

Evaluates student code submissions through:
- Tree-sitter AST analysis (unified across Python & C++)
- Judge0 test case execution (when test cases are available)
- LLM relevance verification
- Keyword heuristics (fallback)
"""

import re
from typing import Any, Dict, List, Optional

from .base_agent import EvaluationAgent
from utils.llm_service import LLMService
from backend.core.services.treesitter_parser import extract_features


class CodeEvaluationAgent(EvaluationAgent):
    """Evaluates student code submissions through static analysis."""

    def __init__(self):
        super().__init__()
        self.llm_service = LLMService()
        self.STOP_WORDS = {
            "function", "return", "class", "solution", "input", "output", "code",
            "string", "include", "std", "write", "example", "explanation", "leetcode",
            "implement", "given", "problem", "following", "int", "float", "double",
            "bool", "void", "vector", "list", "map", "set", "array", "if", "for",
            "while", "const", "main", "args", "public", "private"
        }
        self._judge0_service = None  # Lazy-loaded

    def _get_judge0(self):
        """Lazy-load Judge0 service."""
        if self._judge0_service is None:
            try:
                from backend.core.services.judge0_service import Judge0Service
                self._judge0_service = Judge0Service()
            except Exception:
                self._judge0_service = False  # Mark as unavailable
        return self._judge0_service if self._judge0_service is not False else None

    def _detect_language(self, code: str, filename: str = "") -> str:
        """Detect programming language from code or filename."""
        if filename:
            ext = filename.lower().split('.')[-1] if '.' in filename else ""
            if ext in ['cpp', 'cc', 'cxx', 'h', 'hpp']:
                return 'cpp'
            elif ext == 'py':
                return 'python'

        # Fallback: check code patterns
        if '#include' in code or 'std::' in code:
            return 'cpp'
        return 'python'

    def evaluate(self, input_data: Any) -> Dict[str, Any]:
        """
        Evaluate student code through static analysis + optional test execution.

        Args:
            input_data: Dictionary containing:
                - problem_statement (str): The coding problem
                - rubric (dict): Evaluation criteria with weights
                - student_code (str): The student's code submission
                - filename (str): Original filename for language detection
                - test_cases (list, optional): [{stdin, expected_output}, ...]

        Returns:
            Dictionary with score, max_score, feedback
        """
        problem_statement = input_data.get("problem_statement", "")
        rubric = input_data.get("rubric", {})
        student_code = input_data.get("student_code", "")
        filename = input_data.get("filename", "")
        test_cases = input_data.get("test_cases", [])

        language = self._detect_language(student_code, filename)

        # ── Parse code once via tree-sitter (used by all scoring methods) ──
        features = extract_features(student_code, language)

        # Immediate fail if syntax error detected
        if features.get("has_syntax_error"):
            return {
                "score": 0,
                "max_score": 100,
                "feedback": [
                    "❌ Code has syntax errors and cannot be parsed.",
                    f"→ Parser mode: {features.get('parser_mode', 'unknown')}",
                    "→ Fix syntax errors before resubmitting.",
                ],
            }

        feedback = []
        scores = {}

        # ── Approach scoring (LLM + keywords + optional Judge0 tests) ──
        approach_score = self._evaluate_approach(
            student_code, problem_statement, feedback, language, test_cases
        )
        scores["approach"] = approach_score

        # ── Conditional Effort Rewarding (relevance gate) ──
        if approach_score >= 60:
            relevance_multiplier = 1.0
        else:
            relevance_multiplier = approach_score / 60.0

        # ── Readability ──
        readability_raw = self._evaluate_readability(student_code, feedback, language)
        if approach_score == 0:
            scores["readability"] = min(readability_raw, 10)
        else:
            scores["readability"] = readability_raw * relevance_multiplier

        # ── Structure (now uses unified features dict) ──
        structure_raw = self._evaluate_structure(student_code, feedback, language, features)
        scores["structure"] = structure_raw * relevance_multiplier

        # ── Effort (now uses unified features dict) ──
        effort_raw = self._evaluate_effort(student_code, feedback, language, features)
        scores["effort"] = effort_raw * relevance_multiplier

        if approach_score == 0:
            feedback.append(
                "Evaluation Note: Non-relevant submission. "
                "Effort and structure rewards are withheld."
            )

        # ── Calculate total score ──
        weights = rubric.get("weights", {
            "approach": 0.4,
            "readability": 0.2,
            "structure": 0.2,
            "effort": 0.2,
        })

        total_score = sum(scores.get(k, 0) * v for k, v in weights.items())
        max_score = sum(weights.values()) * 100

        # ── LLM Feedback ──
        if self.llm_service.enabled:
            missing_concepts = getattr(self, "_last_missing_concepts", [])
            findings = [
                f for f in feedback
                if f.startswith("✓") or f.startswith("→") or f.startswith("❌")
            ]
            llm_feedback = self.llm_service.generate_semantic_feedback(
                context_type="code",
                submission_content=student_code,
                rubric_context=str(rubric),
                deterministic_findings=findings,
                missing_concepts=missing_concepts,
                relevance_status=getattr(self, "_last_relevance_verdict", "UNCERTAIN"),
            )
            if llm_feedback:
                feedback = ["LLM Explanation:"] + llm_feedback

        return {
            "score": round(total_score, 2),
            "max_score": max_score,
            "feedback": feedback,
        }

    # ======================================================================
    # APPROACH — unified implementation (no more Python/C++ split)
    # ======================================================================

    def _evaluate_approach(
        self,
        code: str,
        problem: str,
        feedback: List[str],
        language: str,
        test_cases: List[dict] = None,
    ) -> float:
        """
        Evaluate if the approach addresses the problem.

        Scoring strategy:
        - If test_cases exist → approach = 0.4 * llm_relevance + 0.6 * test_score
        - If no test_cases   → 100% LLM + keyword heuristics (current behaviour)
        """
        test_cases = test_cases or []

        # ── Step 1: LLM-based relevance check ──
        llm_verdict = None
        if self.llm_service.enabled:
            llm_verdict = self.llm_service.check_relevance(problem, code, "code")
            self._last_relevance_verdict = llm_verdict

            if llm_verdict == "IRRELEVANT":
                feedback.append(
                    "⚠️ LLM determined code is irrelevant to the problem. Score: 0."
                )
                return 0
            elif llm_verdict == "PARTIAL":
                feedback.append(
                    "⚠️ LLM found partial relevance. Proceeding with reduced scoring."
                )
            elif llm_verdict == "RELEVANT":
                feedback.append(
                    "✓ LLM verified submission is relevant to the problem."
                )
            # UNCERTAIN falls through to keyword/test logic

        # ── Step 2: Keyword relevance (unified, language-agnostic) ──
        llm_score = self._keyword_relevance_score(code, problem, feedback, llm_verdict)

        # ── Step 3: Judge0 test execution (if test cases exist) ──
        if test_cases:
            judge0 = self._get_judge0()
            if judge0:
                test_score = judge0.compute_test_score(code, language, test_cases)
                feedback.append(
                    f"✓ Test execution: {test_score}% of test cases passed."
                )
                # Blend: 40% LLM/keyword relevance + 60% ground-truth tests
                blended = 0.4 * llm_score + 0.6 * test_score
                return min(round(blended), 100)
            else:
                feedback.append(
                    "⚠️ Judge0 unavailable. Falling back to LLM-only approach scoring."
                )

        return llm_score

    def _keyword_relevance_score(
        self, code: str, problem: str, feedback: List[str], llm_verdict: Optional[str]
    ) -> float:
        """Compute keyword-based relevance score (language-agnostic)."""
        problem_keywords = [
            w for w in set(re.findall(r'\b\w{4,}\b', problem.lower()))
            if w not in self.STOP_WORDS
        ]

        code_lower = code.lower()
        covered_keywords = [w for w in problem_keywords if w in code_lower]
        missing_keywords = [w for w in problem_keywords if w not in code_lower]

        self._last_missing_concepts = missing_keywords

        total_keywords = len(problem_keywords)
        match_ratio = len(covered_keywords) / total_keywords if total_keywords > 0 else 0

        # LLM-augmented scoring
        if llm_verdict in ["RELEVANT", "PARTIAL"]:
            if match_ratio >= 0.3 or len(covered_keywords) >= 3:
                score = 100 if llm_verdict == "RELEVANT" else 80
                feedback.append("Relevant approach with good keyword alignment.")
            elif match_ratio >= 0.15:
                score = 90 if llm_verdict == "RELEVANT" else 60
                feedback.append("Relevant approach (LLM verified).")
            else:
                score = 80 if llm_verdict == "RELEVANT" else 30
                feedback.append("LLM verified relevance, but keyword match is minimal.")
        else:
            # Fallback — strict
            if match_ratio >= 0.25 or len(covered_keywords) >= 2:
                score = 75
                feedback.append(
                    f"Code appears relevant based on keyword match "
                    f"({len(covered_keywords)} matches)."
                )
            else:
                feedback.append(
                    f"Irrelevant submission: Code does not address problem "
                    f"(Low match ratio: {int(match_ratio * 100)}%, "
                    f"Found {len(covered_keywords)} keywords)."
                )
                return 0

        return min(score, 100)

    # ======================================================================
    # READABILITY — (kept mostly unchanged, works for both languages)
    # ======================================================================

    def _evaluate_readability(
        self, code: str, feedback: List[str], language: str = "python"
    ) -> float:
        """Evaluate code readability."""
        score = 0
        lines = code.split("\n")

        # Line length check
        long_lines = sum(1 for line in lines if len(line.strip()) > 100)
        if long_lines == 0:
            score += 60
            feedback.append("Line length is appropriate for readability.")
        else:
            feedback.append(
                f"→ {long_lines} lines exceed 100 characters. "
                "Break them into shorter lines."
            )

        # Comment check (language-specific)
        if language == "python":
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        else:
            single_line_comments = sum(1 for line in lines if "//" in line)
            multi_line_comments = len(re.findall(r'/\*.*?\*/', code, re.DOTALL))
            comment_lines = single_line_comments + multi_line_comments

        if comment_lines > 0:
            score += 40
            feedback.append(f"Code includes comments ({comment_lines} found).")
        else:
            feedback.append("→ Add comments to explain your logic.")

        return min(score, 100)

    # ======================================================================
    # STRUCTURE — now uses the unified features dict
    # ======================================================================

    def _evaluate_structure(
        self,
        code: str,
        feedback: List[str],
        language: str = "python",
        features: Dict = None,
    ) -> float:
        """Evaluate code structure and organization using parsed features."""
        score = 0

        if features is None:
            features = extract_features(code, language)

        if features.get("has_syntax_error"):
            return 0

        total_definitions = features.get("functions", 0) + features.get("classes", 0)

        if total_definitions > 0:
            score += 60
            feedback.append(
                f"Good modularization ({total_definitions} functions/classes)."
            )
        else:
            feedback.append(
                "→ Consider breaking code into functions for reusability."
            )

        # Language-specific bonus checks
        if language == "python":
            # Check for variable assignments as proxy for structured logic
            lines = code.split("\n")
            assignments = sum(1 for line in lines if "=" in line and "==" not in line)
            if assignments > 0:
                score += 40
                feedback.append("Code uses variable assignments (structured logic).")
        elif language == "cpp":
            if 'namespace' in code or 'std::' in code or ('#ifndef' in code and '#define' in code):
                score += 40
                feedback.append("✓ Code uses namespaces/guards (good C++ practice).")

        # Error handling bonus (tree-sitter detects try/catch across languages)
        if features.get("error_handling", 0) > 0:
            score += 10
            feedback.append(
                f"✓ Code includes error handling "
                f"({features['error_handling']} try/catch blocks)."
            )

        return min(score, 100)

    # ======================================================================
    # EFFORT — now uses the unified features dict
    # ======================================================================

    def _evaluate_effort(
        self,
        code: str,
        feedback: List[str],
        language: str = "python",
        features: Dict = None,
    ) -> float:
        """Evaluate visible effort and complexity using parsed features."""
        score = 0

        if features is None:
            features = extract_features(code, language)

        lines = code.split("\n")
        # Filter comments
        if language == "python":
            non_empty = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        else:
            non_empty = [l for l in lines if l.strip() and not l.strip().startswith("//")]

        code_lines = len(non_empty)

        if code_lines > 5:
            score += 60
            feedback.append(f"Substantial code submission ({code_lines} lines).")
        elif code_lines > 0:
            score += 30
            feedback.append(
                "→ Your solution is brief. Consider adding more logic or cases."
            )

        # Control flow from features (unified — no more if/else per language)
        control_flow = features.get("loops", 0) + features.get("conditions", 0)
        if control_flow > 0:
            score += 40
            feedback.append(
                f"✓ Code includes control flow ({control_flow} conditions/loops)."
            )

        return min(score, 100)
