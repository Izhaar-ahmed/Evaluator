<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_AI-2.0-8E75B2?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-Local_SLM-FF6B35?style=for-the-badge&logo=ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Phi--3_Mini-Offline-00D4AA?style=for-the-badge&logo=microsoft&logoColor=white" />
</p>

<h1 align="center">🎓 Evaluator 2.0</h1>
<h3 align="center">Intelligent AI-Powered Academic Assessment Platform</h3>

<p align="center">
  <em>An end-to-end system for evaluating student code and content submissions using AST analysis, LLM reasoning (cloud + offline), semantic embeddings, automated test execution, plagiarism detection, and real-time student performance tracking — with a multi-tier AI fallback chain (Gemini → Ollama Phi-3 → rule-based) and intelligent single-file mixed evaluation, all managed through a beautiful dark-mode teacher dashboard.</em>
</p>

<p align="center">
  <strong>Built by</strong>: B Harsha Vardhan (23BDS015) · L Akash (23BDS031) · S Sasi Rekha (23BDS049) · SK Izhaar Ahmed (23BDS053)
</p>

---

## 📖 Table of Contents

1.  [What is Evaluator 2.0?](#-what-is-evaluator-20)
2.  [Key Features at a Glance](#-key-features-at-a-glance)
3.  [System Architecture](#-system-architecture)
4.  [How the Scoring Pipeline Works](#-how-the-scoring-pipeline-works)
    - [Step 1: File Upload & Parsing](#step-1-file-upload--parsing)
    - [Step 1a: Single-File Mixed Evaluation (Auto-Split)](#step-1a-single-file-mixed-evaluation-auto-split)
    - [Step 2: LLM Relevance Check](#step-2-llm-relevance-check)
    - [Step 3: Code Evaluation (Code Agent)](#step-3-code-evaluation-code-agent)
    - [Step 4: Content Evaluation (Content Agent)](#step-4-content-evaluation-content-agent)
    - [Step 5: Test Case Execution (Judge0 / Local)](#step-5-test-case-execution-judge0--local)
    - [Step 6: Score Aggregation](#step-6-score-aggregation)
    - [Step 7: Integrity Check (Plagiarism + AI Detection)](#step-7-integrity-check-plagiarism--ai-detection)
    - [Step 8: Student Tracking & Percentiles](#step-8-student-tracking--percentiles)
    - [Step 9: Review Queue](#step-9-review-queue)
5.  [Tree-Sitter: How Code is Structurally Analyzed](#-tree-sitter-how-code-is-structurally-analyzed)
6.  [Semantic Embeddings: Understanding Meaning, Not Just Keywords](#-semantic-embeddings-understanding-meaning-not-just-keywords)
7.  [LLM Integration: Multi-Tier AI Fallback Chain](#-llm-integration-multi-tier-ai-fallback-chain)
8.  [Offline SLM: Ollama + Phi-3 Mini](#-offline-slm-ollama--phi-3-mini)
9.  [Test Case Execution: Verifying Code Correctness](#-test-case-execution-verifying-code-correctness)
10. [Integrity System: Plagiarism & AI Detection](#-integrity-system-plagiarism--ai-detection)
11. [Review Queue: Human-in-the-Loop](#-review-queue-human-in-the-loop)
12. [Student Profile Tracking](#-student-profile-tracking)
13. [Frontend: The Teacher Dashboard](#-frontend-the-teacher-dashboard)
14. [API Reference](#-api-reference)
15. [Project Structure](#-project-structure)
16. [How to Run](#-how-to-run)
17. [Environment Variables](#-environment-variables)
18. [Tech Stack](#-tech-stack)
19. [Common Questions](#-common-questions)

---

## 🎯 What is Evaluator 2.0?

**Evaluator 2.0** is an intelligent academic assessment platform designed for **teachers and professors** who need to evaluate student submissions at scale. Instead of manually reading and grading dozens (or hundreds) of code files and written reports, the teacher uploads all submissions through a web interface, and the system automatically:

1. **Parses** each submission using AST (Abstract Syntax Tree) analysis
2. **Runs test cases** against code submissions to check correctness
3. **Checks relevance** — does the submission actually answer the question?
4. **Scores** based on approach, readability, structure, and effort
5. **Detects plagiarism** between students and flags AI-generated content
6. **Generates detailed, personalized feedback** for each student
7. **Tracks student progress** over time with percentiles and trends
8. **Routes uncertain submissions** to a manual review queue for the teacher

The system is **NOT** a simple keyword counter. It combines multiple AI techniques:
- **Tree-sitter** for understanding code structure at the syntax level
- **Sentence-transformers** for understanding meaning through embeddings
- **Google Gemini** for semantic reasoning and natural language feedback (cloud)
- **Ollama + Phi-3 Mini** for offline AI feedback on Apple Silicon GPU (local)
- **GPT-2 perplexity** for detecting AI-generated submissions
- **Judge0 / Local execution** for actually running code against test cases
- **Auto-split parser** for single-file mixed submissions (code + explanation in one file)

---

## ✨ Key Features at a Glance

| Feature | What It Does | Technology Used |
|---|---|---|
| 🧠 **AST-Aware Scoring** | Understands code structure (loops, functions, nesting) | Tree-sitter |
| 🧪 **Test Case Execution** | Runs student code against test inputs/outputs | Judge0 API + Local Python/C++ fallback |
| 💬 **AI Feedback** | Generates personalized, learning-oriented comments | Gemini 2.0 Flash + Ollama Phi-3 fallback |
| 🔍 **Relevance Checking** | Verifies submission actually answers the question | Multi-tier LLM (Gemini → Phi-3 → rule-based) |
| 🕵️ **Plagiarism Detection** | Compares submissions using fingerprinting + similarity | SequenceMatcher + Fingerprinting |
| 🤖 **AI Content Detection** | Flags likely AI-generated submissions | GPT-2 Perplexity Analysis |
| 📊 **Semantic Scoring** | Understands paraphrased content, not just keywords | all-MiniLM-L6-v2 Embeddings |
| 📈 **Student Tracking** | Performance history, trends, percentile ranking | PostgreSQL + NumPy |
| 👨‍🏫 **Review Queue** | Teacher reviews flagged/uncertain submissions | In-memory + DB queue |
| 🌙 **Dark-Mode Dashboard** | Beautiful, enterprise-grade teacher UI | Next.js 14 + Tailwind CSS |
| 📄 **Single-File Mixed Eval** | One file with code + explanation → auto-split and evaluate both | Language-aware parser (Python/Text/PDF) |
| 🔌 **Offline SLM** | Zero API cost, runs locally on Apple Silicon GPU | Ollama + Phi-3 Mini (Q4_K_M, 2.2GB) |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │  Upload   │  │ Results  │  │  Review  │  │  Student Profile  │   │
│  │   Page    │  │Dashboard │  │  Queue   │  │    Dashboard      │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬──────────┘   │
│       │              │             │                  │              │
└───────┼──────────────┼─────────────┼──────────────────┼──────────────┘
        │              │             │                  │
        ▼              ▼             ▼                  ▼
┌─────────────────────── REST API (FastAPI) ──────────────────────────┐
│  POST /api/evaluate    GET /api/evaluations/history                  │
│  GET  /api/reviews     POST /api/reviews/:id/override               │
│  GET  /api/students/:id/profile                                     │
└───────┬─────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────── ORCHESTRATOR ────────────────────────────────┐
│                                                                     │
│   ┌────────────┐    ┌─────────────┐    ┌────────────────────┐      │
│   │ Code Agent │    │Content Agent│    │ Aggregator Agent   │      │
│   │            │    │             │    │                    │      │
│   │ • AST      │    │ • Keywords  │    │ • Weighted average │      │
│   │ • Approach │    │ • Embeddings│    │ • Normalization    │      │
│   │ • Readabi. │    │ • Coverage  │    │ • Score curving    │      │
│   │ • Structur.│    │ • Alignment │    │                    │      │
│   │ • Effort   │    │ • Flow      │    └────────────────────┘      │
│   └──────┬─────┘    └──────┬──────┘                                │
│          │                 │                                        │
│   ┌──────▼─────────────────▼──────┐                                │
│   │        SHARED SERVICES        │                                │
│   │ • LLM Service (Multi-tier)    │    ┌─────────────────────────┐ │
│   │   ├─ Gemini API (cloud)       │    │   INTEGRITY SERVICE     │ │
│   │   ├─ Ollama Phi-3 (local GPU) │    │ • Plagiarism detection  │ │
│   │   └─ llama-cpp (direct GGUF)  │    │ • AI content detection  │ │
│   │ • Tree-sitter Parser          │    │ • Perplexity scoring    │ │
│   │ • Embedding Service           │    └────────────┬────────────┘ │
│   │ • Judge0 / Local Runner       │                                │
│   │ • Rubric Manager              │                                │
│   │ • File Parser (auto-split)    │                                │
│   └───────────────────────────────┘                                │
│                                                      │              │
│   ┌──────────────────────────────────────────────────▼────────────┐ │
│   │                    STUDENT TRACKER                            │ │
│   │  • Score history  • Percentile ranking  • Trend analysis     │ │
│   └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │                     REVIEW QUEUE                              │ │
│   │  • Flags uncertain verdicts  • Routes to teacher dashboard   │ │
│   └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────── DATA LAYER ──────────────────────────────────┐
│  PostgreSQL          In-Memory Fallback        File System          │
│  • evaluation_results  • review queue           • CSV exports       │
│  • review_queue        • submission index       • embedding cache   │
│  • student_scores                                                   │
│  • evaluation_batches                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 How the Scoring Pipeline Works

When a teacher uploads student submissions, the system processes them through a **9-step pipeline**. Here's exactly what happens at each step:

### Step 1: File Upload & Parsing

**Where**: `backend/app/routes/evaluate.py` → `backend/core/controller/orchestrator.py`

The teacher uploads one or more files (`.py`, `.cpp`, `.txt`, etc.) through the web interface along with:
- **Assignment type**: `code`, `content`, or `mixed`
- **Problem statement**: The question that was asked (e.g., "Write a function to find all triplets that sum to zero")
- **Test cases** (optional): JSON array like `[{"input": "1 2 3", "output": "6"}]`

The system:
1. Saves uploaded files to a temporary folder
2. Reads each file's content using `file_parser.py`
3. Extracts the student name from the filename (e.g., `student_alice.py` → `student_alice`)
4. Routes to the appropriate evaluation agent based on assignment type

```python
# Example: How files are parsed (simplified)
submissions = read_folder("/tmp/uploads_abc123/")
# Returns: {"student_alice.py": "class Solution:\n  def threeSum(self, nums)...", ...}
```

### Step 1a: Single-File Mixed Evaluation (Auto-Split)

**Where**: `backend/core/utils/file_parser.py` → `split_mixed_content()` + `_auto_split_single_files()`

In traditional mixed mode, students submit two files — one for code, one for explanation. But many students prefer to put everything in **one file**. Evaluator 2.0 handles this automatically:

**The system detects when a student submits a single file for mixed evaluation and intelligently splits it into code and content streams:**

| Input File Type | Code Extracted From | Content Extracted From |
|---|---|---|
| `.py` (Python) | Full file → Code Agent | Docstrings + standalone comments → Content Agent |
| `.cpp` (C++) | Full file → Code Agent | Block comments (`/* */`) + consecutive `//` lines → Content Agent |
| `.txt` / `.md` | Fenced code blocks (` ``` `) + indented blocks → Code Agent | Everything else (prose) → Content Agent |
| `.pdf` | Fenced code blocks from extracted text → Code Agent | Prose sections → Content Agent |

**How it works internally:**

1. `_auto_split_single_files()` detects that only one submission category has files
2. `split_mixed_content()` dispatches to the appropriate language-specific splitter:
   - `_split_python()`: Extracts docstrings (triple-quoted strings at the start of functions/classes) and standalone comment blocks
   - `_split_cpp()`: Extracts `/* ... */` block comments and consecutive `// ...` line comments
   - `_split_text()`: Uses regex to find fenced code blocks (` ```python ... ``` `) and 4-space indented blocks
3. A virtual file entry is created: e.g., `student_ravi.py` → creates `student_ravi.txt` (content) and keeps `student_ravi.py` (code)
4. Both agents receive their respective portions seamlessly

```python
# Example: A single Python file with docstrings
def binary_search(arr, target):
    """
    Binary search divides a sorted array in half repeatedly.
    Time complexity: O(log n). Space: O(1) for iterative.
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
    return -1

# Code Agent receives: the full file (for AST parsing)
# Content Agent receives: "Binary search divides a sorted array..."
```

> **No student action required**: Students don't need to format their files in any special way. The parser handles Python docstrings, C++ block comments, and markdown code fences automatically.

### Step 2: LLM Relevance Check

**Where**: `utils/llm_service.py` → `check_relevance()`

Before scoring anything, the system asks **Google Gemini AI**: *"Does this submission actually answer the question that was asked?"*

The LLM returns one of **four verdicts**:

| Verdict | Meaning | Effect on Score |
|---|---|---|
| `RELEVANT` | Yes, this answers the question | Full scoring (no penalty) |
| `PARTIAL` | Somewhat related but incomplete | Reduced scoring (0.6x multiplier) |
| `UNCERTAIN` | AI isn't confident | Score as normal (no penalty) |
| `IRRELEVANT` | Completely off-topic | Approach score = 0, other scores × 0.3 |

> **Why UNCERTAIN ≠ IRRELEVANT**: When the LLM can't decide (e.g., API is rate-limited), it would be unfair to penalize the student. The system gives the benefit of the doubt and scores normally. Only a confident `IRRELEVANT` verdict triggers penalties.

If the LLM is available, it also generates rich semantic feedback like:
> *"**Summary**: This code implements a two-pointer approach on a sorted array to find all unique triplets. **Corrections Needed**: Add comments before your duplicate-skipping logic..."*

### Step 3: Code Evaluation (Code Agent)

**Where**: `backend/core/agents/code_agent.py`

This is the core scoring engine for code submissions. It evaluates **four dimensions**:

#### 3a. Approach Score (40% weight)

Measures how well the student's code solves the problem.

**Three strategies are used (best score wins):**

1. **Function Name Matching**: The system uses tree-sitter to extract function names from the code. If a function name matches a keyword from the problem statement (e.g., `threeSum` matches "threeSum" in the problem), it scores 90-100.

2. **Keyword Overlap**: Extracts meaningful keywords from the problem statement (5+ characters, excluding stopwords) and checks how many appear in the code.

3. **LLM Verdict**: If the LLM confirmed `RELEVANT`, the approach score is boosted.

```python
# Example: Function name matching
problem = "Write a function for threeSum"
code_function_names = ["threeSum"]  # extracted via tree-sitter
# "threeSum" appears in problem → approach_score = 95
```

#### 3b. Readability Score (20% weight)

Measures how easy the code is to read:
- **Line length**: Are lines under 80 characters? (good practice)
- **Comments**: Does the code have explanatory comments?
- **LLM feedback**: If Gemini is available, adds suggestions for improving readability

#### 3c. Structure Score (20% weight)

Measures code organization using tree-sitter AST analysis:
- **Number of functions/classes**: Good code is modular
- **Variable assignments**: Shows structured logic
- **Nesting depth**: Deep nesting (5+ levels) shows algorithmic complexity
- **Control flow**: Counts loops, conditions, error handling

#### 3d. Effort Score (20% weight)

Measures the amount of work put in:
- **Lines of code**: More than 20 lines → decent effort
- **Unique identifiers**: Diverse variable names show thoughtful coding
- **Nesting complexity**: Deep nesting takes more effort to write
- **Complexity score**: The tree-sitter composite score (0-100)

```
Final Code Score = approach × 0.40 + readability × 0.20 + structure × 0.20 + effort × 0.20
```

### Step 4: Content Evaluation (Content Agent)

**Where**: `backend/core/agents/content_agent.py`

For written submissions (essays, reports, PPT text), the system evaluates **four dimensions**:

| Dimension | Weight | What It Measures |
|---|---|---|
| **Coverage** | 60% | Does the submission cover the key concepts from the prompt? |
| **Alignment** | 25% | Does it meet the rubric's learning objectives and required sections? |
| **Flow** | 8% | Is the writing logically organized with transitions? |
| **Completeness** | 7% | Is it detailed enough? Does it include examples and evidence? |

**Coverage scoring uses two methods in parallel:**

1. **Keyword matching** (always available): Checks if key terms appear in the text
2. **Semantic embeddings** (if sentence-transformers is installed): Uses AI to understand that "binary search tree" and "BST" mean the same thing

The final coverage score is: `max(keyword_score × 0.5, semantic_score)` — this prevents students from gaming the system by stuffing keywords, while rewarding those who genuinely paraphrase concepts.

### Step 5: Test Case Execution (Judge0 / Local)

**Where**: `backend/core/services/judge0_service.py`

If the teacher provides test cases, the system **actually runs the student's code** against them.

**Execution strategy:**

```
1. Is Judge0 (code execution API) reachable?
   ├── YES → Submit code to Judge0 API for sandboxed execution
   └── NO → Is the code Python?
             ├── YES → Run locally via subprocess (sandboxed)
             └── NO  → Skip test execution (only static analysis)
```

**LeetCode-style auto-wrapping:**

Many students write code in class format (like LeetCode):
```python
class Solution:
    def threeSum(self, nums):
        # ... algorithm ...
```

This code doesn't produce output when run directly. The system detects this pattern and **automatically generates a wrapper**:
```python
# Auto-generated wrapper:
import sys, json
_raw_input = sys.stdin.read().strip()
_args = _parse_input(_raw_input)  # Tries JSON, space-separated, comma-separated
sol = Solution()
_result = sol.threeSum(*_args[:1])
print(_result)
```

This means test cases work even with class-based submissions.

**Test score impact:**

The test pass rate (0-100%) is added to the approach score calculation. If tests pass at 100%, it boosts the score. If tests fail, it reduces the score.

### Step 6: Score Aggregation

**Where**: `backend/core/agents/aggregator_agent.py`

The Aggregator Agent combines all individual agent outputs into a final score:

1. **Normalize** each agent's score to 0-100 scale
2. **Apply weights** from the rubric (default: code = 60%, content = 40%)
3. **Apply learning-oriented normalization**: A gentle curve that pushes scores toward the mid-range, ensuring students aren't harshly penalized for minor issues

```python
# Normalization formula
if raw_score > 85:
    final = 85 + (raw_score - 85) * 0.3    # Compress excellence (diminishing returns)
elif raw_score < 30:
    final = 30 + (raw_score - 30) * 0.5    # Lift failing scores slightly
else:
    final = raw_score                       # Middle range: keep as-is
```

### Step 7: Integrity Check (Plagiarism + AI Detection)

**Where**: `backend/core/services/integrity_service.py`

After scoring, every submission runs through integrity checks:

1. **Exact match detection**: Uses code fingerprinting (hash after normalizing whitespace/comments) to find identical submissions
2. **Fuzzy similarity**: Uses `SequenceMatcher` to detect submissions with renamed variables or slightly modified code. A similarity > 85% is suspicious; > 95% is near-certain copying.
3. **AI-generation detection**: Uses GPT-2 to compute text perplexity. Human writing typically has perplexity > 50; AI-generated text often falls below 20-30.

> **Important**: Integrity checks **never auto-zero a score**. They only produce a `flag_score` (0-1) and `flag_reasons` list. High-flag submissions are routed to the teacher's review queue.

### Step 8: Student Tracking & Percentiles

**Where**: `backend/core/services/student_tracker.py`

After each evaluation, the system updates student profiles:

1. **Record the score** in the database with topic tag
2. **Compute improvement delta**: Compare current score against the student's last 5 submissions on the same topic
3. **Determine trend**: `improving` (>5 point gain), `declining` (>5 point drop), or `stable`
4. **Compute percentile**: Where does this student rank in the class?

```python
# Example output per student:
{
    "percentile": 78,          # Top 22% of class
    "improvement_delta": +11.5, # 11.5 points better than recent average
    "trend": "improving"
}
```

### Step 9: Review Queue

**Where**: `backend/core/services/review_queue.py`

Certain submissions are automatically flagged for teacher review. A submission is queued if ANY of these conditions are true:

| Trigger | Condition | Why |
|---|---|---|
| `UNCERTAIN` | LLM couldn't determine relevance | Teacher should verify |
| `FLAG` | Integrity flag_score > 0.7 | Possible plagiarism or AI-generated |
| `BOUNDARY` | Score within 5 points of 25, 50, or 75 | Grade boundary — teacher should confirm |
| `LOW_SCORE` | Final score < 10 | Likely an evaluation error |

The teacher can then review the submission and **override the score** with their own assessment.

---

## 🌳 Tree-Sitter: How Code is Structurally Analyzed

**Where**: `backend/core/services/treesitter_parser.py`

Tree-sitter is a **parser generator tool** that builds real syntax trees from source code. Unlike regex or keyword matching, tree-sitter understands code the same way a compiler does.

### What is an AST?

An **Abstract Syntax Tree (AST)** is a tree representation of code where each node represents a syntactic element:

```
Code: for i in range(n):
          if nums[i] > 0:
              result.append(nums[i])

AST:
  for_statement
  ├── identifier: "i"
  ├── call: range(n)
  └── block
      └── if_statement
          ├── comparison: nums[i] > 0
          └── block
              └── expression_statement
                  └── call: result.append(nums[i])
```

### What metrics does tree-sitter extract?

| Metric | What It Measures | How It's Used |
|---|---|---|
| `line_count` | Total lines of code | Effort scoring |
| `function_count` | Number of `def` / function definitions | Structure scoring |
| `class_count` | Number of `class` definitions | Structure scoring |
| `comment_count` | Number of comment lines | Readability scoring |
| `loop_count` | Number of `for`/`while` loops | Approach scoring |
| `condition_count` | Number of `if`/`elif`/`else` | Approach scoring |
| `try_except_count` | Number of error-handling blocks | Structure scoring |
| `import_count` | Number of import statements | Structure scoring |
| `variable_count` | Number of variable assignments | Structure scoring |
| `max_nesting_depth` | Deepest level of nested blocks | Complexity scoring |
| `unique_identifiers` | Count of unique variable/function names | Effort scoring |
| `function_names` | List of all function/method names | Approach scoring (name matching) |
| `complexity_score` | Composite 0-100 metric | Final scoring and differentiation |

### The Complexity Score Formula

```python
complexity_score = min(100, (
    nesting_depth × 10 +           # Deep nesting = complex algorithm
    unique_identifiers × 2.5 +     # Diverse names = thoughtful code
    (conditions + loops) × 5       # Control flow = algorithmic thinking
))
```

This score is what **differentiates two structurally similar submissions**. A `threeSum` with 6 levels of nesting and 16 unique identifiers will score differently from a `threeSumClosest` with 5 levels and 19 identifiers.

**Supported Languages**: Python (`.py`) and C++ (`.cpp`)

---

## 🧮 Semantic Embeddings: Understanding Meaning, Not Just Keywords

**Where**: `backend/core/services/embedding_service.py`

### The Problem with Keywords

Simple keyword matching can't understand that:
- "Binary Search Tree" and "BST" mean the same thing
- "implement a sorting algorithm" and "write code to arrange elements" are equivalent
- A student who paraphrases concepts shouldn't be penalized

### How Embeddings Solve This

The system uses **all-MiniLM-L6-v2** (a sentence-transformer model) to convert text into 384-dimensional vectors. Texts with similar meanings end up close together in this vector space.

```
"Binary Search Tree" → [0.23, -0.11, 0.87, ...]  (384 numbers)
"BST"                → [0.21, -0.09, 0.85, ...]  (very similar vector!)
"Hash Table"         → [0.67, 0.45, -0.12, ...]  (very different vector)
```

### Two scoring methods using embeddings:

1. **Semantic Coverage Score**: Computes cosine similarity between the student's text and the ideal answer. Score range: 0-100.

2. **Concept Hit Rate**: For each key concept, finds the best-matching sentence in the student's text. If similarity > 0.55, it's a "hit". Final score = hits / total concepts.

The combined score is: `60% semantic similarity + 40% concept hit rate`

### Embedding cache

Ideal answer embeddings are computed once and cached to disk (as `.npy` files) so subsequent evaluations of the same assignment are faster.

---

## 🤖 LLM Integration: Multi-Tier AI Fallback Chain

**Where**: `utils/llm_service.py` + `utils/local_slm_service.py`

### What the LLM Does

The language model provides two capabilities:

1. **Relevance Checking** (`check_relevance`): Determines if a submission answers the question
2. **Semantic Feedback Generation** (`generate_semantic_feedback`): Creates personalized, detailed feedback

### The Fallback Chain

Evaluator 2.0 uses a **three-tier fallback chain** to ensure AI feedback is always available, even without internet:

```
┌───────────────────────────────────────────────────────────┐
│  Tier 1: Google Gemini API (Cloud)                         │
│  • ~2s response time                                       │
│  • Highest quality feedback                                 │
│  • Requires API key + internet                              │
│  • Subject to rate limits                                   │
└───────────────────────────┬───────────────────────────────┘
                            │ fails?
                            ▼
┌───────────────────────────────────────────────────────────┐
│  Tier 2: Ollama + Phi-3 Mini (Local GPU)                   │
│  • ~1.7s relevance check (warm), ~20s feedback              │
│  • Good quality feedback with code examples                 │
│  • Runs on Apple Silicon Metal GPU                          │
│  • Zero API cost, fully offline                             │
└───────────────────────────┬───────────────────────────────┘
                            │ not running?
                            ▼
┌───────────────────────────────────────────────────────────┐
│  Tier 3: Rule-Based Feedback (Always Works)                │
│  • Instant response                                        │
│  • Keyword-based + AST analysis feedback                    │
│  • No AI model needed                                      │
│  • Always available as final safety net                     │
└───────────────────────────────────────────────────────────┘
```

### Graceful Degradation

The LLM service is designed to **never break the system** when unavailable:

**Key safety rules:**
- On failure → returns `UNCERTAIN`, never `IRRELEVANT`
- Tracks consecutive failures; disables cloud after 3 to conserve quota
- Automatically detects and switches to Ollama when Gemini is rate-limited
- The system ALWAYS produces a score, even without any LLM

### Feedback Quality Comparison

| Tier | Relevance | Feedback Quality | Speed |
|---|---|---|---|
| **Gemini API** | Very accurate | Detailed with code examples | ~2s |
| **Ollama Phi-3** | Accurate | Good with specific suggestions | ~1.7s (relevance) / ~20s (feedback) |
| **Rule-based** | N/A (UNCERTAIN) | Basic keyword-based hints | Instant |

When the LLM is available, feedback looks like this:
> **Summary**: This code implements a two-pointer approach on a sorted array to find all unique triplets that sum to zero.
>
> **Corrections Needed**: Right before your `while left < right:` statement, add a comment like: `# Use two pointers to find pairs that complement nums[i]`. Also explain your duplicate-skipping logic.
>
> **Strengths**:
> - Achieved complexity score of 80.0, reflecting efficient two-pointer strategy
> - 16 unique identifiers show thoughtful variable naming
> - Perfect 100% test pass rate

---

## 🔌 Offline SLM: Ollama + Phi-3 Mini

**Where**: `utils/local_slm_service.py`

### Why Offline?

Cloud APIs are great but have limitations:
- **Cost**: Every API call costs money at scale
- **Rate limits**: Gemini free tier limits can throttle evaluations
- **Privacy**: Student submissions are sent to external servers
- **Connectivity**: Doesn't work without internet

The local SLM solves all of these by running a small but capable language model directly on your machine.

### Architecture: Dual Backend

```
LocalSLMService
├── Ollama REST API (http://127.0.0.1:11434)     ← PRIMARY
│   • Optimized Metal GPU runtime for Apple Silicon
│   • 12 tok/s on M1, faster on M2/M3
│   • Model stays loaded in memory between requests
│   • Auto-detected: checks /api/tags for phi3:mini
│
└── llama-cpp-python (direct GGUF loading)          ← FALLBACK
    • No daemon required (loads .gguf file directly)
    • 3-5 tok/s on M1
    • Uses the existing Phi-3 Q4_K_M GGUF model
```

### Model Details

| Property | Value |
|---|---|
| **Model** | Microsoft Phi-3-mini-4k-instruct |
| **Parameters** | 3.8 billion |
| **Quantization** | Q4_K_M (4-bit, mixed precision) |
| **File Size** | 2.2 GB |
| **Context Window** | 1024 tokens (optimized for speed) |
| **GPU** | Apple Silicon Metal (full layer offload) |

### Performance Benchmarks (Apple M1)

| Task | Ollama (warm) | llama-cpp | Gemini API |
|---|---|---|---|
| **Relevance check** | 1.7s | 7.3s | 2s |
| **Feedback (250 tok)** | 20s | 72s | 2s |
| **Throughput** | 12 tok/s | 3-5 tok/s | N/A |
| **Cost per call** | $0 | $0 | ~$0.001 |

### Setup

```bash
# Install Ollama
brew install ollama

# Start Ollama server (with Metal GPU acceleration)
OLLAMA_FLASH_ATTENTION=1 ollama serve

# Pull Phi-3 Mini (2.2GB download, one-time)
ollama pull phi3:mini

# Or auto-start at login:
brew services start ollama
```

> **No configuration needed**: The system auto-detects Ollama at `localhost:11434` and falls back to llama-cpp-python if Ollama isn't running.

---

## 🧪 Test Case Execution: Verifying Code Correctness

**Where**: `backend/core/services/judge0_service.py`

### How Teachers Provide Test Cases

In the upload form, teachers can paste a JSON array in the test cases textarea:

```json
[
  {"input": "-1 0 1 2 -1 -4", "output": "[[-1, -1, 2], [-1, 0, 1]]"},
  {"input": "0 1 1", "output": "[]"},
  {"input": "0 0 0", "output": "[[0, 0, 0]]"}
]
```

Both `{"input", "output"}` and `{"stdin", "expected_output"}` formats are accepted.

### Execution Flow

```
Test cases provided?
├── NO  → Skip test execution (static analysis only)
└── YES → Is it a "class Solution" pattern?
          ├── YES (Python) → Auto-wrap with stdin parser + method caller
          ├── YES (C++)    → Auto-wrap with #include headers + main() generator
          └── NO           → Run code as-is
          ↓
          Is Judge0 reachable? (actual HTTP ping to /about endpoint)
          ├── YES → Submit to Judge0 API (sandboxed, supports all languages)
          └── NO  → Is the language Python?
                    ├── YES → Run locally via Python subprocess
                    └── NO  → Is the language C++?
                              ├── YES → Compile with g++ -std=c++17 and run locally
                              └── NO  → Skip test execution (log warning)
```

### C++ LeetCode Auto-Wrapping

**Where**: `judge0_service.py` → `_wrap_cpp_class_solution()`

Many students submit LeetCode-style C++ solutions as bare classes without `main()` or `#include` headers:

```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {
        // student code here...
    }
};
```

The system **automatically wraps** this with a complete executable program:

1. **Prepends headers**: `<iostream>`, `<vector>`, `<unordered_map>`, `<sstream>`, `<algorithm>`, `<climits>`, etc.
2. **Adds `using namespace std;`**
3. **Parses the method signature** using regex to detect parameter types (`vector<int>`, `int`, `string`, `bool`, `double`)
4. **Generates a `main()` function** that:
   - Reads each parameter from stdin (line-by-line)
   - Parses JSON arrays like `[-3,4,3,90]` into `vector<int>`
   - Parses scalar values like `9` into `int`
   - Creates a `Solution` instance and calls the detected method
   - Prints the result in the expected format (e.g., `[0,2]` for vector results)

**Example**: Given the input `[-3,4,3,90]\n0` and the class above, the wrapper generates:

```cpp
#include <iostream>
#include <vector>
#include <sstream>
#include <unordered_map>
using namespace std;

class Solution { /* student code */ };

int main() {
    string line0;
    getline(cin, line0);
    vector<int> arg0;
    // ... parse JSON array from line0 ...
    
    string line1;
    getline(cin, line1);
    int arg1 = stoi(line1);
    
    Solution sol;
    vector<int> result = sol.twoSum(arg0, arg1);
    cout << "[";
    for(int i = 0; i < (int)result.size(); i++) {
        if(i > 0) cout << ",";
        cout << result[i];
    }
    cout << "]" << endl;
    return 0;
}
```

This is analogous to how LeetCode itself tests your submissions — the auto-wrapper acts as the invisible test harness.

### Local C++ Execution Fallback

**Where**: `judge0_service.py` → `_run_local_cpp()`

When Judge0 (Docker) is unavailable, C++ code is compiled and executed locally using the system's `g++` compiler:

1. Wrapped code is written to a temporary `.cpp` file
2. Compiled with `g++ -std=c++17 -O2`
3. Binary is executed as a subprocess with stdin piped in
4. stdout is captured, base64-encoded (matching Judge0 response format)
5. All temporary files are cleaned up afterward
6. Returns a Judge0-compatible response dict for unified handling downstream

This means **C++ test cases work out of the box on any Mac or Linux machine** with `g++` installed — no Docker required.

### Self-Hosted Judge0

For full language support and sandboxed execution, you can run Judge0 locally:

```bash
# 1. Open Docker Desktop
# 2. Run:
docker-compose -f docker-compose.judge0.yml up -d
# Judge0 will be available at http://localhost:2358
# Note: The Judge0 image is ~3.3GB and may take several minutes to pull
```

The `.env` file is already configured to point to `localhost:2358`.

---

## 🕵️ Integrity System: Plagiarism & AI Detection

**Where**: `backend/core/services/integrity_service.py` + `submission_index.py`

### Plagiarism Detection Pipeline

```
Student Code → Normalize (strip whitespace, comments) → Fingerprint (MD5 hash)
                                                              │
                                           ┌──────────────────┤
                                           ▼                  ▼
                                     Exact Match?      Fuzzy Similarity
                                     (hash lookup)    (SequenceMatcher)
                                           │                  │
                                           ▼                  ▼
                                     flag_score = 1.0   flag_score = similarity
                                     "Exact code match   "Suspicious similarity
                                      with student_X"     (87% match)"
```

### AI-Generated Content Detection

Uses **GPT-2 perplexity** as a signal:

| Perplexity Score | Interpretation | Flag Action |
|---|---|---|
| > 50 | Likely human-written | No flag |
| 25 - 40 | Moderate AI likelihood | `flag_score += 0.7` |
| < 25 | High AI likelihood | `flag_score += 1.0` |

**How perplexity works**: Language models predict the next token in a sequence. Human writing is more surprising (higher perplexity) because humans make creative, unpredictable choices. AI-generated text is less surprising (lower perplexity) because it follows statistical patterns.

> **Important**: These flags are **advisory only**. They route submissions to the teacher's review queue but never automatically zero a score.

---

## 👨‍🏫 Review Queue: Human-in-the-Loop

**Where**: `backend/core/services/review_queue.py` + `frontend/app/review/page.tsx`

### Philosophy

The system is designed with a **"flag, don't punish"** philosophy. Automated systems can make mistakes, so:

1. Suspicious submissions are **flagged** and queued for review
2. The teacher sees **why** it was flagged (plagiarism evidence, AI detection result, uncertain verdict)
3. The teacher can **override the score** with their own assessment
4. The original AI score is preserved for tracking system accuracy over time

### Queue Persistence

The review queue has a **dual storage strategy**:
- **Primary**: PostgreSQL database (persistent across restarts)
- **Fallback**: In-memory Python dictionary (works when DB is unavailable)

This ensures the review queue **always works**, even without a database.

### Frontend Fallback

The review page also has a fallback: if the API returns no pending reviews, it builds review items from the **session-stored evaluation results** (saved in browser sessionStorage). This means teachers can always access their reviews even if the backend DB is empty.

---

## 📈 Student Profile Tracking

**Where**: `backend/core/services/student_tracker.py` + `frontend/app/student/[id]/page.tsx`

### What's Tracked Per Student

| Metric | Description |
|---|---|
| **Score History** | Every score recorded with timestamp and topic tag |
| **Improvement Delta** | Change vs. average of last 5 submissions on same topic |
| **Trend** | `improving` (+5 pts), `declining` (-5 pts), or `stable` |
| **Percentile** | Where the student ranks in the class (0-100) |
| **Skill Breakdown** | Average score per topic tag (e.g., "sorting": 82, "graphs": 65) |
| **Cumulative GPA** | Letter grade + GPA on 4.0 scale |

### Grade Scale

| Score | Grade | GPA |
|---|---|---|
| 93-100 | A | 4.0 |
| 90-92 | A- | 3.7 |
| 87-89 | B+ | 3.3 |
| 83-86 | B | 3.0 |
| 80-82 | B- | 2.7 |
| 77-79 | C+ | 2.3 |
| 73-76 | C | 2.0 |
| 70-72 | C- | 1.7 |
| 60-69 | D-D+ | 0.7-1.3 |
| < 60 | F | 0.0 |

---

## 🖥 Frontend: The Teacher Dashboard

Built with **Next.js 14**, **TailwindCSS**, and the **"Obsidian Scholar"** design system — a dark-mode, data-dense interface.

### Pages

| Page | Path | Purpose |
|---|---|---|
| **Upload** | `/upload` | Upload files, set problem statement, paste test cases |
| **Results** | `/results` | Dashboard with all evaluation results, scores, feedback |
| **Review Queue** | `/review` | Review flagged submissions, override scores |
| **Student Profile** | `/student/[id]` | Individual student dashboard with history and trends |

### Design System

The UI uses a custom design token system:
- **Background**: Deep obsidian (#0A0A12)
- **Surface layers**: Four tonal levels for depth
- **Primary accent**: Violet (#A78BFA) for interactive elements
- **Semantic colors**: Emerald (success), Coral (warning), Amber (caution)
- **Typography**: System fonts with monospace for scores

---

## 📡 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/evaluate` | Upload and evaluate submissions |
| `GET` | `/api/evaluations/history` | Retrieve all past evaluation results |
| `DELETE` | `/api/evaluations/cleanup?below_score=10` | Remove old broken evaluation results |
| `GET` | `/api/reviews` | Get pending review queue items |
| `POST` | `/api/reviews/{id}/override` | Teacher overrides a score |
| `GET` | `/api/students/{id}/profile` | Get student's complete profile |
| `GET` | `/health` | Health check with DB and LLM status |

### POST /api/evaluate — Request Format

```
Content-Type: multipart/form-data

Fields:
  files[]            - Student submission files (required)
  assignment_type    - "code" | "content" | "mixed" (required)
  problem_statement  - The question asked (recommended)
  test_cases         - JSON array (optional)
  rubric_content     - Custom rubric JSON (optional)
  topic              - Topic tag for tracking (optional)
```

### Response Format

```json
{
  "status": "success",
  "message": "Evaluated 3 submissions successfully",
  "results": [
    {
      "submission_id": "student_alice_Result",
      "final_score": 87.6,
      "max_score": 100,
      "percentage": 87.6,
      "feedback": ["## AI Evaluator", "**Summary**: ..."],
      "assignment_type": "code",
      "file": "student_alice.py",
      "flag_score": 0.7,
      "flag_reasons": ["High AI likelihood: low perplexity score (3.0)."],
      "percentile": 100,
      "improvement_delta": 4.0,
      "trend": "improving"
    }
  ]
}
```

---

## 📁 Project Structure

```
Evaluator/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Application configuration
│   │   ├── routes/
│   │   │   ├── evaluate.py            # POST /api/evaluate (main endpoint)
│   │   │   ├── review_routes.py       # GET/POST /api/reviews
│   │   │   └── student_routes.py      # GET /api/students/:id/profile
│   │   ├── schemas/
│   │   │   └── request.py             # Pydantic models (TestCase, RubricConfig, etc.)
│   │   └── services/
│   │       └── evaluator.py           # Service layer (request → orchestrator adapter)
│   │
│   └── core/
│       ├── agents/
│       │   ├── base_agent.py          # Abstract base class for all agents
│       │   ├── code_agent.py          # Code evaluation (AST + approach + readability)
│       │   ├── content_agent.py       # Content evaluation (coverage + alignment + flow)
│       │   └── aggregator_agent.py    # Combines agent outputs into final score
│       │
│       ├── controller/
│       │   └── orchestrator.py        # Main pipeline coordinator
│       │
│       ├── services/
│       │   ├── database.py            # PostgreSQL connection + schema management
│       │   ├── treesitter_parser.py   # AST parsing (Python, C++)
│       │   ├── judge0_service.py      # Test execution (Judge0 API + local fallback)
│       │   ├── embedding_service.py   # Semantic embeddings (all-MiniLM-L6-v2)
│       │   ├── integrity_service.py   # Plagiarism + AI detection
│       │   ├── review_queue.py        # Manual review queue (DB + in-memory)
│       │   ├── student_tracker.py     # Score history + percentiles + trends
│       │   ├── evaluation_store.py    # Persistent result storage
│       │   └── submission_index.py    # Code fingerprinting for plagiarism
│       │
│       └── utils/
│           ├── file_parser.py         # File reading + student name extraction
│           ├── rubric.py              # Rubric management + validation
│           └── csv_export.py          # CSV report generation
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx                 # Root layout with Obsidian theme
│   │   ├── page.tsx                   # Landing page
│   │   ├── upload/page.tsx            # File upload interface
│   │   ├── results/page.tsx           # Results dashboard
│   │   ├── review/page.tsx            # Review queue page
│   │   └── student/[id]/page.tsx      # Student profile page
│   ├── components/
│   │   ├── AppNavbar.tsx              # Navigation bar
│   │   └── FileUpload.tsx             # Drag-and-drop file upload component
│   └── lib/
│       └── results-store.ts           # Client-side results persistence
│
├── utils/
│   ├── llm_service.py                 # Multi-tier LLM (Gemini → Ollama → rule-based)
│   └── local_slm_service.py           # Offline Phi-3 SLM (Ollama + llama-cpp-python)
│
├── test_submissions/                   # Sample test submissions
│   ├── mixed_single/                  # Single-file mixed eval samples
│   ├── mixed_test/                    # Two-file mixed eval samples
│   └── mixed_txt_test/                # Text-based mixed eval samples
│
├── docker-compose.judge0.yml          # Self-hosted Judge0 setup
├── requirements.txt                   # Python dependencies
├── run_backend.py                     # Backend startup script
└── .env                               # Environment variables (gitignored)
```

---

## 🚀 How to Run

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL 14+** (optional — system works without it)
- **Docker Desktop** (optional — for self-hosted Judge0)

### 1. Clone the Repository

```bash
git clone https://github.com/Izhaar-ahmed/Evaluator.git
cd Evaluator
```

### 2. Set Up the Backend

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate     # macOS/Linux
# .venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# --- LLM ---
LLM_ENABLED=true
GEMINI_API_KEY=your_gemini_api_key_here     # Get from https://aistudio.google.com/apikey
GEMINI_MODEL=gemini-2.0-flash

# --- Database (optional) ---
DB_NAME=evaluator
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres

# --- Judge0 (optional — for code test execution) ---
JUDGE0_API_URL=http://localhost:2358
JUDGE0_API_KEY=
```

### 4. Set Up PostgreSQL (Optional)

```bash
# Create the database (required for persistent results and student tracking)
createdb evaluator

# The schema is auto-created on first startup — no manual migration needed
```

> **Without PostgreSQL**: The system still works! Results are stored in session, and the review queue uses an in-memory fallback. You just lose persistence across server restarts.

### 5. Start the Backend

```bash
python run_backend.py
# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 6. (Optional) Set Up Ollama for Offline AI

```bash
# Install Ollama
brew install ollama

# Start Ollama server with Metal GPU acceleration
OLLAMA_FLASH_ATTENTION=1 ollama serve

# Pull Phi-3 Mini model (2.2GB, one-time download)
ollama pull phi3:mini

# Or auto-start at login:
brew services start ollama
```

> **This is optional**: The system works fine with just the Gemini API. Ollama is only needed if you want offline capability or hit rate limits.

### 7. Set Up and Start the Frontend

```bash
cd frontend
npm install
npx next dev
# Frontend starts at http://localhost:3000
```

### 8. (Optional) Start Self-Hosted Judge0

```bash
# Open Docker Desktop first, then:
docker-compose -f docker-compose.judge0.yml up -d
# Judge0 API available at http://localhost:2358
```

### 9. Use the Application

1. Open `http://localhost:3000` in your browser
2. Click **Upload** in the navigation
3. Select student files, enter the problem statement
4. (Optional) Paste test cases JSON
5. Click **Evaluate**
6. View results on the **Results** page
7. Check flagged submissions in the **Review Queue**

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `LLM_ENABLED` | No | `false` | Enable LLM for relevance checks and feedback |
| `GEMINI_API_KEY` | If LLM enabled | — | Google Gemini API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Gemini model to use |
| `USE_LOCAL_SLM` | No | `true` | Enable local Phi-3 fallback when Gemini fails |
| `LOCAL_MODEL_PATH` | No | `(auto-detected)` | Path to Phi-3 GGUF model file |
| `OLLAMA_URL` | No | `http://127.0.0.1:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `phi3:mini` | Ollama model name |
| `DB_NAME` | No | `evaluator` | PostgreSQL database name |
| `DB_HOST` | No | `localhost` | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | `postgres` | PostgreSQL username |
| `DB_PASSWORD` | No | `postgres` | PostgreSQL password |
| `JUDGE0_API_URL` | No | `http://localhost:2358` | Judge0 API URL |
| `JUDGE0_API_KEY` | No | — | Judge0 API key (for RapidAPI hosted) |

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | REST API framework with automatic OpenAPI docs |
| **Pydantic v2** | Request/response validation and serialization |
| **Uvicorn** | ASGI server for running FastAPI |
| **Tree-sitter** | Production-grade incremental parser for AST analysis |
| **Google Gemini** | LLM for relevance checking and semantic feedback (cloud) |
| **Ollama** | Optimized local LLM runtime with Metal GPU acceleration |
| **Phi-3 Mini** | Microsoft's 3.8B parameter SLM for offline AI feedback |
| **llama-cpp-python** | Direct GGUF model loading for offline inference (fallback) |
| **Sentence-Transformers** | Neural text embeddings for semantic similarity |
| **GPT-2** | Perplexity-based AI-generation detection |
| **PostgreSQL** | Persistent storage for results, reviews, and student data |
| **psycopg2** | PostgreSQL adapter for Python |
| **NumPy** | Numerical operations for embeddings and percentiles |
| **Judge0 CE** | Sandboxed code execution engine |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 14** | React framework with file-based routing |
| **TypeScript** | Type-safe frontend development |
| **TailwindCSS 3** | Utility-first CSS framework |
| **React 18** | UI component library |

---

## ❓ Common Questions

### Q: How does the system differentiate between two similar code submissions?

**A:** Through the **complexity_score** computed by tree-sitter. Even if two submissions implement similar algorithms, they'll have different:
- Nesting depths (how deeply nested are the loops/conditions)
- Unique identifier counts (how many distinct variable names)
- Function names (e.g., `threeSum` vs `threeSumClosest`)
- Control flow count (number of loops, conditions, try-except blocks)

These metrics produce different complexity scores, which lead to different final scores.

### Q: What happens when the Gemini API is rate-limited?

**A:** The system **gracefully degrades** with a three-tier fallback:
1. First tries alternate Gemini models (gemini-2.0-flash, gemini-flash-latest, etc.)
2. When all Gemini models fail, automatically falls back to **Ollama Phi-3** running locally on your M1/M2/M3 GPU (~1.7s relevance, ~20s feedback)
3. If Ollama isn't running, falls back to **llama-cpp-python** loading the GGUF model directly (~7s relevance, ~72s feedback)
4. If no local model is available, uses **rule-based analysis** (AST, keywords, structure)
5. `check_relevance()` returns `UNCERTAIN` on failure (not `IRRELEVANT` — students are never penalized)

You can run evaluations entirely offline with zero API cost.

### Q: What is single-file mixed evaluation?

**A:** Traditionally, mixed assignments require students to submit two files — one with code and one with explanation. With single-file mixed evaluation, students can submit **one file** containing both code and explanation. The system automatically splits it:
- **Python files**: Docstrings and comments become "content"; the full file becomes "code"
- **Text/Markdown files**: Fenced code blocks (` ``` `) become "code"; everything else becomes "content"
- **PDF files**: Same logic as text files, applied to extracted text

Both agents run their respective evaluations seamlessly, producing a combined score.

### Q: How do I set up offline AI evaluation?

**A:** Three steps:
```bash
brew install ollama          # Install Ollama
ollama serve                 # Start the server (keep running)
ollama pull phi3:mini        # Download Phi-3 Mini (2.2GB, once)
```
The system auto-detects Ollama and uses it whenever Gemini is unavailable. Set `USE_LOCAL_SLM=true` in `.env` (enabled by default).

### Q: Do I need Judge0 for the system to work?

**A:** No. Judge0 is **optional**. Without it:
- **Python** test cases still run locally via subprocess
- **C++** test cases run locally via `g++ -std=c++17` compilation and execution
- LeetCode-style `class Solution` submissions are automatically wrapped with headers and a `main()` function
- Only Java/JavaScript test cases would be skipped (static analysis only)
- The system still provides accurate scores based on AST analysis, LLM feedback, and structural metrics

### Q: What file types are supported?

**A:** 
- **Code**: `.py` (Python), `.cpp` (C++) for full AST analysis; any text file for basic analysis
- **Content**: `.txt`, `.md`, `.pdf`, or any text file
- **Mixed (single-file)**: `.py`, `.cpp`, `.txt`, `.md`, `.pdf` — the system auto-splits code and explanation from a single file

### Q: Can I use this without PostgreSQL?

**A:** Yes! Without PostgreSQL:
- Evaluation results are stored in browser sessionStorage
- The review queue uses an in-memory Python dictionary
- Student tracking and percentiles won't persist across restarts
- All scoring and feedback features work normally

### Q: How accurate is the AI-generation detection?

**A:** The GPT-2 perplexity method is a **heuristic signal**, not a definitive detector. It works as a supporting flag that routes submissions for human review. The teacher makes the final decision. Low perplexity doesn't guarantee AI generation — some well-structured human writing can also have low perplexity.

### Q: What is the Rubric and do I need to provide one?

**A:** A rubric defines evaluation weights and criteria. If you don't provide one, the **default rubric** is used:
- Code: approach (40%), readability (20%), structure (20%), effort (20%)
- Content: coverage (60%), alignment (25%), flow (8%), completeness (7%)

You can customize weights by uploading a custom rubric JSON.

---

## 👥 Contributors

| Name | Roll No. | Role | Key Contributions |
|------|----------|------|-------------------|
| **B Harsha Vardhan** | 23BDS015 | Frontend Development | Designed and built the entire Next.js 14 teacher dashboard — landing page, upload interface with drag-and-drop, results dashboard with expandable score cards, review queue with override functionality, and student profile pages with trend visualization. Implemented the Obsidian Dark design system with TailwindCSS. |
| **L Akash** | 23BDS031 | Integration & Testing | Integrated the FastAPI backend with the Next.js frontend via REST API. Configured CORS middleware, implemented multipart file upload handling, and built the `FormData` → backend pipeline. Conducted extensive end-to-end testing, identified and resolved critical bugs including test case format parsing, C++ execution failures, and error propagation across the API boundary. |
| **S Sasi Rekha** | 23BDS049 | Content & Mixed Evaluation | Developed the Content Evaluation Agent with five scoring dimensions (factual accuracy, coverage, alignment, flow, completeness). Implemented the semantic embedding pipeline using all-MiniLM-L6-v2, built the dual keyword/semantic concept hit-rate scoring system, and developed the mixed-mode agent that combines code and content evaluation for hybrid assignments. |
| **SK Izhaar Ahmed** | 23BDS053 | Code Evaluation & Integrity | Built the Code Evaluation Agent with four scoring dimensions (approach, readability, structure, effort). Integrated Tree-sitter for AST analysis, developed the Judge0 execution service with C++ auto-wrapping and local g++ fallback, implemented the integrity service with MD5 plagiarism fingerprinting, fuzzy SequenceMatcher similarity, and GPT-2 perplexity-based AI content detection. |

---

## 📚 References

1. Ala-Mutka, K. M. (2005). A survey of automated assessment approaches for programming assignments. *Computer Science Education*, 15(2), 83–102.
2. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. *EMNLP 2019*.
3. Tree-sitter. (2024). Tree-sitter documentation. https://tree-sitter.github.io/tree-sitter/
4. Judge0. (2024). Judge0 CE — open-source online code execution system. https://judge0.com/
5. Radford, A., et al. (2019). Language models are unsupervised multitask learners. *OpenAI Technical Report*.
6. Google DeepMind. (2024). Gemini: A family of highly capable multimodal models. *arXiv preprint*.
7. Wang, W., et al. (2020). MiniLM: Deep self-attention distillation for task-agnostic compression. *NeurIPS 2020*.

---

<p align="center">
  <strong>Built with ❤️ for educators who want fair, intelligent, and transparent assessment.</strong>
</p>
