# Sorting and binary search (Python)

Every code block here was run with its asserts on Python 3.12.

## Sorting in real code
Never hand-write a sort in real work. Python's `sorted()` / `list.sort()` use **Timsort**: O(n log n) worst case, O(n) on nearly-sorted data, and **stable** (equal items keep their original order).
```python
words = ["banana", "kiwi", "apple", "fig"]
assert sorted(words) == ["apple", "banana", "fig", "kiwi"]
assert sorted(words, key=len) == ["fig", "kiwi", "apple", "banana"]
assert sorted(words, key=len, reverse=True) == ["banana", "apple", "kiwi", "fig"]

pairs = [(2, "b"), (1, "z"), (2, "a"), (1, "y")]
assert sorted(pairs) == [(1, "y"), (1, "z"), (2, "a"), (2, "b")]
assert sorted(pairs, key=lambda p: p[0]) == [(1, "z"), (1, "y"), (2, "b"), (2, "a")]   # stable
assert sorted(pairs, key=lambda p: (-p[0], p[1])) == [(2, "a"), (2, "b"), (1, "y"), (1, "z")]

a = [3, 1, 2]
a.sort()                       # in place, returns None
assert a == [1, 2, 3]
```
Use `key=` (a function of one item). The old `cmp=` is gone; if you must compare two items, wrap with `functools.cmp_to_key`.

## Comparison table
| Sort | Best | Average | Worst | Space | Stable |
|---|---|---|---|---|---|
| Bubble / insertion / selection | O(n) / O(n) / O(n^2) | O(n^2) | O(n^2) | O(1) | bubble, insertion yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | yes |
| Quick sort | O(n log n) | O(n log n) | O(n^2) | O(log n) | no |
| Heap sort | O(n log n) | O(n log n) | O(n log n) | O(1) | no |
| Counting sort | O(n + k) | O(n + k) | O(n + k) | O(k) | yes |
| Timsort (Python) | O(n) | O(n log n) | O(n log n) | O(n) | yes |

## Merge sort
Split in half, sort each half, merge two sorted halves.
```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:          # <= keeps it stable
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out

def count_inversions(a):                 # pairs i<j with a[i] > a[j]; merge sort in disguise
    def sort(arr):
        if len(arr) <= 1:
            return arr, 0
        mid = len(arr) // 2
        left, x = sort(arr[:mid])
        right, y = sort(arr[mid:])
        merged, i, j, cross = [], 0, 0, 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i]); i += 1
            else:
                merged.append(right[j]); j += 1
                cross += len(left) - i       # everything left in `left` is bigger than right[j]
        merged += left[i:] + right[j:]
        return merged, x + y + cross
    return sort(a)[1]

assert merge_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9]
assert merge_sort([]) == [] and merge_sort([1]) == [1]
assert count_inversions([2, 4, 1, 3, 5]) == 3
assert count_inversions([5, 4, 3, 2, 1]) == 10
assert count_inversions([1, 2, 3]) == 0
```

## Quick sort
Pick a pivot, put smaller items left and bigger right, recurse. A random pivot avoids the O(n^2) worst case on already-sorted input.
```python
import random

def quick_sort(a):
    if len(a) <= 1:
        return a
    pivot = random.choice(a)
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    more = [x for x in a if x > pivot]
    return quick_sort(less) + equal + quick_sort(more)

def quickselect(a, k):                   # k-th smallest (0-based), average O(n)
    pivot = random.choice(a)
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    if k < len(less):
        return quickselect(less, k)
    if k < len(less) + len(equal):
        return pivot
    return quickselect([x for x in a if x > pivot], k - len(less) - len(equal))

data = [random.randint(-50, 50) for _ in range(500)]
assert quick_sort(data) == sorted(data)
assert quick_sort([3, 3, 3]) == [3, 3, 3]
assert quickselect([3, 2, 1, 5, 6, 4], 1) == 2
assert all(quickselect(data, k) == sorted(data)[k] for k in (0, 100, 499))
```
(This version builds new lists, which is easier to learn. The in-place version swaps within the array to save memory.)

## Counting sort and simple sorts
```python
def counting_sort(a, max_val):           # small non-negative integers
    count = [0] * (max_val + 1)
    for x in a:
        count[x] += 1
    return [v for v in range(max_val + 1) for _ in range(count[v])]

def insertion_sort(a):                   # great for tiny or nearly-sorted data
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a

assert counting_sort([4, 2, 2, 8, 3, 3, 1], 8) == [1, 2, 2, 3, 3, 4, 8]
assert insertion_sort([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
```

## Binary search
On **sorted** data, check the middle, throw away the wrong half. O(log n): a million items takes about 20 steps.
```python
def binary_search(a, target):            # index or -1
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2             # Python ints don't overflow, no need for lo + (hi-lo)//2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

assert binary_search([1, 3, 5, 7, 9, 11], 7) == 3
assert binary_search([1, 3, 5, 7, 9, 11], 4) == -1
assert binary_search([], 1) == -1
assert binary_search([5], 5) == 0
```

