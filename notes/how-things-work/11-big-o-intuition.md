# Big-O intuition

**Big-O** answers one practical question: **when the data gets 10 times bigger, how much slower does my code get?** It ignores exact seconds and looks at the shape of the growth. Interviews ask about it, but the real reason to learn it is that it explains why code that was fine on 100 rows freezes on 1 million.

## The shapes you need

| Big-O | Name | Data x10 means | Everyday example |
|---|---|---|---|
| O(1) | constant | same time | Look up a key in a dict |
| O(log n) | logarithmic | a tiny bit more | Find a word in a dictionary by opening the middle, then the middle of the half, ... (binary search) |
| O(n) | linear | 10x time | Read every row once |
| O(n log n) | "sorting" | a bit over 10x | `sorted()` |
| O(n²) | quadratic | **100x time** | Compare every item with every other item |
| O(2ⁿ) | exponential | unusable | Try every possible combination |

The jump from O(n) to O(n²) is where real apps die.

## Experiment 1: `in` on a list vs a set
```python
import time, random
n = 20_000
items = list(range(n)); s = set(items); targets = random.sample(range(n), 2000)
t = time.perf_counter(); [x in items for x in targets]; print(f"list lookup x2000: {time.perf_counter()-t:.4f}s")
t = time.perf_counter(); [x in s for x in targets]; print(f"set  lookup x2000: {time.perf_counter()-t:.6f}s")
```
```
list lookup x2000: 0.1230s
set  lookup x2000: 0.000194s
```

Same question, about **600 times faster**. `x in list` checks items one by one: O(n). `x in set` jumps straight to the right spot using a hash: O(1). If you check membership inside a loop, use a set or dict.

## Experiment 2: watch O(n²) grow
Two ways to ask "does this list have a duplicate?":

```python
def has_dup_slow(a):      # compare every pair: O(n²)
    return any(a[i] == a[j] for i in range(len(a)) for j in range(i+1, len(a)))

def has_dup_fast(a):      # a set drops duplicates: O(n)
    return len(set(a)) != len(a)
```
```
n=1000: O(n^2) 0.029s   O(n) 0.00004s
n=2000: O(n^2) 0.128s   O(n) 0.00012s
n=4000: O(n^2) 0.527s   O(n) 0.00015s
```

Double the data, and the slow version takes about **4 times** longer (0.128 to 0.527). That is the n² signature. At 1 million items it would take hours. The fast one barely notices.

## How to read your own code
- One loop over the data: O(n).
- A loop inside a loop over the same data: O(n²). Look for this first.
- A hidden loop counts: `x in list`, `list.index()`, `list.remove()`, `str += ...` inside a loop, and a database query inside a loop (the "N+1 queries" bug).
- Halving the problem each step: O(log n).
- Keep only the biggest term: O(n² + n) is just O(n²).

## Practical fixes for O(n²)
| Slow pattern | Fix |
|---|---|
| `if x in some_list` inside a loop | Make `some_set = set(some_list)` once |
| Nested loop to match items from two lists | Build a dict from one list, look up from the other |
| One SQL query per row in a loop | One query with `WHERE id IN (...)` or a JOIN |
| Sorting inside a loop | Sort once outside |

## Memory has a Big-O too
Building a set to speed things up costs O(n) extra memory. That trade (more memory for less time) is the most common one in real engineering, and caching (note 24) is the same trade.

## Try it yourself
1. Re-run Experiment 2 at n=8000. Predict the time before running.
2. Find a nested loop in one of your old projects and decide whether a dict could remove it.
