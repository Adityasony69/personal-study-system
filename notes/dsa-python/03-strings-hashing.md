# Strings and hashing (Python)

Every code block here was run with its asserts on Python 3.12.

## Hashing in one paragraph
A `dict` or `set` turns a key into a slot number, so lookup, insert and delete are O(1) on average. Use one whenever you catch yourself writing "have I seen this before?" or "how many times?". Keys must be hashable: numbers, strings, tuples yes; lists, dicts, sets no (use a `tuple` or `frozenset`).

Strings are **immutable**: `s[0] = "x"` is an error and every edit builds a new string. Collect pieces in a list and `"".join(...)` at the end.

## Counting
```python
from collections import Counter, defaultdict

def char_counts(s):
    d = {}
    for ch in s:
        d[ch] = d.get(ch, 0) + 1
    return d

assert char_counts("banana") == {"b": 1, "a": 3, "n": 2}
assert Counter("banana") == {"a": 3, "n": 2, "b": 1}      # same thing, built in
assert Counter("banana").most_common(1) == [("a", 3)]

def top_k_frequent(nums, k):                # bucket sort by frequency, O(n)
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, c in count.items():
        buckets[c].append(num)
    out = []
    for c in range(len(buckets) - 1, 0, -1):
        for num in buckets[c]:
            out.append(num)
            if len(out) == k:
                return out
    return out

assert sorted(top_k_frequent([1, 1, 1, 2, 2, 3], 2)) == [1, 2]
assert top_k_frequent([1], 1) == [1]
```

## Two Sum: the classic
For each number ask "have I already seen its partner?" Store value -> index.
```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []

assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]
assert two_sum([1, 2], 10) == []
```
Note: store `x` **after** checking, so an item is never paired with itself.

## Anagrams
Two words are anagrams if they have the same letters in the same counts.
```python
def is_anagram(a, b):
    return Counter(a) == Counter(b)

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups[tuple(sorted(w))].append(w)      # sorted letters = the group key
    return list(groups.values())

def group_anagrams_counting(words):             # O(total letters), key = 26 counts
    groups = defaultdict(list)
    for w in words:
        key = [0] * 26
        for ch in w:
            key[ord(ch) - ord("a")] += 1
        groups[tuple(key)].append(w)
    return list(groups.values())

assert is_anagram("listen", "silent") and not is_anagram("rat", "car")
g = group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
assert sorted(sorted(x) for x in g) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
g = group_anagrams_counting(["eat", "tea", "tan", "ate", "nat", "bat"])
assert sorted(sorted(x) for x in g) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
```

## First character that does not repeat
```python
def first_unique_char(s):
    count = Counter(s)
    for i, ch in enumerate(s):
        if count[ch] == 1:
            return i
    return -1

assert first_unique_char("leetcode") == 0
assert first_unique_char("loveleetcode") == 2
assert first_unique_char("aabb") == -1
```

## Palindromes and reversing
```python
def is_palindrome(s):                  # ignore case and non-alphanumerics
    l, r = 0, len(s) - 1
    while l < r:
        while l < r and not s[l].isalnum():
            l += 1
        while l < r and not s[r].isalnum():
            r -= 1
        if s[l].lower() != s[r].lower():
            return False
        l += 1
        r -= 1
    return True

def longest_palindromic_substring(s):  # expand around each centre, O(n^2)
    best = ""
    for c in range(len(s)):
        for l, r in ((c, c), (c, c + 1)):      # odd and even length centres
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            if r - l - 1 > len(best):
                best = s[l + 1:r]
    return best

def reverse_words(s):
    return " ".join(reversed(s.split()))      # split() with no argument drops extra spaces

def longest_common_prefix(words):
    if not words:
        return ""
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
    return prefix

assert is_palindrome("A man, a plan, a canal: Panama")
assert not is_palindrome("race a car")
assert is_palindrome("")
assert longest_palindromic_substring("babad") in ("bab", "aba")
assert longest_palindromic_substring("cbbd") == "bb"
assert reverse_words("  the sky   is blue ") == "blue is sky the"
assert longest_common_prefix(["flower", "flow", "flight"]) == "fl"
assert longest_common_prefix(["dog", "car"]) == ""
```

## Longest run of consecutive numbers
Put everything in a set. Only start counting at a number with no `x - 1` in the set, so each run is walked once: O(n).
```python
def longest_consecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:                 # x starts a run
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best

assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
assert longest_consecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert longest_consecutive([]) == 0
```

## A few more classics
```python
def contains_duplicate(nums):
    return len(set(nums)) != len(nums)

def is_valid_sudoku(board):
    seen = set()
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == ".":
                continue
            keys = [(v, "row", r), (v, "col", c), (v, "box", r // 3, c // 3)]
            if any(k in seen for k in keys):
                return False
            seen.update(keys)
    return True

def encode(strs):                          # length-prefix so any character is safe
    return "".join(f"{len(s)}#{s}" for s in strs)

def decode(s):
    out, i = [], 0
    while i < len(s):
        j = s.index("#", i)
        n = int(s[i:j])
        out.append(s[j + 1:j + 1 + n])
        i = j + 1 + n
    return out

def roman_to_int(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    for i, ch in enumerate(s):
        if i + 1 < len(s) and v[ch] < v[s[i + 1]]:
            total -= v[ch]
        else:
            total += v[ch]
    return total

assert contains_duplicate([1, 2, 3, 1]) and not contains_duplicate([1, 2, 3])
board = [["."] * 9 for _ in range(9)]
board[0][0] = "5"; board[0][8] = "5"
assert not is_valid_sudoku(board)
board[0][8] = "6"
assert is_valid_sudoku(board)
words = ["lint", "co#de", "", "love"]
assert decode(encode(words)) == words
assert roman_to_int("MCMXCIV") == 1994
assert roman_to_int("III") == 3
```

## Which structure
| Need | Use |
|---|---|
| Seen before? | `set` |
| Count items | `Counter` / `dict` |
| Group by a key | `defaultdict(list)` |
| Value -> index | `dict` |
| Keep insertion order, unique | `dict.fromkeys(items)` |
| Letters only (26) | list of 26 ints (`ord(c) - ord("a")`) |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Set / count | Contains Duplicate, Valid Anagram | Valid Anagram |
| Hash map | Two Sum, Group Anagrams, Top K Frequent Elements | Two Sum, Majority Element |
| Prefix/suffix + encoding | Product of Array Except Self, Encode and Decode Strings, Valid Sudoku | |
| Set walk | Longest Consecutive Sequence | Longest Consecutive Sequence |
| Palindromes | Valid Palindrome, Longest Palindromic Substring, Palindromic Substrings | Longest Palindromic Substring |
| Strings misc | | Reverse Words in a String, Roman to Integer, Longest Common Prefix, Count and Say, Compare Version Numbers |

## Mistakes to avoid
- Building a string with `s += ch` in a loop on big inputs. Use a list and `join`.
- Using a list as a dict key (`TypeError: unhashable`). Convert to a tuple.
- Comparing `Counter` objects when you wanted lengths too. `Counter(a) == Counter(b)` already covers it.
- Forgetting upper vs lower case or spaces when the problem says "ignore".
- `s.split(" ")` keeps empty strings for repeated spaces; `s.split()` does not.

## Check yourself
- Why is the Two Sum dict filled after the check?
- Why does `longest_consecutive` only start from numbers with no `x - 1`?
- How do you make a list usable as a dict key?
