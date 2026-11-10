# Linked lists

## What it is
A chain of nodes. Each node holds a value and a reference to the next node. The last node points to `null`. You only hold the first node, called the head.

```java
class ListNode {
    int val;
    ListNode next;

    ListNode(int val) {
        this.val = val;
    }
}
```

## Array versus linked list
| Operation | Array / ArrayList | Linked list |
|---|---|---|
| Read item number i | O(1) | O(n): walk from the head |
| Insert or delete at the front | O(n): shift everything | O(1) |
| Insert or delete after a node you already hold | O(n) | O(1) |
| Search for a value | O(n) | O(n) |
| Memory | Compact | Extra reference per node |

## Walking and building

```java
class ListBasics {
    static int length(ListNode head) {
        int count = 0;
        for (ListNode cur = head; cur != null; cur = cur.next) {
            count++;
        }
        return count;
    }

    static ListNode fromArray(int[] values) {
        ListNode dummy = new ListNode(0);              // fake node in front, so there is no special first case
        ListNode tail = dummy;
        for (int v : values) {
            tail.next = new ListNode(v);
            tail = tail.next;
        }
        return dummy.next;
    }

    static ListNode insertAtFront(ListNode head, int val) {
        ListNode node = new ListNode(val);
        node.next = head;
        return node;                                   // the new node is the new head
    }

    static ListNode deleteValue(ListNode head, int val) {   // removes the first node with this value
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode cur = dummy;
        while (cur.next != null) {
            if (cur.next.val == val) {
                cur.next = cur.next.next;              // skip over it
                break;
            }
            cur = cur.next;
        }
        return dummy.next;
    }
}
```

**The dummy node trick:** put a fake node before the head. Then deleting or inserting at the front is no different from the middle, and you return `dummy.next` at the end.

## Reverse a linked list
The most asked linked list question. Walk the list and flip each arrow to point backwards. You need three references so you do not lose the rest of the list.

```java
class ListReverse {
    static ListNode reverse(ListNode head) {
        ListNode prev = null;
        ListNode cur = head;
        while (cur != null) {
            ListNode next = cur.next;                  // 1. remember the rest
            cur.next = prev;                           // 2. flip the arrow
            prev = cur;                                // 3. move both forward
            cur = next;
        }
        return prev;                                   // prev ends on the old last node: the new head
    }

    static ListNode reverseRecursive(ListNode head) {
        if (head == null || head.next == null) return head;
        ListNode newHead = reverseRecursive(head.next);
        head.next.next = head;                         // make the node after me point back to me
        head.next = null;
        return newHead;
    }
}
```

Trace for `1 -> 2 -> 3`: after round one `1 -> null`, after round two `2 -> 1 -> null`, after round three `3 -> 2 -> 1 -> null`.

## Slow and fast pointers
Move one pointer one step at a time and another two steps at a time.

```java
class SlowFast {
    static ListNode middle(ListNode head) {            // when fast reaches the end, slow is in the middle
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }

    static boolean hasCycle(ListNode head) {           // in a loop, the fast one eventually laps the slow one
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) return true;
        }
        return false;
    }

    static ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0);
        dummy.next = head;
        ListNode lead = dummy, trail = dummy;
        for (int i = 0; i < n; i++) lead = lead.next;  // put a gap of n between the two
        while (lead.next != null) {
            lead = lead.next;
            trail = trail.next;
        }
        trail.next = trail.next.next;                  // trail is just before the node to remove
        return dummy.next;
    }
}
```

## Merge two sorted lists

```java
class ListMerge {
    static ListNode mergeSorted(ListNode a, ListNode b) {
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        while (a != null && b != null) {
            if (a.val <= b.val) {
                tail.next = a;
                a = a.next;
            } else {
                tail.next = b;
                b = b.next;
            }
            tail = tail.next;
        }
        tail.next = (a != null) ? a : b;               // attach whatever is left
        return dummy.next;
    }
}
```

## Java's built-in LinkedList
`java.util.LinkedList` is a doubly linked list. In interviews you are usually given a `ListNode` class like the one above instead. For a stack or queue in real code, prefer `ArrayDeque`.

## Mistakes to avoid
- `NullPointerException` from calling `.next` on null. Before writing `x.next.next`, check both `x` and `x.next`.
- Losing the rest of the list: save `cur.next` before you overwrite it.
- Forgetting to return the new head after a change at the front.
- Comparing nodes with `.val` when you mean "same node". In `hasCycle`, `slow == fast` compares the nodes themselves.

## Check yourself
- Why does reversing need three references?
- What does a dummy node save you from?
- Why does the fast pointer check both `fast != null` and `fast.next != null`?
