# Two Pointers

**13 questions:** 6 Easy, 6 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Two indexes move through the data, usually from both ends toward the middle, or one reading and one writing.

## How to spot this pattern

- The array is sorted, or sorting it is allowed.
- Palindromes, pairs with a target sum, reversing, removing in place.
- You are asked for O(1) extra memory.

## Thinking steps (use these on every question here)

1. Decide where the two pointers start (both ends, or both at the start).
2. Write the rule: when does left move, when does right move?
3. Make sure every step moves at least one pointer, so the loop ends.

## Common beginner mistakes

- Using while left <= right when it should be left < right (or the reverse).
- Forgetting to skip duplicates in 3Sum-type problems.

Read first: your `dsa-python` notes, file(s) 04-two-pointers-sliding-window.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Reverse String | Easy | 344 | 250 |
| 2 | Valid Palindrome | Easy | 125 | 150 |
| 3 | Valid Palindrome II | Easy | 680 | 250 |
| 4 | Merge Strings Alternately | Easy | 1768 | 250 |
| 5 | Merge Sorted Array | Easy | 88 | 250 |
| 6 | Remove Duplicates From Sorted Array | Easy | 26 | 250 |
| 7 | Two Sum II Input Array Is Sorted | Medium | 167 | 150 |
| 8 | 3Sum | Medium | 15 | 150 |
| 9 | 4Sum | Medium | 18 | 250 |
| 10 | Rotate Array | Medium | 189 | 250 |
| 11 | Container With Most Water | Medium | 11 | 150 |
| 12 | Boats to Save People | Medium | 881 | 250 |
| 13 | Trapping Rain Water | Hard | 42 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Reverse String  [Easy]

- **Find it:** LeetCode #344, search "Reverse String"
- **Lists:** NeetCode 250
- **Notice:** Reverse in place.
- **First step:** Put one pointer at each end.
- **If stuck:** Swap and move both pointers inward until they meet.

### 2. Valid Palindrome  [Easy]

- **Find it:** LeetCode #125, search "Valid Palindrome"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Ignore everything that is not a letter or digit, and ignore case.
- **First step:** Two pointers from both ends.
- **If stuck:** Skip non-alphanumeric characters on each side, then compare lowercase versions.

### 3. Valid Palindrome II  [Easy]

- **Find it:** LeetCode #680, search "Valid Palindrome II"
- **Lists:** NeetCode 250
- **Notice:** You may delete at most one character.
- **First step:** Run the normal two-pointer palindrome check until a mismatch.
- **If stuck:** At the first mismatch try skipping the left char OR the right char and check if the rest is a palindrome.

### 4. Merge Strings Alternately  [Easy]

- **Find it:** LeetCode #1768, search "Merge Strings Alternately"
- **Lists:** NeetCode 250
- **Notice:** Take one letter from each word in turn.
- **First step:** Loop while either word still has letters.
- **If stuck:** Use one index; append word1[i] if it exists, then word2[i] if it exists.

### 5. Merge Sorted Array  [Easy]

- **Find it:** LeetCode #88, search "Merge Sorted Array"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** nums1 has empty space at the END.
- **First step:** Filling from the front overwrites values you still need. Which end is safe?
- **If stuck:** Three pointers from the back: place the larger of the two tails at the last free position.

### 6. Remove Duplicates From Sorted Array  [Easy]

- **Find it:** LeetCode #26, search "Remove Duplicates From Sorted Array"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Sorted means duplicates sit next to each other.
- **First step:** Read pointer and write pointer again.
- **If stuck:** Write a value only when it differs from the last value you wrote.

## Medium questions

### 7. Two Sum II Input Array Is Sorted  [Medium]

- **Find it:** LeetCode #167, search "Two Sum II Input Array Is Sorted"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Sorted input and O(1) memory: no dictionary needed.
- **First step:** Put pointers at both ends and look at their sum.
- **If stuck:** Sum too big -> move right pointer left; too small -> move left pointer right.

### 8. 3Sum  [Medium]

- **Find it:** LeetCode #15, search "3Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Triplets that sum to zero, with no duplicate triplets.
- **First step:** Sort first. Fix one number, then it becomes Two Sum II on the rest.
- **If stuck:** Skip equal neighbours for the fixed number and also after finding a triplet, to avoid duplicates.

### 9. 4Sum  [Medium]

- **Find it:** LeetCode #18, search "4Sum"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Same idea as 3Sum with one more fixed number.
- **First step:** Sort, two nested loops for the first two numbers, two pointers for the rest.
- **If stuck:** Skip duplicates at every level; watch for large sums.

### 10. Rotate Array  [Medium]

- **Find it:** LeetCode #189, search "Rotate Array"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Rotating right by k moves the last k elements to the front.
- **First step:** Using an extra array is easy. For in place, think about reversing.
- **If stuck:** Take k % n; reverse the whole array, then reverse the first k, then reverse the rest.

### 11. Container With Most Water  [Medium]

- **Find it:** LeetCode #11, search "Container With Most Water"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Area = width x the SHORTER of the two lines.
- **First step:** Start with the widest container: pointers at both ends.
- **If stuck:** Move the pointer at the shorter line; moving the taller one can never help.

### 12. Boats to Save People  [Medium]

- **Find it:** LeetCode #881, search "Boats to Save People"
- **Lists:** NeetCode 250
- **Notice:** Each boat carries at most two people within a weight limit.
- **First step:** Sort. Try pairing the heaviest person with the lightest.
- **If stuck:** If they fit together, move both pointers; otherwise the heaviest goes alone.

## Hard questions

### 13. Trapping Rain Water  [Hard]

- **Find it:** LeetCode #42, search "Trapping Rain Water"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Water above a bar = min(tallest on left, tallest on right) - its height.
- **First step:** First solve it with two helper arrays: max-left and max-right.
- **If stuck:** Then use two pointers with running leftMax and rightMax; process the side with the smaller max.
