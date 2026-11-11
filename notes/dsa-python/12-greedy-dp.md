# Greedy and dynamic programming (Python)

Every code block here was run with its asserts on Python 3.12. The DP answers were also cross-checked against brute force on random inputs.

## Greedy
At each step take the choice that looks best right now and never look back. It is fast (often O(n log n) or O(n)) but only correct when the problem has the "greedy-choice property". You need a reason, not a hunch.

### Most meetings in one room
Sort by **end time**, always take the meeting that ends first.
```python
def max_meetings(intervals):
    count, last_end = 0, float("-inf")
    for start, end in sorted(intervals, key=lambda x: x[1]):
        if start >= last_end:
            count += 1
            last_end = end
    return count

def erase_overlap_intervals(intervals):   # min removals so none overlap = total - max kept
    return len(intervals) - max_meetings(intervals)

def merge_intervals(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

def insert_interval(intervals, new):
    out, i, n = [], 0, len(intervals)
    while i < n and intervals[i][1] < new[0]:
        out.append(intervals[i]); i += 1
    while i < n and intervals[i][0] <= new[1]:
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    out.append(new)
    out.extend(intervals[i:])
    return out

assert max_meetings([(1, 3), (2, 4), (3, 5), (0, 6), (5, 7), (8, 9), (5, 9)]) == 4
assert erase_overlap_intervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
assert insert_interval([], [5, 7]) == [[5, 7]]
```

### Jump games and gas stations
```python
def can_jump(nums):                       # track the furthest index reachable
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True

def min_jumps(nums):                      # BFS by "layers" of reach
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps

def can_complete_circuit(gas, cost):      # start station index, or -1
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                      # can't reach i+1 from `start`: restart after i
            start, tank = i + 1, 0
    return start

def partition_labels(s):                  # cut as many pieces as possible, each letter in one piece
    last = {ch: i for i, ch in enumerate(s)}
    out, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            out.append(end - start + 1)
            start = i + 1
    return out

def is_n_straight_hand(hand, w):          # split into groups of w consecutive cards
    from collections import Counter
    count = Counter(hand)
    for card in sorted(count):
        need = count[card]
        if need:
            for c in range(card, card + w):
                if count[c] < need:
                    return False
                count[c] -= need
    return True

def assign_cookies(greed, sizes):
    greed, sizes = sorted(greed), sorted(sizes)
    i = 0
    for s in sizes:
        if i < len(greed) and s >= greed[i]:
            i += 1
    return i

assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4])
assert min_jumps([2, 3, 1, 1, 4]) == 2 and min_jumps([1]) == 0
assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
assert is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3)
assert not is_n_straight_hand([1, 2, 3, 4, 5], 4)
assert assign_cookies([1, 2, 3], [1, 1]) == 1
assert assign_cookies([1, 2], [1, 2, 3]) == 2
```

### When greedy fails
Coins `[1, 3, 4]`, make 6. Greedy takes 4 first, then 1 + 1: three coins. The answer is 3 + 3: two coins. When local best is not global best, use DP.
```python
def coin_change_greedy(coins, amount):    # WRONG in general, shown so you recognise it
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c
    return count if amount == 0 else -1

assert coin_change_greedy([1, 3, 4], 6) == 3          # greedy answer; the true best is 2
```

## Dynamic programming (DP)
DP = recursion where the same subproblems repeat, so you **store each answer once**.
Use it when you see: "count the ways", "minimum/maximum", "is it possible", and choices that overlap.

Recipe:
1. **State**: what do you need to know to describe a subproblem? (`dp[i]` = best using the first i items)
2. **Transition**: how does a state follow from smaller states?
3. **Base case**: the smallest states.
4. **Order / answer**: which cell holds the answer?

### Two ways to write it
- **Top-down (memoization)**: write the recursion, cache results (`@lru_cache`).
- **Bottom-up (tabulation)**: fill a table from small to large. No recursion-limit problems.

```python
from functools import lru_cache

def climb_stairs_memo(n):                 # ways to climb n stairs taking 1 or 2 steps
    @lru_cache(maxsize=None)
    def go(i):
        return 1 if i <= 1 else go(i - 1) + go(i - 2)
    return go(n)

def climb_stairs(n):                      # bottom-up, O(1) space: only the last two matter
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

assert climb_stairs_memo(10) == climb_stairs(10) == 89
assert climb_stairs(1) == 1 and climb_stairs(2) == 2 and climb_stairs(45) == 1836311903
```

