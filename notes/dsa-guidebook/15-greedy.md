# Greedy

**14 questions:** 1 Easy, 12 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Make the choice that looks best right now and never go back. It only works when you can argue that the local best leads to the overall best.

## How to spot this pattern

- Intervals, jumps, reaching the end, minimum number of something.
- A DP solution exists but looks too slow.

## Thinking steps (use these on every question here)

1. Try a simple rule on the examples by hand.
2. Try to break your own rule with a small counter-example.
3. Sorting first often reveals the greedy rule.

## Common beginner mistakes

- Trusting a greedy rule without testing it on tricky cases.

Read first: your `dsa-python` notes, file(s) 12-greedy-dp.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Lemonade Change | Easy | 860 | 250 |
| 2 | Maximum Subarray | Medium | 53 | 150 |
| 3 | Maximum Sum Circular Subarray | Medium | 918 | 250 |
| 4 | Longest Turbulent Subarray | Medium | 978 | 250 |
| 5 | Jump Game | Medium | 55 | 150 |
| 6 | Jump Game II | Medium | 45 | 150 |
| 7 | Jump Game VII | Medium | 1871 | 250 |
| 8 | Gas Station | Medium | 134 | 150 |
| 9 | Hand of Straights | Medium | 846 | 150 |
| 10 | Dota2 Senate | Medium | 649 | 250 |
| 11 | Merge Triplets to Form Target Triplet | Medium | 1899 | 150 |
| 12 | Partition Labels | Medium | 763 | 150 |
| 13 | Valid Parenthesis String | Medium | 678 | 150 |
| 14 | Candy | Hard | 135 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Lemonade Change  [Easy]

- **Find it:** LeetCode #860, search "Lemonade Change"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** You give change with the bills you already hold.
- **First step:** Count your $5 and $10 bills.
- **If stuck:** For a $20, prefer giving 10 + 5 over 5 + 5 + 5, since $5 bills are more useful.

## Medium questions

### 2. Maximum Subarray  [Medium]

- **Find it:** LeetCode #53, search "Maximum Subarray"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A negative running sum only hurts whatever comes next.
- **First step:** Keep a running sum.
- **If stuck:** If the running sum drops below 0, reset it to 0 (Kadane); track the best seen. Handle all-negative arrays.

### 3. Maximum Sum Circular Subarray  [Medium]

- **Find it:** LeetCode #918, search "Maximum Sum Circular Subarray"
- **Lists:** NeetCode 250
- **Notice:** The best subarray either sits in the middle or wraps around.
- **First step:** A wrapping subarray = total - (a middle subarray with the minimum sum).
- **If stuck:** Run Kadane for max and for min; answer = max(maxSum, total - minSum), except when all numbers are negative.

### 4. Longest Turbulent Subarray  [Medium]

- **Find it:** LeetCode #978, search "Longest Turbulent Subarray"
- **Lists:** NeetCode 250
- **Notice:** The comparison sign must flip between every pair of neighbours.
- **First step:** Track the length of the current valid run.
- **If stuck:** Extend when the sign flips, restart at 2 when it does not, restart at 1 on equal values.

### 5. Jump Game  [Medium]

- **Find it:** LeetCode #55, search "Jump Game"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Can you reach the last index?
- **First step:** Track the farthest index reachable so far.
- **If stuck:** If you are ever standing at an index beyond that farthest reach, return false. (Or move a goal post backward from the end.)

### 6. Jump Game II  [Medium]

- **Find it:** LeetCode #45, search "Jump Game II"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Fewest jumps: think of it as BFS levels over index ranges.
- **First step:** The current jump covers a range [l, r].
- **If stuck:** Find the farthest reach from any index in the range; that becomes the next range; count one jump.

### 7. Jump Game VII  [Medium]

- **Find it:** LeetCode #1871, search "Jump Game VII"
- **Lists:** NeetCode 250
- **Notice:** You can land on a "0" within a jump distance window.
- **First step:** BFS, but do not re-scan indexes you already checked.
- **If stuck:** Keep a "farthest index already queued" pointer so each index is looked at once.

### 8. Gas Station  [Medium]

- **Find it:** LeetCode #134, search "Gas Station"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** If total gas < total cost there is no answer; otherwise exactly one.
- **First step:** Walk once keeping a running tank.
- **If stuck:** When the tank goes negative, the start must be after this station: reset the tank and move the start.

### 9. Hand of Straights  [Medium]

- **Find it:** LeetCode #846, search "Hand of Straights"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Groups of consecutive cards of a fixed size.
- **First step:** The smallest remaining card must START a group.
- **If stuck:** Count the cards; repeatedly take the smallest (sorted keys or min-heap) and remove it and the next size-1 values.

### 10. Dota2 Senate  [Medium]

- **Find it:** LeetCode #649, search "Dota2 Senate"
- **Lists:** NeetCode 250
- **Notice:** Each senator should ban the next opponent who would act.
- **First step:** Keep two queues of indexes, one per party.
- **If stuck:** Pop the front of each; the smaller index wins and re-enters its queue with index + n.

### 11. Merge Triplets to Form Target Triplet  [Medium]

- **Find it:** LeetCode #1899, search "Merge Triplets to Form Target Triplet"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Merging takes the max in each position, so one bad value ruins a triplet.
- **First step:** Throw away any triplet that has a value larger than the target in any position.
- **If stuck:** From the rest, check that each of the three target values appears in its position.

### 12. Partition Labels  [Medium]

- **Find it:** LeetCode #763, search "Partition Labels"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A part must contain every occurrence of each of its letters.
- **First step:** Record the last index of every letter.
- **If stuck:** Walk the string extending the end of the current part to the last index of each letter seen; cut when i reaches the end.

### 13. Valid Parenthesis String  [Medium]

- **Find it:** LeetCode #678, search "Valid Parenthesis String"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** "*" can be "(", ")" or nothing.
- **First step:** Track a RANGE of possible open counts instead of one number.
- **If stuck:** "(" raises both low and high, ")" lowers both, "*" lowers low and raises high; fail if high < 0, clamp low at 0, end needs low == 0.

## Hard questions

### 14. Candy  [Hard]

- **Find it:** LeetCode #135, search "Candy"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Each child must beat a lower-rated neighbour on both sides.
- **First step:** Handle one direction at a time.
- **If stuck:** Left-to-right pass for the left neighbour, right-to-left pass for the right neighbour, taking the max.
