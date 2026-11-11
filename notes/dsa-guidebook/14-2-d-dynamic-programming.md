# 2-D Dynamic Programming

**16 questions:** 0 Easy, 12 Medium, 4 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Same idea as 1-D DP, but the state needs two things, such as two indexes, or an index and a remaining amount.

## How to spot this pattern

- Two strings compared against each other.
- Grid paths.
- An index plus a second quantity (capacity, target, holding/not holding).

## Thinking steps (use these on every question here)

1. Write the recursion with two parameters.
2. Write in words what dp[i][j] means before any code.
3. Find which neighbouring cells each cell depends on.
4. Fill the base row and base column first.

## Common beginner mistakes

- Off-by-one errors between string indexes and table indexes.
- Filling the table in an order where needed cells are not ready yet.

Read first: your `dsa-python` notes, file(s) 12-greedy-dp.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Unique Paths | Medium | 62 | 150 |
| 2 | Unique Paths II | Medium | 63 | 250 |
| 3 | Minimum Path Sum | Medium | 64 | 250 |
| 4 | Longest Common Subsequence | Medium | 1143 | 150 |
| 5 | Last Stone Weight II | Medium | 1049 | 250 |
| 6 | Best Time to Buy And Sell Stock With Cooldown | Medium | 309 | 150 |
| 7 | Coin Change II | Medium | 518 | 150 |
| 8 | Target Sum | Medium | 494 | 150 |
| 9 | Interleaving String | Medium | 97 | 150 |
| 10 | Stone Game | Medium | 877 | 250 |
| 11 | Stone Game II | Medium | 1140 | 250 |
| 12 | Edit Distance | Medium | 72 | 150 |
| 13 | Longest Increasing Path In a Matrix | Hard | 329 | 150 |
| 14 | Distinct Subsequences | Hard | 115 | 150 |
| 15 | Burst Balloons | Hard | 312 | 150 |
| 16 | Regular Expression Matching | Hard | 10 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Medium questions

### 1. Unique Paths  [Medium]

- **Find it:** LeetCode #62, search "Unique Paths"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You can only move right or down.
- **First step:** paths(cell) = paths(cell above) + paths(cell to the left).
- **If stuck:** The first row and first column are all 1; one row of memory is enough.

### 2. Unique Paths II  [Medium]

- **Find it:** LeetCode #63, search "Unique Paths II"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Same grid with blocked cells.
- **First step:** A blocked cell has 0 paths.
- **If stuck:** Same formula; be careful with the first row/column after an obstacle.

### 3. Minimum Path Sum  [Medium]

- **Find it:** LeetCode #64, search "Minimum Path Sum"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Cheapest path moving right/down.
- **First step:** cost(cell) = grid value + min(cost above, cost left).
- **If stuck:** Fill row by row; you can reuse the grid itself.

### 4. Longest Common Subsequence  [Medium]

- **Find it:** LeetCode #1143, search "Longest Common Subsequence"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Compare two strings character by character.
- **First step:** dp[i][j] = LCS of the first i chars of one and first j chars of the other.
- **If stuck:** If the chars match: 1 + dp[i-1][j-1]; otherwise max(dp[i-1][j], dp[i][j-1]).

### 5. Last Stone Weight II  [Medium]

- **Find it:** LeetCode #1049, search "Last Stone Weight II"
- **Lists:** NeetCode 250
- **Notice:** Smashing stones = splitting them into two piles and taking the difference.
- **First step:** You want two piles with sums as close as possible.
- **If stuck:** Subset-sum DP up to total // 2; answer = total - 2 * best reachable sum.

### 6. Best Time to Buy And Sell Stock With Cooldown  [Medium]

- **Find it:** LeetCode #309, search "Best Time to Buy And Sell Stock With Cooldown"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** After selling you must wait one day.
- **First step:** Define states: holding a stock, just sold, resting.
- **If stuck:** Write how each state today comes from the states yesterday; three variables are enough.

### 7. Coin Change II  [Medium]

- **Find it:** LeetCode #518, search "Coin Change II"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Count COMBINATIONS (order does not matter).
- **First step:** dp[a] = number of ways to make amount a.
- **If stuck:** Put the coin loop OUTSIDE and the amount loop inside: dp[a] += dp[a - coin].

### 8. Target Sum  [Medium]

- **Find it:** LeetCode #494, search "Target Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Each number gets + or -.
- **First step:** Recursion on (index, current sum) with memoization.
- **If stuck:** Or: it becomes "count subsets with sum (total + target) / 2".

### 9. Interleaving String  [Medium]

- **Find it:** LeetCode #97, search "Interleaving String"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** s3 must be built by taking characters in order from s1 and s2.
- **First step:** dp[i][j] = can the first i of s1 and first j of s2 build the first i+j of s3?
- **If stuck:** It is true if the next char of s3 matches s1[i-1] with dp[i-1][j], or matches s2[j-1] with dp[i][j-1]. Check lengths first.

### 10. Stone Game  [Medium]

- **Find it:** LeetCode #877, search "Stone Game"
- **Lists:** NeetCode 250
- **Notice:** Both players play optimally, taking from either end.
- **First step:** dp[l][r] = best score difference the current player can get on piles l..r.
- **If stuck:** Take left: piles[l] - dp[l+1][r]; take right: piles[r] - dp[l][r-1]. (There is also a one-line answer worth discovering.)

### 11. Stone Game II  [Medium]

- **Find it:** LeetCode #1140, search "Stone Game II"
- **Lists:** NeetCode 250
- **Notice:** The number of piles you may take depends on M, which grows.
- **First step:** dp(i, M) = most stones the current player gets from index i.
- **If stuck:** Using suffix sums: best = max over x in 1..2M of suffix[i] - dp(i + x, max(M, x)).

### 12. Edit Distance  [Medium]

- **Find it:** LeetCode #72, search "Edit Distance"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Three operations: insert, delete, replace.
- **First step:** dp[i][j] = edits to turn the first i chars of word1 into the first j of word2.
- **If stuck:** Chars equal: dp[i-1][j-1]; otherwise 1 + min of the three neighbours. Fill the first row and column with 0..n.

## Hard questions

### 13. Longest Increasing Path In a Matrix  [Hard]

- **Find it:** LeetCode #329, search "Longest Increasing Path In a Matrix"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Paths only go to strictly bigger neighbours, so no cycles are possible.
- **First step:** DFS from each cell returning the longest path starting there.
- **If stuck:** Memoize the result per cell; no visited set is needed.

### 14. Distinct Subsequences  [Hard]

- **Find it:** LeetCode #115, search "Distinct Subsequences"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Count the ways t appears as a subsequence of s.
- **First step:** dp[i][j] = ways to form t[j:] from s[i:].
- **If stuck:** Always: skip s[i] (dp[i+1][j]); if s[i] == t[j] also add dp[i+1][j+1].

### 15. Burst Balloons  [Hard]

- **Find it:** LeetCode #312, search "Burst Balloons"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Choosing which balloon to burst FIRST breaks the problem apart badly.
- **First step:** Think about which balloon is burst LAST in a range.
- **If stuck:** dp[l][r] = max over k of dp[l][k-1] + nums[l-1]*nums[k]*nums[r+1] + dp[k+1][r]; pad the array with 1s.

### 16. Regular Expression Matching  [Hard]

- **Find it:** LeetCode #10, search "Regular Expression Matching"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** "*" applies to the character before it.
- **First step:** dp(i, j) = does s[i:] match p[j:]?
- **If stuck:** If p[j+1] is "*": either skip the pair (j+2) or, if the current chars match, consume one char of s (i+1, same j). Otherwise both must match and move on.
