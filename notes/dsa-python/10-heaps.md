# Heaps and priority queues (Python)

Every code block here was run with its asserts on Python 3.12.

## What a heap gives you
A structure that always hands you the **smallest** (min-heap) item fast:
- peek the min: O(1)
- push: O(log n)
- pop the min: O(log n)
Use it when you keep asking "what is the current best?" while items keep arriving. Sorting repeatedly would be O(n log n) each time.

## How it is stored
A heap is a binary tree packed into a plain list. For index `i`: children at `2i + 1` and `2i + 2`, parent at `(i - 1) // 2`. Every parent is <= its children, so `heap[0]` is always the minimum. The list is *not* fully sorted, only parent-vs-child ordered.

## `heapq` in Python
Python has only a **min-heap**, as functions that work on an ordinary list (there is no `Heap` class).
```python
import heapq

h = []
for x in (5, 1, 8, 3, 2):
    heapq.heappush(h, x)
assert h[0] == 1                         # peek
assert heapq.heappop(h) == 1 and heapq.heappop(h) == 2
assert len(h) == 3

nums = [9, 4, 7, 1, 8]
heapq.heapify(nums)                      # in place, O(n) (faster than n pushes)
assert nums[0] == 1

# max-heap trick: push negatives
mh = []
for x in (5, 1, 8):
    heapq.heappush(mh, -x)
assert -heapq.heappop(mh) == 8

# tuples compare left to right: (priority, anything)
tasks = []
heapq.heappush(tasks, (2, "write"))
heapq.heappush(tasks, (1, "plan"))
heapq.heappush(tasks, (3, "ship"))
assert heapq.heappop(tasks) == (1, "plan")

# built-ins for "top few"
assert heapq.nlargest(2, [4, 9, 1, 7]) == [9, 7]
assert heapq.nsmallest(2, [4, 9, 1, 7]) == [1, 4]
assert heapq.nlargest(1, ["aa", "b", "cccc"], key=len) == ["cccc"]
assert list(heapq.merge([1, 4, 9], [2, 3, 10])) == [1, 2, 3, 4, 9, 10]
```
If two tuples tie on the first element, Python compares the second. If that is an object that can't be compared (like a `ListNode`) you get `TypeError`. Add a tie-breaker counter: `(priority, next_id, obj)`.

## Pattern 1: the k largest items
Keep a **min-heap of size k**. Its top is the k-th largest. Anything smaller than the top can't be in the answer. O(n log k) time, O(k) space.
```python
def kth_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)             # drop the smallest of the k+1
    return h[0]

def k_closest_points(points, k):         # k points nearest the origin
    h = []
    for x, y in points:
        heapq.heappush(h, (-(x * x + y * y), x, y))   # negative distance: farthest on top
        if len(h) > k:
            heapq.heappop(h)
    return sorted([x, y] for _, x, y in h)

class KthLargest:                        # streaming version
    def __init__(self, k, nums):
        self.k, self.h = k, []
        for x in nums:
            self.add(x)

    def add(self, val):
        heapq.heappush(self.h, val)
        if len(self.h) > self.k:
            heapq.heappop(self.h)
        return self.h[0]

def last_stone_weight(stones):           # smash the two heaviest repeatedly
    h = [-s for s in stones]
    heapq.heapify(h)
    while len(h) > 1:
        a, b = -heapq.heappop(h), -heapq.heappop(h)
        if a != b:
            heapq.heappush(h, -(a - b))
    return -h[0] if h else 0

assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert k_closest_points([[1, 3], [-2, 2]], 1) == [[-2, 2]]
assert k_closest_points([[3, 3], [5, -1], [-2, 4]], 2) == [[-2, 4], [3, 3]]
kl = KthLargest(3, [4, 5, 8, 2])
assert [kl.add(x) for x in (3, 5, 10, 9, 4)] == [4, 5, 5, 8, 8]
assert last_stone_weight([2, 7, 4, 1, 8, 1]) == 1
assert last_stone_weight([]) == 0
```

## Pattern 2: top k most frequent
```python
from collections import Counter

def top_k_frequent(nums, k):
    counts = Counter(nums)
    return [x for x, _ in heapq.nlargest(k, counts.items(), key=lambda p: p[1])]

def reorganize_string(s):                # no two equal letters adjacent, or ""
    h = [(-c, ch) for ch, c in Counter(s).items()]
    heapq.heapify(h)
    out, prev = [], None
    while h:
        c, ch = heapq.heappop(h)
        out.append(ch)
        if prev:
            heapq.heappush(h, prev)      # the previous letter may be used again now
            prev = None
        if c + 1 < 0:
            prev = (c + 1, ch)
    return "".join(out) if len(out) == len(s) else ""

assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert top_k_frequent([1], 1) == [1]
r = reorganize_string("aab")
assert sorted(r) == ["a", "a", "b"] and all(r[i] != r[i + 1] for i in range(len(r) - 1))
assert reorganize_string("aaab") == ""
```

