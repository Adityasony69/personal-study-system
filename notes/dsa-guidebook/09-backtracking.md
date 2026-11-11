# Backtracking

**17 questions:** 1 Easy, 13 Medium, 3 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Try a choice, go deeper, then undo the choice and try the next one. It explores a decision tree.

## How to spot this pattern

- Words like: all subsets, all permutations, all combinations, every way.
- Small input sizes (n around 10 to 20).
- Placing things under rules (queens, sudoku).

## Thinking steps (use these on every question here)

1. Draw the decision tree for a tiny input.
2. Define the state: index plus the current partial answer.
3. Write the stop condition and record a COPY of the answer.
4. Loop over choices: choose, recurse, un-choose.
5. With duplicates: sort first and skip equal choices at the same level.

## Common beginner mistakes

- Appending the same list object instead of a copy.
- Forgetting to undo the choice after the recursive call.

Read first: your `dsa-python` notes, file(s) 05-recursion-backtracking.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Sum of All Subsets XOR Total | Easy | 1863 | 250 |
| 2 | Subsets | Medium | 78 | 150 |
| 3 | Combination Sum | Medium | 39 | 150 |
| 4 | Combination Sum II | Medium | 40 | 150 |
| 5 | Combinations | Medium | 77 | 250 |
| 6 | Permutations | Medium | 46 | 150 |
| 7 | Subsets II | Medium | 90 | 150 |
| 8 | Permutations II | Medium | 47 | 250 |
| 9 | Generate Parentheses | Medium | 22 | 150 |
| 10 | Word Search | Medium | 79 | 150 |
| 11 | Palindrome Partitioning | Medium | 131 | 150 |
| 12 | Letter Combinations of a Phone Number | Medium | 17 | 150 |
| 13 | Matchsticks to Square | Medium | 473 | 250 |
| 14 | Partition to K Equal Sum Subsets | Medium | 698 | 250 |
| 15 | N Queens | Hard | 51 | 150 |
| 16 | N Queens II | Hard | 52 | 250 |
| 17 | Word Break II | Hard | 140 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Sum of All Subsets XOR Total  [Easy]

- **Find it:** LeetCode #1863, search "Sum of All Subsets XOR Total"
- **Lists:** NeetCode 250
- **Notice:** Each element is either in a subset or not.
- **First step:** Recursion with two branches per element: include or skip.
- **If stuck:** Carry the running XOR; add it to the total when you pass the last index.

## Medium questions

### 2. Subsets  [Medium]

- **Find it:** LeetCode #78, search "Subsets"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Every element has two choices: take it or leave it.
- **First step:** Draw the decision tree for [1,2,3].
- **If stuck:** Recursive function (index, current list): add element and recurse, remove it and recurse; record at the end.

### 3. Combination Sum  [Medium]

- **Find it:** LeetCode #39, search "Combination Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You can reuse a number any number of times.
- **First step:** Decision at each step: use candidates[i] again, or move on to i+1 for good.
- **If stuck:** Stop when the remaining target is 0 (record) or negative (dead end).

### 4. Combination Sum II  [Medium]

- **Find it:** LeetCode #40, search "Combination Sum II"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Each number used once and the input has duplicates.
- **First step:** Sort first.
- **If stuck:** In the loop at one level, skip a value equal to the previous one at that same level.

### 5. Combinations  [Medium]

- **Find it:** LeetCode #77, search "Combinations"
- **Lists:** NeetCode 250
- **Notice:** Choose k numbers from 1..n; order does not matter.
- **First step:** Recursive function (start, current).
- **If stuck:** Loop from start to n, add the number, recurse with start+1, remove it. Record when length is k.

### 6. Permutations  [Medium]

- **Find it:** LeetCode #46, search "Permutations"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Order matters and every element is used exactly once.
- **First step:** At each position try every number not used yet.
- **If stuck:** Keep a "used" set or swap elements in place; record when the current list is full.

### 7. Subsets II  [Medium]

- **Find it:** LeetCode #90, search "Subsets II"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Subsets, but the input has duplicates.
- **First step:** Sort so duplicates are neighbours.
- **If stuck:** When you decide to SKIP a value, skip all copies of it.

### 8. Permutations II  [Medium]

- **Find it:** LeetCode #47, search "Permutations II"
- **Lists:** NeetCode 250
- **Notice:** Permutations with duplicate numbers.
- **First step:** Count how many of each value you have.
- **If stuck:** At each position try each DISTINCT value that still has count left.

### 9. Generate Parentheses  [Medium]

- **Find it:** LeetCode #22, search "Generate Parentheses"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A string is valid if you never close more than you have opened.
- **First step:** Track open and close counts while building the string.
- **If stuck:** Add "(" if open < n; add ")" if close < open.

### 10. Word Search  [Medium]

- **Find it:** LeetCode #79, search "Word Search"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Find a path of neighbouring cells spelling the word; a cell cannot be reused.
- **First step:** Start a DFS from every cell matching the first letter.
- **If stuck:** Mark the cell visited before exploring 4 neighbours, and UNMARK it when you return.

### 11. Palindrome Partitioning  [Medium]

- **Find it:** LeetCode #131, search "Palindrome Partitioning"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Cut the string so every piece is a palindrome.
- **First step:** At each position, try every possible end for the next piece.
- **If stuck:** Only recurse if the piece is a palindrome; record when you reach the end of the string.

### 12. Letter Combinations of a Phone Number  [Medium]

- **Find it:** LeetCode #17, search "Letter Combinations of a Phone Number"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Each digit offers 3 or 4 letters.
- **First step:** Map digits to letters with a dictionary.
- **If stuck:** Recursion on the digit index: for each letter of this digit, add it and go to the next digit.

### 13. Matchsticks to Square  [Medium]

- **Find it:** LeetCode #473, search "Matchsticks to Square"
- **Lists:** NeetCode 250
- **Notice:** Split all sticks into 4 groups with equal sums.
- **First step:** Total must be divisible by 4; side = total / 4.
- **If stuck:** Sort descending; place each stick into one of 4 sides if it fits, backtrack if stuck. Skip sides with the same current length.

### 14. Partition to K Equal Sum Subsets  [Medium]

- **Find it:** LeetCode #698, search "Partition to K Equal Sum Subsets"
- **Lists:** NeetCode 250
- **Notice:** Same idea as the matchsticks problem with k groups.
- **First step:** Target per group = total / k.
- **If stuck:** Fill one bucket at a time with a used-marker; sorting descending prunes a lot.

## Hard questions

### 15. N Queens  [Hard]

- **Find it:** LeetCode #51, search "N Queens"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** One queen per row; no shared column or diagonal.
- **First step:** Place queens row by row.
- **If stuck:** Keep three sets: columns, (row - col) diagonals and (row + col) diagonals; remove from the sets when you backtrack.

### 16. N Queens II  [Hard]

- **Find it:** LeetCode #52, search "N Queens II"
- **Lists:** NeetCode 250
- **Notice:** Same as N-Queens but you only count.
- **First step:** Reuse the same backtracking.
- **If stuck:** Return 1 when you reach row n and sum up the counts.

### 17. Word Break II  [Hard]

- **Find it:** LeetCode #140, search "Word Break II"
- **Lists:** NeetCode 250
- **Notice:** Return every way to split the string into dictionary words.
- **First step:** At each index try every dictionary word that matches there.
- **If stuck:** Recurse on the rest; memoize the list of sentences for each start index.
