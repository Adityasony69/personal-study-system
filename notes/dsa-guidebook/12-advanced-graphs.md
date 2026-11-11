# Advanced Graphs

**10 questions:** 0 Easy, 4 Medium, 6 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Graphs where edges have weights: shortest paths (Dijkstra, Bellman-Ford) and cheapest way to connect everything (Prim, Kruskal).

## How to spot this pattern

- Costs, times or distances on edges.
- "Cheapest", "minimum time", "connect all points".

## Thinking steps (use these on every question here)

1. Non-negative weights and shortest path: Dijkstra with a min-heap.
2. A limit on the number of edges: Bellman-Ford rounds.
3. Connect everything cheaply: Prim (heap) or Kruskal (sort edges + union-find).
4. Ordering letters or tasks: topological sort.

## Common beginner mistakes

- Using plain BFS when edges have different weights.
- Not skipping stale heap entries in Dijkstra.

Read first: your `dsa-python` notes, file(s) 11-graphs.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Path with Minimum Effort | Medium | 1631 | 250 |
| 2 | Network Delay Time | Medium | 743 | 150 |
| 3 | Min Cost to Connect All Points | Medium | 1584 | 150 |
| 4 | Cheapest Flights Within K Stops | Medium | 787 | 150 |
| 5 | Reconstruct Itinerary | Hard | 332 | 150 |
| 6 | Swim In Rising Water | Hard | 778 | 150 |
| 7 | Alien Dictionary | Hard | 269 | 150 |
| 8 | Find Critical and Pseudo Critical Edges in Minimum Spanning Tree | Hard | 1489 | 250 |
| 9 | Build a Matrix With Conditions | Hard | 2392 | 250 |
| 10 | Greatest Common Divisor Traversal | Hard | 2709 | 250 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Medium questions

### 1. Path with Minimum Effort  [Medium]

- **Find it:** LeetCode #1631, search "Path with Minimum Effort"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** The cost of a path is its LARGEST step, not the sum.
- **First step:** Modify Dijkstra.
- **If stuck:** Distance to a neighbour = max(effort so far, height difference); pop the smallest effort from a heap.

### 2. Network Delay Time  [Medium]

- **Find it:** LeetCode #743, search "Network Delay Time"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Time for a signal to reach everyone = the longest of the shortest paths.
- **First step:** Run Dijkstra from the source.
- **If stuck:** The answer is the largest distance; if some node was never reached return -1.

### 3. Min Cost to Connect All Points  [Medium]

- **Find it:** LeetCode #1584, search "Min Cost to Connect All Points"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Connect all points with the least total cost: minimum spanning tree.
- **First step:** Edge cost is the Manhattan distance between two points.
- **If stuck:** Prim algorithm: grow from one point, always adding the cheapest edge to an unvisited point (heap).

### 4. Cheapest Flights Within K Stops  [Medium]

- **Find it:** LeetCode #787, search "Cheapest Flights Within K Stops"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Shortest path with a limit on the number of edges.
- **First step:** Plain Dijkstra ignores the stop limit.
- **If stuck:** Bellman-Ford style: repeat k+1 rounds, each round relaxing all flights using a COPY of the prices from the previous round.

## Hard questions

### 5. Reconstruct Itinerary  [Hard]

- **Find it:** LeetCode #332, search "Reconstruct Itinerary"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Use every ticket exactly once, smallest lexical order.
- **First step:** Sort the destinations of each airport.
- **If stuck:** DFS always taking the smallest unused destination; add the airport to the route AFTER its edges are used, then reverse the route.

### 6. Swim In Rising Water  [Hard]

- **Find it:** LeetCode #778, search "Swim In Rising Water"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You want the path whose highest cell is as low as possible.
- **First step:** Same shape as Path With Minimum Effort.
- **If stuck:** Dijkstra where the path cost is the max elevation seen so far; answer when you pop the bottom-right cell.

### 7. Alien Dictionary  [Hard]

- **Find it:** LeetCode #269, search "Alien Dictionary"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Each neighbouring pair of words gives one rule "letter a comes before letter b".
- **First step:** Compare neighbouring words at their first different letter to build edges.
- **If stuck:** Topological sort the letters; a cycle, or a longer word before its own prefix, means no valid order.

### 8. Find Critical and Pseudo Critical Edges in Minimum Spanning Tree  [Hard]

- **Find it:** LeetCode #1489, search "Find Critical and Pseudo Critical Edges in Minimum Spanning Tree"
- **Lists:** NeetCode 250
- **Notice:** Test each edge by building MSTs with and without it.
- **First step:** Write a Kruskal function with union-find; get the base MST weight.
- **If stuck:** Critical: skipping it makes the weight bigger (or disconnects). Pseudo-critical: forcing it first still gives the base weight.

### 9. Build a Matrix With Conditions  [Hard]

- **Find it:** LeetCode #2392, search "Build a Matrix With Conditions"
- **Lists:** NeetCode 250
- **Notice:** Row rules and column rules are independent.
- **First step:** Each set of conditions is an ordering problem.
- **If stuck:** Topological sort for row order and again for column order; place number k at (rowPos[k], colPos[k]). A cycle means no answer.

### 10. Greatest Common Divisor Traversal  [Hard]

- **Find it:** LeetCode #2709, search "Greatest Common Divisor Traversal"
- **Lists:** NeetCode 250
- **Notice:** Two numbers connect if they share a prime factor.
- **First step:** Do not compare every pair; link numbers through their prime factors.
- **If stuck:** Union each number with its prime factors (union-find); the answer is whether everything ends up in one group. Watch the value 1.
