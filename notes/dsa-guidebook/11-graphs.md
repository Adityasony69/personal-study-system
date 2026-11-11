# Graphs

**21 questions:** 3 Easy, 17 Medium, 1 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Things connected to other things. Most questions are solved by visiting everything reachable with DFS or BFS and a visited set.

## How to spot this pattern

- Grids of cells, networks, prerequisites, connections.
- "Shortest number of steps" on unweighted moves means BFS.
- "Order" with dependencies means topological sort.
- "Are these connected" or groups means union-find or DFS.

## Thinking steps (use these on every question here)

1. Decide what a node is and what an edge is.
2. Build an adjacency list if you are given edges.
3. Pick the tool: DFS (explore), BFS (shortest steps), topological sort (ordering), union-find (grouping).
4. Always keep a visited set.

## Common beginner mistakes

- Marking visited too late in BFS, so nodes enter the queue many times.
- Forgetting grid boundary checks.

Read first: your `dsa-python` notes, file(s) 11-graphs.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Island Perimeter | Easy | 463 | 250 |
| 2 | Verifying An Alien Dictionary | Easy | 953 | 250 |
| 3 | Find the Town Judge | Easy | 997 | 250 |
| 4 | Number of Islands | Medium | 200 | 150 |
| 5 | Max Area of Island | Medium | 695 | 150 |
| 6 | Clone Graph | Medium | 133 | 150 |
| 7 | Walls And Gates | Medium | 286 | 150 |
| 8 | Rotting Oranges | Medium | 994 | 150 |
| 9 | Pacific Atlantic Water Flow | Medium | 417 | 150 |
| 10 | Surrounded Regions | Medium | 130 | 150 |
| 11 | Open The Lock | Medium | 752 | 250 |
| 12 | Course Schedule | Medium | 207 | 150 |
| 13 | Course Schedule II | Medium | 210 | 150 |
| 14 | Graph Valid Tree | Medium | 261 | 150 |
| 15 | Course Schedule IV | Medium | 1462 | 250 |
| 16 | Number of Connected Components In An Undirected Graph | Medium | 323 | 150 |
| 17 | Redundant Connection | Medium | 684 | 150 |
| 18 | Accounts Merge | Medium | 721 | 250 |
| 19 | Evaluate Division | Medium | 399 | 250 |
| 20 | Minimum Height Trees | Medium | 310 | 250 |
| 21 | Word Ladder | Hard | 127 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Island Perimeter  [Easy]

- **Find it:** LeetCode #463, search "Island Perimeter"
- **Lists:** NeetCode 250
- **Notice:** Every land cell brings 4 edges; shared edges do not count.
- **First step:** Loop over all cells.
- **If stuck:** For each land cell add 4 and subtract 1 for every land neighbour (or count edges touching water/border).

### 2. Verifying An Alien Dictionary  [Easy]

- **Find it:** LeetCode #953, search "Verifying An Alien Dictionary"
- **Lists:** NeetCode 250
- **Notice:** Compare words the way a dictionary does, with a different alphabet order.
- **First step:** Map each letter to its rank.
- **If stuck:** Compare each neighbouring pair at the first differing letter; also a longer word may not come before its own prefix.

### 3. Find the Town Judge  [Easy]

- **Find it:** LeetCode #997, search "Find the Town Judge"
- **Lists:** NeetCode 250
- **Notice:** The judge trusts nobody and is trusted by everyone else.
- **First step:** Count for each person: trusted-by minus trusts.
- **If stuck:** The judge is the person whose score is n - 1.

## Medium questions

### 4. Number of Islands  [Medium]

- **Find it:** LeetCode #200, search "Number of Islands"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Connected groups of land cells.
- **First step:** Scan the grid; each time you find unvisited land, that is a new island.
- **If stuck:** From that cell run DFS or BFS marking all connected land as visited.

### 5. Max Area of Island  [Medium]

- **Find it:** LeetCode #695, search "Max Area of Island"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Same as Number of Islands, but measure each island.
- **First step:** Make the DFS return a count.
- **If stuck:** return 1 + the sum of DFS on the four neighbours.

### 6. Clone Graph  [Medium]

- **Find it:** LeetCode #133, search "Clone Graph"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Cycles mean you may reach a node you have already copied.
- **First step:** Keep a dictionary old node -> copy.
- **If stuck:** DFS: if the node is in the dictionary return its copy; otherwise create the copy, store it, then clone its neighbours.

### 7. Walls And Gates  [Medium]

- **Find it:** LeetCode #286, search "Walls And Gates"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Distance to the NEAREST gate for every room.
- **First step:** BFS from each room is too slow; flip it around.
- **If stuck:** Put ALL gates in the queue at the start (multi-source BFS) and spread outward level by level.

### 8. Rotting Oranges  [Medium]