## 1D problems
### House robber
Cannot take two neighbours. `dp[i] = max(skip i, take i) = max(dp[i-1], dp[i-2] + a[i])`.
```python
def rob(nums):
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1

def rob_circular(nums):                   # first and last are neighbours: best of two linear cases
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))

assert rob([1, 2, 3, 1]) == 4 and rob([2, 7, 9, 3, 1]) == 12 and rob([]) == 0
assert rob_circular([2, 3, 2]) == 3 and rob_circular([1, 2, 3, 1]) == 4
```

### Coin change: fewest coins
`dp[a]` = fewest coins to make amount `a`. Try each coin as the last one.
```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return -1 if dp[amount] == INF else dp[amount]

def coin_change_ways(coins, amount):      # number of combinations (order does not matter)
    dp = [1] + [0] * amount
    for c in coins:                       # coin loop OUTSIDE: avoids counting 1+2 and 2+1 twice
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]

assert coin_change([1, 3, 4], 6) == 2     # greedy gets this wrong
assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1 and coin_change([1], 0) == 0
assert coin_change_ways([1, 2, 5], 5) == 4
assert coin_change_ways([2], 3) == 0
```

### Longest increasing subsequence
```python
import bisect

def lis_n2(a):                            # dp[i] = longest ending at i, O(n^2)
    if not a:
        return 0
    dp = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

def lis(a):                               # O(n log n): tails[k] = smallest tail of an increasing run of length k+1
    tails = []
    for x in a:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)

assert lis_n2([10, 9, 2, 5, 3, 7, 101, 18]) == lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert lis([0, 1, 0, 3, 2, 3]) == 4 and lis([7, 7, 7]) == 1 and lis([]) == 0
```

### More 1D classics
```python
def word_break(s, words):
    ws = set(words)
    dp = [True] + [False] * len(s)        # dp[i]: first i chars can be split into words
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in ws for j in range(i))
    return dp[-1]

def num_decodings(s):                     # "12" -> 2 ("AB" or "L")
    if not s or s[0] == "0":
        return 0
    prev2, prev1 = 1, 1
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1

def min_cost_climbing_stairs(cost):
    a = b = 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b

def count_palindromic_substrings(s):
    n, count = len(s), 0
    for c in range(n):
        for l, r in ((c, c), (c, c + 1)):
            while l >= 0 and r < n and s[l] == s[r]:
                count += 1
                l -= 1
                r += 1
    return count

def partition_equal_subset_sum(nums):     # subset-sum with a set of reachable sums
    total = sum(nums)
    if total % 2:
        return False
    reachable = {0}
    for x in nums:
        reachable |= {r + x for r in reachable}
    return total // 2 in reachable

def integer_break(n):
    if n <= 3:
        return n - 1
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        dp[i] = max(max(j * (i - j), j * dp[i - j]) for j in range(1, i))
    return dp[n]

assert word_break("leetcode", ["leet", "code"]) and not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
assert num_decodings("12") == 2 and num_decodings("226") == 3 and num_decodings("06") == 0
assert min_cost_climbing_stairs([10, 15, 20]) == 15
assert min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
assert count_palindromic_substrings("aaa") == 6
assert partition_equal_subset_sum([1, 5, 11, 5]) and not partition_equal_subset_sum([1, 2, 3, 5])
assert integer_break(10) == 36
```

### Best time to buy and sell stock with cooldown / many transactions
```python
def max_profit_many(prices):              # unlimited transactions: take every rise
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))

def max_profit_cooldown(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)

assert max_profit_many([7, 1, 5, 3, 6, 4]) == 7
assert max_profit_cooldown([1, 2, 3, 0, 2]) == 3
```

## 2D problems
### Paths in a grid
```python
def unique_paths(m, n):                   # move only right or down
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]          # from above (old row[j]) plus from the left
    return row[-1]

def unique_paths_obstacles(grid):
    n = len(grid[0])
    dp = [0] * n
    dp[0] = 1
    for row in grid:
        for j in range(n):
            if row[j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]

def min_path_sum(grid):
    R, C = len(grid), len(grid[0])
    dp = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            if r == 0 and c == 0:
                dp[r][c] = grid[0][0]
            elif r == 0:
                dp[r][c] = dp[r][c - 1] + grid[r][c]
            elif c == 0:
                dp[r][c] = dp[r - 1][c] + grid[r][c]
            else:
                dp[r][c] = min(dp[r - 1][c], dp[r][c - 1]) + grid[r][c]
    return dp[-1][-1]

def maximal_square(matrix):               # dp = side of the biggest square ending at this corner
    best, prev = 0, [0] * (len(matrix[0]) + 1)
    for row in matrix:
        cur = [0]
        for j, ch in enumerate(row):
            cur.append(min(prev[j], prev[j + 1], cur[j]) + 1 if ch == "1" else 0)
            best = max(best, cur[-1])
        prev = cur
    return best * best

assert unique_paths(3, 7) == 28 and unique_paths(3, 2) == 3 and unique_paths(1, 1) == 1
assert unique_paths_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
assert maximal_square([list("10100"), list("10111"), list("11111"), list("10010")]) == 4
```

