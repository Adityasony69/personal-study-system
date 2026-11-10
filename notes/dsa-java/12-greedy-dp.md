# Greedy and dynamic programming

## Greedy
At every step take the choice that looks best right now, and never go back. Fast and simple, but only correct for problems where the local best choice leads to the overall best.

### Most meetings in one room
Sort by **end** time and always take the meeting that finishes earliest. Finishing early leaves the most room for the rest.

```java
static int maxMeetings(int[][] meetings) {             // each meeting is {start, end}
    Arrays.sort(meetings, (p, q) -> Integer.compare(p[1], q[1]));
    int count = 0, lastEnd = Integer.MIN_VALUE;
    for (int[] m : meetings) {
        if (m[0] >= lastEnd) {                         // starts after the previous one ended
            count++;
            lastEnd = m[1];
        }
    }
    return count;
}
```

### Can you reach the last index?
Each value says how far you may jump from there. Track the farthest index reachable so far.

```java
static boolean canReachEnd(int[] jumps) {
    int farthest = 0;
    for (int i = 0; i < jumps.length; i++) {
        if (i > farthest) return false;                // stuck: cannot even get to i
        farthest = Math.max(farthest, i + jumps[i]);
    }
    return true;
}
```

### When greedy fails
Coins `{1, 3, 4}`, amount 6. Greedy takes 4, then 1, then 1: three coins. The best is 3 + 3: two coins. Taking the biggest coin first was a trap. When one choice changes which later choices are good, you need dynamic programming.

## Dynamic programming (DP)
DP is recursion that remembers. Use it when:

1. the problem can be built from answers to smaller versions of itself, and
2. the same smaller versions come up again and again.

How to solve a DP problem:

1. **State:** what does `dp[i]` mean, in words?
2. **Recurrence:** how do you get `dp[i]` from smaller states?
3. **Base cases:** the smallest states, filled in by hand.
4. **Order:** fill the table so everything a state needs is ready.
5. **Answer:** which cell holds the result?

### Two ways to write it

```java
static long fibMemo(int n, long[] memo) {              // top-down: recursion + remember
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    return memo[n];
}

static long fibTable(int n) {                          // bottom-up: fill a table with a loop
    if (n < 2) return n;
    long[] dp = new long[n + 1];
    dp[1] = 1;
    for (int i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    return dp[n];
}
```

Call the first one as `fibMemo(n, new long[n + 1])`. Both are O(n), down from O(2^n) for plain recursion.

## 1D problems

### Climbing stairs
You can take 1 or 2 steps. How many ways to reach step n? State: `dp[i]` = ways to reach step i. You arrive from step i - 1 or step i - 2.

```java
static int climbStairs(int n) {
    if (n <= 2) return n;
    int twoBack = 1, oneBack = 2;                      // only the last two values are needed
    for (int i = 3; i <= n; i++) {
        int current = oneBack + twoBack;
        twoBack = oneBack;
        oneBack = current;
    }
    return oneBack;
}
```

### House robber
You cannot rob two neighbouring houses. State: `dp[i]` = most money using houses up to i. Either skip house i, or rob it and add the best from two houses back.

```java
static int rob(int[] money) {
    int skipPrev = 0, best = 0;                        // best up to i-2, best up to i-1
    for (int m : money) {
        int current = Math.max(best, skipPrev + m);
        skipPrev = best;
        best = current;
    }
    return best;
}
```

### Coin change: fewest coins
State: `dp[a]` = fewest coins that make amount a. Try every coin as the last coin used.

```java
static int minCoins(int[] coins, int amount) {
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, amount + 1);                       // amount + 1 stands for "impossible"
    dp[0] = 0;
    for (int a = 1; a <= amount; a++) {
        for (int coin : coins) {
            if (coin <= a) dp[a] = Math.min(dp[a], dp[a - coin] + 1);
        }
    }
    return dp[amount] > amount ? -1 : dp[amount];
}
```

For coins `{1, 3, 4}` and amount 6 this gives 2, where greedy gave 3.

### Longest increasing subsequence
State: `dp[i]` = length of the longest increasing subsequence that ends at index i.

```java
static int longestIncreasing(int[] a) {
    int[] dp = new int[a.length];
    int best = 0;
    for (int i = 0; i < a.length; i++) {
        dp[i] = 1;                                     // the item alone
        for (int j = 0; j < i; j++) {
            if (a[j] < a[i]) dp[i] = Math.max(dp[i], dp[j] + 1);
        }
        best = Math.max(best, dp[i]);
    }
    return best;
}
```

## 2D problems
The state needs two numbers, so the table is a grid.

### Paths in a grid
Move only right or down. State: `dp[r][c]` = number of ways to reach that cell = ways from above + ways from the left.

```java
static int gridPaths(int rows, int cols) {
    int[][] dp = new int[rows][cols];
    for (int r = 0; r < rows; r++) {
        for (int c = 0; c < cols; c++) {
            if (r == 0 || c == 0) dp[r][c] = 1;        // only one way along the top row or left column
            else dp[r][c] = dp[r - 1][c] + dp[r][c - 1];
        }
    }
    return dp[rows - 1][cols - 1];
}
```

### Longest common subsequence
State: `dp[i][j]` = LCS length of the first i characters of `a` and the first j characters of `b`.

```java
static int longestCommonSubsequence(String a, String b) {
    int[][] dp = new int[a.length() + 1][b.length() + 1];      // row 0 and column 0 = empty string
    for (int i = 1; i <= a.length(); i++) {
        for (int j = 1; j <= b.length(); j++) {
            if (a.charAt(i - 1) == b.charAt(j - 1)) {
                dp[i][j] = dp[i - 1][j - 1] + 1;               // characters match: extend
            } else {
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);   // drop one character from either string
            }
        }
    }
    return dp[a.length()][b.length()];
}
```

### 0/1 knapsack
Each item can be taken once. State: `dp[w]` = best value with capacity w. Loop the capacity **downwards** so an item is not used twice.

```java
static int knapsack(int[] weight, int[] value, int capacity) {
    int[] dp = new int[capacity + 1];
    for (int i = 0; i < weight.length; i++) {
        for (int w = capacity; w >= weight[i]; w--) {
            dp[w] = Math.max(dp[w], dp[w - weight[i]] + value[i]);
        }
    }
    return dp[capacity];
}
```

## Greedy or DP?
| Sign | Likely approach |
|---|---|
| Sorting makes one choice obviously safe, and you can argue why | Greedy |
| "Count the number of ways" | DP |
| "Minimum or maximum" where choices affect later choices | DP |
| Take or skip each item | DP (knapsack style) |
| Two strings or a grid | 2D DP |

## Mistakes to avoid
- Trusting greedy without testing a small counter-example.
- Not being able to say in words what `dp[i]` means. If you cannot, the recurrence will be wrong.
- Wrong base cases, or a table that is one cell too small. Size `n + 1` is common.
- Using 0 as "not computed" in a memo when 0 is a real answer. Fill with -1 instead.
- Looping capacity upwards in 0/1 knapsack, which lets one item be taken many times.

## Check yourself
- Why does greedy fail for coins `{1, 3, 4}` and amount 6?
- What two properties make a problem suitable for DP?
- In `longestCommonSubsequence`, why is the table one row and one column bigger than the strings?
