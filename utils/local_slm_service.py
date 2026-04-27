"""
Local SLM (Small Language Model) Service using Phi-3 Mini via llama-cpp-python.

Provides the same interface as the Gemini LLM service but runs entirely offline
using a quantized GGUF model. Zero API cost, zero rate limits, full privacy.

Model: Phi-3-mini-4k-instruct (Q4_K_M quantization, ~2.2GB)
Runtime: llama-cpp-python (CPU inference, ~5-15s per response on Apple Silicon)
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path


class LocalSLMService:
    """
    Offline language model service using Phi-3 Mini via llama-cpp-python.

    Acts as a drop-in replacement for the Gemini LLM service when:
    - No API key is available
    - API is rate-limited
    - Offline operation is needed
    - Cost savings are required
    """

    # Default model path — override via LOCAL_MODEL_PATH env var
    DEFAULT_MODEL_PATH = "/Users/bilal/offline-rag/models/Phi-3-mini-4k-instruct-Q4_K_M.gguf"

    def __init__(self):
        self.model_path = os.getenv("LOCAL_MODEL_PATH", self.DEFAULT_MODEL_PATH)
        self._model = None
        self._available = None  # None = not checked yet

    @property
    def available(self) -> bool:
        """Check if the local model file exists and llama-cpp-python is installed."""
        if self._available is not None:
            return self._available

        if not Path(self.model_path).exists():
            print(f"⚠ Local SLM: Model file not found at {self.model_path}")
            self._available = False
            return False

        try:
            from llama_cpp import Llama
            self._available = True
        except ImportError:
            print("⚠ Local SLM: llama-cpp-python not installed. Run: pip install llama-cpp-python")
            self._available = False

        return self._available

    def _ensure_loaded(self) -> bool:
        """Lazy-load the model on first use (takes ~2-5 seconds)."""
        if self._model is not None:
            return True

        if not self.available:
            return False

        try:
            from llama_cpp import Llama
            print(f"⏳ Loading local SLM from {Path(self.model_path).name}...")
            self._model = Llama(
                model_path=self.model_path,
                n_ctx=2048,        # Context window (keep small for speed)
                n_threads=4,       # CPU threads (for non-GPU ops)
                n_gpu_layers=-1,   # Offload ALL layers to Apple Silicon GPU (Metal)
                verbose=False,
            )
            print(f"✓ Local SLM loaded: Phi-3 Mini (Q4_K_M)")
            return True
        except Exception as e:
            print(f"⚠ Local SLM: Failed to load model: {e}")
            self._available = False
            return False

    def generate(self, prompt: str, max_tokens: int = 800) -> Optional[str]:
        """
        Generate a response from the local model.

        Args:
            prompt: The input prompt (Phi-3 instruct format applied internally)
            max_tokens: Maximum tokens in the response

        Returns:
            Generated text, or None on failure
        """
        if not self._ensure_loaded():
            return None

        try:
            # Phi-3 instruct format
            formatted = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

            response = self._model(
                formatted,
                max_tokens=max_tokens,
                temperature=0.3,       # Low temp for consistent evaluation
                top_p=0.9,
                stop=["<|end|>", "<|user|>"],
                echo=False,
            )

            text = response["choices"][0]["text"].strip()
            return text if text else None

        except Exception as e:
            print(f"⚠ Local SLM generation failed: {e}")
            return None

    def check_relevance(
        self,
        problem_statement: str,
        submission_content: str,
        context_type: str = "code"
    ) -> str:
        """
        Check if a submission is relevant to the problem statement.

        Returns: RELEVANT, PARTIAL, IRRELEVANT, or UNCERTAIN
        """
        prompt = f"""You are evaluating if a student's {context_type} submission answers the assigned problem.

Problem: {problem_statement[:800]}

Submission (first 1500 chars):
{submission_content[:1500]}

Does this submission attempt to solve the assigned problem?
Reply with ONLY one word: RELEVANT, PARTIAL, IRRELEVANT, or UNCERTAIN."""

        result = self.generate(prompt, max_tokens=20)
        if not result:
            return "UNCERTAIN"

        result = result.strip().upper()
        for verdict in ["RELEVANT", "PARTIAL", "IRRELEVANT", "UNCERTAIN"]:
            if verdict in result:
                return verdict

        return "UNCERTAIN"

    def generate_semantic_feedback(
        self,
        context_type: str,
        submission_content: str,
        rubric_context: str,
        deterministic_findings: List[str],
        missing_concepts: List[str] = None,
        relevance_status: str = "UNCERTAIN"
    ) -> List[str]:
        """
        Generate qualitative feedback for a student submission.

        Returns: List of feedback strings
        """
        findings_str = "\n".join(f"- {f}" for f in deterministic_findings[:10])
        missing_str = ", ".join(missing_concepts[:8]) if missing_concepts else "None"

        prompt = f"""You are a helpful teaching assistant providing feedback on a student's {context_type} submission.

Evaluation Findings:
{findings_str}

Missing Concepts: {missing_str}

Student Submission (excerpt):
{submission_content[:1200]}

Provide feedback in this EXACT format:
**Summary**: One sentence about what the submission does.
**Corrections Needed**: Specific, actionable improvements the student should make. Give examples.
**Strengths**: 2-3 bullet points of what was done well.

Be encouraging but precise. Do not assign scores."""

        result = self.generate(prompt, max_tokens=600)
        if not result:
            return []

        lines = [line.strip() for line in result.split("\n") if line.strip()]
        return lines

    def parse_rubric_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Convert plain text rubric description into structured JSON.

        Returns: Parsed rubric dict, or None on failure
        """
        import json

        prompt = f"""Convert this grading rubric description into a JSON object.

Rubric Text:
{text[:1000]}

Output ONLY valid JSON matching this structure (no markdown, no explanation):
{{
  "name": "Custom Rubric",
  "version": "1.0",
  "dimensions": {{
    "code": {{
      "weight": 0.6,
      "max_score": 100,
      "criteria": {{
        "approach": {{"weight": 0.4, "max_score": 100}},
        "readability": {{"weight": 0.3, "max_score": 100}},
        "structure": {{"weight": 0.3, "max_score": 100}}
      }}
    }},
    "content": {{
      "weight": 0.4,
      "max_score": 100,
      "criteria": {{
        "coverage": {{"weight": 0.5, "max_score": 100}},
        "alignment": {{"weight": 0.5, "max_score": 100}}
      }}
    }}
  }}
}}

Adjust weights and criteria based on the rubric text. Output ONLY JSON."""

        result = self.generate(prompt, max_tokens=500)
        if not result:
            return None

        try:
            # Clean up any markdown
            json_str = result.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("\n", 1)[1] if "\n" in json_str else json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            return json.loads(json_str.strip())
        except Exception as e:
            print(f"⚠ Local SLM rubric parse failed: {e}")
            return None


# Singleton instance for reuse across the application
_local_slm = None

def get_local_slm() -> LocalSLMService:
    """Get or create the singleton LocalSLMService instance."""
    global _local_slm
    if _local_slm is None:
        _local_slm = LocalSLMService()
    return _local_slm
