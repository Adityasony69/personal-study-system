# Embeddings and vector search

An **embedding** turns a piece of text (or an image, song, product) into a list of numbers such that **things with similar meaning get similar numbers**. Then "find related things" becomes "find nearby points". This powers semantic search, "similar products", recommendations (note 14) and RAG, the "chat with your PDFs" pattern used with LLMs.

## Run a real embedding model
`sentence-transformers` with the small free model `all-MiniLM-L6-v2` (about 90 MB, downloads on first use, runs on a normal laptop CPU):

```python
from sentence_transformers import SentenceTransformer   # python -m pip install sentence-transformers
import numpy as np
model = SentenceTransformer("all-MiniLM-L6-v2")
docs = ["How do I reset my password?",
        "Steps to change your login credentials",
        "Best biryani places in Jalandhar",
        "My account is locked and I can't sign in"]
vecs = model.encode(docs, normalize_embeddings=True)
print("shape:", vecs.shape, "first 5 numbers:", np.round(vecs[0][:5], 3))
q = model.encode(["forgot password"], normalize_embeddings=True)[0]
for score, d in sorted(zip(vecs @ q, docs), reverse=True):
    print(f"{score:.3f}  {d}")
```
```
shape: (4, 384) first 5 numbers: [ 0.007 -0.063 -0.072 -0.032 -0.043]
0.779  How do I reset my password?
0.598  My account is locked and I can't sign in
0.440  Steps to change your login credentials
-0.012  Best biryani places in Jalandhar
```

- Each sentence became **384 numbers**. Single numbers mean nothing alone; only the overall direction matters.
- `vecs @ q` is cosine similarity (because the vectors were normalized): 1 is same meaning, 0 is unrelated.
- "My account is locked and I can't sign in" scored 0.598 for "forgot password" while sharing **no words** with it. Keyword search (BM25, note 13) would score it 0. That is the whole point of semantic search.
- Biryani scored about 0, correctly unrelated.
- Small models are imperfect: "change your login credentials" arguably deserved second place. Bigger models do better; always test on your own data.

## Where embeddings come from
A neural network is trained on huge numbers of pairs that should be close (a question and its answer, a title and its article) and pairs that should be far apart. Over time it learns to place meanings in a 384-dimensional (or 768, 1536, ...) space. You do not train one yourself; you pick a pre-trained model.

## Vector search at scale
Comparing a query with every document (`vecs @ q`) is fine up to maybe 100,000 items. Beyond that, a **vector database** or index finds nearest neighbours approximately but very fast:

- Libraries: FAISS, hnswlib.
- Databases: PostgreSQL with `pgvector`, Chroma, Qdrant, Pinecone, Weaviate.

Start with plain NumPy, move to `pgvector` or Chroma when it gets big.

## RAG in one picture
How "ask questions about your notes" apps work:

```
1. Split your documents into chunks (a few paragraphs each)
2. Embed every chunk, store vectors          (once)
3. User asks a question -> embed the question
4. Find the 5 nearest chunks                  (vector search)
5. Send the question + those 5 chunks to an LLM: "answer using only this text"
```

The LLM never saw your notes during training; RAG feeds the relevant bits into its context (and costs tokens, note 10). Most "AI features" in company products today are some version of this.

## Practical tips
- Use the **same model** for documents and queries. Vectors from different models are not comparable.
- Chunk size matters: too big and the meaning blurs, too small and context is lost. A few hundred tokens with some overlap is a common start.
- Best real search often combines both: BM25 for exact words (names, error codes) + embeddings for meaning ("hybrid search").

## A project that fits your roadmap
Embed all the notes in this folder, then write a script that takes a question and prints the 3 most relevant notes. That is a working semantic search over your own study material in about 30 lines, and step 1 of a RAG app.
