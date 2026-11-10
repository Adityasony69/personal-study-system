# Heaps and priority queues

## What a heap gives you
A heap always knows its smallest item (min-heap) or its largest item (max-heap), and stays that way cheaply as you add and remove.

| Operation | Cost |
|---|---|
| Look at the top (`peek`) | O(1) |
| Add (`offer`) | O(log n) |
| Remove the top (`poll`) | O(log n) |
| Search for some other value | O(n): a heap is not sorted |

A heap is **not** a sorted list. Only the top is guaranteed. Use it when you keep needing "the best one so far" while items are still coming in.

## How it is stored
A heap is a complete binary tree kept in a plain array. For the item at index `i`:

- parent is at `(i - 1) / 2`
- left child is at `2 * i + 1`
- right child is at `2 * i + 2`

Min-heap rule: every parent is less than or equal to its children. Adding puts the new item at the end and swaps it upward. Removing the top moves the last item to the top and swaps it downward. Both walk one path of the tree, which is why they cost O(log n).

## PriorityQueue in Java

```java
PriorityQueue<Integer> minHeap = new PriorityQueue<>();                             // smallest on top
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Collections.reverseOrder());   // largest on top

minHeap.offer(5);
minHeap.offer(1);
minHeap.offer(3);
int smallest = minHeap.peek();       // 1
int removed = minHeap.poll();        // 1; now 3 is on top
int size = minHeap.size();           // 2

// order by something else: here, arrays ordered by their second number
PriorityQueue<int[]> byDistance = new PriorityQueue<>((p, q) -> Integer.compare(p[1], q[1]));
byDistance.offer(new int[]{7, 20});
byDistance.offer(new int[]{9, 5});
int[] nearest = byDistance.poll();   // {9, 5}
```

## Pattern 1: the k largest items
Keep a **min**-heap of size k. Its top is the smallest of the k largest, so anything smaller than the top gets thrown out.

```java
static int kthLargest(int[] a, int k) {
    PriorityQueue<Integer> heap = new PriorityQueue<>();   // min-heap holding the k largest so far
    for (int x : a) {
        heap.offer(x);
        if (heap.size() > k) heap.poll();                  // drop the smallest
    }
    return heap.peek();
}
```

O(n log k) time, O(k) space. Sorting the whole array would be O(n log n).

Easy to get backwards: **k largest uses a min-heap, k smallest uses a max-heap.**

## Pattern 2: top k most frequent
Count with a map, then keep a heap of size k ordered by count.

```java
static List<Integer> topKFrequent(int[] a, int k) {
    Map<Integer, Integer> freq = new HashMap<>();
    for (int x : a) freq.merge(x, 1, Integer::sum);

    PriorityQueue<Integer> heap = new PriorityQueue<>((p, q) -> Integer.compare(freq.get(p), freq.get(q)));
    for (int value : freq.keySet()) {
        heap.offer(value);
        if (heap.size() > k) heap.poll();                  // drop the least frequent
    }
    List<Integer> out = new ArrayList<>(heap);
    out.sort((p, q) -> Integer.compare(freq.get(q), freq.get(p)));   // most frequent first
    return out;
}
```

## Pattern 3: merge k sorted arrays
Put the first item of each array in a min-heap. Repeatedly take the smallest, then push the next item from the same array.

```java
static List<Integer> mergeSortedArrays(int[][] arrays) {
    // each heap entry: {value, which array, index inside that array}
    PriorityQueue<int[]> heap = new PriorityQueue<>((p, q) -> Integer.compare(p[0], q[0]));
    for (int i = 0; i < arrays.length; i++) {
        if (arrays[i].length > 0) heap.offer(new int[]{arrays[i][0], i, 0});
    }
    List<Integer> out = new ArrayList<>();
    while (!heap.isEmpty()) {
        int[] top = heap.poll();
        out.add(top[0]);
        int array = top[1], next = top[2] + 1;
        if (next < arrays[array].length) {
            heap.offer(new int[]{arrays[array][next], array, next});
        }
    }
    return out;
}
```

O(N log k) where N is the total number of items and k is the number of arrays.

## Pattern 4: running median with two heaps
Keep the smaller half in a max-heap and the larger half in a min-heap. The median is at the tops.

```java
class RunningMedian {
    private final PriorityQueue<Integer> lower = new PriorityQueue<>(Collections.reverseOrder());  // smaller half
    private final PriorityQueue<Integer> upper = new PriorityQueue<>();                            // larger half

    void add(int x) {
        lower.offer(x);
        upper.offer(lower.poll());                         // pass the largest of the lower half up
        if (upper.size() > lower.size()) {
            lower.offer(upper.poll());                     // keep lower the same size or one bigger
        }
    }

    double median() {
        if (lower.size() > upper.size()) return lower.peek();
        return (lower.peek() + upper.peek()) / 2.0;
    }
}
```

## Heap sort in one sentence
Put everything in a heap, then poll n times: O(n log n). The result comes out sorted.

## When to reach for a heap
| Clue in the problem | Idea |
|---|---|
| "k largest", "k smallest", "k closest", "top k" | Heap of size k |
| "Merge k sorted ..." | Min-heap of the current fronts |
| "Median of a stream" | Two heaps |
| "Always process the cheapest or earliest next" | Min-heap (also Dijkstra's shortest path) |

## Mistakes to avoid
- Expecting a for-each loop over a `PriorityQueue` to come out sorted. Only `poll()` gives sorted order.
- Using a max-heap for "k largest" and keeping all n items: correct, but O(n) space instead of O(k).
- Comparator `p - q`: overflows for large values. Use `Integer.compare(p, q)`.
- Calling `poll()` or `peek()` on an empty heap and unboxing the `null` into an `int`.

## Check yourself
- Why does "k largest" use a min-heap?
- Why are `offer` and `poll` O(log n) and not O(n)?
- Where are the children of the item at index 3 in the array?