### Longest common subsequence
`dp[i][j]` = LCS of the first i chars of a and first j chars of b. Match: `dp[i-1][j-1] + 1`. No match: best of dropping one char.
```python
def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]

def edit_distance(a, b):                  # insert / delete / replace
    prev = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[-1]

def longest_palindromic_subsequence(s):
    return lcs(s, s[::-1])

def min_insertions_to_palindrome(s):
    return len(s) - longest_palindromic_subsequence(s)

def is_interleave(a, b, c):
    if len(a) + len(b) != len(c):
        return False
    dp = [[False] * (len(b) + 1) for _ in range(len(a) + 1)]
    dp[0][0] = True
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            if i and dp[i - 1][j] and a[i - 1] == c[i + j - 1]:
                dp[i][j] = True
            if j and dp[i][j - 1] and b[j - 1] == c[i + j - 1]:
                dp[i][j] = True
    return dp[-1][-1]

def distinct_subsequences(s, t):
    dp = [1] + [0] * len(t)
    for ch in s:
        for j in range(len(t), 0, -1):    # go backwards so each char of s is used once
            if t[j - 1] == ch:
                dp[j] += dp[j - 1]
    return dp[-1]

def is_match_regex(s, p):                 # '.' any char, '*' zero or more of the previous
    @lru_cache(maxsize=None)
    def go(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and p[j] in (s[i], ".")
        if j + 1 < len(p) and p[j + 1] == "*":
            return go(i, j + 2) or (first and go(i + 1, j))
        return first and go(i + 1, j + 1)
    return go(0, 0)

assert lcs("abcde", "ace") == 3 and lcs("abc", "def") == 0 and lcs("", "x") == 0
assert edit_distance("horse", "ros") == 3 and edit_distance("intention", "execution") == 5
assert edit_distance("", "abc") == 3
assert longest_palindromic_subsequence("bbbab") == 4
assert min_insertions_to_palindrome("mbadm") == 2
assert is_interleave("aabcc", "dbbca", "aadbbcbcac") and not is_interleave("aabcc", "dbbca", "aadbbbaccc")
assert distinct_subsequences("rabbbit", "rabbit") == 3
assert is_match_regex("aa", "a*") and is_match_regex("ab", ".*") and not is_match_regex("aa", "a")
assert is_match_regex("aab", "c*a*b") and not is_match_regex("mississippi", "mis*is*p*.")
```

### 0/1 knapsack
Each item once. `dp[w]` = best value with capacity `w`. Loop capacity **downwards** so each item is used at most once.
```python
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]

def target_sum_ways(nums, target):        # assign + or - to each number
    dp = {0: 1}
    for x in nums:
        nxt = {}
        for s, ways in dp.items():
            nxt[s + x] = nxt.get(s + x, 0) + ways
            nxt[s - x] = nxt.get(s - x, 0) + ways
        dp = nxt
    return dp.get(target, 0)

def last_stone_weight_ii(stones):
    total = sum(stones)
    reachable = {0}
    for s in stones:
        reachable |= {r + s for r in reachable}
    return min(abs(total - 2 * r) for r in reachable)

assert knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7) == 9
assert knapsack([5], [10], 4) == 0
assert target_sum_ways([1, 1, 1, 1, 1], 3) == 5
assert last_stone_weight_ii([2, 7, 4, 1, 8, 1]) == 1
```