### First position that is at least the target (lower bound)
The most useful variant. Answers "where would this go?", "first occurrence", and "count of x".
```python
import bisect

def lower_bound(a, target):              # first index with a[i] >= target, or len(a)
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(a, target):              # first index with a[i] > target
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def first_and_last(a, target):
    lo = lower_bound(a, target)
    if lo == len(a) or a[lo] != target:
        return [-1, -1]
    return [lo, upper_bound(a, target) - 1]

a = [1, 2, 2, 2, 3, 5]
assert lower_bound(a, 2) == 1 and upper_bound(a, 2) == 4
assert lower_bound(a, 4) == 5 and lower_bound(a, 9) == 6 and lower_bound(a, 0) == 0
assert first_and_last(a, 2) == [1, 3]
assert first_and_last(a, 4) == [-1, -1]
# Python ships these: bisect_left == lower_bound, bisect_right == upper_bound
for t in range(0, 7):
    assert lower_bound(a, t) == bisect.bisect_left(a, t)
    assert upper_bound(a, t) == bisect.bisect_right(a, t)
```

### Rotated sorted array and other "sorted-ish" searches
```python
def search_rotated(a, target):           # [4,5,6,7,0,1,2]: one half is always sorted
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:              # left half sorted
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                            # right half sorted
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

def find_min_rotated(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        else:
            hi = mid
    return a[lo]

def search_matrix(m, target):            # rows sorted, each row starts above the last row's end
    R, C = len(m), len(m[0])
    lo, hi = 0, R * C - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = m[mid // C][mid % C]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False

def single_non_duplicate(a):             # every number twice except one, array sorted
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid % 2 == 1:
            mid -= 1                     # make mid even: pairs start at even indexes
        if a[mid] == a[mid + 1]:
            lo = mid + 2
        else:
            hi = mid
    return a[lo]

def median_two_sorted(a, b):             # O(log(min(m, n))): binary search the partition
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    half = (m + n + 1) // 2
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return max(a_left, b_left)
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1

assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
assert search_rotated([1], 1) == 0
assert find_min_rotated([4, 5, 6, 7, 0, 1, 2]) == 0
assert find_min_rotated([1, 2, 3]) == 1
m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
assert search_matrix(m, 3) and not search_matrix(m, 13)
assert single_non_duplicate([1, 1, 2, 3, 3, 4, 4, 8, 8]) == 2
assert single_non_duplicate([3, 3, 7, 7, 10, 11, 11]) == 10
assert median_two_sorted([1, 3], [2]) == 2
assert median_two_sorted([1, 2], [3, 4]) == 2.5
assert median_two_sorted([], [1]) == 1
```

### Binary search on the answer
When you can't search an array but you can test "does value X work?" and the answer flips from no to yes exactly once, binary-search the value itself.
```python
import math

def koko_eating_bananas(piles, h):       # smallest speed so all piles finish within h hours
    lo, hi = 1, max(piles)
    while lo < hi:
        speed = (lo + hi) // 2
        hours = sum(math.ceil(p / speed) for p in piles)
        if hours <= h:
            hi = speed                   # works: try slower
        else:
            lo = speed + 1
    return lo

def ship_within_days(weights, days):     # smallest ship capacity
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        cap = (lo + hi) // 2
        need, load = 1, 0
        for w in weights:
            if load + w > cap:
                need += 1
                load = 0
            load += w
        if need <= days:
            hi = cap
        else:
            lo = cap + 1
    return lo

def sqrt_floor(x):
    lo, hi = 0, x
    while lo < hi:
        mid = (lo + hi + 1) // 2         # +1 when moving lo up, or the loop never ends
        if mid * mid <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo

assert koko_eating_bananas([3, 6, 7, 11], 8) == 4
assert koko_eating_bananas([30, 11, 23, 4, 20], 5) == 30
assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
assert [sqrt_floor(x) for x in (0, 1, 8, 16, 99)] == [0, 1, 2, 4, 9]
```

## The two loop styles: do not mix them
| Style | Loop | Update | Use for |
|---|---|---|---|
| Find exact | `while lo <= hi` | `lo = mid + 1` / `hi = mid - 1` | value present or not |
| Find boundary | `while lo < hi` | `lo = mid + 1` / `hi = mid` | first true / lower bound / answer search |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Plain binary search | Binary Search, Search a 2D Matrix | Search a 2D Matrix |
| Rotated array | Find Minimum in Rotated Sorted Array, Search in Rotated Sorted Array | Search in Rotated Sorted Array |
| On the answer | Koko Eating Bananas | (Aggressive cows / Allocate books style drills) |
| Hard | Median of Two Sorted Arrays, Time Based Key-Value Store | Median of Two Sorted Arrays, Single Element in a Sorted Array |
| Sorting use | Merge Intervals, Meeting Rooms | Merge Intervals, Count Inversions, Reverse Pairs |

## Mistakes to avoid
- Binary search on unsorted data.
- Infinite loop: `lo = mid` with `mid = (lo + hi) // 2` can stall. Use `mid + 1`, or round mid up.
- Off-by-one on `hi` (`len(a)` vs `len(a) - 1`) for the style you chose.
- Using `list.sort()` result: it returns `None`. `a = a.sort()` wipes your list.
- Sorting just to find the min or max: O(n log n) when `min()` is O(n).

## Check yourself
- Why is Python's `sort` called stable and why does it matter?
- Difference between `bisect_left` and `bisect_right`?
- What property must "does X work?" have for answer-search to work?
