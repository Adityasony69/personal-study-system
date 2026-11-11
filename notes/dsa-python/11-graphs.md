# Graphs: BFS, DFS, shortest path, topological sort (Python)

Every code block here was run with its asserts on Python 3.12.

## Words to know
- **Node (vertex)** and **edge**: a thing and a link between two things.
- **Directed**: edges have a direction (A -> B). **Undirected**: both ways.
- **Weighted**: edges carry a cost. **Cycle**: you can come back to where you started.
- **Connected component**: a group of nodes that can all reach each other.
- **Degree**: number of edges at a node. In directed graphs: in-degree and out-degree.

## Storing a graph: adjacency list
A `dict` (or list) of neighbours. O(V + E) space, the default choice.
```python
from collections import defaultdict, deque

def build_graph(n, edges, directed=False):
    g = defaultdict(list)
    for a, b in edges:
        g[a].append(b)
        if not directed:
            g[b].append(a)
    for i in range(n):
        g[i]                              # make sure isolated nodes exist
    return g

g = build_graph(5, [(0, 1), (0, 2), (1, 3)])
assert sorted(g[0]) == [1, 2] and g[4] == [] and sorted(g[3]) == [1]
```
An adjacency matrix (`n x n` grid of 0/1) is O(V^2) space: only good for small dense graphs.

## BFS: breadth-first search
Explore in rings around the start using a queue. In an **unweighted** graph the first time BFS reaches a node is the shortest path.
```python
def bfs_distances(g, start):
    dist = {start: 0}
    q = deque([start])
    while q:
        node = q.popleft()
        for nxt in g[node]:
            if nxt not in dist:           # "visited" check BEFORE pushing
                dist[nxt] = dist[node] + 1
                q.append(nxt)
    return dist

def shortest_path(g, start, goal):
    prev = {start: None}
    q = deque([start])
    while q:
        node = q.popleft()
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = prev[node]
            return path[::-1]
        for nxt in g[node]:
            if nxt not in prev:
                prev[nxt] = node
                q.append(nxt)
    return None

g = build_graph(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)])
assert bfs_distances(g, 0) == {0: 0, 1: 1, 2: 1, 3: 2, 4: 3}
assert shortest_path(g, 0, 4) in ([0, 1, 3, 4], [0, 2, 3, 4])
assert shortest_path(g, 0, 5) is None
assert shortest_path(g, 2, 2) == [2]
```

## DFS: depth-first search
Go as deep as possible, then back up. Use recursion or an explicit stack.
```python
def dfs_recursive(g, node, seen=None):
    seen = seen if seen is not None else set()
    seen.add(node)
    for nxt in g[node]:
        if nxt not in seen:
            dfs_recursive(g, nxt, seen)
    return seen

def dfs_iterative(g, start):
    seen, stack, order = set(), [start], []
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        stack.extend(reversed(g[node]))
    return order

def count_components(n, edges):
    g = build_graph(n, edges)
    seen, count = set(), 0
    for i in range(n):
        if i not in seen:
            dfs_recursive(g, i, seen)
            count += 1
    return count

def has_path(g, a, b):
    return b in dfs_recursive(g, a)

def has_cycle_undirected(n, edges):
    g = build_graph(n, edges)
    seen = set()

    def go(node, parent):
        seen.add(node)
        for nxt in g[node]:
            if nxt == parent:
                continue
            if nxt in seen or go(nxt, node):
                return True
        return False

    return any(go(i, -1) for i in range(n) if i not in seen)

def valid_tree(n, edges):                # connected + exactly n-1 edges
    return len(edges) == n - 1 and count_components(n, edges) == 1

g = build_graph(6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)])
assert dfs_recursive(g, 0) == {0, 1, 2, 3, 4}
assert dfs_iterative(g, 0) == [0, 1, 3, 2, 4]
assert count_components(5, [(0, 1), (1, 2), (3, 4)]) == 2
assert count_components(4, []) == 4
assert has_path(g, 0, 4) and not has_path(g, 0, 5)
assert has_cycle_undirected(4, [(0, 1), (1, 2), (2, 0)])
assert not has_cycle_undirected(4, [(0, 1), (1, 2), (2, 3)])
assert valid_tree(5, [(0, 1), (0, 2), (0, 3), (1, 4)])
assert not valid_tree(5, [(0, 1), (1, 2), (2, 3), (1, 3)])
```

## BFS or DFS?
| Need | Use |
|---|---|
| Shortest path, fewest steps (unweighted) | BFS |
| Level by level | BFS |
| Is it reachable / count components / cycle / all paths | DFS (or BFS) |
| Topological order, backtracking on a graph | DFS |
| Very deep graph (recursion limit) | BFS or iterative DFS |

