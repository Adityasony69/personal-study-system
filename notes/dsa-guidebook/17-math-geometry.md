# Math & Geometry

**13 questions:** 6 Easy, 7 Medium, 0 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Problems solved by simulating carefully or by a number property. Matrix questions are about getting the indexes right.

## How to spot this pattern

- Digits, powers, matrices, rotation, spirals.

## Thinking steps (use these on every question here)

1. Work a small example on paper and watch the indexes.
2. Use % 10 and // 10 to take digits apart.
3. For matrices, name your boundaries clearly.

## Common beginner mistakes

- Off-by-one mistakes at the boundaries.
- Overflow in languages with fixed-size integers.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Excel Sheet Column Title | Easy | 168 | 250 |
| 2 | Greatest Common Divisor of Strings | Easy | 1071 | 250 |
| 3 | Transpose Matrix | Easy | 867 | 250 |
| 4 | Happy Number | Easy | 202 | 150 |
| 5 | Plus One | Easy | 66 | 150 |
| 6 | Roman to Integer | Easy | 13 | 250 |
| 7 | Insert Greatest Common Divisors in Linked List | Medium | 2807 | 250 |
| 8 | Rotate Image | Medium | 48 | 150 |
| 9 | Spiral Matrix | Medium | 54 | 150 |
| 10 | Set Matrix Zeroes | Medium | 73 | 150 |
| 11 | Pow(x, n) | Medium | 50 | 150 |
| 12 | Multiply Strings | Medium | 43 | 150 |
| 13 | Detect Squares | Medium | 2013 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Excel Sheet Column Title  [Easy]

- **Find it:** LeetCode #168, search "Excel Sheet Column Title"
- **Lists:** NeetCode 250
- **Notice:** It looks like base 26 but has no zero.
- **First step:** Take the last letter with a remainder.
- **If stuck:** Subtract 1 before each % 26 and // 26 step.

### 2. Greatest Common Divisor of Strings  [Easy]

- **Find it:** LeetCode #1071, search "Greatest Common Divisor of Strings"
- **Lists:** NeetCode 250
- **Notice:** If a common divisor string exists, s1 + s2 equals s2 + s1.
- **First step:** Check that condition first.
- **If stuck:** The answer length is gcd(len(s1), len(s2)).

### 3. Transpose Matrix  [Easy]

- **Find it:** LeetCode #867, search "Transpose Matrix"
- **Lists:** NeetCode 250
- **Notice:** Rows become columns.
- **First step:** The result has the swapped dimensions.
- **If stuck:** result[c][r] = matrix[r][c].

### 4. Happy Number  [Easy]

- **Find it:** LeetCode #202, search "Happy Number"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** The process either reaches 1 or loops forever.
- **First step:** Write a helper for the sum of squared digits.
- **If stuck:** Detect the loop with a set of seen numbers (or slow/fast pointers).

### 5. Plus One  [Easy]

- **Find it:** LeetCode #66, search "Plus One"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Adding one can carry through a run of 9s.
- **First step:** Go from the last digit backward.
- **If stuck:** A digit less than 9: add one and return. A 9 becomes 0 and you continue; if all were 9, put a 1 in front.

### 6. Roman to Integer  [Easy]

- **Find it:** LeetCode #13, search "Roman to Integer"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** A smaller symbol before a larger one means subtract.
- **First step:** Map symbols to values.
- **If stuck:** Walk left to right: if the current value is less than the next, subtract it; otherwise add it.

## Medium questions

### 7. Insert Greatest Common Divisors in Linked List  [Medium]

- **Find it:** LeetCode #2807, search "Insert Greatest Common Divisors in Linked List"
- **Lists:** NeetCode 250
- **Notice:** Insert a new node between each pair of neighbours.
- **First step:** Walk the list with a pointer.
- **If stuck:** Create the gcd node, link it in, then jump two nodes ahead.

### 8. Rotate Image  [Medium]

- **Find it:** LeetCode #48, search "Rotate Image"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Rotate 90 degrees clockwise in place.
- **First step:** Try combining two simple operations.
- **If stuck:** Transpose the matrix, then reverse each row.

### 9. Spiral Matrix  [Medium]

- **Find it:** LeetCode #54, search "Spiral Matrix"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Walk the outer ring, then the next ring inward.
- **First step:** Keep four boundaries: top, bottom, left, right.
- **If stuck:** Go right, down, left, up, shrinking a boundary after each; check the boundaries before the left and up passes.

### 10. Set Matrix Zeroes  [Medium]

- **Find it:** LeetCode #73, search "Set Matrix Zeroes"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** If you zero cells immediately you lose information about the original zeros.
- **First step:** First record which rows and columns need zeroing.
- **If stuck:** For O(1) space use the first row and first column as the markers, with one extra flag for the first row/column itself.

### 11. Pow(x, n)  [Medium]

- **Find it:** LeetCode #50, search "Pow(x, n)"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Multiplying n times is too slow for big n.
- **First step:** x^n = (x^(n/2))^2.
- **If stuck:** Recursion halving n; multiply by one extra x when n is odd; for negative n take the reciprocal.

### 12. Multiply Strings  [Medium]

- **Find it:** LeetCode #43, search "Multiply Strings"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** No converting the whole string to an integer.
- **First step:** Do school multiplication digit by digit.
- **If stuck:** The product of digit i and digit j lands at position i + j in a result array of length len1 + len2; handle carries, strip leading zeros.

### 13. Detect Squares  [Medium]

- **Find it:** LeetCode #2013, search "Detect Squares"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Fix the query point and one diagonal corner.
- **First step:** Store a count for every added point.
- **If stuck:** For each stored point that is diagonal to the query (same |dx| and |dy|, not zero), multiply the counts of the two remaining corners.
