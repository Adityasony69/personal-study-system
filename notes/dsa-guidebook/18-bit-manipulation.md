# Bit Manipulation

**10 questions:** 6 Easy, 4 Medium, 0 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Working directly with the 0s and 1s of a number using AND, OR, XOR and shifts.

## How to spot this pattern

- Words like: appears twice, single, without using +, binary, power of two.

## Thinking steps (use these on every question here)

1. Remember: x ^ x = 0, x ^ 0 = x, x & 1 gives the last bit.
2. n & (n - 1) removes the lowest set bit.
3. Shifting right by one is dividing by 2.

## Common beginner mistakes

- In Python integers never overflow, so 32-bit tricks need a mask.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Single Number | Easy | 136 | 150 |
| 2 | Number of 1 Bits | Easy | 191 | 150 |
| 3 | Counting Bits | Easy | 338 | 150 |
| 4 | Add Binary | Easy | 67 | 250 |
| 5 | Reverse Bits | Easy | 190 | 150 |
| 6 | Missing Number | Easy | 268 | 150 |
| 7 | Sum of Two Integers | Medium | 371 | 150 |
| 8 | Reverse Integer | Medium | 7 | 150 |
| 9 | Bitwise AND of Numbers Range | Medium | 201 | 250 |
| 10 | Minimum Array End | Medium | 3133 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Single Number  [Easy]

- **Find it:** LeetCode #136, search "Single Number"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Every number appears twice except one.
- **First step:** Recall that x ^ x = 0 and x ^ 0 = x.
- **If stuck:** XOR everything together.

### 2. Number of 1 Bits  [Easy]

- **Find it:** LeetCode #191, search "Number of 1 Bits"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Count the set bits.
- **First step:** Check the last bit with n & 1 and shift right.
- **If stuck:** Trick: n & (n - 1) removes the lowest set bit; count how many times you can do it.

### 3. Counting Bits  [Easy]

- **Find it:** LeetCode #338, search "Counting Bits"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Bit counts for every number from 0 to n.
- **First step:** Relate a number to a smaller one you have already solved.
- **If stuck:** bits[i] = bits[i >> 1] + (i & 1).

### 4. Add Binary  [Easy]

- **Find it:** LeetCode #67, search "Add Binary"
- **Lists:** NeetCode 250
- **Notice:** School addition in base 2.
- **First step:** Walk both strings from the right with a carry.
- **If stuck:** digit = total % 2, carry = total // 2; continue while either string or the carry remains.

### 5. Reverse Bits  [Easy]

- **Find it:** LeetCode #190, search "Reverse Bits"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Bit i moves to position 31 - i.
- **First step:** Loop 32 times.
- **If stuck:** Shift the result left, add the last bit of n, shift n right.

### 6. Missing Number  [Easy]

- **Find it:** LeetCode #268, search "Missing Number"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Numbers 0..n with one missing.
- **First step:** Compare with what the full sum should be.
- **If stuck:** Expected sum n(n+1)/2 minus the actual sum; or XOR all indexes and values.

## Medium questions

### 7. Sum of Two Integers  [Medium]

- **Find it:** LeetCode #371, search "Sum of Two Integers"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Add without + or -.
- **First step:** XOR gives the sum without carries; AND shifted left gives the carries.
- **If stuck:** Repeat until the carry is 0. In Python you need a 32-bit mask because integers are unbounded.

### 8. Reverse Integer  [Medium]

- **Find it:** LeetCode #7, search "Reverse Integer"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Reverse the digits, returning 0 on 32-bit overflow.
- **First step:** Pop the last digit with % 10 and push it onto the result.
- **If stuck:** Check the overflow limit; in Python handle the sign separately since % behaves differently for negatives.

### 9. Bitwise AND of Numbers Range  [Medium]

- **Find it:** LeetCode #201, search "Bitwise AND of Numbers Range"
- **Lists:** NeetCode 250
- **Notice:** Any bit that changes somewhere in the range becomes 0.
- **First step:** Only the common left-side prefix of left and right survives.
- **If stuck:** Shift both right until they are equal, counting shifts; then shift back.

### 10. Minimum Array End  [Medium]

- **Find it:** LeetCode #3133, search "Minimum Array End"
- **Lists:** NeetCode 250
- **Notice:** Every element must keep all the bits of x set.
- **First step:** The free positions are the ZERO bits of x.
- **If stuck:** Write the number n - 1 in binary into those zero-bit positions of x, lowest first.
