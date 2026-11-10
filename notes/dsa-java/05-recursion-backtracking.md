# Recursion and backtracking

## Recursion
A method that calls itself on a smaller version of the same problem. Every recursive method needs two things:

- **Base case:** the smallest input, answered directly. Without it you get `StackOverflowError`.
- **Recursive case:** do a little work, then call yourself on something smaller.

Trust the call: assume the recursive call already returns the right answer for the smaller input, then ask only "how do I use that answer?"

```java
static int factorial(int n) {
    if (n <= 1) return 1;                  // base case
    return n * factorial(n - 1);           // smaller problem: n - 1
}

static int sumDigits(int n) {              // 472 -> 4 + 7 + 2 = 13
    if (n < 10) return n;
    return n % 10 + sumDigits(n / 10);
}

static long power(long base, int exp) {    // O(log exp): halve the exponent
    if (exp == 0) return 1;
    long half = power(base, exp / 2);
    return exp % 2 == 0 ? half * half : half * half * base;
}

static boolean isPalindrome(String s, int l, int r) {
    if (l >= r) return true;
    if (s.charAt(l) != s.charAt(r)) return false;
    return isPalindrome(s, l + 1, r - 1);
}
```

## What happens in memory
Each call gets its own frame on the call stack with its own copies of the parameters. `factorial(4)` waits for `factorial(3)`, which waits for `factorial(2)`, and so on. The answers come back in reverse order. So recursion of depth n uses O(n) stack space even when you create no arrays.

## Slow recursion: repeated work

```java
static int fibSlow(int n) {                // O(2^n): solves the same n again and again
    if (n < 2) return n;
    return fibSlow(n - 1) + fibSlow(n - 2);
}
```

`fibSlow(5)` computes `fibSlow(3)` twice and `fibSlow(2)` three times. Storing each answer the first time fixes this. That fix is called memoisation and is the start of dynamic programming.

## Backtracking
Backtracking is recursion that builds an answer one choice at a time and undoes the choice when it comes back. It tries every option in an organised way.

The template, three lines to memorise:
1. **Choose:** add an option to the current path.
2. **Explore:** recurse.
3. **Un-choose:** remove it, so the next option starts clean.

### All subsets
For each item there are two choices: take it or skip it. That gives 2^n subsets.

```java
static void subsets(int[] a, int index, List<Integer> path, List<List<Integer>> out) {
    if (index == a.length) {
        out.add(new ArrayList<>(path));    // copy: path keeps changing after this
        return;
    }
    path.add(a[index]);                    // choose: take a[index]
    subsets(a, index + 1, path, out);      // explore
    path.remove(path.size() - 1);          // un-choose
    subsets(a, index + 1, path, out);      // explore the "skip it" branch
}
```

### All permutations
Every position can hold any item that is not used yet. That gives n! orderings.

```java
static void permutations(int[] a, boolean[] used, List<Integer> path, List<List<Integer>> out) {
    if (path.size() == a.length) {
        out.add(new ArrayList<>(path));
        return;
    }
    for (int i = 0; i < a.length; i++) {
        if (used[i]) continue;
        used[i] = true;                    // choose
        path.add(a[i]);
        permutations(a, used, path, out);  // explore
        path.remove(path.size() - 1);      // un-choose
        used[i] = false;
    }
}
```

### Combinations that add up to a target
Each number may be used many times. Passing `start` stops the same combination appearing in a different order.

```java
static void combinationSum(int[] candidates, int start, int remaining,
                           List<Integer> path, List<List<Integer>> out) {
    if (remaining == 0) {
        out.add(new ArrayList<>(path));
        return;
    }
    for (int i = start; i < candidates.length; i++) {
        if (candidates[i] > remaining) continue;       // pruning: this branch cannot work
        path.add(candidates[i]);
        combinationSum(candidates, i, remaining - candidates[i], path, out);   // i, not i + 1: reuse allowed
        path.remove(path.size() - 1);
    }
}
```

**Pruning** means stopping a branch early when it clearly cannot lead to an answer. It is what makes backtracking usable.

## How to call them

```java
List<List<Integer>> all = new ArrayList<>();
subsets(new int[]{1, 2, 3}, 0, new ArrayList<>(), all);
System.out.println(all.size());            // 8
```

## Complexity
| Problem | Number of answers | Time |
|---|---|---|
| Subsets | 2^n | O(n * 2^n) |
| Permutations | n! | O(n * n!) |
| Linear recursion like factorial | 1 | O(n) time, O(n) stack |

## Mistakes to avoid
- No base case, or a base case that is never reached.
- Adding `path` itself to the output instead of a copy. Every entry ends up the same, usually empty.
- Forgetting the un-choose step.
- `path.remove(i)` on a `List<Integer>` removes by index. That is what you want here: `path.size() - 1` is the last index.

## Check yourself
- What are the two parts every recursive method needs?
- Why must you copy `path` before adding it to the output?
- Why is plain recursive Fibonacci so slow?
