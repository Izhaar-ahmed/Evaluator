"""
Judge0 code execution service.

Submits student code + test cases to the Judge0 CE API, compares output
against expected values, and returns a pass rate (0–100).

Supports both the free Community Edition and RapidAPI-hosted Judge0.
"""

import os
import base64
import time
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Language ID mapping (Judge0 v13+)
# ---------------------------------------------------------------------------

LANGUAGE_MAP = {
    "python": 71,    # Python 3
    "cpp": 54,       # C++ (GCC 9.2)
    "java": 62,      # Java (OpenJDK 13)
    "javascript": 63, # JavaScript (Node.js 12)
}


class Judge0Service:
    """Interface to the Judge0 code execution API."""

    def __init__(self):
        self.api_url = os.getenv("JUDGE0_API_URL", "https://ce.judge0.com")
        self.api_key = os.getenv("JUDGE0_API_KEY", "")
        self.timeout = int(os.getenv("JUDGE0_TIMEOUT", "15"))
        self.cpu_time_limit = float(os.getenv("JUDGE0_CPU_LIMIT", "5"))
        self.memory_limit = int(os.getenv("JUDGE0_MEMORY_LIMIT", "262144"))  # 256 MB

    @property
    def available(self) -> bool:
        """Check if Judge0 API is configured."""
        return bool(self.api_url)

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers (include API key if RapidAPI)."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            # RapidAPI format
            headers["X-RapidAPI-Key"] = self.api_key
            headers["X-RapidAPI-Host"] = "judge0-ce.p.rapidapi.com"
        return headers

    def _get_language_id(self, language: str) -> Optional[int]:
        """Map language name to Judge0 language ID."""
        return LANGUAGE_MAP.get(language)

    # -----------------------------------------------------------------------
    # Core execution
    # -----------------------------------------------------------------------

    def run_test(self, code: str, lang_id: int, stdin: str) -> Dict:
        """
        Submit a single test case to Judge0.

        Args:
            code: Source code to execute.
            lang_id: Judge0 language ID.
            stdin: Standard input for the test case.

        Returns:
            Judge0 response dict (contains stdout, stderr, status, etc.)
        """
        payload = {
            "source_code": base64.b64encode(code.encode()).decode(),
            "language_id": lang_id,
            "stdin": base64.b64encode(stdin.encode()).decode(),
            "cpu_time_limit": self.cpu_time_limit,
            "memory_limit": self.memory_limit,
            "enable_network": False,
        }

        url = f"{self.api_url}/submissions?base64_encoded=true&wait=true"

        # Retry with exponential backoff for rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )

                if resp.status_code == 429:
                    # Rate limited — back off
                    wait_time = 2 ** attempt
                    print(f"Judge0 rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                resp.raise_for_status()
                return resp.json()

            except requests.exceptions.Timeout:
                print(f"Judge0 timeout on attempt {attempt + 1}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Judge0 request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return {"status": {"id": -1, "description": str(e)}}

        return {"status": {"id": -1, "description": "Max retries exceeded"}}

    def check_output(self, result: Dict, expected: str) -> bool:
        """
        Compare Judge0 output against expected output.

        Args:
            result: Judge0 submission result dict.
            expected: Expected output string.

        Returns:
            True if output matches expected (after stripping whitespace).
        """
        status_id = result.get("status", {}).get("id", -1)

        # Status 3 = "Accepted" (program ran successfully)
        if status_id != 3:
            return False

        raw_stdout = result.get("stdout") or ""
        try:
            actual = base64.b64decode(raw_stdout).decode().strip()
        except Exception:
            actual = raw_stdout.strip()

        return actual == expected.strip()

    # -----------------------------------------------------------------------
    # Aggregate scoring
    # -----------------------------------------------------------------------

    def compute_test_score(
        self, code: str, language: str, test_cases: List[Dict]
    ) -> float:
        """
        Run all test cases and compute a pass rate (0–100).

        Args:
            code: Student source code.
            language: Language name ("python", "cpp", etc.)
            test_cases: List of {"stdin": str, "expected_output": str}.

        Returns:
            Score from 0 to 100.
        """
        if not test_cases:
            return 0

        lang_id = self._get_language_id(language)
        if lang_id is None:
            print(f"Judge0: unsupported language '{language}'")
            return 0

        passed = 0
        for tc in test_cases:
            stdin = tc.get("stdin", "")
            expected = tc.get("expected_output", "")
            result = self.run_test(code, lang_id, stdin)
            if self.check_output(result, expected):
                passed += 1

        return round((passed / len(test_cases)) * 100)
