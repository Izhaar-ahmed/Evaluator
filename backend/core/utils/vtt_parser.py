"""
VTT Transcript Parser & Keyword Extractor.

Parses WebVTT lecture transcripts, filters noise, and extracts
key educational concepts using pure TF-IDF — zero LLM dependency.

Usage:
    from backend.core.utils.vtt_parser import parse_vtt, extract_concepts

    clean_text = parse_vtt(vtt_string)
    concepts = extract_concepts(clean_text)
"""

import re
import math
from collections import Counter
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Stopwords + noise patterns
# ---------------------------------------------------------------------------

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "from", "by", "as", "is", "it", "its", "was", "are",
    "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "should", "could", "may", "might", "must",
    "can", "this", "that", "these", "those", "your", "their", "our",
    "his", "her", "my", "you", "we", "they", "he", "she", "what",
    "which", "where", "when", "who", "whom", "whose", "how", "why",
    "there", "here", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "than", "too", "very", "just",
    "about", "above", "after", "again", "also", "any", "because",
    "before", "below", "between", "come", "does", "doing", "down",
    "during", "even", "first", "get", "give", "go", "going", "got",
    "him", "into", "know", "like", "look", "make", "many", "much",
    "need", "new", "not", "now", "off", "old", "only", "out", "over",
    "own", "part", "same", "say", "see", "take", "tell", "thing",
    "think", "time", "two", "under", "use", "used", "using", "want",
    "way", "well", "will", "work", "yeah", "yes", "okay", "right",
    "let", "something", "sir", "maam", "thank", "thanks", "please",
    "sure", "actually", "basically", "mean", "one", "said", "then",
    "so", "if", "no", "oh", "um", "uh", "like", "kind", "sort",
    "still", "try", "try", "already", "another", "back", "bit",
    "called", "done", "else", "enough", "fine", "good", "great",
    "help", "keep", "last", "lot", "made", "next", "put", "really",
    "second", "show", "small", "start", "talk", "through", "went",
    "whether", "without", "yet", "maybe", "also", "able", "given",
}

# Lines matching these patterns are filtered out as noise
NOISE_PATTERNS = [
    re.compile(r"^(good\s+)?(morning|afternoon|evening|night)", re.I),
    re.compile(r"^(hi|hello|hey|bye|goodbye)\b", re.I),
    re.compile(r"^thank\s+you", re.I),
    re.compile(r"^(yes|no|okay|ok|yep|yea|yeah|got\s*it|sure|fine)\s*[.,!?]?\s*$", re.I),
    re.compile(r"^(can you|are you|am i|is it)\s+(hear|see|audible|visible)", re.I),
    re.compile(r"(join|submit|deadline|upload|lms|portal|timetable|dashboard)", re.I),
    re.compile(r"(unmute|mute|camera|mic|screen\s*share)", re.I),
    re.compile(r"^(have a nice|enjoy|see you)", re.I),
    re.compile(r"^(pardon|sorry|excuse me)", re.I),
    re.compile(r"^\w+:\s*(yes|no|okay|ok|sure|fine|thanks)\s*[.!?]?\s*$", re.I),
]

# Technical bigrams/trigrams to preserve as single concepts
TECHNICAL_PHRASES = [
    "supervised learning", "unsupervised learning", "reinforcement learning",
    "machine learning", "deep learning", "neural network", "neural networks",
    "logistic regression", "linear regression", "decision tree", "random forest",
    "support vector", "gradient descent", "gradient boosting",
    "confusion matrix", "classification report", "cross validation",
    "train test split", "training data", "test data", "training set", "test set",
    "feature engineering", "feature selection", "feature extraction",
    "dimensionality reduction", "principal component", "data frame",
    "data set", "data cleaning", "data preprocessing", "data visualization",
    "standard scalar", "standard scaler", "standard deviation",
    "false positive", "false negative", "true positive", "true negative",
    "precision recall", "f1 score", "mean squared", "root mean",
    "scikit learn", "colab account", "google colab",
    "iris dataset", "iris data", "labeled data", "label data",
    "scatter plot", "heat map", "pair plot",
    "sepal length", "sepal width", "petal length", "petal width",
    "classification model", "regression model", "prediction model",
    "model evaluation", "model training", "model building",
    "accuracy score", "model accuracy",
]


