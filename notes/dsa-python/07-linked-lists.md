# Linked lists (Python)

Every code block here was run with its asserts on Python 3.12.

## What it is
A chain of nodes. Each node holds a value and a reference to the next node. The last node's `next` is `None`. You only keep the **head**.

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def build(values):                       # list -> linked list
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def to_list(head):                       # linked list -> list (handy in tests)
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

assert to_list(build([1, 2, 3])) == [1, 2, 3]
assert build([]) is None
```
The `dummy` node trick (a fake node before the head) removes special cases for "what if the list is empty or the head changes". Use it often.

## Array versus linked list
| | Python list (array) | Linked list |
|---|---|---|
| Get item i | O(1) | O(n) |
| Insert/delete at the front | O(n) | O(1) |
| Insert/delete after a known node | O(n) | O(1) |
| Memory | compact | extra pointer per item |
In real Python you almost never use a linked list; `deque` covers queue needs. Linked lists matter because interviews love them and they teach pointer thinking.

## Walking and building
```python
def length(head):
    n = 0
    while head:
        n += 1
        head = head.next
    return n

def insert_front(head, val):
    return ListNode(val, head)

def delete_value(head, val):             # remove first node holding val
    dummy = ListNode(0, head)
    cur = dummy
    while cur.next:
        if cur.next.val == val:
            cur.next = cur.next.next
            break
        cur = cur.next
    return dummy.next

def delete_node_given_only_it(node):     # not the tail: copy the next value, skip the next node
    node.val = node.next.val
    node.next = node.next.next

def remove_nth_from_end(head, n):        # gap of n between two pointers
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    return dummy.next

h = build([1, 2, 3])
assert length(h) == 3
assert to_list(insert_front(h, 0)) == [0, 1, 2, 3]
assert to_list(delete_value(build([1, 2, 3]), 1)) == [2, 3]
assert to_list(delete_value(build([1, 2, 3]), 3)) == [1, 2]
assert to_list(delete_value(build([1, 2, 3]), 9)) == [1, 2, 3]
n = build([1, 2, 3, 4]); delete_node_given_only_it(n.next); assert to_list(n) == [1, 3, 4]
assert to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
assert to_list(remove_nth_from_end(build([1]), 1)) == []
```

## Reverse a linked list
Walk once, flipping each `next` to point backwards. Keep three names: `prev`, `cur`, `nxt`.
```python
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next                   # 1. remember the rest
        cur.next = prev                  # 2. flip the arrow
        prev = cur                       # 3. move both forward
        cur = nxt
    return prev                          # prev is the new head

def reverse_recursive(head):
    if not head or not head.next:
        return head
    new_head = reverse_recursive(head.next)
    head.next.next = head
    head.next = None
    return new_head

def reverse_k_group(head, k):
    count, node = 0, head
    while node and count < k:            # is there a full group of k?
        node = node.next
        count += 1
    if count < k:
        return head
    prev, cur = reverse_k_group(node, k), head   # rest already done; becomes the tail target
    for _ in range(k):
        cur.next, prev, cur = prev, cur, cur.next
    return prev

assert to_list(reverse(build([1, 2, 3, 4]))) == [4, 3, 2, 1]
assert reverse(None) is None
assert to_list(reverse_recursive(build([1, 2, 3]))) == [3, 2, 1]
assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
assert to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
```

## Slow and fast pointers
`slow` moves 1 step, `fast` moves 2.
```python
def middle(head):                        # when fast ends, slow is in the middle
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

def has_cycle(head):                     # if there's a loop, fast laps slow
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False

def cycle_start(head):                   # after they meet, restart one from head; they meet at the entry
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None

def is_palindrome(head):                 # find the middle, reverse 2nd half, compare
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second = reverse(slow)
    first = head
    while second:
        if first.val != second.val:
            return False
        first, second = first.next, second.next
    return True

def intersection(a, b):                  # switch heads at the end: both walk len(a)+len(b)
    p, q = a, b
    while p is not q:
        p = p.next if p else b
        q = q.next if q else a
    return p

def reorder(head):                       # 1,2,3,4,5 -> 1,5,2,4,3
    if not head or not head.next:
        return
    slow = fast = head
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = reverse(slow.next), None
    first = head
    while second:
        f_next, s_next = first.next, second.next
        first.next, second.next = second, f_next
        first, second = f_next, s_next

assert middle(build([1, 2, 3, 4, 5])).val == 3
assert middle(build([1, 2, 3, 4])).val == 3          # second middle for even lengths
h = build([1, 2, 3, 4]); h.next.next.next.next = h.next      # tail points back to node 2
assert has_cycle(h) and cycle_start(h).val == 2
assert not has_cycle(build([1, 2, 3])) and cycle_start(build([1, 2])) is None
assert is_palindrome(build([1, 2, 2, 1])) and is_palindrome(build([1, 2, 3, 2, 1]))
assert not is_palindrome(build([1, 2, 3]))
shared = build([8, 9])
a_list, b_list = build([1, 2]), build([5])
a_list.next.next, b_list.next = shared, shared
assert intersection(a_list, b_list) is shared
assert intersection(build([1]), build([2])) is None
h = build([1, 2, 3, 4, 5]); reorder(h); assert to_list(h) == [1, 5, 2, 4, 3]
```

## Merge two sorted lists
```python
def merge_two(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b                   # attach whatever is left
    return dummy.next

import heapq

def merge_k_lists(lists):                # heap holds the front of each list: O(N log k)
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]
    heapq.heapify(heap)                  # i breaks ties so nodes are never compared
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

