# Transformers + Attention Intuition

Transformers power ChatGPT, Claude, BERT, modern translation, and image and speech models. They're one idea, **attention**, repeated many times.

## The problem attention solves

RNNs read a sentence word by word and squeeze everything into one running memory. Long sentences lose detail, and it's slow because step 5 waits for step 4.

Take: *"The cat sat because **it** was tired."* To understand "it", the model must look back at "cat". Attention lets every word **look at every other word directly** and decide how much each matters, all at once and in parallel.

## Attention in four steps

For each word:

1. Compare it with every word (a similarity score).
2. Turn the scores into percentages with **softmax** (they sum to 1).
3. Take a **weighted mix** of all the words' information using those percentages.
4. That mix is the word's new, context-aware meaning.

Real models give each word three learned versions: a **Query** ("what am I looking for?"), a **Key** ("what do I offer?") and a **Value** ("what do I pass along?"). Attention is `softmax(Q·Kᵀ / √d) · V`.

## Code: attention by hand, then a real Transformer

```python
import numpy as np, torch, torch.nn as nn
np.set_printoptions(precision=2, suppress=True)

words = ["the", "cat", "sat", "because", "it", "was", "tired"]
rng = np.random.default_rng(1)
E = rng.normal(size=(len(words), 8))           # toy word vectors
E[4] = E[1] + rng.normal(0, 0.1, 8)            # make "it" similar to "cat" so the demo is visible
Q = K = V = E                                  # self-attention (real models use learned projections)
scores = Q @ K.T / np.sqrt(E.shape[1])         # similarity of every word with every other word
weights = np.exp(scores) / np.exp(scores).sum(1, keepdims=True)   # softmax: each row sums to 1
out = weights @ V                              # new vector = weighted mix of all words
print("row sums:", weights.sum(1))
print('attention from "it":')
for w, a in sorted(zip(words, weights[4]), key=lambda x: -x[1])[:3]:
    print(f"   {w:8s} {a:.2f}")

torch.manual_seed(0)
layer = nn.TransformerEncoderLayer(d_model=32, nhead=4, dim_feedforward=64, batch_first=True)
enc = nn.TransformerEncoder(layer, num_layers=2)
tokens = torch.randn(1, 7, 32)                 # 1 sentence, 7 tokens, 32-dim each
print("transformer in/out shape:", tuple(tokens.shape), "->", tuple(enc(tokens).shape))
print("params:", sum(p.numel() for p in enc.parameters()))
```

Output:

```
row sums: [1. 1. 1. 1. 1. 1. 1.]
attention from "it":
   it       0.27
   cat      0.26
   sat      0.13
```
```
transformer in/out shape: (1, 7, 32) -> (1, 7, 32)
params: 17088
```

Important honesty note: **these word vectors are random numbers**, and I deliberately made "it" similar to "cat" so you can see the mechanism. This shows *how attention is computed*, not that a model learned coreference. In a trained model the vectors are learned so that such links appear naturally. (Also, a word attends strongly to itself, which is why "it" scores 0.27 on "it" and 0.26 on "cat".)

Notice that the output shape equals the input shape: 7 tokens in, 7 context-enriched tokens out.

## What makes a full Transformer

- **Multi-head attention:** several attention "views" in parallel (`nhead=4`), each able to track a different relationship (grammar, meaning, position).
- **Feed-forward layer** after attention for extra processing.
- **Residual connections + layer norm** so deep stacks train stably.
- **Positional encoding:** attention alone ignores word order, so position information is added to each token.
- **Stack many layers.** Our toy has 2 (17,088 parameters). GPT-style models have dozens of layers and billions of parameters.

Three flavours worth knowing:

| Type | Example | Good at |
|---|---|---|
| Encoder-only | BERT | understanding: classification, search, embeddings |
| Decoder-only | GPT, Claude | generating text |
| Encoder-decoder | T5 | translation, summarising |

## Real-world rules of thumb

- You will almost never train a Transformer from scratch. You use or fine-tune a pretrained one ([note 06](06-hugging-face-pretrained-models.md)) or call an LLM API.
- Attention cost grows with the **square** of the text length, which is why context windows are limited and long documents are expensive.
- Text is split into **tokens** (word pieces), not words. Prices and limits are counted in tokens.
- Decoder models generate one token at a time by predicting the next token, over and over.

## Quick check

Why does a Transformer need positional information? *(Attention treats the input as an unordered set, so "dog bites man" and "man bites dog" would look identical.)*

Next: [06 Hugging Face pretrained models](06-hugging-face-pretrained-models.md).
