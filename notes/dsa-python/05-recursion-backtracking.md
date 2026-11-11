# Recursion and backtracking (Python)

Every code block here was run with its asserts on Python 3.12.

## Recursion
A function that calls itself on a smaller version of the problem. Every recursive function needs:
1. **Base case**: when to stop (otherwise `RecursionError`).
2. **Recursive step**: shrink the problem and call yourself.

```python
def factorial(n):
    if n <= 1:                         # base case
        return 1
    return n * factorial(n - 1)        # smaller problem

def power(x, n):                       # fast power, O(log n): halve the exponent
    if n == 0:
        return 1.0
    if n < 0:
        return 1 / power(x, -n)
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x

def sum_digits(n):
    return n if n < 10 else n % 10 + sum_digits(n // 10)

def reverse_string(s):
    return s if len(s) <= 1 else reverse_string(s[1:]) + s[0]

assert factorial(5) == 120 and factorial(0) == 1
assert power(2, 10) == 1024
assert abs(power(2.0, -2) - 0.25) < 1e-9
assert sum_digits(1234) == 10
assert reverse_string("abc") == "cba"
```

## What happens in memory
Each call gets a **stack frame** holding its variables. Calls pile up until the base case returns, then unwind. Python's default limit is about 1000 frames:
```python
import sys

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

assert sys.getrecursionlimit() >= 1000
try:
    depth(10 ** 6)
    raised = False
except RecursionError:
    raised = True
assert raised                          # too deep: Python protects itself
```
In contests you can raise it with `sys.setrecursionlimit(10**6)`, but deep recursion is better rewritten as a loop or an explicit stack.

## Slow recursion: repeated work
Naive Fibonacci recomputes the same values exponentially many times (O(2^n)). Remember answers (**memoization**) and it becomes O(n):
```python
from functools import lru_cache

def fib_slow(n):
    return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def fib_loop(n):                       # O(n) time, O(1) space
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

assert fib_slow(15) == 610
assert fib(80) == 23416728348467685
assert fib_loop(80) == fib(80)
```
This idea is the doorway to dynamic programming (note 12).

## Backtracking
Build an answer one choice at a time. **Choose, explore, un-choose.** If a path cannot work, undo the last choice and try the next one.

```
def backtrack(path):
    if path is complete:   save a COPY of it; return
    for each choice available:
        add choice to path       # choose
        backtrack(path)          # explore
        remove choice from path  # un-choose
```

### All subsets
```python
def subsets(nums):
    out, path = [], []

    def go(i):
        if i == len(nums):
            out.append(path[:])            # copy! path keeps changing
            return
        path.append(nums[i])               # take it
        go(i + 1)
        path.pop()                         # undo
        go(i + 1)                          # skip it

    go(0)
    return out

def subsets_with_duplicates(nums):         # sort, then skip repeated choices at the same level
    nums = sorted(nums)
    out, path = [], []

    def go(start):
        out.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return out

assert sorted(subsets([1, 2, 3])) == sorted([[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])
assert len(subsets(list(range(10)))) == 2 ** 10
assert sorted(subsets_with_duplicates([1, 2, 2])) == sorted([[], [1], [1, 2], [1, 2, 2], [2], [2, 2]])
```

### All permutations
```python
def permutations(nums):
    out, path, used = [], [], [False] * len(nums)

    def go():
        if len(path) == len(nums):
            out.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            go()
            path.pop()
            used[i] = False

    go()
    return out

def permutation_sequence(n, k):            # k-th permutation of 1..n, by factorial math, O(n^2)
    digits = list(range(1, n + 1))
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    k -= 1
    out = []
    for i in range(n, 0, -1):
        idx, k = divmod(k, fact[i - 1])
        out.append(str(digits.pop(idx)))
    return "".join(out)

assert sorted(permutations([1, 2, 3])) == [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
assert len(permutations([1, 2, 3, 4, 5])) == 120
assert permutation_sequence(3, 3) == "213"
assert permutation_sequence(4, 9) == "2314"
```

