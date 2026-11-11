# Binary Search

**14 questions:** 4 Easy, 7 Medium, 3 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Each step throws away half of the remaining possibilities. It works on sorted data and also on a range of possible answers.

## How to spot this pattern

- Sorted input and O(log n) is asked.
- "Minimum X such that it is possible" or "maximum X that still works".
- Rotated sorted arrays.

## Thinking steps (use these on every question here)

1. Define low and high: indexes, or the smallest and largest possible answer.
2. Write a check for mid. Which half can be thrown away?
3. Decide the loop style (low <= high with mid +/- 1 is the safest to start with).
4. For answer search: write a helper feasible(x) first.

## Common beginner mistakes

- Infinite loop because low or high never moves past mid.
- Searching the answer range with the wrong lower bound (often it must be max of the array, not 1).

Read first: your `dsa-python` notes, file(s) 06-sorting-binary-search.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Binary Search | Easy | 704 | 150 |
| 2 | Search Insert Position | Easy | 35 | 250 |
| 3 | Guess Number Higher Or Lower | Easy | 374 | 250 |
| 4 | Sqrt(x) | Easy | 69 | 250 |
| 5 | Search a 2D Matrix | Medium | 74 | 150 |
| 6 | Koko Eating Bananas | Medium | 875 | 150 |
| 7 | Capacity to Ship Packages Within D Days | Medium | 1011 | 250 |
| 8 | Find Minimum In Rotated Sorted Array | Medium | 153 | 150 |
| 9 | Search In Rotated Sorted Array | Medium | 33 | 150 |
| 10 | Search In Rotated Sorted Array II | Medium | 81 | 250 |
| 11 | Time Based Key Value Store | Medium | 981 | 150 |
| 12 | Split Array Largest Sum | Hard | 410 | 250 |
| 13 | Median of Two Sorted Arrays | Hard | 4 | 150 |
| 14 | Find in Mountain Array | Hard | 1095 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Binary Search  [Easy]

- **Find it:** LeetCode #704, search "Binary Search"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Sorted array and O(log n).
- **First step:** Keep low and high; look at the middle.
- **If stuck:** If the middle is too small move low to mid+1, too big move high to mid-1; loop while low <= high.

### 2. Search Insert Position  [Easy]

- **Find it:** LeetCode #35, search "Search Insert Position"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Find the first index whose value is >= target.
- **First step:** Run a normal binary search.
- **If stuck:** When the loop ends without finding it, low is the insert position.

### 3. Guess Number Higher Or Lower  [Easy]

- **Find it:** LeetCode #374, search "Guess Number Higher Or Lower"
- **Lists:** NeetCode 250
- **Notice:** The API tells you higher or lower: exactly binary search.
- **First step:** Search between 1 and n.
- **If stuck:** Read the meaning of the API result carefully: -1 means your guess is too high.

### 4. Sqrt(x)  [Easy]

- **Find it:** LeetCode #69, search "Sqrt(x)"
- **Lists:** NeetCode 250
- **Notice:** Find the largest integer whose square is <= x.
- **First step:** Binary search over the answers 0..x.
- **If stuck:** If mid*mid <= x remember mid and go right; otherwise go left.

## Medium questions

### 5. Search a 2D Matrix  [Medium]

- **Find it:** LeetCode #74, search "Search a 2D Matrix"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Rows are sorted and each row starts after the previous one ends.
- **First step:** Imagine the matrix as one long sorted list.
- **If stuck:** Binary search on index 0..m*n-1 with row = i // n and col = i % n.

### 6. Koko Eating Bananas  [Medium]

- **Find it:** LeetCode #875, search "Koko Eating Bananas"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You are asked for the minimum speed that works: "binary search on the answer".
- **First step:** For a given speed you can compute the hours needed. Faster speed -> fewer hours.
- **If stuck:** Search speed between 1 and max(piles); if hours <= h try smaller, else go bigger.

### 7. Capacity to Ship Packages Within D Days  [Medium]

- **Find it:** LeetCode #1011, search "Capacity to Ship Packages Within D Days"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Minimum capacity that works: binary search on the answer again.
- **First step:** Write a helper that counts the days needed for a given capacity.
- **If stuck:** Search between max(weights) and sum(weights).

### 8. Find Minimum In Rotated Sorted Array  [Medium]

- **Find it:** LeetCode #153, search "Find Minimum In Rotated Sorted Array"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A sorted array cut and swapped; one half is always sorted.
- **First step:** Compare the middle with the rightmost element.
- **If stuck:** If nums[mid] > nums[right] the minimum is to the right of mid; otherwise it is at mid or to the left.

### 9. Search In Rotated Sorted Array  [Medium]

- **Find it:** LeetCode #33, search "Search In Rotated Sorted Array"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** At any mid, one of the two halves is properly sorted.
- **First step:** Find out which half is sorted by comparing nums[low] with nums[mid].
- **If stuck:** Check if the target lies inside the sorted half; if yes search there, if not search the other half.

### 10. Search In Rotated Sorted Array II  [Medium]

- **Find it:** LeetCode #81, search "Search In Rotated Sorted Array II"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Same as above but duplicates can hide which half is sorted.
- **First step:** Start from the previous solution.
- **If stuck:** When nums[low] == nums[mid] == nums[high] you cannot decide: just shrink both ends by one.

### 11. Time Based Key Value Store  [Medium]

- **Find it:** LeetCode #981, search "Time Based Key Value Store"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Timestamps for a key always increase, so the list for each key is sorted.
- **First step:** Store key -> list of (timestamp, value).
- **If stuck:** On get, binary search for the last timestamp <= the asked one.

## Hard questions

### 12. Split Array Largest Sum  [Hard]

- **Find it:** LeetCode #410, search "Split Array Largest Sum"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** "Minimise the largest" means binary search on the answer.
- **First step:** For a guessed limit, greedily count how many pieces you need.
- **If stuck:** Search between max(nums) and sum(nums); if pieces <= k try a smaller limit.

### 13. Median of Two Sorted Arrays  [Hard]

- **Find it:** LeetCode #4, search "Median of Two Sorted Arrays"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** O(log) needed, so merging is too slow.
- **First step:** Think of cutting both arrays so the left parts together hold half the elements.
- **If stuck:** Binary search the cut in the SHORTER array; valid when left1 <= right2 and left2 <= right1.

### 14. Find in Mountain Array  [Hard]

- **Find it:** LeetCode #1095, search "Find in Mountain Array"
- **Lists:** NeetCode 250
- **Notice:** The array goes up then down, and calls to get() are limited.
- **First step:** Three binary searches.
- **If stuck:** First find the peak; then search the rising side; if not found, search the falling side (comparisons flipped).
