# Arrays: prefix sums and Kadane

## Why arrays come first
Almost every other topic is built on them. Reading `a[i]` is O(1). Inserting or deleting in the middle is O(n) because everything after it has to shift.

## Basic moves

```java
static int maxOf(int[] a) {
    int best = a[0];                       // start from a real item, not from 0
    for (int x : a) best = Math.max(best, x);
    return best;
}

static void reverseInPlace(int[] a) {
    int l = 0, r = a.length - 1;
    while (l < r) {
        int tmp = a[l];
        a[l] = a[r];
        a[r] = tmp;
        l++;
        r--;
    }
}

static void rotateRight(int[] a, int k) {  // [1,2,3,4,5], k=2 -> [4,5,1,2,3]
    int n = a.length;
    k %= n;
    reversePart(a, 0, n - 1);              // reverse everything
    reversePart(a, 0, k - 1);              // reverse the first k
    reversePart(a, k, n - 1);              // reverse the rest
}

static void reversePart(int[] a, int l, int r) {
    while (l < r) {
        int tmp = a[l];
        a[l++] = a[r];
        a[r--] = tmp;
    }
}
```

## Prefix sums
**Problem it solves:** many "sum from index l to r" questions on the same array. A loop per question is O(n) each. With a prefix array each answer is O(1).

**Idea:** `pre[i]` = sum of the first i items. Then sum of `a[l..r]` = `pre[r + 1] - pre[l]`.

```java
static int[] buildPrefix(int[] a) {
    int[] pre = new int[a.length + 1];     // one extra slot: pre[0] = 0
    for (int i = 0; i < a.length; i++) {
        pre[i + 1] = pre[i] + a[i];
    }
    return pre;
}

static int rangeSum(int[] pre, int l, int r) {   // both ends included
    return pre[r + 1] - pre[l];
}
```

Example: `a = [2, 4, 1, 3]` gives `pre = [0, 2, 6, 7, 10]`. Sum of `a[1..2]` = `pre[3] - pre[1]` = 7 - 2 = 5.

Build is O(n) time and O(n) space. Each query is O(1).

## Subarrays with sum k: prefix sum plus a HashMap
If `pre[j] - pre[i] = k` then the items between i and j add up to k. So while walking, ask: "have I seen a prefix equal to (current - k) before?"

```java
static int countSubarraysWithSum(int[] a, int k) {
    Map<Integer, Integer> seen = new HashMap<>();   // prefix value -> how many times seen
    seen.put(0, 1);                                 // the empty prefix
    int sum = 0, count = 0;
    for (int x : a) {
        sum += x;
        count += seen.getOrDefault(sum - k, 0);
        seen.merge(sum, 1, Integer::sum);
    }
    return count;
}
```

O(n) time, O(n) space. Works with negative numbers, which a sliding window does not.

## Kadane's algorithm: largest subarray sum
**Idea:** walk left to right. At each item choose the better of "continue the run I have" or "start again here". A run with a negative total only drags the next item down, so drop it.

```java
static int maxSubarraySum(int[] a) {
    int current = a[0], best = a[0];
    for (int i = 1; i < a.length; i++) {
        current = Math.max(a[i], current + a[i]);   // extend, or start fresh at i
        best = Math.max(best, current);
    }
    return best;
}
```

Trace on `[-2, 1, -3, 4, -1, 2, 1, -5, 4]`:

| item | -2 | 1 | -3 | 4 | -1 | 2 | 1 | -5 | 4 |
|---|---|---|---|---|---|---|---|---|---|
| current | -2 | 1 | -2 | 4 | 3 | 5 | 6 | 1 | 5 |
| best | -2 | 1 | 1 | 4 | 4 | 5 | 6 | 6 | 6 |

Answer 6, from `[4, -1, 2, 1]`. O(n) time, O(1) space.

## More one-pass patterns

```java
static int maxProfit(int[] prices) {       // buy once, sell once later
    int minSoFar = prices[0], best = 0;
    for (int p : prices) {
        minSoFar = Math.min(minSoFar, p);
        best = Math.max(best, p - minSoFar);
    }
    return best;
}

static void moveZeroesToEnd(int[] a) {     // keep the order of the non-zero items
    int write = 0;
    for (int x : a)
        if (x != 0) a[write++] = x;
    while (write < a.length) a[write++] = 0;
}
```

## Mistakes to avoid
- Starting `best` at 0 in Kadane: wrong when every number is negative. Start from `a[0]`.
- Off-by-one in prefix sums. Keep the extra slot so the formula is always `pre[r + 1] - pre[l]`.
- Sums that overflow `int`. Use `long` when values or lengths are large.
- Forgetting `k %= n` when rotating by more than the length.

## Check yourself
- Why does `pre` have length n + 1?
- In Kadane, when do you start a new run?
- Why does the subarray-sum-k trick put `(0, 1)` in the map first?
