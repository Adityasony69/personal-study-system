# RAG: Chat with Your Own PDFs

**RAG = Retrieval-Augmented Generation.** LLMs don't know your private documents, and they make things up when unsure. RAG fixes both: **find the relevant passages first, then hand them to the model and say "answer from this only"**.

> **Verification status:** the PDF creation, text extraction, chunking, embedding, retrieval and prompt assembly below all ran for real (pypdf, sentence-transformers, CPU). The final *generation* call needs an API key, which I didn't have, so that step is shown as code but **was not run**.

## The pipeline

```
 PDF -> extract text -> split into chunks -> embed each chunk -> store vectors      (done once, "indexing")

 question -> embed -> find top-k similar chunks -> build prompt with them -> LLM -> answer + citations
```

## Code: indexing + retrieval (ran for real)

I generate a small 3-page "company handbook" PDF so the example is self-contained. Swap in your own file path.

```python
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# ---- make a small test PDF (stand-in for "your own PDF") ----
pages = [
 ["Acme Laptop Warranty", "All Acme laptops include a 24 month limited warranty from the purchase date.",
  "Battery packs are covered for 12 months only. Accidental damage such as drops or spills is not covered."],
 ["Returns and Refunds", "You may return an unused product within 30 days for a full refund.",
  "Refunds are issued to the original payment method within 7 business days after we receive the item."],
 ["Support Hours", "Phone support is available Monday to Friday from 9am to 6pm IST.",
  "Email support replies within one business day. There is no weekend phone support."]]
c = canvas.Canvas("handbook.pdf", pagesize=A4)
for p in pages:
    y = 800
    for line in p:
        c.drawString(60, y, line); y -= 24
    c.showPage()
c.save()

# ---- 1. load + 2. chunk ----
reader = PdfReader("handbook.pdf")
chunks = []
for pno, page in enumerate(reader.pages, 1):
    text = page.extract_text()
    for sent in [s.strip() for s in text.split("\n") if len(s.strip()) > 30]:
        chunks.append({"page": pno, "text": sent})
print(f"{len(reader.pages)} pages -> {len(chunks)} chunks")

# ---- 3. embed + 4. retrieve ----
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
E = model.encode([c["text"] for c in chunks], normalize_embeddings=True)

def retrieve(q, k=2):
    sims = E @ model.encode([q], normalize_embeddings=True)[0]
    return [(float(sims[i]), chunks[i]) for i in np.argsort(-sims)[:k]]

def build_prompt(q, hits):
    ctx = "\n".join(f"[page {h['page']}] {h['text']}" for _, h in hits)
    return (f"Answer using ONLY the context below. Cite the page. If the answer is not in the context, "
            f"say \"I don't know\".\n\n<context>\n{ctx}\n</context>\n\nQuestion: {q}")
```

Retrieval results:

```
3 pages -> 6 chunks
Q: How long is the warranty?
   0.45 p1: All Acme laptops include a 24 month limited warranty from the purchase
   0.28 p1: Battery packs are covered for 12 months only. Accidental damage such a
Q: Can I get my money back after 3 weeks?
   0.50 p2: Refunds are issued to the original payment method within 7 business da
   0.48 p2: You may return an unused product within 30 days for a full refund.
Q: Is the phone open on Sunday?
   0.58 p3: Phone support is available Monday to Friday from 9am to 6pm IST.
   0.52 p3: Email support replies within one business day. There is no weekend phone support.
Q: Who is the CEO?
   0.13 p3: Email support replies within one business day. There is no weekend pho
   0.08 p3: Phone support is available Monday to Friday from 9am to 6pm IST.
```

How to read it:

- Questions 1, 3 and the "3 weeks" question found the right page. Notice the "3 weeks" question retrieved *both* the refund-timing chunk and the 30-day-return chunk. The second (0.48) is actually the one that answers it, but it ranks just below the first (0.50). This is why you retrieve several chunks (`k` of 3 to 5) and let the LLM read them all, rather than trusting rank 1.
- **"Who is the CEO?"** isn't in the document, and scores collapse to 0.13 and 0.08. That's your signal to answer "I don't know". In real systems, add a minimum similarity cutoff (tune it on your data) so irrelevant chunks aren't sent at all.

The prompt assembled for that last question:

```
Answer using ONLY the context below. Cite the page. If the answer is not in the context, say "I don't know".

<context>
[page 3] Email support replies within one business day. There is no weekend phone support.
[page 3] Phone support is available Monday to Friday from 9am to 6pm IST.
</context>

Question: Who is the CEO?
```

## The generation step (code only, not run: needs an API key)

```python
import anthropic
client = anthropic.Anthropic()

def ask(question: str) -> str:
    hits = retrieve(question, k=3)
    resp = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=400,
        messages=[{"role": "user", "content": build_prompt(question, hits)}])
    return resp.content[0].text
```

The instruction "say I don't know" is what stops hallucination when retrieval finds nothing relevant. For the CEO question, a well-behaved model replies that it doesn't know. Test this on your own data rather than assuming.

## Where real PDFs get hard

- **Chunking is the biggest quality lever.** My toy splits by line. Real documents need paragraph-sized chunks (about 200 to 500 words) with a small overlap, so an answer isn't cut in half. Keep headings with their text.
- **Scanned PDFs** have no text layer; `extract_text()` returns nothing. You need OCR first.
- **Tables and multi-column layouts** extract badly. Check what the extractor actually produced.
- **Store metadata** (file name, page, section) with every chunk so you can cite sources. Users trust answers they can verify.
- **Scale:** past about 100k chunks, use a vector DB ([note 03](03-embeddings-vector-search.md)).
- **Improve retrieval:** hybrid keyword + vector search, then a *re-ranker* model to reorder the top 20.

## Real-world rules of thumb

- Debug retrieval first. If the right chunk isn't in what you send, no model can answer. Print the chunks.
- Build a test set of 20 questions with known answers, and track how often the right chunk is in the top 3 and how often the final answer is correct.
- Retrieved text is untrusted input. A PDF could contain "ignore your instructions"; see the prompt-injection point in [note 02](02-prompt-engineering-properly.md).
- Don't send confidential documents to a provider you haven't vetted. A local embedding model plus a provider agreement for the LLM step is a common compromise.
- Long-context models can sometimes take a whole small document directly. For a handful of short PDFs, try that before building RAG.

## Quick check

Retrieval returns nothing relevant. What should the bot do? *(Say it doesn't know. Never let the model guess without grounding.)*
