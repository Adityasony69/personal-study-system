# Strings and hashing

## Hashing in one paragraph
A HashMap turns a key into a number (its hash) and uses that number to jump straight to a bucket. That is why `put`, `get` and `contains` are O(1) on average instead of O(n). You pay with extra memory. The whole topic is one trade: **use memory to remember what you have seen, so you never search for it again.**

Signals that a problem wants a HashMap or HashSet:
- "count how many times each..."
- "have we seen this before?"
- "find a pair that..."
- "group the items that share..."

## Counting

```java
static Map<Character, Integer> countLetters(String s) {
    Map<Character, Integer> freq = new HashMap<>();
    for (char c : s.toCharArray()) {
        freq.put(c, freq.getOrDefault(c, 0) + 1);
    }
    return freq;
}

static int[] countLowercase(String s) {    // faster when you know it is only a to z
    int[] count = new int[26];
    for (char c : s.toCharArray()) {
        count[c - 'a']++;
    }
    return count;
}
```

## Two Sum: the classic
Find two indexes whose values add to the target. Brute force checks every pair, O(n^2). With a map: for each number, ask whether the number it needs has already gone past.

```java
static int[] twoSum(int[] a, int target) {
    Map<Integer, Integer> indexOf = new HashMap<>();   // value -> index where we saw it
    for (int i = 0; i < a.length; i++) {
        Integer j = indexOf.get(target - a[i]);
        if (j != null) return new int[]{j, i};
        indexOf.put(a[i], i);                          // store after checking, so i is not paired with itself
    }
    return new int[0];
}
```

O(n) time, O(n) space.

## Anagrams
Two words are anagrams when they use the same letters the same number of times.

```java
static boolean isAnagram(String s, String t) {
    if (s.length() != t.length()) return false;
    int[] count = new int[26];
    for (char c : s.toCharArray()) count[c - 'a']++;
    for (char c : t.toCharArray()) {
        if (--count[c - 'a'] < 0) return false;        // t has a letter s does not have enough of
    }
    return true;
}

static List<List<String>> groupAnagrams(String[] words) {
    Map<String, List<String>> groups = new HashMap<>();
    for (String w : words) {
        char[] letters = w.toCharArray();
        Arrays.sort(letters);
        String key = new String(letters);              // "eat" and "tea" both become "aet"
        groups.computeIfAbsent(key, k -> new ArrayList<>()).add(w);
    }
    return new ArrayList<>(groups.values());
}
```

## First character that does not repeat

```java
static int firstUniqueIndex(String s) {
    int[] count = new int[26];
    for (char c : s.toCharArray()) count[c - 'a']++;
    for (int i = 0; i < s.length(); i++) {
        if (count[s.charAt(i) - 'a'] == 1) return i;
    }
    return -1;
}
```

Two passes: count everything first, then find the first one with count 1.

## Palindromes and reversing

```java
static boolean isPalindrome(String s) {
    int l = 0, r = s.length() - 1;
    while (l < r) {
        if (s.charAt(l) != s.charAt(r)) return false;
        l++;
        r--;
    }
    return true;
}

static String reverseWords(String s) {                 // "the sky is blue" -> "blue is sky the"
    String[] words = s.trim().split("\\s+");
    StringBuilder sb = new StringBuilder();
    for (int i = words.length - 1; i >= 0; i--) {
        sb.append(words[i]);
        if (i > 0) sb.append(' ');
    }
    return sb.toString();
}
```

## Longest run of consecutive numbers
`[100, 4, 200, 1, 3, 2]` gives 4, because of 1, 2, 3, 4. Put everything in a set, then only start counting from numbers that are the beginning of a run.

```java
static int longestConsecutive(int[] a) {
    Set<Integer> set = new HashSet<>();
    for (int x : a) set.add(x);
    int best = 0;
    for (int x : set) {
        if (set.contains(x - 1)) continue;             // not the start of a run
        int length = 1;
        while (set.contains(x + length)) length++;
        best = Math.max(best, length);
    }
    return best;
}
```

O(n) overall: each number is visited by the inner loop at most once.

## Which structure
| Need | Use |
|---|---|
| Count lowercase letters | `int[26]` |
| Count anything else | `HashMap<Thing, Integer>` |
| Only "seen or not" | `HashSet` |
| Keep keys sorted | `TreeMap` |
| Remember the order things were added | `LinkedHashMap` |

## Mistakes to avoid
- Comparing strings with `==`.
- Building a string with `+` in a loop. Use `StringBuilder`.
- Using a `char[]` or `int[]` as a map key: arrays compare by identity. Turn it into a `String` first.
- `map.get(key)` on a missing key gives `null`. Use `getOrDefault`.

## Check yourself
- Why is Two Sum O(n) with a map but O(n^2) without?
- Why does `groupAnagrams` sort the letters of each word?
- In `longestConsecutive`, why skip numbers that have `x - 1` in the set?
