# Prompt Compressor Skill and CLI

`prompt-compressor` helps reduce LLM token usage by converting verbose natural-language requests into concise, executable prompts. It is designed as both:

- a Codex-style skill at `skills/prompt-compressor/`, and
- a deterministic Python CLI at `scripts/refine_prompt.py`.

## Why it exists

Verbose prompts often spend tokens on social filler, repeated context, and vague preferences. This tool keeps the important parts:

- task objective,
- required context,
- hard constraints,
- output format,
- acceptance criteria.

## CLI usage

```bash
python scripts/refine_prompt.py --text "请你帮我写一个很详细的营销邮件，最好语气专业一点，不要超过200字，目标用户是BCI研究者"
```

Return JSON with token estimates:

```bash
python scripts/refine_prompt.py --style agent --json --text "Build a tool that turns long descriptions into precise prompts and saves tokens. It must not lose key requirements."
```

Read from a file:

```bash
python scripts/refine_prompt.py --file prompt.txt --style compact --max-words 80
```

## Skill usage

When installed as a skill, ask for prompt compression or prompt refinement, for example:

```text
Use prompt-compressor to turn this requirement into a concise agent prompt: <text>
```

The skill includes a deterministic script plus compression patterns in `references/compression-patterns.md`.

## Publishing to GitHub

This repository now contains the skill files, CLI wrapper, and documentation. After merging the PR, GitHub users can clone the repo and run the CLI directly, or copy `skills/prompt-compressor/` into their Codex skills directory.