# ---------------------------------------------------------------------------
# VTT Parsing
# ---------------------------------------------------------------------------

def parse_vtt(vtt_text: str) -> str:
    """
    Parse a WebVTT transcript into clean lecture text.

    Strips timestamps, cue numbers, speaker labels, and filters
    noise lines (greetings, admin chat, short affirmations).

    Args:
        vtt_text: Raw VTT file content.

    Returns:
        Cleaned lecture text with noise removed.
    """
    lines = vtt_text.strip().split("\n")
    clean_lines = []

    # Skip the WEBVTT header
    start = 0
    for i, line in enumerate(lines):
        if line.strip().upper().startswith("WEBVTT"):
            start = i + 1
            break

    # Parse cue blocks
    i = start
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and cue numbers
        if not line or re.match(r"^\d+$", line):
            i += 1
            continue

        # Skip timestamp lines
        if "-->" in line:
            i += 1
            continue

        # Extract speaker and text
        speaker_match = re.match(r"^([^:]+):\s*(.*)$", line)
        if speaker_match:
            text = speaker_match.group(2).strip()
        else:
            text = line.strip()

        # Filter noise
        if text and len(text.split()) >= 3 and not _is_noise(text):
            clean_lines.append(text)

        i += 1

    return " ".join(clean_lines)


def _is_noise(text: str) -> bool:
    """Check if a line is noise (greetings, admin talk, etc.)."""
    for pattern in NOISE_PATTERNS:
        if pattern.search(text):
            return True
    return False


# ---------------------------------------------------------------------------
# LLM-Powered Concept Refinement (Groq)
# ---------------------------------------------------------------------------

def llm_refine_concepts(
    candidates: List[str],
    transcript_snippet: str,
    fallback_count: int = 10,
) -> List[str]:
    """
    Use Groq LLM to filter TF-IDF candidates to only genuinely
    teachable lecture concepts. Returns a dynamic-length list.

    Args:
        candidates: TF-IDF candidate terms (typically 20).
        transcript_snippet: First ~1500 chars of transcript for context.
        fallback_count: Number of candidates to return if LLM fails.

    Returns:
        Filtered list of real concepts (typically 5-15).
    """
    import os
    import json

    if not os.getenv("GROQ_API_KEY") or not os.getenv("LLM_ENABLED", "false").lower() == "true":
        print("  ⚠ LLM not available for concept refinement — using TF-IDF top candidates")
        return candidates[:fallback_count]

    if not candidates:
        return []

    prompt = f"""You are an academic concept extractor analyzing a lecture transcript.

Given these candidate terms extracted from a lecture, return ONLY the ones that are genuine, 
teachable technical/academic concepts that a student should demonstrate understanding of.

REMOVE:
- Generic words that appear in any lecture (e.g., "data set", "classified", "precision", "value") 
  UNLESS they are a CORE TOPIC of THIS specific lecture
- Vague terms that aren't real concepts (e.g., "multiple", "threshold", "conventional")
- Near-duplicates — keep only the more specific one

KEEP:
- Actual algorithms, techniques, methods (e.g., "supervised learning", "random forest")
- Domain-specific terminology (e.g., "feature extraction", "cross validation")
- Key principles or frameworks being taught

Return ONLY a valid JSON array of strings. No explanation, no markdown.
Return as many or as few as are genuinely important (typically 5-12 for a 30-60 minute lecture).

Candidate terms: {json.dumps(candidates)}

Transcript snippet (for context):
{transcript_snippet[:1500]}"""

    try:
        import asyncio
        from utils.llm_service import _call_groq

        loop = asyncio.new_event_loop()
        messages = [{"role": "user", "content": prompt}]
        raw_response = loop.run_until_complete(_call_groq(messages, max_tokens=300))
        loop.close()

        # Parse JSON array from response
        # Handle potential markdown wrapping
        cleaned = raw_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        refined = json.loads(cleaned)

        if isinstance(refined, list) and len(refined) >= 3:
            # Only keep terms that were in the original candidates (prevent hallucination)
            candidates_lower = {c.lower() for c in candidates}
            validated = [c for c in refined if c.lower() in candidates_lower]

            if len(validated) >= 3:
                print(f"  ✓ LLM refined {len(candidates)} candidates → {len(validated)} real concepts: {validated}")
                return validated
            else:
                print(f"  ⚠ LLM returned too few valid concepts ({len(validated)}), using TF-IDF top {fallback_count}")
                return candidates[:fallback_count]
        else:
            print(f"  ⚠ LLM returned invalid format, using TF-IDF top {fallback_count}")
            return candidates[:fallback_count]

    except Exception as e:
        print(f"  ⚠ LLM concept refinement failed ({e}), using TF-IDF top {fallback_count}")
        return candidates[:fallback_count]


