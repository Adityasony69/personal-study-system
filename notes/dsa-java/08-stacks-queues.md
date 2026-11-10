# Stacks, queues and deques

## The three shapes
- **Stack:** last in, first out (LIFO). Like a pile of plates: you add and remove at the top.
- **Queue:** first in, first out (FIFO). Like a line at a counter: join at the back, leave from the front.
- **Deque** (say "deck"): double-ended queue. Add or remove at both ends.

In Java, `ArrayDeque` does all three. Every operation below is O(1).

```java
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1);                       // put on top
stack.push(2);
int top = stack.peek();              // 2: look, do not remove
int taken = stack.pop();             // 2: remove from the top
boolean empty = stack.isEmpty();

Queue<Integer> queue = new ArrayDeque<>();
queue.offer(1);                      // join at the back
queue.offer(2);
int front = queue.peek();            // 1
int served = queue.poll();           // 1: leave from the front

Deque<Integer> deque = new ArrayDeque<>();
deque.offerFirst(1);
deque.offerLast(2);
int first = deque.pollFirst();       // 1
int last = deque.pollLast();         // 2
```

`pop()` on an empty stack throws an exception. `poll()` and `peek()` on an empty queue return `null`. Check `isEmpty()` first.

## When to think "stack"
- Matching pairs: brackets, tags.
- "Most recent thing first": undo, back button.
- "Next greater" or "previous smaller" questions.
- Turning recursion into a loop.

### Balanced brackets
Push every opening bracket. On a closing bracket, the top of the stack must be its partner.

```java
static boolean isBalanced(String s) {
    Deque<Character> stack = new ArrayDeque<>();
    for (char c : s.toCharArray()) {
        if (c == '(' || c == '[' || c == '{') {
            stack.push(c);
        } else {
            if (stack.isEmpty()) return false;         // a closer with nothing to close
            char open = stack.pop();
            if ((c == ')' && open != '(') || (c == ']' && open != '[') || (c == '}' && open != '{')) {
                return false;
            }
        }
    }
    return stack.isEmpty();                            // leftovers mean something was never closed
}
```

### Next greater element: the monotonic stack
For each item, find the first bigger item to its right. Keep a stack of indexes still waiting for their answer. When a bigger number arrives, it is the answer for everything smaller on the stack.

```java
static int[] nextGreater(int[] a) {
    int[] answer = new int[a.length];
    Arrays.fill(answer, -1);                           // -1 = no bigger item to the right
    Deque<Integer> waiting = new ArrayDeque<>();       // indexes, values decreasing from bottom to top
    for (int i = 0; i < a.length; i++) {
        while (!waiting.isEmpty() && a[waiting.peek()] < a[i]) {
            answer[waiting.pop()] = a[i];
        }
        waiting.push(i);
    }
    return answer;
}
```

`[2, 1, 5, 3]` gives `[5, 5, -1, -1]`. O(n): each index is pushed once and popped at most once.

### Stack that also knows its minimum
Keep a second stack holding "the minimum so far" at every level.

```java
class MinStack {
    private final Deque<Integer> values = new ArrayDeque<>();
    private final Deque<Integer> mins = new ArrayDeque<>();

    void push(int x) {
        values.push(x);
        mins.push(mins.isEmpty() ? x : Math.min(x, mins.peek()));
    }

    int pop() {
        mins.pop();
        return values.pop();
    }

    int getMin() {
        return mins.peek();
    }
}
```

## When to think "queue"
- Process things in the order they arrived.
- Breadth-first search on trees and graphs: visit level by level.

### Queue built from two stacks
A favourite interview question. Push onto `in`. To remove, pour `in` into `out` only when `out` is empty, which reverses the order once.

```java
class QueueFromStacks {
    private final Deque<Integer> in = new ArrayDeque<>();
    private final Deque<Integer> out = new ArrayDeque<>();

    void enqueue(int x) {
        in.push(x);
    }

    int dequeue() {
        if (out.isEmpty()) {
            while (!in.isEmpty()) out.push(in.pop());
        }
        return out.pop();
    }
}
```

Each item moves at most twice, so every operation is O(1) amortised.

## When to think "deque"
Sliding window maximum: the largest value in every window of size k. Keep indexes in the deque so their values are decreasing. The front is always the biggest in the window.

```java
static int[] slidingWindowMax(int[] a, int k) {
    int[] out = new int[a.length - k + 1];
    Deque<Integer> deque = new ArrayDeque<>();         // indexes; values decrease from front to back
    for (int i = 0; i < a.length; i++) {
        if (!deque.isEmpty() && deque.peekFirst() <= i - k) {
            deque.pollFirst();                         // front has slid out of the window
        }
        while (!deque.isEmpty() && a[deque.peekLast()] <= a[i]) {
            deque.pollLast();                          // smaller items can never be the max again
        }
        deque.offerLast(i);
        if (i >= k - 1) out[i - k + 1] = a[deque.peekFirst()];
    }
    return out;
}
```

## Method names side by side
| Action | Stack (`Deque`) | Queue |
|---|---|---|
| Add | `push(x)` | `offer(x)` |
| Remove | `pop()` | `poll()` |
| Look | `peek()` | `peek()` |

## Mistakes to avoid
- Using the old `Stack` class. `ArrayDeque` is faster and is the recommended one.
- Calling `pop()` without checking `isEmpty()`.
- Putting `null` into an `ArrayDeque`: not allowed.
- In monotonic stack problems, storing values when you need indexes. Store indexes: you can always look the value up.

## Check yourself
- Why does bracket matching need a stack and not just a counter?
- In `nextGreater`, why is the total work O(n) even with a while loop inside the for loop?
- How do two stacks manage to behave like a queue?