def add_two_numbers(a, b):               # digits stored in reverse: 2->4->3 is 342
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        total = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        a, b = a.next if a else None, b.next if b else None
    return dummy.next

def sort_list(head):                     # merge sort on a list: O(n log n)
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    right, slow.next = slow.next, None
    return merge_two(sort_list(head), sort_list(right))

def rotate_right(head, k):
    if not head or not head.next or k == 0:
        return head
    n, tail = 1, head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head                      # make a ring, then cut at the right spot
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head, new_tail.next = new_tail.next, None
    return new_head

assert to_list(merge_two(build([1, 2, 4]), build([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
assert to_list(merge_two(None, build([0]))) == [0]
assert to_list(merge_k_lists([build([1, 4, 5]), build([1, 3, 4]), build([2, 6])])) == [1, 1, 2, 3, 4, 4, 5, 6]
assert merge_k_lists([]) is None
assert to_list(add_two_numbers(build([2, 4, 3]), build([5, 6, 4]))) == [7, 0, 8]
assert to_list(add_two_numbers(build([9, 9]), build([1]))) == [0, 0, 1]
assert to_list(sort_list(build([4, 2, 1, 3]))) == [1, 2, 3, 4]
assert to_list(rotate_right(build([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
assert to_list(rotate_right(build([1, 2]), 4)) == [1, 2]
```

## Copy a list with random pointers
```python
class RNode:
    def __init__(self, val, next=None, random=None):
        self.val, self.next, self.random = val, next, random

def copy_random_list(head):
    clones = {None: None}                # old node -> new node
    cur = head
    while cur:
        clones[cur] = RNode(cur.val)
        cur = cur.next
    cur = head
    while cur:
        clones[cur].next = clones[cur.next]
        clones[cur].random = clones[cur.random]
        cur = cur.next
    return clones[head]

n1, n2, n3 = RNode(1), RNode(2), RNode(3)
n1.next, n2.next = n2, n3
n1.random, n3.random = n3, n1
c = copy_random_list(n1)
assert (c.val, c.next.val, c.next.next.val) == (1, 2, 3)
assert c.random is c.next.next and c.next.next.random is c
assert c is not n1 and c.next is not n2
```

## LRU cache: linked list plus dict
The standard interview "design" problem. Python gives you the shortcut `OrderedDict`:
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = OrderedDict()

    def get(self, key):
        if key not in self.data:
            return -1
        self.data.move_to_end(key)           # now the most recently used
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.cap:
            self.data.popitem(last=False)    # evict the least recently used

c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)                                  # evicts key 2
assert c.get(2) == -1
c.put(4, 4)                                  # evicts key 1
assert c.get(1) == -1 and c.get(3) == 3 and c.get(4) == 4
```
`OrderedDict` is a hash map plus a doubly linked list inside. An interviewer may ask you to build that by hand with `Node(prev, next)` and a dict from key to node.

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Reverse | Reverse Linked List, Reverse Nodes in k-Group | Reverse Linked List, Reverse Nodes in k-Group |
| Merge | Merge Two Sorted Lists, Merge k Sorted Lists | Merge Two Sorted Lists, Merge k Sorted Lists |
| Fast / slow | Linked List Cycle, Find the Duplicate Number, Reorder List | Middle of the Linked List, Linked List Cycle (I, II), Palindrome Linked List |
| Gap pointers | Remove Nth Node From End of List | Remove Nth Node From End of List |
| Arithmetic | Add Two Numbers | Add Two Numbers |
| Copy / design | Copy List with Random Pointer, LRU Cache | Copy List with Random Pointer, LRU Cache, LFU Cache |
| Misc | | Intersection of Two Linked Lists, Rotate List, Delete Node in a Linked List, Flatten a Linked List |

## Mistakes to avoid
- Losing the rest of the list: save `nxt = cur.next` **before** changing `cur.next`.
- Forgetting the empty list (`head is None`) and one-node cases.
- `while fast.next.next` without checking `fast.next` first: `AttributeError`.
- Comparing nodes by value when you mean identity: use `is` for "same node".
- Not returning the new head after reversing or deleting the old head.
- Heap tuples without a tie-breaker: Python tries to compare the node objects and raises `TypeError`.

## Check yourself
- Why use a dummy node?
- In `reverse`, why save `cur.next` first?
- How does the slow/fast trick find the middle and detect a cycle?