# ---------------------------------------------------------------------------
# TF-IDF Keyword Extraction (zero LLM)
# ---------------------------------------------------------------------------

def extract_concepts(clean_text: str, top_n: int = 20) -> List[str]:
    """
    Extract key educational concepts from lecture text using TF-IDF.

    Uses term frequency with inverse document frequency approximation
    to find the most important technical terms in the lecture.
    No LLM or external API needed.

    Args:
        clean_text: Cleaned lecture transcript text.
        top_n: Number of top concepts to return.

    Returns:
        List of key concept strings, ordered by importance.
    """
    if not clean_text or len(clean_text.strip()) < 50:
        return []

    text_lower = clean_text.lower()

    # Step 1: Extract technical phrases (bigrams/trigrams) first
    found_phrases = []
    for phrase in TECHNICAL_PHRASES:
        count = text_lower.count(phrase)
        if count > 0:
            found_phrases.append((phrase, count))

    # Step 2: Extract single-word terms
    words = re.findall(r"\b[a-z][a-z0-9_]{2,}\b", text_lower)
    word_counts = Counter(words)

    # Remove stopwords
    for sw in STOPWORDS:
        word_counts.pop(sw, None)

    # Remove very common lecture filler words + generic English
    fillers = {
        # Lecture interaction / classroom
        "class", "today", "going", "will", "come", "look", "lets",
        "explain", "understand", "question", "answer", "discuss",
        "slide", "slides", "page", "click", "share", "screen",
        "minutes", "wait", "tell", "told", "says", "check",
        "particular", "available", "different", "important",
        "basically", "mentioned", "certain", "everything",
        "student", "students", "everybody", "everyone", "anybody",
        "professor", "teacher", "learned",
        # Common lecture filler / vague words
        "whatever", "something", "anything", "nothing", "things",
        "thing", "stuff", "like", "just", "also", "actually",
        "really", "always", "never", "often", "sometimes",
        "many", "much", "some", "every", "each", "other",
        "such", "more", "most", "less", "very", "quite",
        "already", "still", "even", "right", "left", "next",
        "first", "second", "third", "last", "another", "same",
        "new", "old", "big", "small", "high", "low",
        "good", "bad", "best", "worst", "better", "worse",
        "able", "way", "ways", "part", "parts", "case", "cases",
        "point", "points", "example", "examples", "kind", "type",
        "types", "form", "forms", "level", "levels", "area", "areas",
        "place", "side", "fact", "idea", "ideas", "order",
        "step", "steps", "process", "system", "group", "set",
        # Generic verbs / actions (not concepts)
        "uses", "shows", "gives", "takes", "means", "gets",
        "called", "require", "requires", "required", "needs",
        "build", "built", "building", "creates", "created",
        "define", "defined", "defines", "execute", "executed",
        "result", "results", "output", "outputs", "input", "inputs",
        "applied", "apply", "shown", "given", "taken",
        "make", "made", "making", "start", "started", "keep",
        "try", "trying", "tried", "want", "wanted", "need",
        "know", "known", "knowing", "think", "thought",
        "see", "seen", "seeing", "say", "said", "saying",
        "work", "works", "working", "worked", "run", "running",
        "use", "used", "using", "write", "writing", "written",
        "read", "reading", "find", "finding", "found",
        "put", "putting", "move", "moving", "change", "changed",
        "help", "helping", "helped", "provide", "provided",
        "consider", "considered", "based", "play", "playing",
        # Math / number noise
        "divided", "plus", "minus", "times", "equal", "equals",
        "ratio", "value", "values", "number", "numbers",
        "zero", "hundred", "percent", "percentage",
        "division", "multiple", "single", "double", "total",
        "half", "quarter", "above", "below",
        # Generic academic / non-specific terms
        "method", "methods", "approach", "approaches",
        "problem", "problems", "solution", "solutions",
        "technique", "techniques", "concept", "concepts",
        "practice", "practices", "principle", "principles",
        "general", "specific", "simple", "complex",
        "common", "basic", "standard", "main", "major",
        "real", "true", "false", "possible", "actual",
        "term", "terms", "word", "words", "line", "lines",
        "table", "column", "row", "rows", "field", "fields",
        "section", "chapter", "topic", "topics",
        # Transition / connector words
        "however", "therefore", "hence", "thus", "also",
        "moreover", "furthermore", "although", "though",
        "because", "since", "while", "whereas", "whether",
        "either", "neither", "both", "between", "among",
        "through", "within", "without", "across", "along",
        "around", "before", "after", "during", "until",
        # Pronouns / determiners that slip through
        "this", "that", "these", "those", "which",
        "what", "where", "when", "how", "why", "who",
        "here", "there", "then", "now",
        # Threshold / generic measurement words
        "threshold", "range", "limit", "limits", "size",
        "count", "length", "width", "height", "depth",
        "rate", "score", "scores", "measure", "measures",
        "amount", "quantity", "condition", "conditions",
        "conventional",
    }
    for f in fillers:
        word_counts.pop(f, None)

    # Step 3: Compute TF-IDF-like scores
    total_words = len(words) or 1
    scored_terms: List[Tuple[str, float]] = []

    # Score phrases (boosted 3x because multi-word = more specific)
    for phrase, count in found_phrases:
        tf = count / total_words
        boost = 3.0  # Phrases are more meaningful than single words
        scored_terms.append((phrase, tf * boost * 1000))

    # Score single words
    for word, count in word_counts.items():
        if count < 2:
            continue  # Skip hapax legomena (mentioned only once = probably noise)
        tf = count / total_words

        # IDF approximation: common English words get lower scores
        # Technical terms (longer, less common) get higher scores
        idf = math.log(1 + len(word))  # Longer words tend to be more technical

        # Boost words that look technical
        tech_boost = 1.0
        if any(c.isdigit() for c in word):
            tech_boost = 1.5  # Contains numbers (e.g., f1, k2)
        if word.endswith(("tion", "ment", "ity", "ics", "sis", "ing")):
            tech_boost = 1.2  # Technical suffixes
        if len(word) >= 8:
            tech_boost *= 1.3  # Long words are usually more specific

        scored_terms.append((word, tf * idf * tech_boost * 1000))

    # Step 4: Deduplicate (remove single words that are part of found phrases)
    phrase_words = set()
    for phrase, _ in found_phrases:
        phrase_words.update(phrase.split())

    scored_terms = [
        (term, score) for term, score in scored_terms
        if " " in term or term not in phrase_words
    ]

    # Step 5: Sort by score and deduplicate with STEM awareness
    scored_terms.sort(key=lambda x: x[1], reverse=True)

    def _get_stem(word: str) -> str:
        """Simple suffix-stripping stemmer (no external deps)."""
        w = word.lower()
        # Remove common suffixes in order of length
        for suffix in [
            "ization", "isation", "ational", "ioning",
            "ation", "ment", "ness", "ical", "ious", "ible",
            "able", "ally", "ting", "ling", "sion", "tion",
            "ity", "ive", "ful", "ing", "ous", "ial",
            "ies", "ied", "ely", "ion",
            "ed", "ly", "er", "al", "es",
            "s",
        ]:
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                return w[:-len(suffix)]
        return w

    def _get_stems(term: str) -> set:
        """Get stems for all words in a term."""
        return {_get_stem(w) for w in term.lower().split()}

    seen_stems = set()
    seen_terms = set()  # for substring checking
    concepts = []

    for term, score in scored_terms:
        normalized = term.strip().lower()
        if len(normalized) <= 2:
            continue

        # Get stems for this term
        stems = _get_stems(normalized)

        # Skip if any stem was already covered by a previous concept
        if stems & seen_stems:
            continue

        # Skip single words that are substrings of already-selected phrases
        if " " not in normalized:
            is_substring = False
            for existing in seen_terms:
                if normalized in existing or existing in normalized:
                    is_substring = True
                    break
            if is_substring:
                continue

        seen_stems.update(stems)
        seen_terms.add(normalized)
        concepts.append(term)
        if len(concepts) >= top_n:
            break

    return concepts


