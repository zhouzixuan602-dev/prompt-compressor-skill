---
name: prompt-compressor
description: Convert verbose, vague, or conversational user requests into precise, token-efficient prompts while preserving intent. Use when the user asks to reduce token usage, compress prompts, clarify instructions, rewrite language into a better prompt, create reusable prompt templates, or prepare concise prompts for AI agents/LLMs.
---

# Prompt Compressor

## Overview

Use this skill to turn natural-language descriptions into compact prompts that are clear enough for an AI agent to execute without wasting context. Preserve requirements, remove filler, expose assumptions, and choose the shortest structure that still prevents ambiguity.

## Quick workflow

1. Identify the task objective in one imperative sentence.
2. Preserve hard constraints, output format, audience, tone, inputs, and success criteria.
3. Delete social filler, repeated context, hedging, and implementation details that do not affect the result.
4. Replace vague adjectives with measurable requirements where possible.
5. Return a prompt in the smallest useful shape:
   - One line for simple tasks.
   - Bullets for constraints and deliverables.
   - A template with placeholders for repeated use.
6. If compression would remove important uncertainty, add a short `Assumptions` line instead of expanding the prompt.

## Prompt shape

Prefer this structure for most requests:

```text
Task: <imperative objective>
Context: <only facts needed to do the task>
Constraints: <must/avoid/limits>
Output: <format, length, language, acceptance criteria>
```

For very small tasks, use:

```text
<Verb> <object> for <audience/use case>; output <format>; constraints: <limits>.
```

## Use the bundled CLI

Run `scripts/refine_prompt.py` for deterministic first-pass compression without API keys:

```bash
python skills/prompt-compressor/scripts/refine_prompt.py --text "请你帮我写一个很详细的营销邮件，最好语气专业一点，不要超过200字，目标用户是BCI研究者"
```

Useful options:

- `--style compact` for one-line prompts.
- `--style balanced` for concise bullets.
- `--style agent` for agent-oriented `Task/Output/Constraints/Context` fields.
- `--max-words N` for a hard length cap.
- `--json` to include estimated token savings.

## Quality checklist

Before finalizing the compressed prompt, verify:

- The main verb is explicit: build, analyze, summarize, compare, translate, refactor, etc.
- Inputs and output format are named.
- Non-negotiable constraints are preserved.
- Ambiguous words like “better,” “high quality,” and “appropriate” are converted into observable criteria.
- The result is shorter than the original unless structure is needed to prevent errors.
- The prompt does not introduce new requirements not present in the source.

## Optional reference

Read `references/compression-patterns.md` when you need examples of before/after rewrites, reusable prompt templates, or a stricter compression rubric.
