# LLM APIs: Calling a Model from Python

An LLM API lets your code send text to a hosted model and get text back. It's how every "AI feature" in an app is built. No GPU, no training: one HTTP request.

> **Verification status:** I had no API key in my environment, so I did **not** make a live call. I ran the real `anthropic` SDK (v2.8.0) against a local fake server to confirm the request the SDK builds and how it parses a response. The code below is the real-use version; the output is from the fake server, so the answer text is canned. Run it yourself with a key to see a real reply.

## Setup

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."     # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
```

Get the key from the provider's console. **Never hard-code it or commit it to git.** `anthropic.Anthropic()` reads the environment variable automatically.

## The basic call

```python
import anthropic
client = anthropic.Anthropic()          # uses ANTHROPIC_API_KEY

resp = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=200,
    system="You are a concise Python tutor.",
    messages=[{"role": "user", "content": "Explain list vs dict in one sentence."}],
)
print("answer :", resp.content[0].text)
print("stop   :", resp.stop_reason)
print("tokens :", resp.usage.input_tokens, "in /", resp.usage.output_tokens, "out")
```

Output from my fake-server test (the first two lines show what the SDK actually sent over the wire):

```
SDK sent: model = claude-sonnet-5-5 | max_tokens = 200 | messages = [{'role': 'user', 'content': 'Explain list vs dict in one sentence.'}]
          system = You are a concise Python tutor.
answer : A list stores items in order; a dict looks values up by key.
stop   : end_turn
tokens : 31 in / 17 out
```

## The parts you must understand

| Piece | Meaning |
|---|---|
| `model` | which model; bigger = smarter, slower, pricier. Check the provider's docs for current IDs |
| `system` | standing instructions (role, tone, rules). Not part of the chat turns |
| `messages` | the conversation: alternating `user` / `assistant` turns |
| `max_tokens` | hard cap on the reply length. **Required** |
| `stop_reason` | `end_turn` (finished), `max_tokens` (cut off!), `tool_use` (wants a tool, see note 05) |
| `usage` | tokens in/out: what you're billed for |

## The model has no memory: you resend the history

Every call is independent. A chatbot is just you appending to a list and sending all of it again:

```python
history = [{"role": "user", "content": "Explain list vs dict in one sentence."},
           {"role": "assistant", "content": resp.content[0].text},
           {"role": "user", "content": "Now give a tiny example."}]
client.messages.create(model="claude-sonnet-5-5", max_tokens=200, messages=history)
```

I confirmed against the fake server that the SDK sends all three turns. This is why long chats cost more per message: you pay for the whole history each time.

## Real-world rules of thumb

- **Tokens are money.** A token is roughly 3/4 of an English word. Cost = input tokens x input price + output tokens x output price. Log `usage` from day one.
- **Always check `stop_reason`.** `max_tokens` means the reply was truncated mid-sentence.
- **Handle failures.** Networks drop and rate limits happen. The SDK retries a couple of times by default; wrap calls in `try/except anthropic.APIError` and show the user something sensible.
- **Stream for chat UIs** (`client.messages.stream(...)`) so words appear as they're generated instead of after a long wait.
- **Keep secrets server-side.** Never call the API from browser code with your key inside.
- **Temperature** controls randomness: low (0 to 0.3) for extraction and classification, higher for creative writing.
- **Don't trust output blindly.** Models can state wrong things confidently. Validate anything that matters (see [02 Prompt engineering](02-prompt-engineering-properly.md)).
- **Cost control:** use a smaller, cheaper model for simple tasks, set `max_tokens` sensibly, and cache repeated prompts where the provider supports it.

## Quick check

A user says "what did I just ask you?" and your bot has no idea. What did you forget? *(To resend the earlier messages in `messages`.)*