### Combinations that add up to a target
```python
def combination_sum(candidates, target):   # each number may be reused
    out, path = [], []

    def go(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue
            path.append(candidates[i])
            go(i, remaining - candidates[i])     # i, not i+1: reuse allowed
            path.pop()

    go(0, target)
    return out

def combination_sum2(candidates, target):  # each number used once, input has duplicates
    candidates = sorted(candidates)
    out, path = [], []

    def go(start, remaining):
        if remaining == 0:
            out.append(path[:])
            return
        for i in range(start, len(candidates)):
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            if candidates[i] > remaining:
                break
            path.append(candidates[i])
            go(i + 1, remaining - candidates[i])
            path.pop()

    go(0, target)
    return out

assert sorted(combination_sum([2, 3, 6, 7], 7)) == [[2, 2, 3], [7]]
assert sorted(combination_sum([2, 3, 5], 8)) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
assert combination_sum([2], 1) == []
assert sorted(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8)) == [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
```

### Pruning classics: N-Queens, palindrome partitions, letter combinations, word search
```python
def solve_n_queens(n):
    cols, d1, d2 = set(), set(), set()     # column, r-c diagonal, r+c diagonal
    board, out = [], []

    def go(r):
        if r == n:
            out.append(["." * c + "Q" + "." * (n - c - 1) for c in board])
            return
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue                    # pruned: this square is attacked
            cols.add(c); d1.add(r - c); d2.add(r + c); board.append(c)
            go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c); board.pop()

    go(0)
    return out

def partition_palindromes(s):
    out, path = [], []

    def go(start):
        if start == len(s):
            out.append(path[:])
            return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                path.append(piece)
                go(end)
                path.pop()

    go(0)
    return out

def letter_combinations(digits):
    if not digits:
        return []
    phone = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
             "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    out = []

    def go(i, cur):
        if i == len(digits):
            out.append(cur)
            return
        for ch in phone[digits[i]]:
            go(i + 1, cur + ch)

    go(0, "")
    return out

def word_search(board, word):
    R, C = len(board), len(board[0])

    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < R and 0 <= c < C) or board[r][c] != word[i]:
            return False
        saved, board[r][c] = board[r][c], "#"      # mark visited
        found = any(go(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = saved                        # un-choose
        return found

    return any(go(r, c, 0) for r in range(R) for c in range(C))

assert len(solve_n_queens(4)) == 2
assert [len(solve_n_queens(n)) for n in (1, 5, 6, 8)] == [1, 10, 4, 92]
assert solve_n_queens(4)[0] == [".Q..", "...Q", "Q...", "..Q."]
assert sorted(partition_palindromes("aab")) == [["a", "a", "b"], ["aa", "b"]]
assert sorted(letter_combinations("23")) == ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]
assert letter_combinations("") == []
grid = [list("ABCE"), list("SFCS"), list("ADEE")]
assert word_search(grid, "ABCCED")
assert word_search(grid, "SEE")
assert not word_search(grid, "ABCB")
```

## Complexity
| Problem | Time |
|---|---|
| Subsets | O(n * 2^n) |
| Permutations | O(n * n!) |
| Combination sum | Depends on target; exponential |
| N-Queens | Far less than n^n thanks to pruning |
Backtracking is brute force with early exits. Pruning (stopping a bad path as soon as it is bad) is what makes it usable.

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Subsets | Subsets, Subsets II | Subsets II |
| Combinations | Combination Sum, Combination Sum II | Combination Sum, Combination Sum II |
| Permutations | Permutations | Permutations, Permutation Sequence |
| Partition / strings | Palindrome Partitioning, Letter Combinations of a Phone Number, Generate Parentheses | Palindrome Partitioning |
| Grid backtracking | Word Search | Sudoku Solver |
| Board constraints | N-Queens | N-Queens |
| Fast power | Pow(x, n) | Pow(x, n) |

## Mistakes to avoid
- Appending `path` instead of `path[:]` (or `list(path)`): every stored answer ends up as the same final list.
- Forgetting to un-choose (`pop`, `used[i] = False`, restore the grid cell).
- Missing base case: `RecursionError`.
- Duplicate handling: sort first, then skip `nums[i] == nums[i-1]` **at the same level** (`i > start`).
- Mutable default arguments (`def go(path=[])`) shared across calls.

## Check yourself
- What are the three steps in a backtracking loop?
- Why must you store a copy of `path`?
- Why does memoization turn Fibonacci from O(2^n) into O(n)?
