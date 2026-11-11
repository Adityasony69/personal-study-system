# Linked List

**14 questions:** 3 Easy, 8 Medium, 3 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

Nodes connected by pointers. There is no index, so everything is done by carefully rewiring the next pointers.

## How to spot this pattern

- The input is a ListNode.
- Reverse, merge, find the middle, detect a cycle, remove a node.

## Thinking steps (use these on every question here)

1. Draw 3 or 4 boxes with arrows on paper before coding.
2. Use a dummy node before the head when the head itself might change.
3. Slow and fast pointers find the middle and detect cycles.
4. Save the next pointer before you overwrite it.

## Common beginner mistakes

- Losing the rest of the list by overwriting next too early.
- Not handling an empty list or a single node.

Read first: your `dsa-python` notes, file(s) 07-linked-lists.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Reverse Linked List | Easy | 206 | 150 |
| 2 | Merge Two Sorted Lists | Easy | 21 | 150 |
| 3 | Linked List Cycle | Easy | 141 | 150 |
| 4 | Reorder List | Medium | 143 | 150 |
| 5 | Remove Nth Node From End of List | Medium | 19 | 150 |
| 6 | Copy List With Random Pointer | Medium | 138 | 150 |
| 7 | Add Two Numbers | Medium | 2 | 150 |
| 8 | Find The Duplicate Number | Medium | 287 | 150 |
| 9 | Reverse Linked List II | Medium | 92 | 250 |
| 10 | Design Circular Queue | Medium | 622 | 250 |
| 11 | LRU Cache | Medium | 146 | 150 |
| 12 | LFU Cache | Hard | 460 | 250 |
| 13 | Merge K Sorted Lists | Hard | 23 | 150 |
| 14 | Reverse Nodes In K Group | Hard | 25 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Reverse Linked List  [Easy]

- **Find it:** LeetCode #206, search "Reverse Linked List"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Every arrow must point the other way.
- **First step:** Walk the list with prev and curr pointers.
- **If stuck:** Save curr.next first, point curr.next to prev, then move both forward. Return prev.

### 2. Merge Two Sorted Lists  [Easy]

- **Find it:** LeetCode #21, search "Merge Two Sorted Lists"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Always take the smaller head.
- **First step:** Create a dummy node so you never special-case the first node.
- **If stuck:** Attach the smaller node, advance that list; at the end attach whatever is left.

### 3. Linked List Cycle  [Easy]

- **Find it:** LeetCode #141, search "Linked List Cycle"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** If there is a loop, a walker never reaches the end.
- **First step:** A set of visited nodes works. Then try O(1) memory.
- **If stuck:** Slow moves 1 step, fast moves 2; if they ever meet there is a cycle.

## Medium questions

### 4. Reorder List  [Medium]

- **Find it:** LeetCode #143, search "Reorder List"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** The result alternates nodes from the front and from the back.
- **First step:** Break it into three smaller tasks you already know.
- **If stuck:** Find the middle (slow/fast), reverse the second half, then merge the two halves alternately.

### 5. Remove Nth Node From End of List  [Medium]

- **Find it:** LeetCode #19, search "Remove Nth Node From End of List"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You need the node just BEFORE the one to delete, in one pass.
- **First step:** Use two pointers with a fixed gap.
- **If stuck:** Move fast n steps ahead, then move both until fast reaches the end; a dummy head handles deleting the first node.

### 6. Copy List With Random Pointer  [Medium]

- **Find it:** LeetCode #138, search "Copy List With Random Pointer"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Random pointers may point to nodes you have not copied yet.
- **First step:** Do two passes.
- **If stuck:** Pass 1: build a dictionary old node -> new node. Pass 2: set next and random using the dictionary.

### 7. Add Two Numbers  [Medium]

- **Find it:** LeetCode #2, search "Add Two Numbers"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Digits are stored in reverse, so you start at the ones place: just like school addition.
- **First step:** Walk both lists together with a carry.
- **If stuck:** Continue while either list has nodes OR carry is non-zero; new digit = sum % 10.

### 8. Find The Duplicate Number  [Medium]

- **Find it:** LeetCode #287, search "Find The Duplicate Number"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** You cannot modify the array or use extra memory.
- **First step:** Treat index -> nums[index] as a linked list; a duplicate creates a cycle.
- **If stuck:** Floyd cycle detection: find the meeting point, then start a second pointer from the beginning; they meet at the duplicate.

### 9. Reverse Linked List II  [Medium]

- **Find it:** LeetCode #92, search "Reverse Linked List II"
- **Lists:** NeetCode 250
- **Notice:** Reverse only the part between positions left and right.
- **First step:** Use a dummy head and walk to the node just before position left.
- **If stuck:** Reverse the sublist as usual, then reconnect its two ends to the nodes before and after.

### 10. Design Circular Queue  [Medium]

- **Find it:** LeetCode #622, search "Design Circular Queue"
- **Lists:** NeetCode 250
- **Notice:** Fixed size, and the end wraps around to the start.
- **First step:** Use an array with a front index and a count.
- **If stuck:** Rear index = (front + count - 1) % capacity; full when count == capacity.

### 11. LRU Cache  [Medium]

- **Find it:** LeetCode #146, search "LRU Cache"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** get and put must both be O(1), and you must know the least recently used item.
- **First step:** A dictionary finds items fast; what structure lets you move an item to "most recent" in O(1)?
- **If stuck:** Dictionary + doubly linked list with dummy head and tail; on each use move the node to one end, evict from the other.

## Hard questions

### 12. LFU Cache  [Hard]

- **Find it:** LeetCode #460, search "LFU Cache"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Evict the least FREQUENTLY used; ties go to the least recently used.
- **First step:** Extend the LRU idea: one LRU list per frequency.
- **If stuck:** Keep key -> (value, freq), freq -> ordered keys, and a minFreq variable that you update on insert and when a list empties.

### 13. Merge K Sorted Lists  [Hard]

- **Find it:** LeetCode #23, search "Merge K Sorted Lists"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You repeatedly need the smallest head among k lists.
- **First step:** Option A: merge lists in pairs again and again.
- **If stuck:** Option B: a min-heap holding one node per list; pop the smallest, push its next.

### 14. Reverse Nodes In K Group  [Hard]

- **Find it:** LeetCode #25, search "Reverse Nodes In K Group"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Reverse k nodes at a time; leftover nodes stay as they are.
- **First step:** First check that k nodes exist from the current point.
- **If stuck:** Reverse that group, connect the tail of the previous group to the new head, and continue from the next group.
