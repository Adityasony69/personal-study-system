# Big-O and complexity

## What it measures
Big-O says how the work grows when the input grows. It is not about seconds. It answers: "if n becomes 10 times bigger, how much more work is that?"

- Keep only the fastest-growing term: `3n^2 + 5n + 2` is O(n^2).
- Drop constants: O(2n) is O(n).
- Unless told otherwise, talk about the worst case.
- **Time** complexity counts steps. **Space** complexity counts extra memory you create (not the input itself).

## The common ones, fastest to slowest
| Big-O | Name | Typical cause | n = 1,000,000 |
|---|---|---|---|
| O(1) | Constant | Array index, HashMap get | 1 step |
| O(log n) | Logarithmic | Halving each time: binary search | about 20 steps |
| O(n) | Linear | One loop over the input | 1 million |
| O(n log n) | Linearithmic | Good sorting: merge sort, `Arrays.sort` | about 20 million |
| O(n^2) | Quadratic | A loop inside a loop | 1 trillion: too slow |
| O(2^n) | Exponential | Trying every subset | impossible past n = 30 or so |
| O(n!) | Factorial | Trying every ordering | impossible past n = 11 or so |

## Reading code

```java
static int sum(int[] a) {                 // O(n) time, O(1) space: one pass
    int total = 0;
    for (int x : a) total += x;
    return total;
}

static boolean hasDuplicateSlow(int[] a) { // O(n^2) time: every pair
    for (int i = 0; i < a.length; i++)
        for (int j = i + 1; j < a.length; j++)
            if (a[i] == a[j]) return true;
    return false;
}

static boolean hasDuplicateFast(int[] a) { // O(n) time, O(n) space: trade memory for speed
    Set<Integer> seen = new HashSet<>();
    for (int x : a)
        if (!seen.add(x)) return true;     // add returns false if x was already there
    return false;
}

static int halvings(int n) {              // O(log n): n is cut in half each round
    int steps = 0;
    while (n > 1) {
        n /= 2;
        steps++;
    }
    return steps;
}
```

## Rules of thumb
- Loops one after another: add. O(n) + O(n) = O(n).
- Loops inside each other: multiply. O(n) * O(n) = O(n^2).
- Input halved every step: O(log n).
- Sorting first: at least O(n log n).
- Recursion: (number of calls) * (work per call). Recursion depth also costs stack space.

## From the constraint to the target complexity
A judge does roughly 100 million simple steps per second. Use the size of n to guess what is expected.

| n up to | Aim for |
|---|---|
| 10 to 20 | O(2^n) or O(n!) is fine: brute force, backtracking |
| 500 | O(n^3) |
| 5,000 | O(n^2) |
| 100,000 to 1,000,000 | O(n log n) or O(n) |
| 1,000,000,000 and above | O(log n) or O(1): maths or binary search |

## Cost of Java operations
| Operation | Cost |
|---|---|
| `arr[i]`, `list.get(i)` on ArrayList | O(1) |
| `list.add(x)` at the end | O(1) amortised |
| `list.add(0, x)`, `list.remove(0)`, `list.contains(x)` | O(n) |
| `map.get`, `map.put`, `set.add`, `set.contains` (Hash versions) | O(1) average |
| TreeMap and TreeSet operations | O(log n) |
| `pq.offer`, `pq.poll` | O(log n) |
| `pq.peek`, stack and queue push or pop on ArrayDeque | O(1) |
| `Arrays.sort`, `Collections.sort` | O(n log n) |
| `s.substring`, `s1 + s2`, `s.equals` | O(length) |

"Amortised" means: usually O(1), now and then an expensive resize, and averaged over many calls it still works out to O(1) each.

## How to answer "what is the complexity?"
1. Say what n is (length of the array, number of nodes, and so on).
2. Count the loops and how many times each runs.
3. Add any hidden costs: a `contains` on a list inside a loop is another loop.
4. State time, then space.

## Mistakes to avoid
- Calling string concatenation in a loop O(n). It is O(n^2) because each `+` copies the string.
- Forgetting the sort: "one loop" after `Arrays.sort` is still O(n log n) overall.
- Ignoring recursion stack space.

## Check yourself
- Why is binary search O(log n)?
- What is the complexity of a loop that calls `list.contains` on every item?
- n is 200,000. Is an O(n^2) solution going to pass?
