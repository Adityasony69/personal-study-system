# Trees and binary search trees (Python)

Every code block here was run with its asserts on Python 3.12.

## Words to know
- **Node**: holds a value and up to two children (`left`, `right`).
- **Root**: top node. **Leaf**: no children.
- **Depth/height**: number of levels. A single node has height 1 here.
- **Balanced**: left and right heights differ by at most 1 at every node.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def build_tree(values):                  # level-order list, None = missing: [3,9,20,None,None,15,7]
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    q, i = deque([root]), 1
    while q and i < len(values):
        node = q.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i]); q.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i]); q.append(node.right)
        i += 1
    return root

t = build_tree([3, 9, 20, None, None, 15, 7])
assert t.val == 3 and t.left.val == 9 and t.right.right.val == 7 and t.left.left is None
assert build_tree([]) is None
```

## Depth-first traversals
Recursive versions are 3 lines. Only the position of the "visit" line changes.
```python
def preorder(n):                         # root, left, right
    return [n.val] + preorder(n.left) + preorder(n.right) if n else []

def inorder(n):                          # left, root, right  (sorted order for a BST!)
    return inorder(n.left) + [n.val] + inorder(n.right) if n else []

def postorder(n):                        # left, right, root
    return postorder(n.left) + postorder(n.right) + [n.val] if n else []

def inorder_iterative(root):             # explicit stack: no recursion limit worries
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out

def preorder_iterative(root):
    out, stack = [], [root] if root else []
    while stack:
        n = stack.pop()
        out.append(n.val)
        if n.right: stack.append(n.right)    # right first so left is popped first
        if n.left: stack.append(n.left)
    return out

t = build_tree([1, 2, 3, 4, 5])
assert preorder(t) == [1, 2, 4, 5, 3]
assert inorder(t) == [4, 2, 5, 1, 3]
assert postorder(t) == [4, 5, 2, 3, 1]
assert inorder_iterative(t) == inorder(t)
assert preorder_iterative(t) == preorder(t)
assert inorder(None) == []
```

## Breadth-first: level order
Use a queue. Process exactly `len(queue)` nodes per round to separate levels.
```python
def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        out.append([])
        for _ in range(len(q)):          # freeze the level size first
            n = q.popleft()
            out[-1].append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
    return out

def right_side_view(root):               # last node of each level
    return [lvl[-1] for lvl in level_order(root)]

def zigzag_level_order(root):
    return [lvl if i % 2 == 0 else lvl[::-1] for i, lvl in enumerate(level_order(root))]

t = build_tree([3, 9, 20, None, None, 15, 7])
assert level_order(t) == [[3], [9, 20], [15, 7]]
assert right_side_view(t) == [3, 20, 7]
assert zigzag_level_order(t) == [[3], [20, 9], [15, 7]]
assert level_order(None) == []
```

## The recursive pattern for most tree questions
Answer for a node = combine(answer for left, answer for right). Decide what to return, handle `None`, combine.
```python
def max_depth(n):
    return 0 if not n else 1 + max(max_depth(n.left), max_depth(n.right))

def count_nodes(n):
    return 0 if not n else 1 + count_nodes(n.left) + count_nodes(n.right)

def is_same(a, b):
    if not a and not b:
        return True
    if not a or not b or a.val != b.val:
        return False
    return is_same(a.left, b.left) and is_same(a.right, b.right)

def is_symmetric(root):
    def mirror(a, b):
        if not a and not b:
            return True
        if not a or not b or a.val != b.val:
            return False
        return mirror(a.left, b.right) and mirror(a.right, b.left)
    return mirror(root.left, root.right) if root else True

def invert(n):
    if n:
        n.left, n.right = invert(n.right), invert(n.left)
    return n

def diameter(root):                      # longest path (in edges) between any two nodes
    best = 0

    def height(n):
        nonlocal best
        if not n:
            return 0
        l, r = height(n.left), height(n.right)
        best = max(best, l + r)          # path bending at this node
        return 1 + max(l, r)

    height(root)
    return best

def is_balanced(root):
    def h(n):                            # returns height, or -1 if unbalanced below
        if not n:
            return 0
        l, r = h(n.left), h(n.right)
        if l == -1 or r == -1 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)
    return h(root) != -1

def max_path_sum(root):                  # best path sum, any start and end
    best = float("-inf")

    def gain(n):
        nonlocal best
        if not n:
            return 0
        l, r = max(gain(n.left), 0), max(gain(n.right), 0)   # ignore negative branches
        best = max(best, n.val + l + r)
        return n.val + max(l, r)

    gain(root)
    return best

def has_path_sum(n, target):
    if not n:
        return False
    if not n.left and not n.right:
        return n.val == target
    return has_path_sum(n.left, target - n.val) or has_path_sum(n.right, target - n.val)