- **Find it:** LeetCode #994, search "Rotting Oranges"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Rot spreads one step per minute from all rotten oranges at once.
- **First step:** Multi-source BFS starting with every rotten orange.
- **If stuck:** Count fresh oranges at the start; each BFS level is one minute; at the end fresh must be 0.

### 9. Pacific Atlantic Water Flow  [Medium]

- **Find it:** LeetCode #417, search "Pacific Atlantic Water Flow"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Checking the downhill path of every cell is slow.
- **First step:** Start from the oceans and climb UPHILL instead.
- **If stuck:** Run DFS/BFS from the Pacific border and from the Atlantic border; the answer is cells reached by both.

### 10. Surrounded Regions  [Medium]

- **Find it:** LeetCode #130, search "Surrounded Regions"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** An "O" region survives only if it touches the border.
- **First step:** Start from the border "O" cells.
- **If stuck:** Mark everything connected to the border as safe; flip all other "O" to "X"; restore the safe ones.

### 11. Open The Lock  [Medium]

- **Find it:** LeetCode #752, search "Open The Lock"
- **Lists:** NeetCode 250
- **Notice:** Fewest moves from 0000 to the target: shortest path.
- **First step:** Each state has 8 neighbours (each wheel up or down).
- **If stuck:** BFS with a visited set; treat dead ends as already visited.

### 12. Course Schedule  [Medium]

- **Find it:** LeetCode #207, search "Course Schedule"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Can all courses be finished = is there a cycle in a directed graph?
- **First step:** Build an adjacency list of prerequisites.
- **If stuck:** DFS with three states (unvisited, in progress, done): reaching an "in progress" node means a cycle. Or use the Kahn algorithm.

### 13. Course Schedule II  [Medium]

- **Find it:** LeetCode #210, search "Course Schedule II"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Now return a valid order: topological sort.
- **First step:** Compute the in-degree of every course.
- **If stuck:** Kahn algorithm: queue the courses with in-degree 0, pop, reduce the in-degrees of neighbours; if the order is shorter than n there is a cycle.

### 14. Graph Valid Tree  [Medium]

- **Find it:** LeetCode #261, search "Graph Valid Tree"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A tree has exactly n - 1 edges, is connected, and has no cycle.
- **First step:** Check the edge count first.
- **If stuck:** Then DFS/BFS from node 0 and see that all n nodes are reached (or use union-find).

### 15. Course Schedule IV  [Medium]

- **Find it:** LeetCode #1462, search "Course Schedule IV"
- **Lists:** NeetCode 250
- **Notice:** Many queries asking "is a a prerequisite of b, directly or indirectly?"
- **First step:** For each course compute the full set of its prerequisites.
- **If stuck:** DFS with memoization, or process in topological order merging prerequisite sets.

### 16. Number of Connected Components In An Undirected Graph  [Medium]

- **Find it:** LeetCode #323, search "Number of Connected Components In An Undirected Graph"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Count separate groups.
- **First step:** Loop over the nodes; each unvisited node starts a new component.
- **If stuck:** DFS to mark its whole group. Or union-find: start with n and subtract 1 per successful union.

### 17. Redundant Connection  [Medium]

- **Find it:** LeetCode #684, search "Redundant Connection"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** The extra edge is the one joining two nodes that are already connected.
- **First step:** Use union-find.
- **If stuck:** Process edges in order; the first edge whose two ends already have the same root is the answer.

### 18. Accounts Merge  [Medium]

- **Find it:** LeetCode #721, search "Accounts Merge"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Accounts sharing any email belong to the same person.
- **First step:** Treat each email as a node and link the emails inside one account.
- **If stuck:** Union-find over emails (or accounts), then group emails by root and sort each group.

### 19. Evaluate Division  [Medium]

- **Find it:** LeetCode #399, search "Evaluate Division"
- **Lists:** NeetCode 250
- **Notice:** a / b = 2 is a weighted edge a -> b (2) and b -> a (1/2).
- **First step:** Build a graph from the equations.
- **If stuck:** To answer a query, DFS/BFS from the numerator to the denominator multiplying the edge weights.

### 20. Minimum Height Trees  [Medium]

- **Find it:** LeetCode #310, search "Minimum Height Trees"
- **Lists:** NeetCode 250
- **Notice:** The best roots are in the centre of the tree.
- **First step:** Think about peeling leaves off, layer by layer.
- **If stuck:** Repeatedly remove all current leaves (degree 1) until 1 or 2 nodes remain.

## Hard questions

### 21. Word Ladder  [Hard]

- **Find it:** LeetCode #127, search "Word Ladder"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Shortest transformation sequence = BFS.
- **First step:** Two words are neighbours if they differ by one letter.
- **If stuck:** For each word try changing each position to a-z and check the word set; or bucket words by patterns like h*t.
