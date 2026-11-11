# 1-D Dynamic Programming

**17 questions:** 3 Easy, 13 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Break the problem into smaller versions of itself and store each answer so it is computed once.

## How to spot this pattern

- Words like: number of ways, minimum cost, maximum profit, can you reach.
- A choice at each step that affects later steps.
- Brute force recursion repeats the same sub-question many times.

## Thinking steps (use these on every question here)

1. Write the recursive brute force first.
2. Name the state: what changes between calls? (usually one index or one amount)
3. Add a memo dictionary.
4. Only then turn it into a table filled in order.
5. Often the table can shrink to two or three variables.

## Common beginner mistakes

- Jumping straight to the table without understanding the recursion.
- Wrong base cases.

Read first: your `dsa-python` notes, file(s) 12-greedy-dp.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Climbing Stairs | Easy | 70 | 150 |
| 2 | Min Cost Climbing Stairs | Easy | 746 | 150 |
| 3 | N-th Tribonacci Number | Easy | 1137 | 250 |
| 4 | House Robber | Medium | 198 | 150 |
| 5 | House Robber II | Medium | 213 | 150 |
| 6 | Longest Palindromic Substring | Medium | 5 | 150 |
| 7 | Palindromic Substrings | Medium | 647 | 150 |
| 8 | Decode Ways | Medium | 91 | 150 |
| 9 | Coin Change | Medium | 322 | 150 |
| 10 | Maximum Product Subarray | Medium | 152 | 150 |
| 11 | Word Break | Medium | 139 | 150 |
| 12 | Longest Increasing Subsequence | Medium | 300 | 150 |
| 13 | Partition Equal Subset Sum | Medium | 416 | 150 |
| 14 | Combination Sum IV | Medium | 377 | 250 |
| 15 | Perfect Squares | Medium | 279 | 250 |
| 16 | Integer Break | Medium | 343 | 250 |
| 17 | Stone Game III | Hard | 1406 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Climbing Stairs  [Easy]

- **Find it:** LeetCode #70, search "Climbing Stairs"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** To reach step n you came from step n-1 or n-2.
- **First step:** Write ways(n) in terms of smaller steps.
- **If stuck:** It is the Fibonacci pattern; keep just the last two values.

### 2. Min Cost Climbing Stairs  [Easy]

- **Find it:** LeetCode #746, search "Min Cost Climbing Stairs"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Same steps as Climbing Stairs, minimising cost.
- **First step:** cost to reach step i = min of the two ways to arrive.
- **If stuck:** dp[i] = cost[i] + min(dp[i-1], dp[i-2]); the answer is the min of the last two.

### 3. N-th Tribonacci Number  [Easy]

- **Find it:** LeetCode #1137, search "N-th Tribonacci Number"
- **Lists:** NeetCode 250
- **Notice:** Each value is the sum of the previous three.
- **First step:** Start from the three base values.
- **If stuck:** Keep three variables and roll them forward.

## Medium questions

### 4. House Robber  [Medium]

- **Find it:** LeetCode #198, search "House Robber"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You cannot rob two neighbouring houses.
- **First step:** At each house: rob it (and skip the previous one) or skip it.
- **If stuck:** dp[i] = max(dp[i-1], dp[i-2] + nums[i]); two variables are enough.

### 5. House Robber II  [Medium]

- **Find it:** LeetCode #213, search "House Robber II"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Houses are in a circle, so the first and last are neighbours.
- **First step:** You can never rob both the first and the last.
- **If stuck:** Run House Robber twice: once without the first house, once without the last; take the max.

### 6. Longest Palindromic Substring  [Medium]

- **Find it:** LeetCode #5, search "Longest Palindromic Substring"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A palindrome mirrors around its centre.
- **First step:** Treat every index (and every gap between indexes) as a centre.
- **If stuck:** Expand outward while the two ends match; remember the longest.

### 7. Palindromic Substrings  [Medium]

- **Find it:** LeetCode #647, search "Palindromic Substrings"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Same expand-around-centre idea, but count.
- **First step:** 2n - 1 centres: each letter and each gap.
- **If stuck:** Every successful expansion step is one more palindrome.

### 8. Decode Ways  [Medium]

- **Find it:** LeetCode #91, search "Decode Ways"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** At each position you can take one digit or two digits.
- **First step:** ways(i) depends on ways(i+1) and ways(i+2).
- **If stuck:** One digit is valid if it is not "0"; two digits are valid if between 10 and 26.

### 9. Coin Change  [Medium]

- **Find it:** LeetCode #322, search "Coin Change"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Fewest coins to make an amount; greedy fails for some coin sets.
- **First step:** dp[a] = fewest coins for amount a.
- **If stuck:** dp[a] = 1 + min(dp[a - coin]) over all coins; start with dp[0] = 0 and infinity elsewhere.

### 10. Maximum Product Subarray  [Medium]

- **Find it:** LeetCode #152, search "Maximum Product Subarray"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A negative number can turn the smallest product into the largest.
- **First step:** Track BOTH the max and the min product ending at each position.
- **If stuck:** New max and min come from: the number itself, number * old max, number * old min.

### 11. Word Break  [Medium]

- **Find it:** LeetCode #139, search "Word Break"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Can the string be cut into dictionary words?
- **First step:** dp[i] = can the first i characters be segmented?
- **If stuck:** dp[i] is true if some j has dp[j] true and s[j:i] in the dictionary. dp[0] = true.

### 12. Longest Increasing Subsequence  [Medium]

- **Find it:** LeetCode #300, search "Longest Increasing Subsequence"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A subsequence can skip elements.
- **First step:** dp[i] = length of the longest increasing subsequence ending at i.
- **If stuck:** Look at all j < i with nums[j] < nums[i]. Faster: keep a "tails" list and binary search.

### 13. Partition Equal Subset Sum  [Medium]

- **Find it:** LeetCode #416, search "Partition Equal Subset Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Two equal halves means: find a subset with sum = total / 2.
- **First step:** If the total is odd, answer false immediately.
- **If stuck:** Keep a set (or boolean array) of reachable sums; for each number add it to every existing sum (go backwards in an array).

### 14. Combination Sum IV  [Medium]

- **Find it:** LeetCode #377, search "Combination Sum IV"
- **Lists:** NeetCode 250
- **Notice:** Order matters here, so it is counting sequences.
- **First step:** dp[t] = number of ways to make total t.
- **If stuck:** dp[t] = sum of dp[t - num] for every num; dp[0] = 1.

### 15. Perfect Squares  [Medium]

- **Find it:** LeetCode #279, search "Perfect Squares"
- **Lists:** NeetCode 250
- **Notice:** Fewest squares that sum to n: Coin Change with squares as coins.
- **First step:** dp[i] = fewest squares for i.
- **If stuck:** dp[i] = 1 + min(dp[i - s*s]) for all s*s <= i.

### 16. Integer Break  [Medium]

- **Find it:** LeetCode #343, search "Integer Break"
- **Lists:** NeetCode 250
- **Notice:** Split n into at least two parts to maximise the product.
- **First step:** dp[i] = best product for i.
- **If stuck:** Try every first cut j: max(j * (i - j), j * dp[i - j]).

## Hard questions

### 17. Stone Game III  [Hard]

- **Find it:** LeetCode #1406, search "Stone Game III"
- **Lists:** NeetCode 250
- **Notice:** Two players both play their best; think in "score difference".
- **First step:** dp[i] = best (my score - opponent score) starting at stone i.
- **If stuck:** Try taking 1, 2 or 3 stones: taken sum - dp[i + k]; the sign of dp[0] decides the winner.
