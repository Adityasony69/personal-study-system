# Graphs: BFS, DFS, shortest path, topological sort

## Words to know
- **Graph:** nodes (also called vertices) joined by edges. A tree is a graph with no cycles and one path between any two nodes.
- **Undirected:** edges go both ways (friendship). **Directed:** edges have a direction (follows).
- **Weighted:** each edge has a cost (road length).
- **Cycle:** a path that comes back to where it started.

V = number of nodes, E = number of edges.

## Storing a graph: adjacency list
For each node, keep a list of its neighbours. Uses O(V + E) memory and is the default choice.

```java
static List<List<Integer>> buildGraph(int n, int[][] edges, boolean directed) {
    List<List<Integer>> graph = new ArrayList<>();
    for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
    for (int[] e : edges) {
        graph.get(e[0]).add(e[1]);
        if (!directed) graph.get(e[1]).add(e[0]);      // both directions
    }
    return graph;
}
```

The other option is an adjacency matrix, `boolean[n][n]`. It answers "is there an edge between a and b?" in O(1) but always uses O(V^2) memory.

## BFS: breadth-first search
Explore in rings: the start, then everything one step away, then two steps away. Uses a **queue**. Because of the ring order, BFS finds the shortest path when every edge counts the same.

```java
static List<Integer> bfs(List<List<Integer>> graph, int start) {
    List<Integer> order = new ArrayList<>();
    boolean[] visited = new boolean[graph.size()];
    Queue<Integer> queue = new ArrayDeque<>();
    visited[start] = true;                             // mark when adding, not when removing
    queue.offer(start);
    while (!queue.isEmpty()) {
        int node = queue.poll();
        order.add(node);
        for (int next : graph.get(node)) {
            if (!visited[next]) {
                visited[next] = true;
                queue.offer(next);
            }
        }
    }
    return order;
}

static int[] shortestSteps(List<List<Integer>> graph, int start) {   // -1 = cannot be reached
    int[] dist = new int[graph.size()];
    Arrays.fill(dist, -1);
    Queue<Integer> queue = new ArrayDeque<>();
    dist[start] = 0;
    queue.offer(start);
    while (!queue.isEmpty()) {
        int node = queue.poll();
        for (int next : graph.get(node)) {
            if (dist[next] == -1) {
                dist[next] = dist[node] + 1;
                queue.offer(next);
            }
        }
    }
    return dist;
}
```

## DFS: depth-first search
Go as deep as possible along one path, then back up and try the next. Uses **recursion** (or a stack).

```java
static void dfs(List<List<Integer>> graph, int node, boolean[] visited, List<Integer> order) {
    visited[node] = true;
    order.add(node);
    for (int next : graph.get(node)) {
        if (!visited[next]) dfs(graph, next, visited, order);
    }
}

static int countComponents(List<List<Integer>> graph) {   // number of separate groups
    boolean[] visited = new boolean[graph.size()];
    int groups = 0;
    for (int node = 0; node < graph.size(); node++) {
        if (!visited[node]) {
            groups++;
            dfs(graph, node, visited, new ArrayList<>());   // marks everything connected to node
        }
    }
    return groups;
}
```

Both BFS and DFS are O(V + E): each node and each edge is handled once.

## BFS or DFS?
| Need | Use |
|---|---|
| Shortest path, all edges equal | BFS |
| Level by level, "minimum number of moves" | BFS |
| Does a path exist? Count the groups | Either |
| Detect a cycle, explore every path, topological sort | DFS |

## Grids are graphs too
Each cell is a node, and its neighbours are up, down, left and right. Counting islands: every time you find unvisited land, that is a new island, so flood it.

```java
static int countIslands(char[][] grid) {
    int islands = 0;
    for (int r = 0; r < grid.length; r++) {
        for (int c = 0; c < grid[0].length; c++) {
            if (grid[r][c] == '1') {
                islands++;
                sink(grid, r, c);
            }
        }
    }
    return islands;
}

static void sink(char[][] grid, int r, int c) {
    if (r < 0 || c < 0 || r >= grid.length || c >= grid[0].length || grid[r][c] != '1') return;
    grid[r][c] = '0';                                  // mark as visited by changing it
    sink(grid, r + 1, c);
    sink(grid, r - 1, c);
    sink(grid, r, c + 1);
    sink(grid, r, c - 1);
}
```

## Dijkstra: shortest path with weights
When edges have different costs (none negative), BFS is no longer enough. Dijkstra always expands the closest unfinished node next, using a min-heap.

```java
static int[] dijkstra(List<List<int[]>> graph, int start) {    // graph.get(u) holds {v, weight} pairs
    int[] dist = new int[graph.size()];
    Arrays.fill(dist, Integer.MAX_VALUE);
    dist[start] = 0;
    PriorityQueue<int[]> heap = new PriorityQueue<>((p, q) -> Integer.compare(p[1], q[1]));  // {node, distance}
    heap.offer(new int[]{start, 0});
    while (!heap.isEmpty()) {
        int[] top = heap.poll();
        int node = top[0], d = top[1];
        if (d > dist[node]) continue;                  // an old, worse entry: skip it
        for (int[] edge : graph.get(node)) {
            int next = edge[0], candidate = d + edge[1];
            if (candidate < dist[next]) {
                dist[next] = candidate;
                heap.offer(new int[]{next, candidate});
            }
        }
    }
    return dist;                                       // Integer.MAX_VALUE = cannot be reached
}
```

O((V + E) log V). It gives wrong answers if any edge weight is negative.

## Topological sort
For a directed graph with no cycles (a DAG), put the nodes in an order where every edge points forward. Think "course A must come before course B".

**Kahn's algorithm:** the in-degree of a node is the number of edges coming into it. Nodes with in-degree 0 have nothing left to wait for, so take them, then lower the in-degree of their neighbours.

```java
static List<Integer> topologicalOrder(int n, int[][] edges) {   // edge {a, b} means a comes before b
    List<List<Integer>> graph = new ArrayList<>();
    for (int i = 0; i < n; i++) graph.add(new ArrayList<>());
    int[] indegree = new int[n];
    for (int[] e : edges) {
        graph.get(e[0]).add(e[1]);
        indegree[e[1]]++;
    }
    Queue<Integer> ready = new ArrayDeque<>();
    for (int i = 0; i < n; i++) {
        if (indegree[i] == 0) ready.offer(i);
    }
    List<Integer> order = new ArrayList<>();
    while (!ready.isEmpty()) {
        int node = ready.poll();
        order.add(node);
        for (int next : graph.get(node)) {
            if (--indegree[next] == 0) ready.offer(next);
        }
    }
    return order.size() == n ? order : new ArrayList<>();   // empty list = there was a cycle
}
```

If the order ends up shorter than n, some nodes never reached in-degree 0, which means the graph has a cycle.

## Mistakes to avoid
- No visited set: on a graph with a cycle the search never ends.
- Marking a node visited when you take it out of the queue instead of when you put it in. The same node gets queued many times.
- Using BFS for shortest path on a weighted graph.
- Forgetting that a graph may be in several pieces. Loop over every node as a possible start.
- Deep recursion on a huge grid can overflow the stack. Switch to BFS with a queue.

## Check yourself
- Why does BFS give the shortest path on an unweighted graph?
- What does in-degree mean, and why do nodes with in-degree 0 go first?
- What does the `if (d > dist[node]) continue;` line in Dijkstra protect against?
