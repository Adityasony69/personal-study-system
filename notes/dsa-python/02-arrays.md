# Arrays (Python lists): prefix sums and Kadane

Every code block here was run with its asserts on Python 3.12.

## Why arrays come first
Most interview problems are an array in disguise. A Python `list` is a dynamic array: O(1) index, O(1) amortized append, O(n) insert/delete in the middle.

## Basic moves
```python
def reverse_in_place(a):
    l, r = 0, len(a) - 1
    while l < r:
        a[l], a[r] = a[r], a[l]      # Python swaps without a temp variable
        l += 1
        r -= 1

def rotate_right(a, k):              # rotate by k places, in place
    n = len(a)
    k %= n
    a.reverse()                      # reverse all, then reverse the two parts
    a[:k] = reversed(a[:k])
    a[k:] = reversed(a[k:])

def second_largest(a):
    first = second = float("-inf")
    for x in a:
        if x > first:
            first, second = x, first
        elif first > x > second:
            second = x
    return second

def move_zeros_to_end(a):            # keeps order of the non-zero items
    write = 0
    for read in range(len(a)):
        if a[read] != 0:
            a[write], a[read] = a[read], a[write]
            write += 1

a = [1, 2, 3, 4]; reverse_in_place(a); assert a == [4, 3, 2, 1]
a = [1, 2, 3, 4, 5, 6, 7]; rotate_right(a, 3); assert a == [5, 6, 7, 1, 2, 3, 4]
a = [1, 2]; rotate_right(a, 5); assert a == [2, 1]
assert second_largest([5, 9, 2, 9, 7]) == 7
assert second_largest([3, 1]) == 1
a = [0, 1, 0, 3, 12]; move_zeros_to_end(a); assert a == [1, 3, 12, 0, 0]
```

## Prefix sums
`prefix[i]` = sum of the first `i` items. Then any range sum is one subtraction: `sum(a[l..r]) = prefix[r+1] - prefix[l]`. Build once O(n), answer each query in O(1).

```python
from itertools import accumulate

def build_prefix(a):
    return [0] + list(accumulate(a))

def range_sum(prefix, l, r):          # inclusive l..r
    return prefix[r + 1] - prefix[l]

def product_except_self(a):           # no division, O(n)
    n = len(a)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left *= a[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= a[i]
    return out

p = build_prefix([2, 4, 6, 8, 10])
assert p == [0, 2, 6, 12, 20, 30]
assert range_sum(p, 1, 3) == 18
assert range_sum(p, 0, 4) == 30
assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
```

## Subarrays with sum k: prefix sum plus a dict
Idea: if the running sum now is `s` and an earlier running sum was `s - k`, the stretch between them sums to `k`. Count how often each running sum has appeared. Works with negatives (unlike a sliding window).

```python
def subarray_sum_equals_k(a, k):
    seen = {0: 1}                      # the empty prefix
    running = count = 0
    for x in a:
        running += x
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return count

assert subarray_sum_equals_k([1, 1, 1], 2) == 2
assert subarray_sum_equals_k([1, 2, 3], 3) == 2
assert subarray_sum_equals_k([1, -1, 0], 0) == 3
assert subarray_sum_equals_k([], 0) == 0
```

## Kadane's algorithm: largest subarray sum
At each item choose: extend the subarray so far, or start fresh here. If the sum so far is negative it only hurts, so drop it.

```python
def max_subarray(a):
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def max_subarray_with_indices(a):
    best, cur, start, bs, be = a[0], a[0], 0, 0, 0
    for i in range(1, len(a)):
        if cur < 0:
            cur, start = a[i], i
        else:
            cur += a[i]
        if cur > best:
            best, bs, be = cur, start, i
    return best, bs, be

def max_product_subarray(a):          # track max AND min: a negative flips them
    best = cur_max = cur_min = a[0]
    for x in a[1:]:
        cands = (x, cur_max * x, cur_min * x)
        cur_max, cur_min = max(cands), min(cands)
        best = max(best, cur_max)
    return best

assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([-3, -1, -2]) == -1
assert max_subarray([5]) == 5
assert max_subarray_with_indices([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == (6, 3, 6)
assert max_product_subarray([2, 3, -2, 4]) == 6
assert max_product_subarray([-2, 0, -1]) == 0
assert max_product_subarray([-2, 3, -4]) == 24
```

