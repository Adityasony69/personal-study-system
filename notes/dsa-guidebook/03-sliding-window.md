# Sliding Window

**9 questions:** 2 Easy, 5 Medium, 2 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A window is a continuous piece of an array or string. You grow it on the right and shrink it on the left instead of restarting each time.

## How to spot this pattern

- Words like: substring, subarray, contiguous, longest, shortest, "at most k".
- The brute force checks every start and every end.

## Thinking steps (use these on every question here)

1. Decide what makes the window valid.
2. Grow the right side one step at a time, updating your counts.
3. While the window is invalid (or can be made smaller), move the left side.
4. Update the answer at the right moment (after fixing for longest, while valid for shortest).

## Common beginner mistakes

- Using a sliding window when numbers can be negative (use prefix sums there).
- Forgetting to remove the left element from your counts when shrinking.

Read first: your `dsa-python` notes, file(s) 04-two-pointers-sliding-window.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Contains Duplicate II | Easy | 219 | 250 |
| 2 | Best Time to Buy And Sell Stock | Easy | 121 | 150 |
| 3 | Longest Substring Without Repeating Characters | Medium | 3 | 150 |
| 4 | Longest Repeating Character Replacement | Medium | 424 | 150 |
| 5 | Permutation In String | Medium | 567 | 150 |
| 6 | Minimum Size Subarray Sum | Medium | 209 | 250 |
| 7 | Find K Closest Elements | Medium | 658 | 250 |
| 8 | Minimum Window Substring | Hard | 76 | 150 |
| 9 | Sliding Window Maximum | Hard | 239 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Contains Duplicate II  [Easy]

- **Find it:** LeetCode #219, search "Contains Duplicate II"
- **Lists:** NeetCode 250
- **Notice:** Duplicates must be at most k apart.
- **First step:** You only care about the last k elements.
- **If stuck:** Keep a set of the current window (size <= k) or a dictionary of value -> last index.

### 2. Best Time to Buy And Sell Stock  [Easy]

- **Find it:** LeetCode #121, search "Best Time to Buy And Sell Stock"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** One buy, then one sell later.
- **First step:** For each day, what is the best day before it to have bought?
- **If stuck:** Track the lowest price so far and the best (price - lowest) as you walk once.

## Medium questions

### 3. Longest Substring Without Repeating Characters  [Medium]

- **Find it:** LeetCode #3, search "Longest Substring Without Repeating Characters"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** "Longest substring with a condition" signals a sliding window.
- **First step:** Grow the window to the right; keep a set of characters inside it.
- **If stuck:** When the new character is already inside, shrink from the left until it is gone.

### 4. Longest Repeating Character Replacement  [Medium]

- **Find it:** LeetCode #424, search "Longest Repeating Character Replacement"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A window is valid when (window length - count of its most common letter) <= k.
- **First step:** Keep letter counts for the window.
- **If stuck:** Grow right; if the window is invalid, move left by one. Track the best length.

### 5. Permutation In String  [Medium]

- **Find it:** LeetCode #567, search "Permutation In String"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A permutation has the same letter counts, and the same length.
- **First step:** Use a fixed-size window of len(s1) sliding over s2.
- **If stuck:** Compare the 26 counts of the window with the counts of s1; update counts as one letter enters and one leaves.

### 6. Minimum Size Subarray Sum  [Medium]

- **Find it:** LeetCode #209, search "Minimum Size Subarray Sum"
- **Lists:** NeetCode 250
- **Notice:** All numbers are positive, so growing a window only increases the sum.
- **First step:** Grow right until the sum reaches the target.
- **If stuck:** Then shrink from the left while it still reaches the target, recording the shortest length.

### 7. Find K Closest Elements  [Medium]

- **Find it:** LeetCode #658, search "Find K Closest Elements"
- **Lists:** NeetCode 250
- **Notice:** The answer is a contiguous block of k elements in the sorted array.
- **First step:** Simple way: two pointers at both ends, drop the farther one until k remain.
- **If stuck:** Faster: binary search for the left edge of the block, comparing x - arr[mid] with arr[mid + k] - x.

## Hard questions

### 8. Minimum Window Substring  [Hard]

- **Find it:** LeetCode #76, search "Minimum Window Substring"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The smallest window that contains all letters of t (with counts).
- **First step:** Keep "need" counts from t and "have" counts for the window.
- **If stuck:** Grow right until every needed letter is satisfied, then shrink left as far as possible while still valid; record the best.

### 9. Sliding Window Maximum  [Hard]

- **Find it:** LeetCode #239, search "Sliding Window Maximum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Maximum of each window, faster than re-scanning the window.
- **First step:** Ask which elements can never be a maximum again once a bigger one enters.
- **If stuck:** Keep a deque of indices with decreasing values: pop smaller ones from the back, pop the front when it leaves the window.
