# Prompt Compressor Skill

Turn verbose instructions into precise, token-efficient prompts while preserving intent, constraints, output format, and success criteria.

## Why

Long prompts waste tokens on filler, repeated context, and vague wording. `prompt-compressor` rewrites them into concise prompts that are easier for LLMs and coding agents to execute.

## Features

- Compress long natural-language requests into concise prompts
- Preserve hard constraints, audience, tone, inputs, and output format
- Estimate token savings locally
- Run as a Codex skill or a standalone Python CLI
- Works offline with only the Python standard library

## Quick Start

```bash
python scripts/refine_prompt.py --text "请你帮我写一个很详细的营销邮件，最好语气专业一点，不要超过200字，目标用户是BCI研究者"
```

JSON output with token estimates:

```bash
python scripts/refine_prompt.py --style agent --json --text "Build a tool that turns long descriptions into precise prompts and saves tokens. It must not lose key requirements."
```

Read from a file:

```bash
python scripts/refine_prompt.py --file prompt.txt --style compact --max-words 80
```

## Example

Before:

```text
Could you maybe look through the app and fix the issue where the search seems weird and also make sure not to break anything else if possible?
```

After:

```text
Debug and fix the app search behavior. Preserve existing APIs and UI. Add or update tests that cover the failing search case, then report files changed and commands run.
```

## Use As A Codex Skill

Copy the skill directory into your Codex skills folder:

```bash
cp -R skills/prompt-compressor ~/.codex/skills/
```

Then ask Codex:

```text
Use prompt-compressor to turn this requirement into a concise agent prompt: <text>
```

## Project Structure

```text
prompt-compressor-skill/
├── README.md
├── docs/
│   └── prompt-compressor.md
├── scripts/
│   └── refine_prompt.py
└── skills/
    └── prompt-compressor/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/compression-patterns.md
        └── scripts/refine_prompt.py
```

## License

MIT
