# Arrays & Hashing

**22 questions:** 9 Easy, 12 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A hash map (dictionary) or set lets you answer "have I seen this?" or "how many times?" in one step instead of scanning again.

## How to spot this pattern

- The brute force uses two nested loops to find a pair or a repeat.
- Words like: duplicate, frequency, count, anagram, group, "seen before".
- You need fast lookup by value.

## Thinking steps (use these on every question here)

1. Write the two-loop brute force in words first.
2. Ask: what am I searching for in the inner loop? Store exactly that in a dictionary or set.
3. Decide what the key is and what the value is (index? count? list?).
4. For range sums think prefix sums.

## Common beginner mistakes

- Forgetting that a dictionary key must be unchangeable (use a tuple, not a list).
- Storing the current element before checking, so it matches itself.

Read first: your `dsa-python` notes, file(s) 02-arrays, 03-strings-hashing.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Concatenation of Array | Easy | 1929 | 250 |
| 2 | Contains Duplicate | Easy | 217 | 150 |
| 3 | Valid Anagram | Easy | 242 | 150 |
| 4 | Two Sum | Easy | 1 | 150 |
| 5 | Longest Common Prefix | Easy | 14 | 250 |
| 6 | Remove Element | Easy | 27 | 250 |
| 7 | Majority Element | Easy | 169 | 250 |
| 8 | Design HashSet | Easy | 705 | 250 |
| 9 | Design HashMap | Easy | 706 | 250 |
| 10 | Group Anagrams | Medium | 49 | 150 |
| 11 | Sort an Array | Medium | 912 | 250 |
| 12 | Sort Colors | Medium | 75 | 250 |
| 13 | Top K Frequent Elements | Medium | 347 | 150 |
| 14 | Encode and Decode Strings | Medium | 271 | 150 |
| 15 | Range Sum Query 2D Immutable | Medium | 304 | 250 |
| 16 | Product of Array Except Self | Medium | 238 | 150 |
| 17 | Valid Sudoku | Medium | 36 | 150 |
| 18 | Longest Consecutive Sequence | Medium | 128 | 150 |
| 19 | Best Time to Buy And Sell Stock II | Medium | 122 | 250 |
| 20 | Majority Element II | Medium | 229 | 250 |
| 21 | Subarray Sum Equals K | Medium | 560 | 250 |
| 22 | First Missing Positive | Hard | 41 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Concatenation of Array  [Easy]

- **Find it:** LeetCode #1929, search "Concatenation of Array"
- **Lists:** NeetCode 250
- **Notice:** The answer is just the array written twice.
- **First step:** Make a result of size 2n and think about which index of the original each position copies.
- **If stuck:** Position i and position i+n both hold nums[i].

### 2. Contains Duplicate  [Easy]

- **Find it:** LeetCode #217, search "Contains Duplicate"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** You only need to know "have I seen this before?"
- **First step:** Ask which data structure answers "seen before?" instantly.
- **If stuck:** Walk the array once, putting each value in a set; stop when a value is already there.

### 3. Valid Anagram  [Easy]

- **Find it:** LeetCode #242, search "Valid Anagram"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Two words are anagrams when they use the same letters the same number of times.
- **First step:** Check lengths first, then think about counting letters.
- **If stuck:** Count letters of one string in a dictionary, subtract with the other; every count must end at zero.

### 4. Two Sum  [Easy]

- **Find it:** LeetCode #1, search "Two Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** For each number x you already know the partner you need: target - x.
- **First step:** Brute force is two loops. Ask how to find the partner without the second loop.
- **If stuck:** Keep a dictionary of value -> index as you go; before storing x, check if target - x is already in it.

### 5. Longest Common Prefix  [Easy]

- **Find it:** LeetCode #14, search "Longest Common Prefix"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** A prefix has to match in every word at the same position.
- **First step:** Compare character 0 of all words, then character 1, and so on.
- **If stuck:** Stop at the first position where any word is too short or differs; the shortest word limits the answer.

### 6. Remove Element  [Easy]

- **Find it:** LeetCode #27, search "Remove Element"
- **Lists:** NeetCode 250
- **Notice:** You must edit the array in place and return the new length.
- **First step:** Use one pointer that reads and one that writes.
- **If stuck:** Copy a value to the write position only when it is not the value to remove.

### 7. Majority Element  [Easy]

- **Find it:** LeetCode #169, search "Majority Element"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** One value appears more than half the time.
- **First step:** Counting in a dictionary works; then try for O(1) memory.
- **If stuck:** Boyer-Moore voting: keep a candidate and a counter, +1 when equal, -1 when different, switch candidate at zero.

### 8. Design HashSet  [Easy]

- **Find it:** LeetCode #705, search "Design HashSet"
- **Lists:** NeetCode 250
- **Notice:** You are building what a Python set does inside.
- **First step:** Decide on a number of buckets and a hash function such as key % size.
- **If stuck:** Each bucket is a small list; add, remove and contains all search only inside one bucket.

### 9. Design HashMap  [Easy]

