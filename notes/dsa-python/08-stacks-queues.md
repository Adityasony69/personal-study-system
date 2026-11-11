# Stacks, queues and deques (Python)

Every code block here was run with its asserts on Python 3.12.

## The three shapes
| Shape | Rule | Python tool |
|---|---|---|
| Stack | Last in, first out (LIFO) | a plain `list`: `append`, `pop`, `[-1]` to peek |
| Queue | First in, first out (FIFO) | `collections.deque`: `append`, `popleft` |
| Deque | Add/remove at both ends | `collections.deque`: `appendleft`, `popleft`, `append`, `pop` |

Don't use `list.pop(0)` as a queue: it is O(n). `deque.popleft()` is O(1). (`queue.Queue` also exists but is for threads and is slower.)

```python
from collections import deque

stack = []
stack.append(1); stack.append(2)
assert stack[-1] == 2 and stack.pop() == 2 and stack == [1]

q = deque()
q.append("a"); q.append("b"); q.appendleft("z")
assert q.popleft() == "z" and q.popleft() == "a" and q.pop() == "b"
assert not q                                   # empty deques/lists are falsy
```

## When to think "stack"
Matching pairs, undo, "most recent unresolved thing", nested structure, DFS without recursion.

### Balanced brackets
```python
def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return not stack                     # leftovers mean unclosed brackets

assert is_valid("()[]{}") and is_valid("{[()]}") and is_valid("")
assert not is_valid("(]") and not is_valid("(") and not is_valid("]")
```

### Evaluate and decode expressions
```python
def eval_rpn(tokens):                    # reverse Polish notation: "2 1 + 3 *"
    stack = []
    for t in tokens:
        if t in "+-*/" and len(t) == 1:
            b, a = stack.pop(), stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))     # truncate toward 0 (// would round down)
        else:
            stack.append(int(t))
    return stack[0]

def decode_string(s):                    # "3[a2[c]]" -> "accaccacc"
    stack, cur, num = [], "", 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))
            cur, num = "", 0
        elif ch == "]":
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += ch
    return cur

def generate_parentheses(n):             # backtracking with open/close counts
    out = []

    def go(cur, opened, closed):
        if len(cur) == 2 * n:
            out.append(cur)
            return
        if opened < n:
            go(cur + "(", opened + 1, closed)
        if closed < opened:
            go(cur + ")", opened, closed + 1)

    go("", 0, 0)
    return out

assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
assert eval_rpn(["4", "13", "5", "/", "+"]) == 6
assert eval_rpn(["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]) == 22
assert decode_string("3[a2[c]]") == "accaccacc"
assert decode_string("2[ab]c") == "ababc"
assert sorted(generate_parentheses(3)) == ["((()))", "(()())", "(())()", "()(())", "()()()"]
```

### Next greater element: the monotonic stack
Keep a stack of indexes whose answer is still unknown, with values in decreasing order. When a bigger value arrives it resolves everything smaller on top. Each index is pushed and popped once, so O(n).
```python
def next_greater(a):                     # next bigger value to the right, or -1
    out = [-1] * len(a)
    stack = []                           # indexes waiting for an answer
    for i, x in enumerate(a):
        while stack and a[stack[-1]] < x:
            out[stack.pop()] = x
        stack.append(i)
    return out

def daily_temperatures(temps):           # days until a warmer day
    out = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out

def next_greater_circular(a):            # array is circular: walk it twice
    n = len(a)
    out, stack = [-1] * n, []
    for i in range(2 * n):
        x = a[i % n]
        while stack and a[stack[-1]] < x:
            out[stack.pop()] = x
        if i < n:
            stack.append(i)
    return out

def largest_rectangle(heights):          # classic: stack of increasing bar heights
    stack, best = [], 0                  # (start index, height)
    for i, h in enumerate(heights + [0]):    # sentinel 0 flushes the stack
        start = i
        while stack and stack[-1][1] >= h:
            idx, height = stack.pop()
            best = max(best, height * (i - idx))
            start = idx
        stack.append((start, h))
    return best

def car_fleet(target, position, speed):  # cars can't pass; count fleets arriving
    cars = sorted(zip(position, speed), reverse=True)
    fleets, slowest = 0, 0.0
    for pos, spd in cars:
        time = (target - pos) / spd
        if time > slowest:               # takes longer than the fleet ahead: new fleet
            fleets += 1
            slowest = time
    return fleets

assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert next_greater_circular([1, 2, 1]) == [2, -1, 2]
assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
assert largest_rectangle([2, 4]) == 4
assert largest_rectangle([]) == 0
assert car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3
```