def extract_concept_dict(clean_text: str, top_n: int = 20) -> Dict[str, float]:
    """
    Extract concepts with their importance scores.

    Returns:
        Dict mapping concept -> importance score (0-1 normalized).
    """
    if not clean_text:
        return {}

    text_lower = clean_text.lower()
    total_words = len(re.findall(r"\b\w+\b", text_lower)) or 1

    concepts = extract_concepts(clean_text, top_n)
    if not concepts:
        return {}

    result = {}
    for i, concept in enumerate(concepts):
        # Score based on rank and frequency
        freq = text_lower.count(concept.lower())
        tf = freq / total_words
        rank_score = 1.0 - (i / len(concepts))  # Higher rank = higher score
        result[concept] = round(min(tf * 500 + rank_score * 0.5, 1.0), 3)

    return result


# ---------------------------------------------------------------------------
# Batch Semantic Scoring — FAST + FAIR
# ---------------------------------------------------------------------------

def batch_score_summaries(
    summaries: Dict[str, str],
    concepts: List[str],
    clean_transcript: str,
) -> Dict[str, Dict]:
    """
    Score ALL student summaries in one batch using cached embeddings.

    This is 10-20x faster than scoring one-by-one because:
    - Concepts are encoded ONCE (not 120 times)
    - Summaries are batch-encoded in one GPU/CPU call
    - No redundant transcript encoding

    Args:
        summaries: Dict of student_id -> cleaned summary text.
        concepts: List of key concepts from transcript.
        clean_transcript: Cleaned transcript (for keyword fallback only).

    Returns:
        Dict of student_id -> scoring result dict.
    """
    if not summaries:
        return {}

    # Try batch semantic scoring
    use_semantic = False
    concept_embs = None
    summary_embs = None

    try:
        from backend.core.services.embedding_service import is_available, _ensure_model, _model
        if is_available():
            _ensure_model()
            model = _model

            # Encode concepts ONCE
            concept_embs = model.encode(concepts, normalize_embeddings=True, batch_size=64)

            # Encode ALL summaries in ONE batch call
            student_ids = list(summaries.keys())
            summary_texts = [summaries[sid] for sid in student_ids]

            # Split each summary into sentences for concept matching
            all_sentences = []
            sentence_map = {}  # maps (student_idx, sent_idx) for reconstruction
            for idx, text in enumerate(summary_texts):
                sents = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip() and len(s.strip()) > 5]
                if not sents:
                    sents = [text]  # Fallback: use whole text as one sentence
                sentence_map[idx] = (len(all_sentences), len(all_sentences) + len(sents))
                all_sentences.extend(sents)

            # One big batch encode for ALL sentences from ALL students
            if all_sentences:
                all_sent_embs = model.encode(all_sentences, normalize_embeddings=True, batch_size=128)
                use_semantic = True
                print(f"  ✓ Batch encoded {len(all_sentences)} sentences from {len(summaries)} students")
            else:
                use_semantic = False

    except Exception as e:
        print(f"  ⚠ Semantic batch encoding failed ({e}), using keyword scoring")
        use_semantic = False

    # Score each student
    import numpy as np
    results = {}

    for idx, (student_id, summary) in enumerate(summaries.items()):
        summary_lower = summary.lower()
        summary_words = re.findall(r"\b\w+\b", summary_lower)
        word_count = len(summary_words)

        # --- Semantic concept coverage (FAST: uses cached embeddings) ---
        semantic_hits = 0
        semantic_hit_details = []

        if use_semantic and concept_embs is not None:
            start_idx, end_idx = sentence_map.get(idx, (0, 0))
            if start_idx < end_idx:
                student_sent_embs = all_sent_embs[start_idx:end_idx]

                for c_idx, c_emb in enumerate(concept_embs):
                    sims = np.dot(student_sent_embs, c_emb)
                    best_sim = float(sims.max())
                    # Lower threshold for generous matching
                    concept = concepts[c_idx]
                    threshold = 0.30 if " " in concept else 0.35
                    if best_sim >= threshold:
                        semantic_hits += 1
                        semantic_hit_details.append(concept)

        semantic_coverage = (semantic_hits / len(concepts) * 100) if concepts else 0

        # --- Keyword concept match (supplementary) ---
        matched_kw, missing_kw = _keyword_concept_match(summary_lower, concepts)
        keyword_coverage = (len(matched_kw) / len(concepts) * 100) if concepts else 0

        # --- Combine: take the BETTER of semantic vs keyword per concept ---
        if use_semantic:
            # Merge: any concept found by either method counts
            all_matched = list(set(semantic_hit_details) | set(matched_kw))
            all_missing = [c for c in concepts if c not in all_matched]
            concept_coverage = (len(all_matched) / len(concepts) * 100) if concepts else 0
        else:
            all_matched = matched_kw
            all_missing = missing_kw
            concept_coverage = keyword_coverage

        # --- Depth Score ---
        depth = _score_depth(summary_lower, summary_words)

        # --- Attempt Bonus (30%) ---
        # Submit 10+ words = full attempt marks. Rewards effort.
        attempt_score = 100 if word_count >= 10 else (word_count / 10 * 100)

        # --- Expression Quality ---
        expression = _score_expression(summary, summary_words)

        # --- Weighted Total (generous — rewards student effort) ---
        total = (
            concept_coverage * 0.35 +    # Topic coverage
            depth * 0.15 +               # Comprehension depth
            expression * 0.10 +          # Writing quality
            attempt_score * 0.30 +       # Effort bonus (30% just for submitting)
            10.0                         # Base points (everyone gets 10/100 = 1/10)
        )

        # Floor: any genuine submission (10+ words) gets at least 3.5/10
        if word_count >= 10:
            total = max(total, 35)

        results[student_id] = {
            "concept_coverage": round(concept_coverage, 1),
            "matched_concepts": all_matched,
            "missing_concepts": all_missing,
            "word_count": word_count,
            "depth_score": round(depth, 1),
            "expression_score": round(expression, 1),
            "attempt_score": round(attempt_score, 1),
            "total_score": round(min(total, 100), 1),
            "scoring_method": "semantic" if use_semantic else "keyword",
        }

    return results