- **Find it:** LeetCode #706, search "Design HashMap"
- **Lists:** NeetCode 250
- **Notice:** Same as the hash set, but each entry stores a key and a value.
- **First step:** Reuse the bucket idea; store pairs.
- **If stuck:** On put, search the bucket for the key first: update if found, append if not.

## Medium questions

### 10. Group Anagrams  [Medium]

- **Find it:** LeetCode #49, search "Group Anagrams"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Anagrams become identical if you put their letters in a fixed order.
- **First step:** Find a "signature" that is the same for all anagrams of a word.
- **If stuck:** Use the sorted word (or a 26-letter count tuple) as a dictionary key and append each word to the list for its key.

### 11. Sort an Array  [Medium]

- **Find it:** LeetCode #912, search "Sort an Array"
- **Lists:** NeetCode 250
- **Notice:** You may not use the built-in sort and need O(n log n).
- **First step:** Pick merge sort: split in half, sort halves, merge.
- **If stuck:** The merge step is two pointers over two sorted halves; write that helper first.

### 12. Sort Colors  [Medium]

- **Find it:** LeetCode #75, search "Sort Colors"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Only three different values exist.
- **First step:** A two-pass count-and-rewrite works. Then try one pass.
- **If stuck:** Dutch flag: three pointers low, mid, high; swap 0s to the front and 2s to the back, and do not advance mid after swapping with high.

### 13. Top K Frequent Elements  [Medium]

- **Find it:** LeetCode #347, search "Top K Frequent Elements"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** First you need frequencies, then the k biggest.
- **First step:** Count with a dictionary. Then ask how to get the top k without sorting everything.
- **If stuck:** Bucket sort: index = frequency, value = list of numbers with that frequency; read buckets from the high end.

### 14. Encode and Decode Strings  [Medium]

- **Find it:** LeetCode #271, search "Encode and Decode Strings"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Any separator character could also appear inside a string.
- **First step:** Think about how to tell the reader where each string ends without a special character.
- **If stuck:** Write the length, then a marker, then the string, e.g. "4#word"; decode by reading the number first.

### 15. Range Sum Query 2D Immutable  [Medium]

- **Find it:** LeetCode #304, search "Range Sum Query 2D Immutable"
- **Lists:** NeetCode 250
- **Notice:** Many sum queries on a grid that never changes.
- **First step:** Recall 1D prefix sums and extend to 2D.
- **If stuck:** Store sums of the rectangle from (0,0) to each cell; a query is big - top - left + corner (inclusion-exclusion).

### 16. Product of Array Except Self  [Medium]

- **Find it:** LeetCode #238, search "Product of Array Except Self"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Division is not allowed, so think "everything to my left times everything to my right".
- **First step:** Build an array of products of all elements before each index.
- **If stuck:** Do a second pass from the right keeping a running product, multiplying into the same result array.

### 17. Valid Sudoku  [Medium]

- **Find it:** LeetCode #36, search "Valid Sudoku"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Three rules to check: rows, columns, 3x3 boxes.
- **First step:** Keep a set for each row, each column and each box.
- **If stuck:** The box of cell (r, c) is (r // 3, c // 3); a repeat in any of the three sets means invalid.

### 18. Longest Consecutive Sequence  [Medium]

- **Find it:** LeetCode #128, search "Longest Consecutive Sequence"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** O(n) is required, so sorting is out.
- **First step:** Put all numbers in a set. Ask which numbers can START a sequence.
- **If stuck:** Only start counting from x when x - 1 is not in the set, then walk x+1, x+2...

### 19. Best Time to Buy And Sell Stock II  [Medium]

- **Find it:** LeetCode #122, search "Best Time to Buy And Sell Stock II"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** You can trade as many times as you like.
- **First step:** Draw the prices as a line chart and look at every upward step.
- **If stuck:** Add every positive day-to-day difference; that equals buying at each valley and selling at each peak.

### 20. Majority Element II  [Medium]

- **Find it:** LeetCode #229, search "Majority Element II"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Values that appear more than n/3 times: at most two can exist.
- **First step:** Extend the voting idea from Majority Element to two candidates.
- **If stuck:** Keep two candidates with two counters, then do a second pass to verify their real counts.

### 21. Subarray Sum Equals K  [Medium]

- **Find it:** LeetCode #560, search "Subarray Sum Equals K"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Negative numbers exist, so a sliding window will not work.
- **First step:** Think in prefix sums: sum(i..j) = prefix[j] - prefix[i-1].
- **If stuck:** Keep a dictionary of how many times each prefix sum has occurred; at each step add count[prefix - k]. Start with {0: 1}.

## Hard questions

### 22. First Missing Positive  [Hard]

- **Find it:** LeetCode #41, search "First Missing Positive"
- **Lists:** NeetCode 250
- **Notice:** O(n) time and O(1) extra space: the array itself must be your memory.
- **First step:** The answer is always between 1 and n+1.
- **If stuck:** Put each value v (1..n) at index v-1 by swapping; the first index i where nums[i] != i+1 gives the answer.