## Grids are graphs too
Each cell is a node; its neighbours are up, down, left, right.
```python
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

def num_islands(grid):
    R, C = len(grid), len(grid[0])
    seen = set()

    def sink(r, c):
        stack = [(r, c)]
        while stack:
            r, c = stack.pop()
            if not (0 <= r < R and 0 <= c < C) or grid[r][c] != "1" or (r, c) in seen:
                continue
            seen.add((r, c))
            for dr, dc in DIRS:
                stack.append((r + dr, c + dc))

    count = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == "1" and (r, c) not in seen:
                sink(r, c)
                count += 1
    return count

def max_area_of_island(grid):
    R, C = len(grid), len(grid[0])
    best = 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 1:
                area, stack = 0, [(r, c)]
                grid[r][c] = 0           # mark visited by overwriting
                while stack:
                    cr, cc = stack.pop()
                    area += 1
                    for dr, dc in DIRS:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                            grid[nr][nc] = 0
                            stack.append((nr, nc))
                best = max(best, area)
    return best

def shortest_path_binary_matrix(grid):   # 8 directions, BFS, 0 = open
    n = len(grid)
    if grid[0][0] or grid[-1][-1]:
        return -1
    q, seen = deque([(0, 0, 1)]), {(0, 0)}
    while q:
        r, c, d = q.popleft()
        if (r, c) == (n - 1, n - 1):
            return d
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and not grid[nr][nc] and (nr, nc) not in seen:
                    seen.add((nr, nc))
                    q.append((nr, nc, d + 1))
    return -1

def clone_graph(node_map):               # adjacency dict {val: [neighbour vals]} -> deep copy
    return {k: list(v) for k, v in node_map.items()}

def pacific_atlantic(h):                 # cells whose water can reach both oceans
    R, C = len(h), len(h[0])

    def flow(starts):
        seen, stack = set(starts), list(starts)
        while stack:
            r, c = stack.pop()
            for dr, dc in DIRS:
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen and h[nr][nc] >= h[r][c]:
                    seen.add((nr, nc))
                    stack.append((nr, nc))
        return seen

    pac = flow([(0, c) for c in range(C)] + [(r, 0) for r in range(R)])
    atl = flow([(R - 1, c) for c in range(C)] + [(r, C - 1) for r in range(R)])
    return sorted(pac & atl)

grid = [list("11000"), list("11000"), list("00100"), list("00011")]
assert num_islands(grid) == 3
assert num_islands([list("111"), list("010"), list("111")]) == 1
assert max_area_of_island([[0, 1, 1], [0, 1, 0], [1, 0, 1]]) == 3
assert shortest_path_binary_matrix([[0, 1], [1, 0]]) == 2
assert shortest_path_binary_matrix([[0, 0, 0], [1, 1, 0], [1, 1, 0]]) == 4
assert shortest_path_binary_matrix([[1, 0], [0, 0]]) == -1
assert pacific_atlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]) == \
    [(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]
assert clone_graph({1: [2], 2: [1]}) == {1: [2], 2: [1]}
```

## Union-Find (disjoint set)
Great for "are these connected?" with edges arriving one by one, and for cycle detection.
```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]     # path compression (halving)
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                 # already together: this edge makes a cycle
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        self.components -= 1
        return True

def redundant_connection(edges):         # the edge that closes a cycle
    uf = UnionFind(len(edges) + 1)
    for a, b in edges:
        if not uf.union(a, b):
            return [a, b]

uf = UnionFind(5)
assert uf.union(0, 1) and uf.union(1, 2) and not uf.union(0, 2)
assert uf.find(0) == uf.find(2) and uf.find(3) != uf.find(0) and uf.components == 3
assert redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert redundant_connection([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]
```

## Dijkstra: shortest path with weights
Like BFS, but a **min-heap** picks the cheapest frontier node. Non-negative weights only. O((V + E) log V).
```python
import heapq

def dijkstra(g, start):                  # g: {node: [(neighbour, weight), ...]}
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue                     # stale entry: we already found better
        for nxt, w in g.get(node, []):
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(heap, (nd, nxt))
    return dist

def network_delay_time(times, n, k):     # time for a signal from k to reach all n nodes
    g = defaultdict(list)
    for u, v, w in times:
        g[u].append((v, w))
    dist = dijkstra(g, k)
    return max(dist.values()) if len(dist) == n else -1

def cheapest_flights_within_k_stops(n, flights, src, dst, k):   # Bellman-Ford, k+1 rounds
    prices = [float("inf")] * n
    prices[src] = 0
    for _ in range(k + 1):
        nxt = prices[:]
        for u, v, w in flights:
            if prices[u] + w < nxt[v]:
                nxt[v] = prices[u] + w
        prices = nxt
    return -1 if prices[dst] == float("inf") else prices[dst]

g = {"A": [("B", 1), ("C", 4)], "B": [("C", 2), ("D", 6)], "C": [("D", 3)], "D": []}
assert dijkstra(g, "A") == {"A": 0, "B": 1, "C": 3, "D": 6}
assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
assert network_delay_time([[1, 2, 1]], 2, 2) == -1
f = [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]]
assert cheapest_flights_within_k_stops(4, f, 0, 3, 1) == 700
assert cheapest_flights_within_k_stops(4, f, 0, 3, 0) == -1
```
Negative weights break Dijkstra; use Bellman-Ford (above). For "fewest steps" with equal weights, plain BFS is simpler.

