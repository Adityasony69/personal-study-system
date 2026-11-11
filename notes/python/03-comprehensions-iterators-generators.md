# Comprehensions, iterators, generators

## List comprehensions
A one-line way to build a list from another sequence. Read it as: "give me `expr` for each `item` in `source` (if `condition`)".

```python
nums = [1, 2, 3, 4, 5, 6]

squares = [n * n for n in nums]
evens = [n for n in nums if n % 2 == 0]
labels = ["even" if n % 2 == 0 else "odd" for n in nums]
print(squares)
print(evens)
print(labels)

names = ["  riya ", "AMAN", " zoya"]
print([n.strip().title() for n in names])
```
```text
[1, 4, 9, 16, 25, 36]
[2, 4, 6]
['odd', 'even', 'odd', 'even', 'odd', 'even']
['Riya', 'Aman', 'Zoya']
```

Note the position of `if`: a filter goes at the **end**; an if/else (choosing between two values) goes at the **front**.

Nested loops and flattening:

```python
matrix = [[1, 2, 3], [4, 5, 6]]
print([x for row in matrix for x in row])        # flatten
print([[x * 2 for x in row] for row in matrix])  # keep the shape
print([(a, b) for a in "ab" for b in (1, 2)])
```
```text
[1, 2, 3, 4, 5, 6]
[[2, 4, 6], [8, 10, 12]]
[('a', 1), ('a', 2), ('b', 1), ('b', 2)]
```

## Dict and set comprehensions
```python
words = ["apple", "kiwi", "banana", "fig"]
print({w: len(w) for w in words})
print({w for w in words if len(w) > 3} == {"apple", "kiwi", "banana"})

prices = {"tea": 20, "coffee": 40, "juice": 60}
print({k: v for k, v in prices.items() if v >= 40})
print({v: k for k, v in prices.items()})                     # invert a dict
print({k: round(v * 1.18, 2) for k, v in prices.items()})    # add 18% tax
```
```text
{'apple': 5, 'kiwi': 4, 'banana': 6, 'fig': 3}
True
{'coffee': 40, 'juice': 60}
{20: 'tea', 40: 'coffee', 60: 'juice'}
{'tea': 23.6, 'coffee': 47.2, 'juice': 70.8}
```

When **not** to use one: if you need several statements, try/except, or it no longer fits comfortably on one line, use a normal `for` loop. Readability wins.

## Iterables and iterators
- **Iterable**: anything you can loop over (list, str, dict, file, range). It can give you an iterator.
- **Iterator**: an object that hands out one item at a time with `next()`, and raises `StopIteration` when finished. It is used up after one pass.

This is what a `for` loop does behind the scenes:

```python
it = iter(["a", "b", "c"])
print(next(it))
print(next(it))
print(next(it))
try:
    next(it)
except StopIteration:
    print("done")

lst = [1, 2, 3]
print(iter(lst) is iter(lst))   # each iter() call makes a fresh iterator
```
```text
a
b
c
done
False
```

A class becomes iterable by defining `__iter__` and `__next__` (more on dunders later), but you will almost never write this by hand. Generators do the same job with far less code.

## Generators
A generator is a function that uses `yield` instead of `return`. It produces values **lazily**, one at a time, remembering where it stopped.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown(3)
print(type(gen).__name__)   # a generator object, nothing ran yet
print(next(gen), next(gen))
print(list(gen))           # the rest
print(list(gen))           # exhausted: empty
```
```text
generator
3 2
[1]
[]
```

**Why bother?** Memory. A list holds everything at once; a generator holds one item.

```python
import sys

big_list = [n * n for n in range(1_000_000)]
big_gen = (n * n for n in range(1_000_000))     # parentheses = generator expression
print(sys.getsizeof(big_list) > 1_000_000)
print(sys.getsizeof(big_gen) < 300)
print(sum(big_gen))
```
```text
True
True
333332833333500000
```

Real-world uses:
- Reading a huge file line by line without loading it all.
- Streaming rows from a database or API pages.
- Infinite sequences (IDs, retries) that you stop when you want.

```python
def read_lines(text):
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line

config = """
# comment
host=localhost

port=5432
"""
for line in read_lines(config):
    print(line)

def ids(start=1):
    n = start
    while True:          # infinite, but lazy, so it's fine
        yield n
        n += 1

gen = ids(100)
print([next(gen) for _ in range(3)])
```
```text
host=localhost
port=5432
[100, 101, 102]
```

Generator expressions work nicely inside functions that consume iterables, with no extra brackets:

```python
nums = [3, 8, 1, 9]
print(sum(n * 2 for n in nums))
print(any(n > 8 for n in nums), all(n > 0 for n in nums))
print(max((len(w), w) for w in ["aa", "b", "cccc"]))
```
```text
42
True True
(4, 'cccc')
```

## Handy iteration tools
```python
from itertools import islice, chain

print(list(islice(range(100), 5)))              # first 5 of anything
print(list(chain([1, 2], [3], (4, 5))))         # join iterables
print(list(zip("abc", [1, 2, 3])))
print(list(enumerate("ab", start=1)))
print(list(reversed([1, 2, 3])), sorted("cab"))
```
```text
[0, 1, 2, 3, 4]
[1, 2, 3, 4, 5]
[('a', 1), ('b', 2), ('c', 3)]
[(1, 'a'), (2, 'b')]
[3, 2, 1] ['a', 'b', 'c']
```

## Remember
- Comprehension = build a whole collection now. Generator = produce items as needed.
- A generator can only be consumed once. Need it twice? Make a list, or call the function again.
- `yield` turns a function into a generator; `return` inside just ends it.
