# AI Agents + Tool Use Basics

A plain LLM only produces text. An **agent** is an LLM in a loop that can **call tools** (functions you write) to look things up or take actions, then use the results to decide what to do next.

> **Verification status:** I had no API key, so the "model" here is a scripted fake server. I ran the **real `anthropic` SDK (v2.8.0)** against it, which proves the loop logic, the message formats, and the tool code work. It does *not* show how a real model decides when to call tools. Try it with a key to see that.

## How tool use works

The model never runs your code. It *asks* you to:

1. You send the question **plus tool descriptions** (name, what it does, input schema).
2. The model replies with `stop_reason = "tool_use"` and a block saying "call `get_order_status` with `order_id="A100"`".
3. **Your code** runs the function.
4. You send the result back as a `tool_result`.
5. The model uses it and answers (`stop_reason = "end_turn"`), or asks for another tool.

Steps 2 to 5 repeat. That loop is the agent.

## Code

```python
import json, anthropic

# ---------- your tools: plain Python functions ----------
def get_order_status(order_id: str) -> str:
    db = {"A100": "shipped, arriving Friday", "A200": "processing"}
    return db.get(order_id, "order not found")

def calculate(expression: str) -> str:
    if not set(expression) <= set("0123456789+-*/(). "):       # never eval() untrusted text raw
        return "error: only numbers and + - * / ( ) allowed"
    return str(eval(expression, {"__builtins__": {}}))

TOOL_FUNCS = {"get_order_status": get_order_status, "calculate": calculate}
TOOLS = [
 {"name": "get_order_status", "description": "Look up the shipping status of a customer order by its ID.",
  "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
 {"name": "calculate", "description": "Evaluate an arithmetic expression.",
  "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}]

client = anthropic.Anthropic()      # real use; my test pointed this at a scripted fake server

def run_agent(question: str, max_steps: int = 5) -> str:
    messages = [{"role": "user", "content": question}]
    for step in range(max_steps):                                   # ALWAYS cap the loop
        resp = client.messages.create(model="claude-sonnet-5-5", max_tokens=500, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  [agent ] step {step}: model wants {block.name}({block.input})")
                try:
                    out = TOOL_FUNCS[block.name](**block.input)
                except Exception as e:                              # tell the model about failures instead of crashing
                    out = f"error: {e}"
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": out})
        messages.append({"role": "user", "content": results})
    return "stopped: too many steps"

print("FINAL:", run_agent("Where is my order A100?"))
```

Output of my scripted test (`[server]` lines come from the fake server):

```
  [server] call #1: 1 messages, tools offered: ['get_order_status', 'calculate']
  [agent ] step 0: model wants get_order_status({'order_id': 'A100'})
  [server] call #2: 3 messages, tools offered: ['get_order_status', 'calculate']
FINAL: Your order A100 is: shipped, arriving Friday.
calculate('2*(3+4)') -> 14
calculate('__import__("os")') -> error: only numbers and + - * / ( ) allowed
```

Look at the second server call: **3 messages** (the question, the assistant's tool request, your tool result). That is the whole protocol. The last two lines test the `calculate` tool itself, including that it refuses a code-injection attempt.

Two details that trip people up:
- Append the **assistant's full `content`** (not just the text) before the tool result, so the `tool_use` block is in the history.
- The `tool_use_id` in each result must match the request's `id`.

## Writing good tools

- **The description is the prompt.** The model chooses tools from your name and description. "Look up the shipping status of a customer order by its ID" beats "orders".
- **Small, single-purpose tools** with simple typed inputs.
- **Return short, useful text.** Dumping a 10,000-line database row wastes tokens and confuses the model.
- **Return errors as text** so the model can retry or explain, rather than crashing the loop.
- Typical tools: search the knowledge base ([note 04](04-rag-chat-with-your-pdfs.md)), query a database, call an internal API, run a calculation, create a ticket.

## Safety: the part that matters most

- **Cap the steps** (`max_steps`). Agents can loop and burn money.
- **Least privilege.** A tool that can only *read* an order can't do harm. Give write access (refunds, emails, deletes) only when needed.
- **Human approval for risky actions:** refunds, sending messages, anything irreversible. Have the tool return "pending approval" rather than doing it.
- **Never `eval` or run shell commands from model-supplied text** without strict validation. Treat model arguments like untrusted user input, because that's what they are.
- **Prompt injection:** text fetched by a tool (a web page, an email) can contain instructions aimed at your agent. Don't let tool output grant new permissions.
- **Log every tool call** with inputs and outputs. You'll need it to debug and audit.

## When to use an agent (and when not)

| Use a plain prompt or fixed pipeline | Use an agent |
|---|---|
| Steps are known in advance | Steps depend on what's found along the way |
| One lookup, then answer | Variable number of lookups |
| Reliability and cost matter most | Flexibility matters more |

**Start with the simplest thing.** A fixed pipeline (retrieve, then answer) is cheaper, faster and easier to test than an agent. Add the loop only when the task needs it. Agents are also slower and cost more, since each step is another model call.

## Quick check

Who actually runs `get_order_status`: the model or your code? *(Your code. The model only requests it.)*

That finishes the GenAI set. A natural next project: combine notes 03 to 05 into a support bot with a RAG search tool and an order-lookup tool.
