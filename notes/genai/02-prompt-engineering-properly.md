# Prompt Engineering, Properly

"Prompt engineering" is not magic phrases. It's writing clear instructions for a very capable but literal colleague who has never seen your project and cannot ask follow-up questions.

> **Verification status:** the prompt builder and the output parser below were run for real (pure Python). The "model replies" are hand-written samples of the kinds of replies models give, since I had no API key. The point is the *engineering around* the prompt.

## The six rules that matter

1. **Say who and why.** "You are a support-ticket triage assistant" plus the goal beats "classify this".
2. **Be specific about the output.** Name the format, the allowed values and the length.
3. **Show examples (few-shot).** Two good examples teach format and tone better than a paragraph of rules.
4. **Separate instructions from data** with tags like `<ticket>...</ticket>`. It stops the data from being mistaken for instructions.
5. **Give an escape hatch.** "If unsure, use `other`" or "say 'I don't know'" reduces made-up answers.
6. **Iterate against real test cases,** not vibes. Keep 20 to 50 realistic inputs and re-run them after every change.

## Code: a structured-output prompt plus a defensive parser

```python
import json, re

def build_prompt(ticket: str) -> str:
    return f"""You are a support-ticket triage assistant.

<rules>
- category must be one of: billing, shipping, technical, other
- urgency is 1 (low) to 5 (critical)
- If unsure, use category "other". Never invent facts.
</rules>

<examples>
<ticket>I was charged twice for order 123</ticket>
{{"category": "billing", "urgency": 4, "summary": "Duplicate charge on order 123"}}

<ticket>Where can I change my avatar?</ticket>
{{"category": "other", "urgency": 1, "summary": "Asks how to change avatar"}}
</examples>

Reply with ONLY a JSON object with keys category, urgency, summary.

<ticket>{ticket}</ticket>"""

ALLOWED = {"billing", "shipping", "technical", "other"}

def parse_reply(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)             # models sometimes add prose or ```json fences
    if not m:
        raise ValueError("no JSON found")
    data = json.loads(m.group(0))
    if data.get("category") not in ALLOWED:
        raise ValueError(f"bad category: {data.get('category')!r}")
    if not (isinstance(data.get("urgency"), int) and 1 <= data["urgency"] <= 5):
        raise ValueError(f"bad urgency: {data.get('urgency')!r}")
    return data
```

Test run of `parse_reply` on five realistic replies:

```
OK   {'category': 'technical', 'urgency': 3, 'summary': 'Crash opening settings'}
OK   {'category': 'technical', 'urgency': 3, 'summary': 'Crash'}              <- had prose + ```json fences, still parsed
FAIL ValueError - bad category: 'bug'                                         <- invented a category
FAIL ValueError - bad urgency: 'high'                                         <- wrong type
FAIL ValueError - no JSON found                                               <- model refused / rambled
```

This is the real lesson: **the prompt asks nicely, the code verifies.** Three of five replies would have crashed or corrupted a database without the validation. In production, on `ValueError` you retry once (optionally including the error in the next message), then fall back to a human queue.

## Techniques worth knowing

| Technique | When |
|---|---|
| **Few-shot examples** | format/tone must be exact |
| **"Think step by step" / reasoning first, answer last** | maths, logic, multi-step decisions. (Many newer models have built-in reasoning modes; use those where available.) |
| **Role + audience** ("explain to a new hire") | tone control |
| **Prefill / structured output / tool schemas** | when you need guaranteed JSON. Prefer the API's structured-output or tool-use features over begging in prose |
| **Prompt chaining** | split big jobs: extract, then classify, then write. Each step is easier to test |
| **Delimiters** | any time user-supplied text is mixed in |

## Weak vs strong, side by side

| Weak | Strong |
|---|---|
| "Summarise this." | "Summarise this contract for a non-lawyer in 5 bullets. Flag any auto-renewal or penalty clause. Quote the clause number." |
| "Write good code." | "Write a Python 3.12 function `parse_date(s)` that returns a `date` or raises `ValueError`. Standard library only. Include 3 pytest tests." |
| "Fix my email." | "Rewrite for a customer who is upset about a late delivery. Apologise once, state the new date (Friday), keep under 80 words." |

## Real-world rules of thumb

- **Put the long data first and the question last** for long documents.
- **Prompts are code.** Version them in git, review changes, and run your test cases before shipping.
- **Prompt injection is real.** If user or web text enters your prompt, it may contain "ignore previous instructions". Delimit it, never let model output trigger dangerous actions without checks, and keep secrets out of prompts.
- Lower temperature for repeatable results, but don't expect bit-identical output.
- If a prompt needs 40 rules, you probably need a better task split, not a longer prompt.

## Quick check

Why validate the model's JSON in code if the prompt already says "reply with ONLY JSON"? *(Prompts make the right behaviour likely, not guaranteed. Code makes it safe.)*
