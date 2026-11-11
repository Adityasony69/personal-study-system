# Two pointers and sliding window (Python)

Both replace a loop inside a loop with one pass: O(n^2) becomes O(n). Every code block was run with its asserts on Python 3.12.

## Two pointers
Keep two indexes and move them by a rule instead of trying every pair.

**When to think of it:** sorted array, a pair or triple to find, comparing from both ends, or rewriting an array in place.

### Opposite ends: pair with a given sum in a sorted array
Sum too small? The only way to grow it is to move the left pointer right. Too big? Move the right pointer left. Each step discards one candidate for good.
```python
def has_pair_with_sum(sorted_a, target):
    l, r = 0, len(sorted_a) - 1
    while l < r:
        s = sorted_a[l] + sorted_a[r]
        if s == target:
            return True
        if s < target:
            l += 1
        else:
            r -= 1
    return False

def two_sum_sorted(numbers, target):         # 1-indexed answer, like the LeetCode version
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]
        l, r = (l + 1, r) if s < target else (l, r - 1)
    return []

assert has_pair_with_sum([1, 3, 4, 6, 9], 10)
assert not has_pair_with_sum([1, 3, 4, 6, 9], 2)
assert two_sum_sorted([2, 7, 11, 15], 9) == [1, 2]
```

### Same direction: remove duplicates from a sorted array in place
`read` scans every item. `write` marks where the next keeper goes.
```python
def remove_duplicates(a):                    # returns the new length
    if not a:
        return 0
    write = 1
    for read in range(1, len(a)):
        if a[read] != a[read - 1]:
            a[write] = a[read]
            write += 1
    return write

a = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
k = remove_duplicates(a)
assert k == 5 and a[:k] == [0, 1, 2, 3, 4]
assert remove_duplicates([]) == 0
```

### Container with most water
Start wide, then always move the shorter line inward: the shorter line is what limits the area.
```python
def max_water(height):
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best

assert max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert max_water([1, 1]) == 1
```

### Three numbers that add to zero
Sort, fix one number, run the pair search on the rest. O(n^2).
```python
def three_sum(a):
    a = sorted(a)
    out = []
    for i in range(len(a) - 2):
        if i > 0 and a[i] == a[i - 1]:          # skip repeated first numbers
            continue
        l, r = i + 1, len(a) - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s == 0:
                out.append([a[i], a[l], a[r]])
                l += 1
                r -= 1
                while l < r and a[l] == a[l - 1]:   # skip repeated second numbers
                    l += 1
            elif s < 0:
                l += 1
            else:
                r -= 1
    return out

def four_sum(nums, target):
    nums = sorted(nums)
    out = []
    for i in range(len(nums) - 3):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, len(nums) - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, len(nums) - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s == target:
                    out.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                elif s < target:
                    l += 1
                else:
                    r -= 1
    return out

assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
assert three_sum([1, 2]) == []
assert four_sum([1, 0, -1, 0, -2, 2], 0) == [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]]
```

### Trapping rain water
Water above a bar = min(tallest bar to its left, tallest to its right) minus its own height. Two pointers keep the running maxima without extra arrays.
```python
def trap(height):
    l, r = 0, len(height) - 1
    left_max = right_max = water = 0
    while l < r:
        if height[l] < height[r]:
            left_max = max(left_max, height[l])
            water += left_max - height[l]
            l += 1
        else:
            right_max = max(right_max, height[r])
            water += right_max - height[r]
            r -= 1
    return water

assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
assert trap([4, 2, 0, 3, 2, 5]) == 9
assert trap([]) == 0
```

## Sliding window
A window is a stretch of neighbours `a[left..right]`. Slide it: add what enters on the right, remove what leaves on the left.

**When to think of it:** "subarray" or "substring" plus "longest", "shortest", "at most k" or "of size k".

### Fixed size: largest sum of any k neighbours
```python
def max_sum_of_size_k(a, k):
    s = sum(a[:k])                    # the first window
    best = s
    for i in range(k, len(a)):
        s += a[i] - a[i - k]          # one comes in, one goes out
        best = max(best, s)
    return best

assert max_sum_of_size_k([2, 1, 5, 1, 3, 2], 3) == 9
assert max_sum_of_size_k([4], 1) == 4
```

### Variable size: the template
1. Grow the window by moving `right`.
2. While the window breaks the rule, shrink it by moving `left`.
3. The window is valid: update the answer.