def lca(root, p, q):                     # lowest common ancestor in a general binary tree
    if not root or root is p or root is q:
        return root
    l, r = lca(root.left, p, q), lca(root.right, p, q)
    return root if l and r else l or r

def good_nodes(root):                    # node >= every value on the path from root
    def go(n, mx):
        if not n:
            return 0
        return (n.val >= mx) + go(n.left, max(mx, n.val)) + go(n.right, max(mx, n.val))
    return go(root, float("-inf"))

t = build_tree([3, 9, 20, None, None, 15, 7])
assert max_depth(t) == 3 and max_depth(None) == 0 and count_nodes(t) == 5
assert is_same(build_tree([1, 2, 3]), build_tree([1, 2, 3]))
assert not is_same(build_tree([1, 2]), build_tree([1, None, 2]))
assert is_symmetric(build_tree([1, 2, 2, 3, 4, 4, 3]))
assert not is_symmetric(build_tree([1, 2, 2, None, 3, None, 3]))
assert level_order(invert(build_tree([4, 2, 7, 1, 3, 6, 9]))) == [[4], [7, 2], [9, 6, 3, 1]]
assert diameter(build_tree([1, 2, 3, 4, 5])) == 3
assert is_balanced(t) and not is_balanced(build_tree([1, 2, None, 3]))
assert max_path_sum(build_tree([-10, 9, 20, None, None, 15, 7])) == 42
assert max_path_sum(build_tree([-3])) == -3
assert has_path_sum(build_tree([5, 4, 8, 11, None, 13, 4, 7, 2]), 22)
assert not has_path_sum(build_tree([1, 2, 3]), 5)
tr = build_tree([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
assert lca(tr, tr.left, tr.right) is tr
assert lca(tr, tr.left, tr.left.right.right).val == 5
assert good_nodes(build_tree([3, 1, 4, 3, None, 1, 5])) == 4
```

## Build a tree from traversals
```python
def build_from_pre_in(preorder_list, inorder_list):
    pos = {v: i for i, v in enumerate(inorder_list)}
    it = iter(preorder_list)

    def go(lo, hi):
        if lo > hi:
            return None
        node = TreeNode(next(it))        # preorder gives the root first
        mid = pos[node.val]
        node.left = go(lo, mid - 1)
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(inorder_list) - 1)

class Codec:                             # serialize / deserialize, preorder with null markers
    def serialize(self, root):
        out = []

        def go(n):
            if not n:
                out.append("N")
                return
            out.append(str(n.val))
            go(n.left)
            go(n.right)

        go(root)
        return ",".join(out)

    def deserialize(self, data):
        it = iter(data.split(","))

        def go():
            v = next(it)
            if v == "N":
                return None
            n = TreeNode(int(v))
            n.left = go()
            n.right = go()
            return n

        return go()

def flatten(root):                       # in place into a right-leaning "linked list" in preorder
    cur = root
    while cur:
        if cur.left:
            pre = cur.left
            while pre.right:
                pre = pre.right
            pre.right, cur.right, cur.left = cur.right, cur.left, None
        cur = cur.right

r = build_from_pre_in([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
assert level_order(r) == [[3], [9, 20], [15, 7]]
c = Codec()
t = build_tree([1, 2, 3, None, None, 4, 5])
assert c.serialize(t) == "1,2,N,N,3,4,N,N,5,N,N"
assert level_order(c.deserialize(c.serialize(t))) == level_order(t)
assert c.deserialize(c.serialize(None)) is None
t = build_tree([1, 2, 5, 3, 4, None, 6]); flatten(t)
assert [t.val, t.right.val, t.right.right.val, t.right.right.right.val] == [1, 2, 3, 4]
```

## Binary search tree (BST)
Rule: for every node, everything in the left subtree is smaller and everything in the right is larger. So search is "go left or right", and an **inorder walk gives sorted order**.
```python
def bst_search(n, target):
    while n and n.val != target:
        n = n.left if target < n.val else n.right
    return n

def bst_insert(n, val):
    if not n:
        return TreeNode(val)
    if val < n.val:
        n.left = bst_insert(n.left, val)
    elif val > n.val:
        n.right = bst_insert(n.right, val)
    return n

def bst_delete(n, val):
    if not n:
        return None
    if val < n.val:
        n.left = bst_delete(n.left, val)
    elif val > n.val:
        n.right = bst_delete(n.right, val)
    else:
        if not n.left:                   # 0 or 1 child: lift the child
            return n.right
        if not n.right:
            return n.left
        succ = n.right                   # 2 children: copy the inorder successor, delete it below
        while succ.left:
            succ = succ.left
        n.val = succ.val
        n.right = bst_delete(n.right, succ.val)
    return n

def is_valid_bst(root):
    def ok(n, lo, hi):                   # pass the allowed range down, not just the parent
        if not n:
            return True
        if not (lo < n.val < hi):
            return False
        return ok(n.left, lo, n.val) and ok(n.right, n.val, hi)
    return ok(root, float("-inf"), float("inf"))

def kth_smallest(root, k):               # inorder, stop at k
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right

def sorted_array_to_bst(a):
    if not a:
        return None
    mid = len(a) // 2
    return TreeNode(a[mid], sorted_array_to_bst(a[:mid]), sorted_array_to_bst(a[mid + 1:]))

def lca_bst(root, p, q):                 # use the ordering: no need to search both sides
    while root:
        if p < root.val and q < root.val:
            root = root.left
        elif p > root.val and q > root.val:
            root = root.right
        else:
            return root

root = None
for v in (5, 3, 8, 1, 4, 7, 9):
    root = bst_insert(root, v)
assert inorder(root) == [1, 3, 4, 5, 7, 8, 9]
assert bst_search(root, 4).val == 4 and bst_search(root, 6) is None
root = bst_delete(root, 3)               # node with two children
assert inorder(root) == [1, 4, 5, 7, 8, 9]
root = bst_delete(root, 1)               # leaf
root = bst_delete(root, 5)               # the root, two children
assert inorder(root) == [4, 7, 8, 9] and root.val == 7
assert is_valid_bst(build_tree([2, 1, 3])) and not is_valid_bst(build_tree([5, 1, 4, None, None, 3, 6]))
assert not is_valid_bst(build_tree([5, 4, 6, None, None, 3, 7]))     # 3 is in the right subtree of 5
assert kth_smallest(build_tree([3, 1, 4, None, 2]), 1) == 1
assert kth_smallest(build_tree([5, 3, 6, 2, 4, None, None, 1]), 3) == 3
b = sorted_array_to_bst([-10, -3, 0, 5, 9])
assert inorder(b) == [-10, -3, 0, 5, 9] and abs(max_depth(b.left) - max_depth(b.right)) <= 1
assert lca_bst(build_tree([6, 2, 8, 0, 4, 7, 9]), 2, 8).val == 6
assert lca_bst(build_tree([6, 2, 8, 0, 4, 7, 9]), 2, 4).val == 2
```

## BST complexity
| Operation | Balanced | Worst (sorted input -> a stick) |
|---|---|---|
| Search / insert / delete | O(log n) | O(n) |
Plain BSTs don't rebalance. In real code use a sorted list with `bisect`, or a library such as `sortedcontainers`; AVL/Red-Black trees are what databases and `std::map` use inside.

Recursion depth equals tree height. A skewed tree of 10,000 nodes will hit Python's recursion limit (note 5), so prefer iterative versions for huge inputs.

## Practice map
| Pattern | NeetCode 150 | Striver SDE Sheet |
|---|---|---|
| Basic recursion | Invert Binary Tree, Maximum Depth of Binary Tree, Same Tree, Subtree of Another Tree | Maximum Depth, Same Tree, Symmetric Tree |
| Height-based | Diameter of Binary Tree, Balanced Binary Tree | Diameter of Binary Tree, Balanced Binary Tree |
| LCA | Lowest Common Ancestor of a BST | Lowest Common Ancestor of a Binary Tree, ...of a BST |
| BFS | Binary Tree Level Order Traversal, Binary Tree Right Side View | Level Order, Zigzag Level Order, Right Side View, Boundary of Binary Tree |
| Path / hard | Binary Tree Maximum Path Sum, Count Good Nodes in Binary Tree | Binary Tree Maximum Path Sum |
| Construct | Construct Binary Tree from Preorder and Inorder Traversal, Serialize and Deserialize Binary Tree | Construct from Preorder and Inorder, from Inorder and Postorder, Flatten Binary Tree to Linked List, Populating Next Right Pointers |
| BST | Validate Binary Search Tree, Kth Smallest Element in a BST | Search in a BST, Convert Sorted Array to BST, Validate BST, Kth Smallest in BST, BST Iterator, Two Sum IV, Inorder Successor, Largest BST Subtree |
| Traversals | Binary Tree Inorder/Preorder/Postorder (drills) | Inorder, Preorder, Postorder Traversal |

## Mistakes to avoid
- Forgetting the `None` base case.
- Validating a BST by only comparing a node with its direct children. Pass down a `(lo, hi)` range.
- Level-order without freezing `len(q)` first: levels blur together.
- Confusing height measured in nodes vs edges (diameter counts edges).
- Mutating a tree while another traversal is using it.

## Check yourself
- Which traversal order of a BST gives sorted values?
- Why does `is_valid_bst` need a range and not just the parent value?
- How do you separate levels in BFS?