## Pattern 3: merge k sorted lists
Heap holds the current front of each list.
```python
def merge_k_sorted(arrays):
    h = [(arr[0], i, 0) for i, arr in enumerate(arrays) if arr]
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        if j + 1 < len(arrays[i]):
            heapq.heappush(h, (arrays[i][j + 1], i, j + 1))
    return out

def kth_smallest_in_sorted_matrix(matrix, k):
    h = [(row[0], r, 0) for r, row in enumerate(matrix)]
    heapq.heapify(h)
    for _ in range(k - 1):
        _, r, c = heapq.heappop(h)
        if c + 1 < len(matrix[r]):
            heapq.heappush(h, (matrix[r][c + 1], r, c + 1))
    return h[0][0]

assert merge_k_sorted([[1, 4, 7], [2, 5], [], [3, 6, 9]]) == [1, 2, 3, 4, 5, 6, 7, 9]
assert merge_k_sorted([]) == []
assert kth_smallest_in_sorted_matrix([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8) == 13
```

## Pattern 4: running median with two heaps
`small` is a max-heap of the lower half, `large` a min-heap of the upper half. Keep sizes within 1. The median sits at the tops.
```python
class MedianFinder:
    def __init__(self):
        self.small = []                  # max-heap via negatives
        self.large = []                  # min-heap

    def add_num(self, x):
        heapq.heappush(self.small, -x)
        heapq.heappush(self.large, -heapq.heappop(self.small))   # biggest of small -> large
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self):
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2

m = MedianFinder()
for x in (1, 2):
    m.add_num(x)
assert m.find_median() == 1.5
m.add_num(3)
assert m.find_median() == 2.0
for x in (10, 20, 30):
    m.add_num(x)
assert m.find_median() == 6.5            # 1,2,3,10,20,30
```

## Scheduling and "greedy with a heap"
```python
from collections import deque

def task_scheduler(tasks, n):            # least time with cooldown n between equal tasks
    counts = [-c for c in Counter(tasks).values()]
    heapq.heapify(counts)
    time = 0
    cooling = deque()                    # (ready_time, remaining_count_negative)
    while counts or cooling:
        time += 1
        if counts:
            c = heapq.heappop(counts) + 1       # run one instance (c is negative)
            if c:
                cooling.append((time + n, c))
        if cooling and cooling[0][0] == time:
            heapq.heappush(counts, cooling.popleft()[1])
    return time

def min_meeting_rooms(intervals):        # heap of end times of rooms in use
    ends = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end) # reuse the room that frees up first
        else:
            heapq.heappush(ends, end)
    return len(ends)

def connect_ropes(ropes):                # always join the two shortest
    heapq.heapify(ropes)
    cost = 0
    while len(ropes) > 1:
        a, b = heapq.heappop(ropes), heapq.heappop(ropes)
        cost += a + b
        heapq.heappush(ropes, a + b)
    return cost

assert task_scheduler(["A", "A", "A", "B", "B", "B"], 2) == 8
assert task_scheduler(["A", "A", "A", "B", "B", "B"], 0) == 6
assert task_scheduler(["A", "A", "A", "A", "A", "A", "B", "C", "D", "E", "F", "G"], 2) == 16
assert min_meeting_rooms([[0, 30], [5, 10], [15, 20]]) == 2
assert min_meeting_rooms([[7, 10], [2, 4]]) == 1
assert connect_ropes([4, 3, 2, 6]) == 29
```

## Heap sort in one sentence
Push everything, pop everything: O(n log n).
```python
def heap_sort(a):
    h = list(a)
    heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]

assert heap_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9]
```

## When to reach for a heap
| Clue | Use |
|---|---|
| "k-th largest / smallest", "top k" | size-k heap |
| "merge k sorted" | heap of fronts |
| "median of a stream" | two heaps |
| "always process the cheapest/earliest next" | min-heap (Dijkstra, scheduling) |
| Need removal of arbitrary items | heap + lazy deletion, or a sorted structure |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Size-k heap | Kth Largest Element in a Stream, Kth Largest Element in an Array, K Closest Points to Origin | Kth Largest Element in an Array |
| Simulation | Last Stone Weight, Task Scheduler | |
| Two heaps | Find Median from Data Stream | Find Median from Data Stream |
| Merge | Merge k Sorted Lists | Merge k Sorted Lists |
| Frequency | Top K Frequent Elements | Top K Frequent Elements |
| Design | Design Twitter | |

## Mistakes to avoid
- Expecting a max-heap: `heapq` is min-only. Negate numbers (or the key).
- Assuming `h` is sorted. Only `h[0]` is guaranteed; use `heappop` or `sorted(h)`.
- Calling `heappush` on a list you didn't heapify when it started non-empty.
- Tuples with un-comparable second items on ties: add a counter.
- Using a heap of size n when size k is enough.

## Check yourself
- Why a min-heap for the k largest?
- What is the cost of `heapify` vs n pushes?
- In the two-heap median, which heap holds the lower half and why store negatives?
