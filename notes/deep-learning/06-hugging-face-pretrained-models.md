# Hugging Face Pretrained Models

**Hugging Face** is the "GitHub of models". The `transformers` library lets you download a model trained by someone else on huge data and use it in a few lines. For most real projects this is the right starting point: no training, no GPU.

## Setup

```bash
pip install transformers torch
```

The first run downloads the model (about 250 MB for the small ones below) into a local cache; later runs are instant. It works offline once cached.

## Code: three things worth knowing

```python
from transformers import pipeline, AutoTokenizer

# 1. Ready-made task: sentiment analysis
clf = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", device=-1)
for r in clf(["The delivery was fast and the packaging was great.",
              "Support never replied and the app keeps crashing.",
              "It's okay, nothing special."]):
    print(r["label"], round(r["score"], 3))

# 2. Zero-shot: classify into labels the model was never trained on
zs = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli", device=-1)
r = zs("My card was charged twice for one order", candidate_labels=["billing", "shipping", "technical issue"])
print(list(zip(r["labels"], [round(s, 2) for s in r["scores"]])))

# 3. Look at the tokenizer
tok = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
print(tok.tokenize("Unbelievably good!"), tok("Unbelievably good!")["input_ids"])
```

Output (transformers 5.22, CPU):

```
POSITIVE 1.0
NEGATIVE 0.998
NEGATIVE 0.819
[('billing', 0.41), ('shipping', 0.33), ('technical issue', 0.26)]
['un', '##bel', '##ie', '##va', '##bly', 'good', '!'] [101, 4895, 8671, 2666, 3567, 6321, 2204, 999, 102]
```

(`device=-1` means CPU; `device=0` would use the first GPU.)

## What the output teaches

- **Sentiment:** the first two are clear-cut. The third, "It's okay, nothing special.", came back **NEGATIVE at 0.819**. This model only knows positive and negative, so it has no "neutral" and was forced to choose. A pretrained model has a fixed world view; check it on *your* kind of text.
- **Zero-shot:** it picked "billing" correctly with no training, but with only 41% confidence against 33% for "shipping". With a small model, the winner is right but the margin is thin. Use a larger model or clearer labels if you need confidence.
- **Tokenizer:** "Unbelievably" is split into `un ##bel ##ie ##va ##bly` (word pieces; `##` marks a continuation). The numbers are token IDs. IDs 101 and 102 are the special `[CLS]` and `[SEP]` markers added around every input.

## Choosing and using models

- Browse huggingface.co/models, filter by **task** (text-classification, summarization, translation, feature-extraction...) and sort by downloads.
- Read the model card: what data it was trained on, its licence, and its limits.
- Smaller models (DistilBERT, MiniLM) run fine on a laptop CPU. Large generative models need a GPU or an API.
- **Fine-tune** when a general model isn't accurate enough on your data: you need a few hundred to a few thousand labelled examples, and `Trainer` handles the loop.
- Other common pipelines: `"summarization"`, `"translation_en_to_fr"`, `"ner"` (find names and places), `"question-answering"`, `"feature-extraction"` (embeddings, see the GenAI notes).

## Real-world rules of thumb

- Pin the model name (and ideally the revision) in your code, so results don't change under you.
- Evaluate on a labelled sample of your own data before trusting a pretrained model.
- Pretrained models inherit biases from their training data. Be careful in hiring, credit, moderation and similar uses.
- Models from the Hub are code plus weights from strangers. Prefer well-known authors and the `safetensors` format, and don't enable `trust_remote_code=True` for repos you don't trust.
- Set a `HF_TOKEN` for faster downloads if you hit rate limits.

## Quick check

The model said NEGATIVE for "It's okay, nothing special." Is that a bug? *(No. The model only has two classes. The fix is a model with a neutral class, or a threshold on the score.)*

Back to the [deep learning notes](01-neural-network-from-scratch-numpy.md) or on to the GenAI notes.
