#!/usr/bin/env python3
"""Deterministic prompt refiner for reducing token usage while preserving intent.

This script intentionally uses only the Python standard library so it can run in
any repository, CI job, or Codex skill without network access or API keys.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

FILLER_PATTERNS = [
    r"\b(?:please|kindly|just|really|basically|actually|maybe|perhaps|i think|i feel like)\b",
    r"\b(?:if you can|if possible|when you get a chance|at your earliest convenience)\b",
    r"\b(?:i would like you to|i want you to|can you|could you|would you|help me|help us)\b",
]

CJK_FILLER_PATTERNS = [
    r"(?:帮我|请你|麻烦你|如果可以|我想让你|能不能|可不可以)",
    r"(?:其实|就是|大概|可能|稍微|尽量|最好是|有点|一个很)",
]

INTENT_VERBS = {
    "build": "Build",
    "create": "Create",
    "make": "Create",
    "write": "Write",
    "draft": "Draft",
    "summarize": "Summarize",
    "analyze": "Analyze",
    "compare": "Compare",
    "fix": "Fix",
    "debug": "Debug",
    "refactor": "Refactor",
    "translate": "Translate",
    "生成": "生成",
    "创建": "创建",
    "建造": "创建",
    "写": "写作",
    "总结": "总结",
    "分析": "分析",
    "比较": "比较",
    "修复": "修复",
    "翻译": "翻译",
}

CONSTRAINT_HINTS = [
    "must", "do not", "don't", "never", "only", "without", "include", "exclude",
    "require", "avoid", "limit", "format", "tone", "audience", "deadline",
    "必须", "不要", "不能", "只", "包含", "排除", "避免", "限制", "格式", "语气", "受众", "截止",
]

@dataclass
class PromptResult:
    refined_prompt: str
    style: str
    original_chars: int
    refined_chars: int
    estimated_original_tokens: int
    estimated_refined_tokens: int
    estimated_token_savings_pct: float
    notes: list[str]


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    for pattern in FILLER_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    for pattern in CJK_FILLER_PATTERNS:
        text = re.sub(pattern, "", text)
    text = re.sub(r"\s+([,.;:!?，。；：！？])", r"\1", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip(" \n\t:：,，")


def split_units(text: str) -> list[str]:
    raw = re.split(r"(?:\n+|(?<=[.!?。！？；;])\s+)", text)
    units = [u.strip(" -•\t") for u in raw if u.strip(" -•\t")]
    # Split long comma-heavy text into semantically useful chunks.
    if len(units) <= 2 and len(text) > 80:
        parts = re.split(r"[,，;；]", text)
        units = [p.strip() for p in parts if p.strip()]
    return units or [text]


def detect_action(text: str) -> str:
    lowered = text.lower()
    for key, label in INTENT_VERBS.items():
        if key in lowered or key in text:
            return label
    return "Produce"


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = re.sub(r"\W+", "", item.lower())[:120]
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def extract_constraints(units: list[str]) -> tuple[list[str], list[str]]:
    constraints: list[str] = []
    remaining: list[str] = []
    for unit in units:
        haystack = unit.lower()
        if any(hint in haystack or hint in unit for hint in CONSTRAINT_HINTS):
            constraints.append(unit)
        else:
            remaining.append(unit)
    return dedupe_keep_order(constraints), dedupe_keep_order(remaining)


def safe_shorten(text: str, width: int) -> str:
    if len(text) <= width:
        return text
    if " " not in text and "\n" not in text:
        return text[: max(1, width - 1)].rstrip(" ,;:，。；：") + "…"
    words = text.split()
    out: list[str] = []
    total = 1
    for word in words:
        if total + len(word) > width:
            break
        out.append(word)
        total += len(word) + 1
    return (" ".join(out).rstrip(" ,;:") or text[: max(1, width - 1)]) + "…"


def clamp_words(text: str, max_words: int | None) -> str:
    if not max_words or max_words <= 0:
        return text
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(" ,;:") + "…"


def refine_prompt(text: str, style: str = "balanced", max_words: int | None = None) -> PromptResult:
    original = text.strip()
    normalized = normalize_text(original)
    if not normalized:
        raise ValueError("Prompt text is empty after normalization.")

    units = split_units(normalized)
    constraints, remaining = extract_constraints(units)
    action = detect_action(normalized)
    objective = remaining[0] if remaining else normalized
    objective = re.sub(r"^(to\s+|that\s+|me\s+|us\s+)", "", objective, flags=re.IGNORECASE).strip()
    objective = re.sub(rf"^{re.escape(action)}\s+", "", objective, flags=re.IGNORECASE).strip()

    notes = ["Removed filler and duplicate whitespace."]

    if style == "compact":
        parts = [f"{action}: {objective}"]
        if constraints:
            parts.append("Constraints: " + "; ".join(constraints[:4]))
        refined = " | ".join(parts)
    elif style == "agent":
        refined_lines = [
            f"Task: {action.lower()} {objective}",
            "Output: concise, directly usable result.",
        ]
        if constraints:
            refined_lines.append("Constraints:")
            refined_lines.extend(f"- {c}" for c in constraints[:6])
        if len(remaining) > 1:
            refined_lines.append("Context:")
            refined_lines.extend(f"- {r}" for r in remaining[1:5])
        refined = "\n".join(refined_lines)
    else:
        refined_lines = [f"{action}: {objective}"]
        if constraints:
            refined_lines.append("Constraints:")
            refined_lines.extend(f"- {c}" for c in constraints[:6])
        if len(remaining) > 1:
            refined_lines.append("Relevant context:")
            refined_lines.extend(f"- {r}" for r in remaining[1:5])
        refined = "\n".join(refined_lines)

    refined = clamp_words(refined, max_words)
    if len(refined) >= len(original):
        if style == "agent" and constraints:
            compact = f"{action}: {objective}; constraints: " + "; ".join(constraints[:4])
            refined = compact if len(compact) < len(original) else safe_shorten(normalized, max(40, int(len(original) * 0.85)))
        else:
            refined = safe_shorten(normalized, max(40, int(len(original) * 0.85)))
        notes.append("Used safe shortening because structured output was not shorter.")

    original_tokens = max(1, round(len(original) / 4))
    refined_tokens = max(1, round(len(refined) / 4))
    savings = max(0.0, round((1 - refined_tokens / original_tokens) * 100, 1))

    return PromptResult(
        refined_prompt=refined,
        style=style,
        original_chars=len(original),
        refined_chars=len(refined),
        estimated_original_tokens=original_tokens,
        estimated_refined_tokens=refined_tokens,
        estimated_token_savings_pct=savings,
        notes=notes,
    )


def read_input(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.file:
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("Provide prompt text via --text, --file, or stdin.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert verbose natural language into a precise, token-efficient prompt."
    )
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--text", help="Prompt text to refine.")
    input_group.add_argument("--file", help="Path to a UTF-8 text file containing the prompt.")
    parser.add_argument(
        "--style",
        choices=["compact", "balanced", "agent"],
        default="balanced",
        help="Output format: one-line compact, balanced bullets, or agent-oriented fields.",
    )
    parser.add_argument("--max-words", type=int, help="Hard cap for output word count.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON with token estimates.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = refine_prompt(read_input(args), style=args.style, max_words=args.max_words)
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(result.refined_prompt)
        print(
            f"\nEstimated tokens: {result.estimated_original_tokens} -> "
            f"{result.estimated_refined_tokens} "
            f"({result.estimated_token_savings_pct}% saved)",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
