# How a search engine ranks pages

A search engine does three jobs: **crawl** (download pages), **index** (build a lookup table of words), **rank** (sort the matching pages best first). Ranking is where the clever part is. Below is a working mini version of each in under 40 lines of Python.

## Job 1: crawl
A crawler is a program that downloads a page, finds every link on it, adds those to a to-do list, and repeats, forever. It obeys each site's `robots.txt` (try `https://lpu.in/robots.txt`), which says which pages bots may visit.

## Job 2: the inverted index
You cannot scan billions of pages for every search. Instead, build a dictionary once: **word -> which pages contain it**. That is an inverted index, the same idea as the index at the back of a textbook.

```python
import re
docs = {
    "A": "cheap flights to goa book cheap flights today",
    "B": "goa beaches guide best beaches in goa",
    "C": "python tutorial for beginners",
    "D": "flights flights flights flights goa",
}
tok = lambda s: re.findall(r"\w+", s.lower())
index = {}
for d, text in docs.items():
    for w in tok(text):
        index.setdefault(w, set()).add(d)
print("index['goa'] =", sorted(index["goa"]))
```
```
index['goa'] = ['A', 'B', 'D']
```

Now "which pages mention goa" is one dictionary lookup, not a scan.

## Job 3a: rank by text relevance (BM25)
For the query `cheap goa flights`, which page is best? **BM25** is the classic formula (used by Elasticsearch and many site-search tools). Its three ideas:

1. **More mentions of the word, higher score**, but with diminishing returns. The 4th "flights" adds less than the 1st.
2. **Rare words count more.** "goa" appears in 3 of 4 pages so it tells you little; "cheap" appears in 1 so it is a strong signal. (This is the IDF part: inverse document frequency.)
3. **Long pages are discounted**, so a page cannot win just by being huge.

```python
import math
N = len(docs); avg = sum(len(tok(t)) for t in docs.values()) / N
def bm25(query, d, k1=1.5, b=0.75):
    words = tok(docs[d]); score = 0
    for q in tok(query):
        f = words.count(q); n = len(index.get(q, ()))
        if f == 0: continue
        idf = math.log((N - n + 0.5) / (n + 0.5) + 1)
        score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * len(words) / avg))
    return score
q = "cheap goa flights"
for d in sorted(docs, key=lambda d: -bm25(q, d)):
    print(d, round(bm25(q, d), 3))
```
```
A 2.758
D 1.69
B 0.484
C 0
```

Page D repeats "flights" four times (keyword stuffing) but still loses to A, which has all three words, including the rare "cheap". That is ideas 1 and 2 at work.

## Job 3b: rank by trust (PageRank)
Text alone is easy to game. Google's original big idea: **a link is a vote**, and a vote from an important page counts more. The score flows around the link graph until it settles:

```python
links = {"A": ["B"], "B": ["A"], "C": ["A", "B"], "D": ["A"]}   # who links to whom
pr = {p: 1 / N for p in links}
for _ in range(30):
    pr = {p: 0.15 / N + 0.85 * sum(pr[q] / len(links[q]) for q in links if p in links[q]) for p in links}
print({p: round(v, 3) for p, v in pr.items()})
```
```
{'A': 0.47, 'B': 0.455, 'C': 0.037, 'D': 0.037}
```

A and B are linked to by others, so they become important. Nobody links to C or D, so they score low. The `0.85` means "a reader follows a link 85% of the time and jumps to a random page 15% of the time".

## What real search engines add
- Hundreds of signals: page speed, mobile-friendliness, freshness, your location and language, whether people click and stay or bounce back.
- **Semantic search**: matching meaning, not just words, so "forgot password" finds "reset login credentials". This uses embeddings (note 25).
- Machine-learned ranking models that combine all the signals.
- Spam fighting, because people will game every signal.

## Real-world use for you
- Adding search to a project? Start with SQLite's FTS5 or PostgreSQL full-text search; both rank with BM25-like scores. Elasticsearch or Meilisearch when it grows.
- SEO advice ("use the words people search for", "get links from good sites") is just Jobs 3a and 3b from the site owner's side.

## Try it yourself
1. Add a page E with "cheap cheap cheap" only, and see where it ranks for the query.
2. Make D link to C in the PageRank graph and see how C's score changes.