# Keep backward-compatible single-student function
def score_summary_against_concepts(
    summary: str,
    concepts: List[str],
    concept_weights: Dict[str, float] = None,
    clean_transcript: str = "",
) -> Dict[str, any]:
    """Single-student scoring (calls batch with 1 student)."""
    result = batch_score_summaries(
        {"_single": summary}, concepts, clean_transcript
    )
    return result.get("_single", {
        "concept_coverage": 0, "matched_concepts": [], "missing_concepts": concepts,
        "word_count": 0, "depth_score": 0, "total_score": 0,
        "scoring_method": "none",
    })


def _keyword_concept_match(
    summary_lower: str, concepts: List[str]
) -> tuple:
    """
    Match concepts against summary using keyword/phrase matching.
    Returns (matched_list, missing_list).
    """
    matched = []
    missing = []

    for concept in concepts:
        concept_lower = concept.lower()
        if concept_lower in summary_lower:
            matched.append(concept)
        else:
            # Check partial match for multi-word phrases
            concept_words = concept_lower.split()
            if len(concept_words) > 1:
                words_found = sum(1 for w in concept_words if w in summary_lower)
                if words_found >= len(concept_words) * 0.6:
                    matched.append(concept)
                else:
                    missing.append(concept)
            else:
                # Check common variations
                variations = _get_variations(concept_lower)
                if any(v in summary_lower for v in variations):
                    matched.append(concept)
                else:
                    missing.append(concept)

    return matched, missing


