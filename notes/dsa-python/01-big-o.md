# Big-O and complexity (Python)

Every code block in this file was run, including the `assert` lines, on Python 3.12.

## What it measures
Big-O tells you how the work grows when the input grows. Not seconds: *shape*. Double the input, does the work double (O(n)), quadruple (O(n^2)), or barely move (O(log n))? Ignore constants and small terms: `3n + 10` is O(n).

## The common ones, fastest to slowest
| Big-O | Name | Example |
|---|---|---|
| O(1) | constant | `d[key]`, `lst[i]`, `lst.append(x)` |
| O(log n) | logarithmic | binary search, heap push |
| O(n) | linear | one loop, `sum(lst)` |
| O(n log n) | linearithmic | `sorted(lst)` |
| O(n^2) | quadratic | loop inside a loop |
| O(2^n) | exponential | all subsets |
| O(n!) | factorial | all permutations |

## Reading code
```python
def first(a):               # O(1): one step no matter the size
    return a[0]

def total(a):               # O(n): touches each item once
    s = 0
    for x in a:
        s += x
    return s

def has_duplicate_slow(a):  # O(n^2): loop inside a loop
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] == a[j]:
                return True
    return False

def has_duplicate_fast(a):  # O(n) time, O(n) extra space
    seen = set()
    for x in a:
        if x in seen:
            return True
        seen.add(x)
    return False

def halvings(n):            # O(log n): n is cut in half every step
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps

assert first([7, 8]) == 7
assert total([1, 2, 3]) == 6
assert has_duplicate_slow([1, 2, 3, 1]) and not has_duplicate_slow([1, 2, 3])
assert has_duplicate_fast([1, 2, 3, 1]) and not has_duplicate_fast([1, 2, 3])
assert halvings(1024) == 10
```

## Rules of thumb
- Sequential steps add: O(n) then O(n) is O(n). Nested steps multiply.
- Drop constants and smaller terms: `n^2 + n` is O(n^2).
- Different inputs get different letters: looping `a` then `b` is O(a + b), not O(n).
- Space counts too: a `set` of n items is O(n) space. Recursion depth counts as space.
- Best, average and worst cases differ. Interviews almost always mean **worst case**.

## From the constraint to the target complexity
Python does roughly 10^7 simple operations per second in a loop (C++ does ~10^8-10^9). Plan for less than Java.

| n in the problem | Aim for |
|---|---|
| n <= 10 | O(n!) or O(2^n) brute force is fine |
| n <= 20 | O(2^n) |
| n <= 500 | O(n^3) |
| n <= 5,000 | O(n^2) |
| n <= 10^5 | O(n log n) or O(n) |
| n <= 10^6+ | O(n) or O(log n) |

## Cost of Python operations
| Operation | Cost |
|---|---|
| `lst[i]`, `lst[i] = x`, `len(lst)` | O(1) |
| `lst.append(x)`, `lst.pop()` | O(1) amortized |
| `lst.pop(0)`, `lst.insert(0, x)` | **O(n)** (shifts everything) |
| `x in lst`, `lst.index(x)`, `lst.remove(x)` | **O(n)** |
| `lst[a:b]` (slice) | O(b - a), makes a copy |
| `x in set`, `x in dict`, `d[k]`, `s.add(x)` | O(1) average |
| `sorted(lst)`, `lst.sort()` | O(n log n) |
| `deque.append / appendleft / popleft / pop` | O(1) |
| `heapq.heappush / heappop` | O(log n) |
| `heapq.heapify(lst)` | O(n) |
| `s + t` (strings), `s[a:b]` | O(len) |
| `min(lst)`, `max(lst)`, `sum(lst)` | O(n) |

### The hidden costs that catch beginners
```python
from collections import deque
import timeit

n = 20000
setup_list = f"a = list(range({n}))"
setup_set = f"a = set(range({n}))"
# membership: list scans, set hashes
t_list = timeit.timeit("n - 1 in a", setup=setup_list + f"; n={n}", number=200)
t_set = timeit.timeit("n - 1 in a", setup=setup_set + f"; n={n}", number=200)
assert t_set < t_list            # set lookup wins by a huge margin

# popping from the front: list shifts, deque doesn't
t_pop_list = timeit.timeit("a.pop(0); a.append(0)", setup=setup_list, number=2000)
t_pop_deque = timeit.timeit("a.popleft(); a.append(0)",
                            setup=f"from collections import deque; a = deque(range({n}))", number=2000)
assert t_pop_deque < t_pop_list

# building a string with += in a loop is quadratic in theory; use join
parts = ["ab"] * 1000
assert "".join(parts) == "ab" * 1000
```
Slicing in a loop (`s = s[1:]`) is also O(n) per step, so the loop becomes O(n^2). Use an index instead.

## How to answer "what is the complexity?"
1. Say time and space separately.
2. Name what n is ("n is the array length").
3. Explain the dominant part: "one pass is O(n), the sort is O(n log n), so O(n log n) overall."

## Practice map (NeetCode 150 and Striver SDE sheet)
Big-O has no problems of its own; it is the skill behind all of them. Habit to build: before you code any problem below, write the brute-force complexity, then the target.
- Brute vs hash set: *Contains Duplicate* (NeetCode, Arrays & Hashing).
- Brute vs sort: *Valid Anagram*.
- Brute O(n^2) vs one pass: *Best Time to Buy and Sell Stock*.

> About the practice maps: every note ends with a table mapping its topic to NeetCode 150 and Striver SDE Sheet problem names. I wrote those from my own knowledge of the two lists. I could not fetch the official pages (NeetCode's list was blocked, and the Striver pages I reached gave only a partial, unordered list), so check the originals for the exact current line-up. Problem names are not verified against the official sheets; the code in these notes is verified.
>
> "350" in the request was ambiguous, so there is no separate 350 list here. NeetCode 150 and Striver are covered. Two gaps: Striver's Trie and bit-manipulation topics have no note because the 12 topics mirror the Java folder. Tell me if you meant another list (for example NeetCode 250 or a 350-problem sheet).

## Mistakes to avoid
- Calling `pop(0)` or `x in list` inside a loop and thinking it is O(1).
- Slicing inside loops without noticing the copy.
- Forgetting space: recursion depth, copies, new sets.
- Quoting average case (hash lookups) as if it were guaranteed worst case.

## Check yourself
- Why is `x in some_list` slower than `x in some_set` for big inputs?
- What is the target complexity when n is 10^5?
- Why is `pop(0)` on a list a trap and what replaces it?
