"""
Local SLM (Small Language Model) Service — Ollama + llama-cpp-python dual backend.

Priority:
1. Ollama (http://localhost:11434) — optimized Metal runtime, ~20-30 tok/s on M1
2. llama-cpp-python fallback — direct GGUF loading, ~3-5 tok/s on M1

Both are fully offline, zero API cost, full privacy.
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path


class LocalSLMService:
    """
    Offline language model service with dual backend support.

    Backend priority:
    1. Ollama REST API (faster Metal runtime, requires ollama serve running)
    2. llama-cpp-python (direct GGUF, slower but no daemon needed)
    """

    DEFAULT_MODEL_PATH = "/Users/bilal/offline-rag/models/Phi-3-mini-4k-instruct-Q4_K_M.gguf"
    OLLAMA_URL = "http://127.0.0.1:11434"
    OLLAMA_MODEL = "phi3:mini"

    def __init__(self):
        self.model_path = os.getenv("LOCAL_MODEL_PATH", self.DEFAULT_MODEL_PATH)
        self.ollama_url = os.getenv("OLLAMA_URL", self.OLLAMA_URL)
        self.ollama_model = os.getenv("OLLAMA_MODEL", self.OLLAMA_MODEL)
        self._llama_model = None
        self._backend = None   # "ollama", "llama_cpp", or None
        self._available = None

    @property
    def available(self) -> bool:
        """Check if any local model backend is available."""
        if self._available is not None:
            return self._available

        # Try Ollama first (faster)
        if self._check_ollama():
            self._backend = "ollama"
            self._available = True
            return True

        # Fall back to llama-cpp-python
        if self._check_llama_cpp():
            self._backend = "llama_cpp"
            self._available = True
            return True

        self._available = False
        return False

    def _check_ollama(self) -> bool:
        """Check if Ollama server is running and has our model."""
        try:
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                # Check for phi3 variants
                for m in models:
                    if "phi3" in m or "phi-3" in m or "phi3:mini" in m:
                        self.ollama_model = m
                        print(f"✓ Ollama backend available: {m}")
                        return True
                # Model not pulled yet
                print(f"⚠ Ollama running but model not found. Available: {models}")
                return False
        except Exception:
            return False

    def _check_llama_cpp(self) -> bool:
        """Check if llama-cpp-python is available with the GGUF model."""
        if not Path(self.model_path).exists():
            return False
        try:
            from llama_cpp import Llama
            return True
        except ImportError:
            return False

    def _ensure_llama_loaded(self) -> bool:
        """Lazy-load the llama-cpp-python model."""
        if self._llama_model is not None:
            return True
        try:
            from llama_cpp import Llama
            print(f"⏳ Loading local SLM from {Path(self.model_path).name}...")
            self._llama_model = Llama(
                model_path=self.model_path,
                n_ctx=1024,
                n_batch=512,
                n_threads=6,
                n_gpu_layers=-1,
                flash_attn=True,
                verbose=False,
            )
            print(f"✓ Local SLM loaded: Phi-3 Mini (llama-cpp, Metal GPU)")
            return True
        except Exception:
            try:
                from llama_cpp import Llama
                self._llama_model = Llama(
                    model_path=self.model_path,
                    n_ctx=1024, n_batch=512, n_threads=6,
                    n_gpu_layers=-1, verbose=False,
                )
                print(f"✓ Local SLM loaded: Phi-3 Mini (llama-cpp, Metal GPU, no flash)")
                return True
            except Exception as e2:
                print(f"⚠ llama-cpp load failed: {e2}")
                return False

    # ================================================================
    # UNIFIED GENERATION
    # ================================================================

    def generate(self, prompt: str, max_tokens: int = 250) -> Optional[str]:
        """Generate text using the best available backend."""
        if not self.available:
            return None

        if self._backend == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        else:
            return self._generate_llama_cpp(prompt, max_tokens)

    def _generate_ollama(self, prompt: str, max_tokens: int = 250) -> Optional[str]:
        """Generate via Ollama REST API (fast Metal runtime)."""
        try:
            payload = json.dumps({
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.2,
                    "top_p": 0.85,
                    "top_k": 30,
                    "repeat_penalty": 1.1,
                },
            }).encode("utf-8")

            req = urllib.request.Request(
                f"{self.ollama_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            t0 = time.time()
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())

            elapsed = time.time() - t0
            text = data.get("response", "").strip()
            eval_count = data.get("eval_count", 0)
            if eval_count and elapsed > 0:
                print(f"  ⚡ Ollama: {eval_count} tokens in {elapsed:.1f}s ({eval_count/elapsed:.0f} tok/s)")

            return text if text else None

        except Exception as e:
            print(f"⚠ Ollama generation failed: {e}")
            # Try falling back to llama-cpp
            if self._check_llama_cpp():
                self._backend = "llama_cpp"
                return self._generate_llama_cpp(prompt, max_tokens)
            return None

    def _generate_llama_cpp(self, prompt: str, max_tokens: int = 250) -> Optional[str]:
        """Generate via llama-cpp-python (fallback)."""
        if not self._ensure_llama_loaded():
            return None

        try:
            formatted = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"

            t0 = time.time()
            response = self._llama_model(
                formatted,
                max_tokens=max_tokens,
                temperature=0.2,
                top_p=0.85,
                top_k=30,
                repeat_penalty=1.1,
                stop=["<|end|>", "<|user|>", "\n\n\n"],
                echo=False,
            )
            elapsed = time.time() - t0

            text = response["choices"][0]["text"].strip()
            tokens = response.get("usage", {}).get("completion_tokens", 0)
            if tokens and elapsed > 0:
                print(f"  ⚡ llama-cpp: {tokens} tokens in {elapsed:.1f}s ({tokens/elapsed:.0f} tok/s)")

            return text if text else None

        except Exception as e:
            print(f"⚠ llama-cpp generation failed: {e}")
            return None

    # ================================================================
    # HIGH-LEVEL API (same interface as Gemini LLMService)
    # ================================================================

    def check_relevance(self, problem_statement: str, submission_content: str,
                        context_type: str = "code") -> str:
        """Check if submission is relevant. Returns: RELEVANT/PARTIAL/IRRELEVANT/UNCERTAIN."""
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

    def generate_semantic_feedback(self, context_type: str, submission_content: str,
                                   rubric_context: str, deterministic_findings: List[str],
                                   missing_concepts: List[str] = None,
                                   relevance_status: str = "UNCERTAIN") -> List[str]:
        """Generate qualitative feedback for a student submission."""
        findings_str = "; ".join(deterministic_findings[:5])
        missing_str = ", ".join(missing_concepts[:5]) if missing_concepts else "none"

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
        """Convert plain text rubric into structured JSON."""
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


# Singleton
_local_slm = None

def get_local_slm() -> LocalSLMService:
    """Get or create the singleton LocalSLMService instance."""
    global _local_slm
    if _local_slm is None:
        _local_slm = LocalSLMService()
    return _local_slm