def _get_variations(word: str) -> List[str]:
    """Generate common variations of a term."""
    variations = [word]
    if word.endswith("s"):
        variations.append(word[:-1])
    else:
        variations.append(word + "s")
    # Common word form variations
    _form_map = {
        "classification": ["classify", "classifying", "classified"],
        "regression": ["regress", "regressing"],
        "prediction": ["predict", "predicting", "predicted"],
        "visualization": ["visualize", "visualizing", "visualized", "visual"],
        "accuracy": ["accurate", "accurately"],
        "precision": ["precise", "precisely"],
        "training": ["train", "trained"],
        "testing": ["test", "tested"],
        "normalization": ["normalize", "normalizing", "normalized"],
        "standardization": ["standardize", "standardizing", "standardized", "standard"],
    }
    variations.extend(_form_map.get(word, []))
    return variations


def _score_depth(text: str, words: List[str]) -> float:
    """
    Score comprehension depth (surface listing vs. understanding).

    Students who explain "why" and "how" score higher than those
    who just list topics.
    """
    score = 50.0  # Base score

    # Indicators of deeper understanding
    depth_indicators = [
        (r"\bbecause\b", 8),
        (r"\bso\s+that\b", 8),
        (r"\bin\s+order\s+to\b", 8),
        (r"\bwhich\s+means\b", 10),
        (r"\bthis\s+(helps|allows|enables|ensures)\b", 8),
        (r"\bfor\s+example\b", 7),
        (r"\bsuch\s+as\b", 5),
        (r"\bthe\s+purpose\s+of\b", 8),
        (r"\bused\s+(for|to)\b", 5),
        (r"\bhelps\s+(us|to|in)\b", 5),
        (r"\bimportant\s+because\b", 10),
        (r"\brelationship\s+between\b", 8),
        (r"\bconvert(s|ed|ing)?\b", 5),
        (r"\bcompare[sd]?\b", 5),
        (r"\banalyze[sd]?\b", 5),
        (r"\bidentif(y|ies|ied)\b", 5),
        (r"\bfollowed\s+by\b", 5),
        (r"\bfinally\b", 4),
        (r"\bbegins?\s+by\b", 4),
        (r"\bevaluated?\s+using\b", 6),
        (r"\btrained\s+on\b", 5),
        (r"\bperformance\b", 4),
        (r"\bworkflow\b", 5),
        (r"\bunderstand(ing)?\b", 4),
        (r"\bapproach\b", 4),
        (r"\btechnique\b", 5),
        (r"\bmethod\b", 4),
    ]

    for pattern, bonus in depth_indicators:
        if re.search(pattern, text):
            score += bonus

    # Penalty for pure listing (just naming things without explanation)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s for s in sentences if s.strip()]
    short_sentences = sum(1 for s in sentences if len(s.split()) < 5)
    if len(sentences) > 2 and short_sentences / len(sentences) > 0.6:
        score -= 15

    return min(max(score, 0), 100)


def _score_expression(text: str, words: List[str]) -> float:
    """Score writing quality (grammar, structure, clarity)."""
    score = 60.0  # Base

    # Proper capitalization at start
    if text and text[0].isupper():
        score += 5

    # Has periods (proper sentences)
    period_count = text.count(".")
    if period_count >= 2:
        score += 10
    elif period_count == 0:
        score -= 15

    # Variety of words (not repetitive)
    unique_ratio = len(set(words)) / len(words) if words else 0
    if unique_ratio > 0.6:
        score += 10
    elif unique_ratio < 0.4:
        score -= 10

    # Not all lowercase (shows some care)
    upper_count = sum(1 for c in text if c.isupper())
    if upper_count < 2 and len(text) > 50:
        score -= 10

    return min(max(score, 0), 100)


# ---------------------------------------------------------------------------
# HTML stripping (for student submissions in HTML format)
# ---------------------------------------------------------------------------

def strip_html(html_text: str) -> str:
    """Strip HTML tags from student submissions."""
    # Remove DOCTYPE, html, head, body, div, p, span tags etc.
    text = re.sub(r"<[^>]+>", " ", html_text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Decode common HTML entities
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&nbsp;", " ")
    text = text.replace("&quot;", '"')
    return text
