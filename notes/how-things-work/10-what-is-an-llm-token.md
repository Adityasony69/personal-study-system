# What is an LLM token

LLMs like ChatGPT and Claude do not read letters or whole words. They read **tokens**: chunks of text, usually a common word or a piece of a word. Pricing, context limits and some strange LLM mistakes all come from this.

## See real tokens
`tiktoken` is OpenAI's tokenizer library (`python -m pip install tiktoken`). This uses `o200k_base`, the tokenizer of recent GPT models:

```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
for s in ["Hello world", "hello world", "unbelievable", "Namaste, kaise ho?", "नमस्ते", "1234567890", "def add(a, b):"]:
    ids = enc.encode(s)
    print(f"{s!r:22} {len(ids):2} tokens {[enc.decode([i]) for i in ids]}")
```

```
'Hello world'           2 tokens ['Hello', ' world']
'hello world'           2 tokens ['hello', ' world']
'unbelievable'          3 tokens ['un', 'bel', 'ievable']
'Namaste, kaise ho?'    7 tokens ['Nam', 'aste', ',', ' ka', 'ise', ' ho', '?']
'नमस्ते'                4 tokens ['न', 'म', 'स्त', 'े']
'1234567890'            4 tokens ['123', '456', '789', '0']
'def add(a, b):'        6 tokens ['def', ' add', '(a', ',', ' b', '):']
```

(On Windows, the Hindi line crashed with `UnicodeEncodeError: 'charmap' codec` until I ran it with `PYTHONUTF8=1`. Note 22 explains why.)

What to notice:

- **The space belongs to the next word**: `' world'` is one token.
- **Common words are one token, rare words are split**: `unbelievable` becomes 3 pieces.
- **Hinglish and Hindi cost more tokens** for the same meaning, because the tokenizer was trained mostly on English. Same message, higher bill.
- **Numbers are cut into chunks of 3 digits.** The model sees `123`, `456`, ... not a number. This is one reason LLMs used to make silly arithmetic mistakes.

Every model family has its own tokenizer. Claude's tokenizer splits text differently from GPT's, so counts differ between providers. Rough rule for English: **1 token ≈ 4 characters ≈ 0.75 words**, so 1000 tokens is about 750 words.

## How the tokenizer was made (BPE in one paragraph)
Start with single bytes. Scan a huge pile of text, find the pair that appears together most often (say `t` + `h`), and glue it into a new token `th`. Repeat tens of thousands of times. Frequent words end up as single tokens; rare words stay as pieces. This is called **Byte Pair Encoding**. Because it starts from bytes, any text (any language, emoji, code) can be tokenized.

## How an LLM uses tokens
1. Your text becomes a list of token IDs (numbers).
2. The model reads all of them and predicts **the single next token**.
3. That token is added to the list, and it predicts the next one again.
4. Repeat until it outputs a stop token.

So an LLM writes one token at a time, which is why answers stream in word by word.

## Why tokens matter in practice

| Thing | Measured in tokens |
|---|---|
| Price | APIs charge per million input tokens and per million output tokens. Output usually costs several times more. |
| Context window | The max tokens the model can see at once (your prompt + chat history + its answer). |
| Speed | Output tokens per second. |
| Rate limits | Tokens per minute. |

Real decisions this leads to: trim long chat history; do not paste a whole PDF when one section will do; ask for short answers when you are paying per token.

## Odd behaviour explained by tokens
- "How many r's in strawberry?" was hard because the model sees chunks like `str` + `aw` + `berry`, not letters.
- Reversing a word or counting characters is hard for the same reason.
- A trailing space in a prompt can change the answer, because `' world'` and `'world'` are different tokens.

## Try it yourself
1. Tokenize the same paragraph in English and in Hindi. Compare counts.
2. Tokenize one of your Python files and estimate what it would cost to send to an API at a price of your choice per million tokens.