### Stack that also knows its minimum
Store, next to each value, the minimum so far.
```python
class MinStack:
    def __init__(self):
        self.stack = []                  # (value, min up to here)

    def push(self, x):
        m = min(x, self.stack[-1][1]) if self.stack else x
        self.stack.append((x, m))

    def pop(self):
        return self.stack.pop()[0]

    def top(self):
        return self.stack[-1][0]

    def get_min(self):
        return self.stack[-1][1]

s = MinStack()
for x in (-2, 0, -3):
    s.push(x)
assert s.get_min() == -3
s.pop()
assert s.top() == 0 and s.get_min() == -2
```

## When to think "queue"
Process in arrival order, level by level, shortest path in an unweighted graph (BFS), buffers and schedulers.

### Queue built from two stacks, and a stack built from queues
```python
class MyQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []

    def push(self, x):
        self.inbox.append(x)

    def _shift(self):
        if not self.outbox:              # only refill when empty
            while self.inbox:
                self.outbox.append(self.inbox.pop())

    def pop(self):
        self._shift()
        return self.outbox.pop()

    def peek(self):
        self._shift()
        return self.outbox[-1]

    def empty(self):
        return not self.inbox and not self.outbox

class MyStack:                           # one queue: after each push, rotate the older items behind it
    def __init__(self):
        self.q = deque()

    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())

    def pop(self):
        return self.q.popleft()

    def top(self):
        return self.q[0]

    def empty(self):
        return not self.q

mq = MyQueue()
mq.push(1); mq.push(2)
assert mq.peek() == 1 and mq.pop() == 1
mq.push(3)
assert mq.pop() == 2 and mq.pop() == 3 and mq.empty()
ms = MyStack()
ms.push(1); ms.push(2)
assert ms.top() == 2 and ms.pop() == 2 and ms.pop() == 1 and ms.empty()
```
Amortized O(1) per operation for the two-stack queue: each item moves at most twice.

## When to think "deque"
Sliding-window maximum (note 4), palindromes, a queue you also need to pop from the back of.
```python
def is_palindrome_deque(s):
    d = deque(ch.lower() for ch in s if ch.isalnum())
    while len(d) > 1:
        if d.popleft() != d.pop():
            return False
    return True

def rotting_oranges(grid):               # multi-source BFS: minutes until nothing is fresh
    R, C = len(grid), len(grid[0])
    q, fresh = deque(), 0
    for r in range(R):
        for c in range(C):
            if grid[r][c] == 2:
                q.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):          # one full level = one minute
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    return minutes if fresh == 0 else -1

class StockSpanner:                      # online stock span: monotonic stack of (price, span)
    def __init__(self):
        self.stack = []

    def next(self, price):
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span

assert is_palindrome_deque("A man, a plan, a canal: Panama")
assert not is_palindrome_deque("hello")
assert rotting_oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
assert rotting_oranges([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
assert rotting_oranges([[0, 2]]) == 0
sp = StockSpanner()
assert [sp.next(p) for p in (100, 80, 60, 70, 60, 75, 85)] == [1, 1, 1, 2, 1, 4, 6]
```

## Method names side by side
| Action | Stack (`list`) | Queue / deque (`deque`) |
|---|---|---|
| Add | `append(x)` | `append(x)` (back), `appendleft(x)` (front) |
| Remove | `pop()` | `popleft()` (front), `pop()` (back) |
| Peek | `s[-1]` | `q[0]` (front), `q[-1]` (back) |
| Empty? | `not s` | `not q` |
| Size | `len(s)` | `len(q)` |
Popping an empty list or deque raises `IndexError`. Check first.

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Brackets / parsing | Valid Parentheses, Evaluate Reverse Polish Notation, Generate Parentheses | Valid Parentheses |
| Design | Min Stack | Min Stack, Implement Stack using Queues, Implement Queue using Stacks |
| Monotonic stack | Daily Temperatures, Car Fleet, Largest Rectangle in Histogram | Next Greater Element I and II, Largest Rectangle in Histogram, Online Stock Span |
| Deque | Sliding Window Maximum | Sliding Window Maximum |
| BFS queue | Rotting Oranges, Binary Tree Level Order Traversal | Rotting Oranges |

## Mistakes to avoid
- `list.pop(0)` as a queue (O(n) each).
- Peeking or popping an empty stack: guard with `if stack`.
- Pushing values when you needed indexes (for distances, widths).
- Monotonic stack: wrong direction of the comparison (`<` vs `<=`) changes how ties behave.
- Forgetting leftover items on the stack at the end (see the `+ [0]` sentinel in the histogram).

## Check yourself
- Why is `deque` better than `list` for a queue?
- In a monotonic stack, why is the work O(n) even though there is a while inside a for?
- How does a queue made from two stacks keep O(1) amortized?