```python
def longest_unique_substring(s):
    last_seen = {}                    # char -> its latest index (lets left jump straight ahead)
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

def longest_unique_substring_template(s):       # same answer, textbook shrink loop
    window = set()
    left = best = 0
    for right, ch in enumerate(s):
        while ch in window:
            window.remove(s[left])
            left += 1
        window.add(ch)
        best = max(best, right - left + 1)
    return best

def shortest_subarray_sum_at_least(a, target):   # positive numbers only
    left = total = 0
    best = float("inf")
    for right, x in enumerate(a):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= a[left]
            left += 1
    return 0 if best == float("inf") else best

def character_replacement(s, k):                 # longest run after at most k changes
    count = {}
    left = best = most = 0
    for right, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        most = max(most, count[ch])
        while (right - left + 1) - most > k:     # too many letters to replace
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best

assert longest_unique_substring("abcabcbb") == 3
assert longest_unique_substring("bbbbb") == 1
assert longest_unique_substring("pwwkew") == 3
assert longest_unique_substring("") == 0
for t in ("abcabcbb", "pwwkew", "abba", ""):
    assert longest_unique_substring(t) == longest_unique_substring_template(t)
assert shortest_subarray_sum_at_least([2, 3, 1, 2, 4, 3], 7) == 2
assert shortest_subarray_sum_at_least([1, 1, 1], 10) == 0
assert character_replacement("ABAB", 2) == 4
assert character_replacement("AABABBA", 1) == 4
```

### Minimum window substring and permutation in string
```python
from collections import Counter

def min_window(s, t):                      # smallest part of s containing all of t's letters
    need = Counter(t)
    missing = len(t)
    left = 0
    best = (float("inf"), 0, 0)
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        if missing == 0:                   # window covers t: shrink
            while need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if right - left + 1 < best[0]:
                best = (right - left + 1, left, right)
            need[s[left]] += 1
            missing += 1
            left += 1
    return "" if best[0] == float("inf") else s[best[1]:best[2] + 1]

def check_inclusion(p, s):                 # does s contain a permutation of p? fixed window
    if len(p) > len(s):
        return False
    need = Counter(p)
    window = Counter(s[:len(p)])
    if window == need:
        return True
    for i in range(len(p), len(s)):
        window[s[i]] += 1
        out = s[i - len(p)]
        window[out] -= 1
        if window[out] == 0:
            del window[out]
        if window == need:
            return True
    return False

from collections import deque

def max_sliding_window(nums, k):           # monotonic deque of indexes, O(n)
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

assert min_window("ADOBECODEBANC", "ABC") == "BANC"
assert min_window("a", "aa") == ""
assert min_window("a", "a") == "a"
assert check_inclusion("ab", "eidbaooo")
assert not check_inclusion("ab", "eidboaoo")
assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
assert max_sliding_window([1], 1) == [1]
```

Why this is O(n) even with a loop inside a loop: `left` only moves forward, so in total it moves at most n times.

## Which one?
| Clue in the problem | Pattern |
|---|---|
| Sorted array, find a pair | Two pointers from both ends |
| Rewrite an array in place | Read pointer and write pointer |
| Palindrome check | Two pointers from both ends |
| Subarray or substring of size k | Fixed window |
| Longest or shortest subarray satisfying a rule | Variable window |
| Window maximum / minimum | Monotonic deque |
| Subarray sum with negative numbers | Prefix sum plus dict, not a window |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Two pointers | Valid Palindrome, Two Sum II, 3Sum, Container With Most Water, Trapping Rain Water | 3Sum, 4Sum, Trapping Rain Water, Remove Duplicates from Sorted Array, Max Consecutive Ones |
| Variable window | Longest Substring Without Repeating Characters, Longest Repeating Character Replacement, Minimum Window Substring | Longest Substring Without Repeating Characters |
| Fixed window | Permutation in String | |
| Monotonic deque | Sliding Window Maximum | Sliding Window Maximum |
| Stock (one pass) | Best Time to Buy and Sell Stock | Best Time to Buy and Sell Stock |

## Mistakes to avoid
- Two pointers from both ends on an **unsorted** array.
- Window length is `right - left + 1`, not `right - left`.
- Sliding window for sums when numbers can be negative: shrinking no longer lowers the sum.
- Forgetting to undo the outgoing item's effect before moving `left`.
- In the `last_seen` version: forgetting the `>= left` check lets `left` jump backwards (try `"abba"`).

## Check yourself
- Why is it safe to move the left pointer when the sum is too small?
- In the variable window template, when do you shrink?
- Why is the variable window O(n) and not O(n^2)?
