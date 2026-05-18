# Prompt compression patterns

## Compression rubric

Score a compressed prompt against four checks:

1. Intent fidelity: no required task, constraint, input, or output format was lost.
2. Token efficiency: filler and duplicate context were removed.
3. Executability: an agent can start without asking obvious follow-up questions.
4. Specificity: vague terms were replaced with concrete constraints when possible.

## Common rewrites

| Verbose phrase | Replace with |
| --- | --- |
| “Can you please help me...” | Imperative verb: “Write”, “Build”, “Analyze” |
| “Make it good/professional” | “Use a concise professional tone” |
| “As soon as possible” | Omit unless there is a real deadline |
| “Do some research” | “Find 3 sources and summarize evidence” |
| “A detailed answer” | “Include: context, steps, risks, examples” |
| “不要太长” | “不超过 N 字/条” |
| “精准合适” | “保留目标、约束、输出格式和验收标准” |

## Before/after examples

### Product request

Before:

```text
我想让你帮我做一个工具，就是用户说一大段话的时候，你能够帮他变成一个更精准的prompt，最好可以少花token，也不要丢掉重要意思。
```

After:

```text
Build a prompt-refinement tool that converts verbose user text into a concise prompt while preserving intent, constraints, output format, and success criteria. Include token-savings estimates.
```

### Research summary

Before:

```text
Please read this paper and give me a pretty detailed but not too long explanation for someone technical who does not know this exact topic.
```

After:

```text
Summarize the paper for a technical non-specialist in ≤500 words. Include: problem, method, key findings, limitations, and practical implications.
```

### Agent coding task

Before:

```text
Could you maybe look through the app and fix the issue where the search seems weird and also make sure not to break anything else if possible?
```

After:

```text
Debug and fix the app search behavior. Preserve existing APIs and UI. Add or update tests that cover the failing search case, then report files changed and commands run.
```

## Reusable template

```text
Task: <action + object>
Context: <facts needed; omit backstory>
Constraints: <must/avoid/limits>
Output: <format + length + language>
Acceptance: <how to verify success>
```
