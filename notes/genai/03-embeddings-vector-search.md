# Embeddings + Vector Search

An **embedding** turns text into a list of numbers (a vector) such that **similar meaning = nearby numbers**. This lets you search by *meaning* instead of exact words. It's the foundation of semantic search, recommendations, duplicate detection and RAG ([note 04](04-rag-chat-with-your-pdfs.md)).

> **Verification status:** everything below was run for real on CPU with `sentence-transformers` 6.2.0 and the free `all-MiniLM-L6-v2` model. No API key is needed.

## The idea

- Each sentence becomes a vector (this model: **384 numbers**).
- "How do I reset my password?" and "Steps to recover a forgotten login" land close together even though they share almost no words.
- **Cosine similarity** measures closeness (1 = same direction, 0 = unrelated).
- **Vector search** = embed the query, compare to every stored vector, return the top matches.

If you normalise vectors to length 1, cosine similarity is just a dot product, which is fast.

## Code

```python
import numpy as np
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
docs = ["How do I reset my password?",
        "Refund policy for cancelled orders",
        "Our office is open Monday to Friday, 9 to 5",
        "Steps to recover a forgotten login",
        "Shipping usually takes 3 to 5 business days",
        "Money-back guarantee within 30 days"]
E = model.encode(docs, normalize_embeddings=True)       # unit-length vectors => dot product = cosine similarity
print("embedding shape:", E.shape, "(6 docs x 384 numbers each)")

def search(q, k=2):
    qv = model.encode([q], normalize_embeddings=True)[0]
    sims = E @ qv
    for i in np.argsort(-sims)[:k]:
        print(f"   {sims[i]:.2f}  {docs[i]}")

for q in ["I can't log in anymore", "I want my money back", "when will my package arrive"]:
    print("Q:", q); search(q)

q = "I can't log in anymore"
print("keyword overlap for", repr(q), "->", [d for d in docs if set(q.lower().split()) & set(d.lower().split())])
```

Output:

```
embedding shape: (6, 384) (6 docs x 384 numbers each)
Q: I can't log in anymore
   0.59  Steps to recover a forgotten login
   0.51  How do I reset my password?
Q: I want my money back
   0.54  Money-back guarantee within 30 days
   0.46  Refund policy for cancelled orders
Q: when will my package arrive
   0.60  Shipping usually takes 3 to 5 business days
   0.23  Our office is open Monday to Friday, 9 to 5
keyword overlap for "I can't log in anymore" -> ['How do I reset my password?']
```

What to notice:

- **"I can't log in anymore"** found both login and password documents with zero shared meaningful words. Plain keyword search returned a single document, and only because both contain the word "I". It matched for the wrong reason and missed the best answer ("forgotten login").
- **"when will my package arrive"** found the shipping doc (0.60), and the next-best result drops to 0.23. A big drop is a good sign.
- Scores are *relative*, not percentages. 0.59 here is a strong match for this model. Different models have different scales, so tune thresholds on your own data.

## Scaling up

A NumPy dot product is fine up to roughly 100k vectors. Beyond that:

| Option | Good for |
|---|---|
| **FAISS** / **hnswlib** | fast in-process approximate search |
| **Chroma**, **LanceDB** | easy local vector DB |
| **pgvector** (Postgres extension) | you already run Postgres and want one system |
| Pinecone, Qdrant, Weaviate | managed or large-scale |

They use **approximate nearest neighbour** indexes: slightly less exact, far faster.

## Real-world rules of thumb

- **Use the same model for documents and queries.** Vectors from different models can't be compared.
- If you change the embedding model, re-embed everything.
- Embeddings capture meaning, not exact facts. Searching for an order number or product code works poorly. Combine with keyword search (**hybrid search**) for those.
- **Chunk long documents** into paragraph-sized pieces first; one vector for 50 pages blurs everything together.
- Embed once and store the vectors. Don't recompute them on every request.
- Embedding APIs (OpenAI, Voyage, Cohere, Google) are an alternative to local models and often stronger, at a per-token cost. Local models keep data on your machine.
- Evaluate with real queries: write 20 questions, note which doc should be found, and measure how often it's in the top 3.

## Quick check

Why normalise the vectors before comparing? *(Then the dot product equals cosine similarity, so it measures direction (meaning) and not text length.)*
