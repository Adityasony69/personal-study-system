# Tries

**4 questions:** 0 Easy, 3 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A trie is a tree of letters. Words that share a beginning share the same path.

## How to spot this pattern

- Words like: prefix, starts with, dictionary of words, autocomplete.
- Many words searched against the same text or board.

## Thinking steps (use these on every question here)

1. Make a node with a children dictionary and an end-of-word flag.
2. Insert: walk letter by letter creating missing nodes.
3. Search: walk letter by letter; fail if a child is missing.

## Common beginner mistakes

- Forgetting the end-of-word flag, so prefixes are reported as words.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Implement Trie Prefix Tree | Medium | 208 | 150 |
| 2 | Design Add And Search Words Data Structure | Medium | 211 | 150 |
| 3 | Extra Characters in a String | Medium | 2707 | 250 |
| 4 | Word Search II | Hard | 212 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Medium questions

### 1. Implement Trie Prefix Tree  [Medium]

- **Find it:** LeetCode #208, search "Implement Trie Prefix Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Words sharing a prefix share a path.
- **First step:** Each node has a dictionary of children and an "end of word" flag.
- **If stuck:** Insert walks and creates nodes; search needs the end flag; startsWith only needs the path to exist.

### 2. Design Add And Search Words Data Structure  [Medium]

- **Find it:** LeetCode #211, search "Design Add And Search Words Data Structure"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A "." can match any letter.
- **First step:** Build a normal trie.
- **If stuck:** In search, when you hit "." try every child with a recursive call.

### 3. Extra Characters in a String  [Medium]

- **Find it:** LeetCode #2707, search "Extra Characters in a String"
- **Lists:** NeetCode 250
- **Notice:** Minimise leftover characters after cutting out dictionary words.
- **First step:** dp[i] = fewest extra characters from index i to the end.
- **If stuck:** Option 1: skip s[i] (1 + dp[i+1]); option 2: any word starting at i gives dp[i + len(word)]. A trie speeds up the matching.

## Hard questions

### 4. Word Search II  [Hard]

- **Find it:** LeetCode #212, search "Word Search II"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Many words on the same board: searching each word separately is too slow.
- **First step:** Put all the words in a trie.
- **If stuck:** DFS from each cell walking the trie at the same time; stop when the path is not a prefix. Remove found words to avoid repeats.
