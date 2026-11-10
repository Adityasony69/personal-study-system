# Sorting and binary search

## Sorting in real code
In practice you call the library. Know how to use it, and know merge sort and quick sort because interviews ask you to write them.

```java
int[] nums = {5, 2, 9, 1};
Arrays.sort(nums);                                     // ascending, O(n log n)

Integer[] boxed = {5, 2, 9, 1};
Arrays.sort(boxed, Collections.reverseOrder());        // descending needs Integer[], not int[]

int[][] intervals = {{5, 8}, {1, 3}, {2, 4}};
Arrays.sort(intervals, (p, q) -> Integer.compare(p[0], q[0]));   // by start

List<String> words = new ArrayList<>(List.of("pear", "fig", "apple"));
words.sort(Comparator.comparing(String::length).thenComparing(Comparator.naturalOrder()));
```

## Comparison table
| Algorithm | Best | Average | Worst | Extra space | Stable |
|---|---|---|---|---|---|
| Bubble sort | O(n) | O(n^2) | O(n^2) | O(1) | Yes |
| Selection sort | O(n^2) | O(n^2) | O(n^2) | O(1) | No |
| Insertion sort | O(n) | O(n^2) | O(n^2) | O(1) | Yes |
| Merge sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick sort | O(n log n) | O(n log n) | O(n^2) | O(log n) | No |

**Stable** means items that compare as equal keep their original order.

## Merge sort
Split in half, sort each half, then merge the two sorted halves. The merge is the real work.

```java
static void mergeSort(int[] a, int lo, int hi) {       // sorts a[lo..hi], both included
    if (lo >= hi) return;                              // one item is already sorted
    int mid = lo + (hi - lo) / 2;
    mergeSort(a, lo, mid);
    mergeSort(a, mid + 1, hi);

    int[] merged = new int[hi - lo + 1];
    int i = lo, j = mid + 1, k = 0;
    while (i <= mid && j <= hi) {
        merged[k++] = a[i] <= a[j] ? a[i++] : a[j++];  // <= keeps it stable
    }
    while (i <= mid) merged[k++] = a[i++];
    while (j <= hi) merged[k++] = a[j++];
    System.arraycopy(merged, 0, a, lo, merged.length);
}
```

Why O(n log n): the array is halved log n times, and each level does O(n) work merging.

## Quick sort
Pick a pivot, move everything smaller to its left and everything bigger to its right, then sort the two sides.

```java
static void quickSort(int[] a, int lo, int hi) {
    if (lo >= hi) return;
    int pivot = a[hi];                                 // last item as the pivot
    int boundary = lo;                                 // everything before boundary is smaller than pivot
    for (int i = lo; i < hi; i++) {
        if (a[i] < pivot) {
            int tmp = a[i];
            a[i] = a[boundary];
            a[boundary] = tmp;
            boundary++;
        }
    }
    int tmp = a[boundary];                             // put the pivot in its final place
    a[boundary] = a[hi];
    a[hi] = tmp;
    quickSort(a, lo, boundary - 1);
    quickSort(a, boundary + 1, hi);
}
```

Worst case O(n^2) happens when the pivot is always the smallest or largest item, for example an already sorted array with this pivot choice. Picking a random pivot avoids it in practice.

## Binary search
Works only on sorted data. Look at the middle, then throw away the half that cannot contain the answer. O(log n).

```java
static int binarySearch(int[] sorted, int target) {    // index of target, or -1
    int lo = 0, hi = sorted.length - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;                  // not (lo + hi) / 2: that can overflow
        if (sorted[mid] == target) return mid;
        if (sorted[mid] < target) lo = mid + 1;
        else hi = mid - 1;
    }
    return -1;
}
```

### First position that is at least the target (lower bound)
The most useful variant. It also tells you where to insert a missing value.

```java
static int lowerBound(int[] sorted, int target) {      // first index with sorted[i] >= target
    int lo = 0, hi = sorted.length;                    // hi is one past the end
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (sorted[mid] < target) lo = mid + 1;
        else hi = mid;                                 // mid might be the answer: keep it
    }
    return lo;                                         // equals sorted.length if every item is smaller
}

static int countOf(int[] sorted, int target) {         // how many times target appears
    return lowerBound(sorted, target + 1) - lowerBound(sorted, target);
}
```

### Binary search on the answer
When the question is "what is the smallest value that works?" and bigger values always work too, binary search over the possible answers instead of over an array.

```java
static int integerSqrt(int x) {                        // largest r with r * r <= x
    int lo = 0, hi = x, answer = 0;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if ((long) mid * mid <= x) {
            answer = mid;                              // works: remember it, try bigger
            lo = mid + 1;
        } else {
            hi = mid - 1;
        }
    }
    return answer;
}
```

## The two loop styles: do not mix them
| Style | Start | Loop while | Shrink with |
|---|---|---|---|
| Exact match | `hi = n - 1` | `lo <= hi` | `lo = mid + 1`, `hi = mid - 1` |
| Boundary (lower bound) | `hi = n` | `lo < hi` | `lo = mid + 1`, `hi = mid` |

## Mistakes to avoid
- Binary search on unsorted data.
- `hi = mid` together with `lo <= hi`: endless loop.
- `(lo + hi) / 2` overflowing for very large indexes.
- `Arrays.sort(int[], Collections.reverseOrder())` does not compile. Use `Integer[]`, or sort ascending and read backwards.
- Writing `p[0] - q[0]` in a comparator: it overflows for large values. Use `Integer.compare`.

## Check yourself
- Why is merge sort O(n log n) in every case, while quick sort has an O(n^2) worst case?
- What does stable mean and when does it matter?
- What does `lowerBound` return when the target is bigger than every item?
