"""
Unified AST-based code parser using tree-sitter.

Replaces the fragmented ast.parse() + regex approach with a single
parser that works for Python, C++, Java, and JavaScript — producing
identical feature dictionaries regardless of language.
"""

from typing import Dict, Optional

# Lazy-load tree-sitter to avoid import errors if not installed
_TREE_SITTER_AVAILABLE = False
_LANGUAGES = {}

def _init_tree_sitter():
    """One-time initialization of tree-sitter languages."""
    global _TREE_SITTER_AVAILABLE, _LANGUAGES
    if _LANGUAGES:
        return  # Already initialized

    try:
        from tree_sitter import Language, Parser

        try:
            import tree_sitter_python as tspython
            _LANGUAGES["python"] = Language(tspython.language())
        except Exception:
            pass

        try:
            import tree_sitter_cpp as tscpp
            _LANGUAGES["cpp"] = Language(tscpp.language())
        except Exception:
            pass

        if _LANGUAGES:
            _TREE_SITTER_AVAILABLE = True
        else:
            print("WARNING: tree-sitter grammars not found. Falling back to regex mode.")
    except ImportError:
        print("WARNING: tree-sitter not installed. Falling back to regex mode.")


# ---------------------------------------------------------------------------
# Node-type → feature mapping per language
# ---------------------------------------------------------------------------

# Maps tree-sitter node types to our canonical feature names.
# Multiple node types can map to the same feature.

NODE_TYPE_MAP = {
    "python": {
        "function_definition": "functions",
        "class_definition": "classes",
        "for_statement": "loops",
        "while_statement": "loops",
        "if_statement": "conditions",
        "try_statement": "error_handling",
        "except_clause": "error_handling",
    },
    "cpp": {
        "function_definition": "functions",
        "function_declarator": "functions",
        "class_specifier": "classes",
        "struct_specifier": "classes",
        "for_statement": "loops",
        "for_range_loop": "loops",
        "while_statement": "loops",
        "do_statement": "loops",
        "if_statement": "conditions",
        "switch_statement": "conditions",
        "try_statement": "error_handling",
        "catch_clause": "error_handling",
    },
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def is_available() -> bool:
    """Check if tree-sitter is available."""
    _init_tree_sitter()
    return _TREE_SITTER_AVAILABLE


def supports_language(lang: str) -> bool:
    """Check if a specific language grammar is loaded."""
    _init_tree_sitter()
    return lang in _LANGUAGES


def extract_features(code: str, lang: str) -> Dict:
    """
    Parse code and extract structural features.

    Args:
        code: Source code string.
        lang: Language key ("python", "cpp").

    Returns:
        Dictionary with counts::

            {
                "functions": int,
                "classes": int,
                "loops": int,
                "conditions": int,
                "error_handling": int,
                "has_syntax_error": bool,
                "total_nodes": int,
                "parser_mode": "tree-sitter" | "regex"
            }
    """
    _init_tree_sitter()

    if _TREE_SITTER_AVAILABLE and lang in _LANGUAGES:
        return _extract_with_tree_sitter(code, lang)
    else:
        return _extract_with_regex(code, lang)


# ---------------------------------------------------------------------------
# tree-sitter implementation
# ---------------------------------------------------------------------------

def _extract_with_tree_sitter(code: str, lang: str) -> Dict:
    """Extract features using tree-sitter AST walk."""
    from tree_sitter import Parser

    parser = Parser(_LANGUAGES[lang])
    tree = parser.parse(code.encode("utf-8"))

    counts = {
        "functions": 0,
        "classes": 0,
        "loops": 0,
        "conditions": 0,
        "error_handling": 0,
    }

    type_map = NODE_TYPE_MAP.get(lang, {})
    total_nodes = 0

    def walk(node):
        nonlocal total_nodes
        total_nodes += 1

        if node.type in type_map:
            feature_key = type_map[node.type]
            counts[feature_key] += 1

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    counts["has_syntax_error"] = tree.root_node.has_error
    counts["total_nodes"] = total_nodes
    counts["parser_mode"] = "tree-sitter"
    return counts


# ---------------------------------------------------------------------------
# Regex fallback (same logic as old code_agent, but returns the same dict)
# ---------------------------------------------------------------------------

def _extract_with_regex(code: str, lang: str) -> Dict:
    """
    Fallback: extract features using regex and Python's ast module.

    Returns the same dict shape as tree-sitter, so callers don't care
    which mode was used.
    """
    import re

    counts = {
        "functions": 0,
        "classes": 0,
        "loops": 0,
        "conditions": 0,
        "error_handling": 0,
        "has_syntax_error": False,
        "total_nodes": 0,
        "parser_mode": "regex",
    }

    if lang == "python":
        try:
            import ast
            tree = ast.parse(code)
            for node in ast.walk(tree):
                counts["total_nodes"] += 1
                if isinstance(node, ast.FunctionDef):
                    counts["functions"] += 1
                elif isinstance(node, ast.ClassDef):
                    counts["classes"] += 1
                elif isinstance(node, (ast.For, ast.While)):
                    counts["loops"] += 1
                elif isinstance(node, ast.If):
                    counts["conditions"] += 1
                elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                    counts["error_handling"] += 1
        except SyntaxError:
            counts["has_syntax_error"] = True

    elif lang == "cpp":
        # Regex patterns for C++ structural elements
        counts["functions"] = len(re.findall(
            r'(?:[\w:]+\s+)+(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:noexcept\s*)?\{', code
        ))
        counts["classes"] = len(re.findall(r'\bclass\s+\w+', code))
        counts["loops"] = (
            len(re.findall(r'\bfor\s*\(', code))
            + len(re.findall(r'\bwhile\s*\(', code))
            + len(re.findall(r'\bdo\s*\{', code))
        )
        counts["conditions"] = (
            len(re.findall(r'\bif\s*\(', code))
            + len(re.findall(r'\bswitch\s*\(', code))
        )
        counts["error_handling"] = (
            len(re.findall(r'\btry\s*\{', code))
            + len(re.findall(r'\bcatch\s*\(', code))
        )
        counts["total_nodes"] = sum(v for k, v in counts.items() if isinstance(v, int))

    return counts
