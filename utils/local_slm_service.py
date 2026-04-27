"""
Local SLM (Small Language Model) Service using Phi-3 Mini via llama-cpp-python.

Provides the same interface as the Gemini LLM service but runs entirely offline
using a quantized GGUF model. Zero API cost, zero rate limits, full privacy.

Model: Phi-3-mini-4k-instruct (Q4_K_M quantization, ~2.2GB)
Runtime: llama-cpp-python with Apple Silicon Metal GPU acceleration

Performance optimizations applied:
- Metal GPU offload (all layers)
- Large batch size for fast prompt processing
- Compact prompts (small models need fewer instructions)
- Aggressive input/output token limits
- Flash attention enabled
"""

import os
import time
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
                n_ctx=1024,        # Smaller context = faster prefill
                n_batch=512,       # Large batch = faster prompt processing
                n_threads=6,       # Use more CPU threads for non-GPU ops
                n_gpu_layers=-1,   # Offload ALL layers to Apple Silicon GPU (Metal)
                flash_attn=True,   # Enable flash attention for speed
                verbose=False,
            )
            print(f"✓ Local SLM loaded: Phi-3 Mini (Q4_K_M, Metal GPU)")
            return True
        except Exception as e:
            # Retry without flash_attn if it fails
            try:
                from llama_cpp import Llama
                self._model = Llama(
                    model_path=self.model_path,
                    n_ctx=1024,
                    n_batch=512,
                    n_threads=6,
                    n_gpu_layers=-1,
                    verbose=False,
                )
                print(f"✓ Local SLM loaded: Phi-3 Mini (Q4_K_M, Metal GPU, no flash_attn)")
                return True
            except Exception as e2:
                print(f"⚠ Local SLM: Failed to load model: {e2}")
                self._available = False
                return False

    def generate(self, prompt: str, max_tokens: int = 250) -> Optional[str]:
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

            t0 = time.time()
            response = self._model(
                formatted,
                max_tokens=max_tokens,
                temperature=0.2,       # Very low temp = faster convergence
                top_p=0.85,
                top_k=30,              # Limit sampling pool for speed
                repeat_penalty=1.1,    # Prevent repetitive output
                stop=["<|end|>", "<|user|>", "\n\n\n"],
                echo=False,
            )
            elapsed = time.time() - t0

            text = response["choices"][0]["text"].strip()
            tokens = response.get("usage", {}).get("completion_tokens", 0)
            if tokens and elapsed > 0:
                print(f"  ⚡ SLM: {tokens} tokens in {elapsed:.1f}s ({tokens/elapsed:.0f} tok/s)")

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
        # Ultra-compact prompt — Phi-3 is smart enough
        prompt = f"""Problem: {problem_statement[:300]}
Submission: {submission_content[:500]}
Is this {context_type} submission solving the problem? Reply ONE word: RELEVANT, PARTIAL, or IRRELEVANT."""

        result = self.generate(prompt, max_tokens=10)
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
        # Take only top 5 findings and top 5 missing concepts
        findings_str = "; ".join(deterministic_findings[:5])
        missing_str = ", ".join(missing_concepts[:5]) if missing_concepts else "none"

        # Compact prompt — every token saved = faster inference
        prompt = f"""Grade feedback for {context_type} submission.
Findings: {findings_str}
Missing: {missing_str}
Code: {submission_content[:400]}

Write exactly:
**Summary**: What the code does (1 line).
**Corrections Needed**: 2-3 specific fixes with examples.
**Strengths**: 2 bullet points."""

        result = self.generate(prompt, max_tokens=250)
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

        prompt = f"""Convert to JSON: {text[:400]}
Output format: {{"name":"Rubric","dimensions":{{"code":{{"weight":0.6,"criteria":{{"approach":{{"weight":0.5}}}}}},"content":{{"weight":0.4,"criteria":{{"coverage":{{"weight":0.5}}}}}}}}}}
Output ONLY valid JSON:"""

        result = self.generate(prompt, max_tokens=200)
        if not result:
            return None

        try:
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