## More one-pass patterns
```python
def max_profit(prices):               # best time to buy and sell stock, once
    lowest, best = float("inf"), 0
    for p in prices:
        lowest = min(lowest, p)
        best = max(best, p - lowest)
    return best

def majority_element(a):              # Boyer-Moore voting, O(1) space (> n/2 guaranteed)
    cand, votes = None, 0
    for x in a:
        if votes == 0:
            cand = x
        votes += 1 if x == cand else -1
    return cand

def find_duplicate(a):                # n+1 numbers in 1..n: Floyd's cycle trick
    slow = fast = a[0]
    while True:
        slow, fast = a[slow], a[a[fast]]
        if slow == fast:
            break
    slow = a[0]
    while slow != fast:
        slow, fast = a[slow], a[fast]
    return slow

def sort_colors(a):                   # Dutch national flag, one pass: 0s, 1s, 2s
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]; hi -= 1

def next_permutation(a):              # in place; wraps to the smallest if it was the last
    i = len(a) - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i >= 0:
        j = len(a) - 1
        while a[j] <= a[i]:
            j -= 1
        a[i], a[j] = a[j], a[i]
    a[i + 1:] = reversed(a[i + 1:])

def set_matrix_zeroes(m):
    rows = {i for i, r in enumerate(m) if 0 in r}
    cols = {j for r in m for j, v in enumerate(r) if v == 0}
    for i in range(len(m)):
        for j in range(len(m[0])):
            if i in rows or j in cols:
                m[i][j] = 0

def rotate_image(m):                  # 90 degrees clockwise: transpose, then reverse rows
    n = len(m)
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    for r in m:
        r.reverse()

def spiral_order(m):
    out = []
    top, bottom, left, right = 0, len(m) - 1, 0, len(m[0]) - 1
    while top <= bottom and left <= right:
        out += m[top][left:right + 1]
        top += 1
        for i in range(top, bottom + 1):
            out.append(m[i][right])
        right -= 1
        if top <= bottom:
            out += m[bottom][left:right + 1][::-1]
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                out.append(m[i][left])
            left += 1
    return out

def pascal(n):
    rows = [[1]]
    for _ in range(n - 1):
        prev = rows[-1]
        rows.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return rows

assert max_profit([7, 1, 5, 3, 6, 4]) == 5
assert max_profit([7, 6, 4, 3, 1]) == 0
assert majority_element([2, 2, 1, 1, 1, 2, 2]) == 2
assert find_duplicate([1, 3, 4, 2, 2]) == 2
assert find_duplicate([3, 1, 3, 4, 2]) == 3
a = [2, 0, 2, 1, 1, 0]; sort_colors(a); assert a == [0, 0, 1, 1, 2, 2]
a = [1, 2, 3]; next_permutation(a); assert a == [1, 3, 2]
a = [3, 2, 1]; next_permutation(a); assert a == [1, 2, 3]
a = [1, 1, 5]; next_permutation(a); assert a == [1, 5, 1]
m = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]; set_matrix_zeroes(m); assert m == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]; rotate_image(m); assert m == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
assert spiral_order([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
assert pascal(5) == [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]
```

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Hash set basics | Contains Duplicate | Find the Duplicate Number |
| Prefix / suffix products | Product of Array Except Self | Set Matrix Zeroes, Pascal's Triangle |
| Kadane | Maximum Subarray | Maximum Subarray, Maximum Product Subarray |
| One pass min/max | Best Time to Buy and Sell Stock | Best Time to Buy and Sell Stock |
| Voting | (Majority Element drill) | Majority Element, Majority Element II |
| In-place tricks | Rotate Image, Spiral Matrix, Set Matrix Zeroes, Sort Colors (drill) | Rotate Image, Sort Colors, Next Permutation |
| Intervals / merging | Merge Intervals, Insert Interval | Merge Intervals, Merge Sorted Array |
| Counting inversions (merge sort) | | Count Inversions, Reverse Pairs |

## Mistakes to avoid
- Modifying a list while looping over it with `for x in a`.
- `a = b` does not copy a list. Use `b = a[:]` or `list(a)`. Nested lists need `copy.deepcopy`, and `[[0]*3]*3` makes three references to one row; use `[[0]*3 for _ in range(3)]`.
- Kadane's start value: use `a[0]`, not 0, or all-negative arrays give a wrong answer.
- Prefix array needs length n+1 (with the leading 0), or off-by-one errors appear.
- Sliding window for sums when negatives exist: use prefix sum plus dict.

## Check yourself
- Why does `range_sum` use `prefix[r + 1] - prefix[l]`?
- In Kadane, when do you throw away the running sum?
- Why do we seed the dict with `{0: 1}` in subarray-sum-equals-k?