## Cross-check against brute force
DP bugs hide easily. Compare against a slow, obviously correct version on random small inputs.
```python
import itertools
import random

random.seed(1)

def lcs_brute(a, b):                      # try every subsequence of a
    best = 0
    for r in range(len(a) + 1):
        for idx in itertools.combinations(range(len(a)), r):
            sub = [a[i] for i in idx]
            it = iter(b)
            if all(ch in it for ch in sub):       # is `sub` a subsequence of b?
                best = max(best, r)
    return best

def knapsack_brute(w, v, cap):
    best = 0
    for mask in range(1 << len(w)):
        tw = sum(w[i] for i in range(len(w)) if mask >> i & 1)
        if tw <= cap:
            best = max(best, sum(v[i] for i in range(len(w)) if mask >> i & 1))
    return best

def coin_brute(coins, amount):
    best = float("inf")
    def go(rem, used):
        nonlocal best
        if rem == 0:
            best = min(best, used)
        if rem <= 0 or used >= best:
            return
        for c in coins:
            go(rem - c, used + 1)
    go(amount, 0)
    return -1 if best == float("inf") else best

def rob_brute(a):
    best = 0
    for mask in range(1 << len(a)):
        if mask & (mask >> 1):
            continue
        best = max(best, sum(a[i] for i in range(len(a)) if mask >> i & 1))
    return best

for _ in range(200):
    a = "".join(random.choice("abc") for _ in range(random.randint(0, 7)))
    b = "".join(random.choice("abc") for _ in range(random.randint(0, 7)))
    assert lcs(a, b) == lcs_brute(a, b), (a, b)
    n = random.randint(0, 8)
    w = [random.randint(1, 6) for _ in range(n)]
    v = [random.randint(1, 9) for _ in range(n)]
    cap = random.randint(0, 15)
    assert knapsack(w, v, cap) == knapsack_brute(w, v, cap), (w, v, cap)
    coins = random.sample([1, 2, 3, 5, 7], random.randint(1, 3))
    amt = random.randint(0, 14)
    assert coin_change(coins, amt) == coin_brute(coins, amt), (coins, amt)
    arr = [random.randint(0, 9) for _ in range(random.randint(0, 9))]
    assert rob(arr) == rob_brute(arr), arr
```

## Greedy or DP?
| Clue | Pick |
|---|---|
| A sort plus a scan solves it and you can argue why | Greedy |
| Intervals, scheduling, "most / fewest" with a clean ordering | Greedy |
| Choices overlap or interact, "count the ways" | DP |
| Greedy fails on a tiny counter-example | DP |
| Constraints are small (n <= 1000-5000) with a 2D state | DP |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Greedy | Maximum Subarray, Jump Game, Jump Game II, Gas Station, Hand of Straights, Merge Triplets to Form Target Triplet, Partition Labels, Valid Parenthesis String | Assign Cookies (Fractional Knapsack / N meetings / Job Sequencing / Min Platforms style), Jump Game |
| Intervals | Insert Interval, Merge Intervals, Non-overlapping Intervals, Meeting Rooms I and II, Minimum Interval to Include Each Query | Merge Intervals |
| 1D DP | Climbing Stairs, Min Cost Climbing Stairs, House Robber I and II, Longest Palindromic Substring, Palindromic Substrings, Decode Ways, Coin Change, Maximum Product Subarray, Word Break, Longest Increasing Subsequence, Partition Equal Subset Sum | Coin Change, Word Break, Maximum Product Subarray, Longest Increasing Subsequence |
| 2D DP | Unique Paths, Longest Common Subsequence, Best Time to Buy and Sell Stock with Cooldown, Coin Change II, Target Sum, Interleaving String, Longest Increasing Path in a Matrix, Distinct Subsequences, Edit Distance, Burst Balloons, Regular Expression Matching | Unique Paths, Longest Common Subsequence, Edit Distance, Minimum Path Sum, Palindrome Partitioning II |
| Knapsack family | Partition Equal Subset Sum, Coin Change II, Target Sum | (Striver's DP series: 0/1 Knapsack, Subset Sum, Rod Cutting) |

## Mistakes to avoid
- Using greedy without a proof or counter-example check (`[1, 3, 4]` coins).
- Wrong loop direction in 1D knapsack: downward = each item once, upward = unlimited use.
- Coin combinations vs permutations: coin loop outside counts combinations.
- Not seeding the base case (`dp[0]`).
- `[[0] * n] * m` makes aliased rows. Use a list comprehension.
- Returning the wrong cell: some problems want `dp[-1]`, others `max(dp)`.
- Memoizing a function with a mutable argument (list): `lru_cache` needs hashable arguments, use indexes or tuples.

## Check yourself
- Why does greedy get coin change `[1, 3, 4]` for 6 wrong?
- What are the four parts of a DP solution?
- Why does the 0/1 knapsack loop go from high capacity to low?