## Topological sort
Order the nodes of a **directed acyclic graph** so every edge points forward (course prerequisites, build order). If there is a cycle, no order exists.

**Kahn's algorithm (BFS):** repeatedly take nodes with no remaining prerequisites.
```python
def topo_sort(n, edges):                 # edge (a, b): a must come before b
    g = defaultdict(list)
    indeg = [0] * n
    for a, b in edges:
        g[a].append(b)
        indeg[b] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in g[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return order if len(order) == n else []      # short result means a cycle

def can_finish(num_courses, prerequisites):      # prerequisites [course, needs]
    return len(topo_sort(num_courses, [(b, a) for a, b in prerequisites])) == num_courses

def find_order(num_courses, prerequisites):
    return topo_sort(num_courses, [(b, a) for a, b in prerequisites])

def alien_order(words):                  # derive letter order from a sorted alien dictionary
    letters = {c: set() for w in words for c in w}
    for a, b in zip(words, words[1:]):
        for x, y in zip(a, b):
            if x != y:
                letters[x].add(y)
                break
        else:
            if len(a) > len(b):
                return ""                # "abc" before "ab" is impossible
    indeg = {c: 0 for c in letters}
    for c in letters:
        for d in letters[c]:
            indeg[d] += 1
    q = deque(c for c in letters if indeg[c] == 0)
    out = []
    while q:
        c = q.popleft()
        out.append(c)
        for d in letters[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                q.append(d)
    return "".join(out) if len(out) == len(letters) else ""

order = topo_sort(6, [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)])
pos = {v: i for i, v in enumerate(order)}
assert len(order) == 6 and all(pos[a] < pos[b] for a, b in [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)])
assert topo_sort(2, [(0, 1), (1, 0)]) == []
assert can_finish(2, [[1, 0]]) and not can_finish(2, [[1, 0], [0, 1]])
assert find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])[0] == 0
assert alien_order(["wrt", "wrf", "er", "ett", "rftt"]) == "wertf"
assert alien_order(["abc", "ab"]) == ""
```

## Complexity
| Algorithm | Time | Space |
|---|---|---|
| BFS / DFS | O(V + E) | O(V) |
| Union-Find | ~O(alpha(n)) per op, nearly constant | O(V) |
| Dijkstra | O((V + E) log V) | O(V) |
| Bellman-Ford | O(V * E) | O(V) |
| Topological sort | O(V + E) | O(V) |

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Grid DFS/BFS | Number of Islands, Max Area of Island, Pacific Atlantic Water Flow, Surrounded Regions, Rotting Oranges, Walls and Gates | Number of Islands, Rotting Oranges |
| Graph copy | Clone Graph | Clone Graph |
| Topological | Course Schedule, Course Schedule II, Alien Dictionary | Course Schedule I, II |
| Union-Find | Redundant Connection, Number of Connected Components in an Undirected Graph, Graph Valid Tree | |
| Shortest path | Network Delay Time, Cheapest Flights Within K Stops, Min Cost to Connect All Points, Swim in Rising Water | |
| Hard / other | Word Ladder, Reconstruct Itinerary | (Detect cycles, bipartite, bridges in the graph sections of the sheet) |

## Mistakes to avoid
- Marking visited **when you pop**, not when you push, in BFS: the same node gets queued many times.
- Forgetting the `seen` set in a graph with cycles: infinite loop.
- Using DFS for "shortest path" in an unweighted graph. Use BFS.
- Using Dijkstra with negative weights.
- Grid bounds check order: test `0 <= r < R` before indexing.
- `defaultdict` side effect: reading `g[x]` creates the key.
- Recursive DFS on a huge graph or long path: `RecursionError`. Use the stack version.

## Check yourself
- Why does BFS find shortest paths in an unweighted graph?
- What does a topological sort that returns fewer than n nodes tell you?
- Why does Dijkstra skip a popped entry whose distance is stale?
