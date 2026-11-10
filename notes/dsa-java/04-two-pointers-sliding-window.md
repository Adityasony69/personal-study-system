# Two pointers and sliding window

Both replace a loop inside a loop with one pass, turning O(n^2) into O(n).

## Two pointers
Keep two indexes and move them according to a rule instead of trying every pair.

**When to think of it:** a sorted array, a pair or triple to find, comparing from both ends, or rewriting an array in place.

### Opposite ends: pair with a given sum in a sorted array
If the sum is too small, the only way to grow it is to move the left pointer right. Too big: move the right pointer left. Each step throws away one candidate for good.

```java
static boolean hasPairWithSum(int[] sorted, int target) {
    int l = 0, r = sorted.length - 1;
    while (l < r) {
        int sum = sorted[l] + sorted[r];
        if (sum == target) return true;
        if (sum < target) l++;
        else r--;
    }
    return false;
}
```

### Same direction: remove duplicates from a sorted array in place
`read` scans every item. `write` marks where the next item worth keeping goes.

```java
static int removeDuplicates(int[] sorted) {    // returns the new length
    if (sorted.length == 0) return 0;
    int write = 1;
    for (int read = 1; read < sorted.length; read++) {
        if (sorted[read] != sorted[read - 1]) {
            sorted[write++] = sorted[read];
        }
    }
    return write;
}
```

### Container with most water
Heights `[1, 8, 6, 2, 5, 4, 8, 3, 7]`: pick two lines that hold the most water. Start wide, then always move the shorter line inward, because the shorter line is what limits the area.

```java
static int maxWater(int[] height) {
    int l = 0, r = height.length - 1, best = 0;
    while (l < r) {
        int area = Math.min(height[l], height[r]) * (r - l);
        best = Math.max(best, area);
        if (height[l] < height[r]) l++;
        else r--;
    }
    return best;
}
```

### Three numbers that add to zero
Sort, fix one number, then run the two-pointer pair search on the rest. O(n^2).

```java
static List<List<Integer>> threeSum(int[] a) {
    Arrays.sort(a);
    List<List<Integer>> out = new ArrayList<>();
    for (int i = 0; i < a.length - 2; i++) {
        if (i > 0 && a[i] == a[i - 1]) continue;       // skip repeated first numbers
        int l = i + 1, r = a.length - 1;
        while (l < r) {
            int sum = a[i] + a[l] + a[r];
            if (sum == 0) {
                out.add(List.of(a[i], a[l], a[r]));
                l++;
                r--;
                while (l < r && a[l] == a[l - 1]) l++; // skip repeated second numbers
            } else if (sum < 0) {
                l++;
            } else {
                r--;
            }
        }
    }
    return out;
}
```

## Sliding window
A window is a stretch of neighbouring items, `a[left..right]`. Instead of recomputing it from scratch, slide it: add the item that enters on the right, remove the item that leaves on the left.

**When to think of it:** the words "subarray" or "substring" together with "longest", "shortest", "at most k" or "of size k".

### Fixed size: largest sum of any k neighbours

```java
static int maxSumOfSizeK(int[] a, int k) {
    int sum = 0;
    for (int i = 0; i < k; i++) sum += a[i];           // the first window
    int best = sum;
    for (int i = k; i < a.length; i++) {
        sum += a[i] - a[i - k];                        // one comes in, one goes out
        best = Math.max(best, sum);
    }
    return best;
}
```

### Variable size: the template
1. Grow the window by moving `right`.
2. While the window breaks the rule, shrink it by moving `left`.
3. The window is now valid: update the answer.

```java
static int longestUniqueSubstring(String s) {          // longest stretch with no repeated character
    Set<Character> window = new HashSet<>();
    int left = 0, best = 0;
    for (int right = 0; right < s.length(); right++) {
        char c = s.charAt(right);
        while (window.contains(c)) {                   // rule broken: c is already inside
            window.remove(s.charAt(left));
            left++;
        }
        window.add(c);
        best = Math.max(best, right - left + 1);
    }
    return best;
}

static int shortestSubarrayWithSumAtLeast(int[] a, int target) {   // positive numbers only
    int left = 0, sum = 0, best = Integer.MAX_VALUE;
    for (int right = 0; right < a.length; right++) {
        sum += a[right];
        while (sum >= target) {                        // valid: try to make it shorter
            best = Math.min(best, right - left + 1);
            sum -= a[left++];
        }
    }
    return best == Integer.MAX_VALUE ? 0 : best;
}
```

Why this is O(n) even with a loop inside a loop: `left` only moves forward, so in total it moves at most n times.

## Which one?
| Clue in the problem | Pattern |
|---|---|
| Sorted array, find a pair | Two pointers from both ends |
| Rewrite an array in place | Read pointer and write pointer |
| Palindrome check | Two pointers from both ends |
| Subarray or substring of size k | Fixed window |
| Longest or shortest subarray that satisfies a rule | Variable window |
| Subarray sum with negative numbers | Prefix sum plus HashMap, not a window |

## Mistakes to avoid
- Using two pointers from both ends on an unsorted array.
- Window length is `right - left + 1`, not `right - left`.
- Using a sliding window for sums when numbers can be negative: shrinking no longer makes the sum smaller.
- Forgetting to remove the outgoing item's effect before moving `left`.

## Check yourself
- Why is it safe to move the left pointer when the sum is too small?
- In the variable window template, when do you shrink?
- Why is the variable window O(n) and not O(n^2)?
