# Trees

**23 questions:** 9 Easy, 12 Medium, 2 Hard. Questions are listed Easy first, then Medium, then Hard.

## The idea in plain words

A tree problem is almost always: solve it for one node, trusting that recursion solves the left and right subtrees.

## How to spot this pattern

- The input is a TreeNode.
- Depth, height, path, ancestor, level, BST order.

## Thinking steps (use these on every question here)

1. Write the base case: what is the answer for an empty node?
2. Decide what the function returns to its parent.
3. Decide the order: before children (preorder), between (inorder), or after (postorder).
4. Level-by-level questions use BFS with a queue.
5. For a BST remember: inorder gives sorted order.

## Common beginner mistakes

- Mixing up what the function returns with what the question asks (often you need a global best plus a returned height).
- Checking only the direct children when validating a BST.

Read first: your `dsa-python` notes, file(s) 09-trees-bst.

## Question list

| # | Question | Difficulty | LeetCode | List |
|---|---|---|---|---|
| 1 | Binary Tree Inorder Traversal | Easy | 94 | 250 |
| 2 | Binary Tree Preorder Traversal | Easy | 144 | 250 |
| 3 | Binary Tree Postorder Traversal | Easy | 145 | 250 |
| 4 | Invert Binary Tree | Easy | 226 | 150 |
| 5 | Maximum Depth of Binary Tree | Easy | 104 | 150 |
| 6 | Diameter of Binary Tree | Easy | 543 | 150 |
| 7 | Balanced Binary Tree | Easy | 110 | 150 |
| 8 | Same Tree | Easy | 100 | 150 |
| 9 | Subtree of Another Tree | Easy | 572 | 150 |
| 10 | Lowest Common Ancestor of a Binary Search Tree | Medium | 235 | 150 |
| 11 | Insert into a Binary Search Tree | Medium | 701 | 250 |
| 12 | Delete Node in a BST | Medium | 450 | 250 |
| 13 | Binary Tree Level Order Traversal | Medium | 102 | 150 |
| 14 | Binary Tree Right Side View | Medium | 199 | 150 |
| 15 | Construct Quad Tree | Medium | 427 | 250 |
| 16 | Count Good Nodes In Binary Tree | Medium | 1448 | 150 |
| 17 | Validate Binary Search Tree | Medium | 98 | 150 |
| 18 | Kth Smallest Element In a Bst | Medium | 230 | 150 |
| 19 | Construct Binary Tree From Preorder And Inorder Traversal | Medium | 105 | 150 |
| 20 | House Robber III | Medium | 337 | 250 |
| 21 | Delete Leaves With a Given Value | Medium | 1325 | 250 |
| 22 | Binary Tree Maximum Path Sum | Hard | 124 | 150 |
| 23 | Serialize And Deserialize Binary Tree | Hard | 297 | 150 |

List column: 150 = in NeetCode 150 (and 250). 250 = only in NeetCode 250.

## Easy questions

### 1. Binary Tree Inorder Traversal  [Easy]

- **Find it:** LeetCode #94, search "Binary Tree Inorder Traversal"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Inorder = left, node, right.
- **First step:** Write it recursively first.
- **If stuck:** Iterative: push nodes while going left; pop, record, then go right.

### 2. Binary Tree Preorder Traversal  [Easy]

- **Find it:** LeetCode #144, search "Binary Tree Preorder Traversal"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Preorder = node, left, right.
- **First step:** Recursion first.
- **If stuck:** Iterative: stack; pop a node, record it, push right child then left child.

### 3. Binary Tree Postorder Traversal  [Easy]

- **Find it:** LeetCode #145, search "Binary Tree Postorder Traversal"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Postorder = left, right, node.
- **First step:** Recursion first.
- **If stuck:** Iterative trick: do node, right, left and reverse the result.

### 4. Invert Binary Tree  [Easy]

- **Find it:** LeetCode #226, search "Invert Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Every node swaps its left and right child.
- **First step:** Think recursively: what do you do at ONE node?
- **If stuck:** Swap the children, then invert each subtree. Base case: empty node.

### 5. Maximum Depth of Binary Tree  [Easy]

- **Find it:** LeetCode #104, search "Maximum Depth of Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Depth of a node = 1 + the deeper of its two subtrees.
- **First step:** Write the base case for an empty node.
- **If stuck:** return 1 + max(depth(left), depth(right)).

### 6. Diameter of Binary Tree  [Easy]

- **Find it:** LeetCode #543, search "Diameter of Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The longest path may not pass through the root.
- **First step:** At each node, the longest path THROUGH it = left height + right height.
- **If stuck:** Write a height function that also updates a global best as it returns.

### 7. Balanced Binary Tree  [Easy]

- **Find it:** LeetCode #110, search "Balanced Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The two subtrees of every node may differ in height by at most 1.
- **First step:** Reuse the height function.
- **If stuck:** Return height from the bottom up; return a special value (like -1) as soon as any subtree is unbalanced.

### 8. Same Tree  [Easy]

- **Find it:** LeetCode #100, search "Same Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Two trees are the same if the roots match and both subtree pairs match.
- **First step:** Handle the cases: both empty, one empty, values differ.
- **If stuck:** Recurse on (left, left) and (right, right).

### 9. Subtree of Another Tree  [Easy]

- **Find it:** LeetCode #572, search "Subtree of Another Tree"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** Some node in the big tree must be the root of an identical tree.
- **First step:** Reuse Same Tree as a helper.
- **If stuck:** At each node check sameTree(node, sub); if not, try the left and right children.

## Medium questions

### 10. Lowest Common Ancestor of a Binary Search Tree  [Medium]

- **Find it:** LeetCode #235, search "Lowest Common Ancestor of a Binary Search Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** In a BST, smaller values go left and larger go right.
- **First step:** Compare both targets with the current node.
- **If stuck:** If both are smaller go left; both larger go right; otherwise the current node is the split point: the answer.

### 11. Insert into a Binary Search Tree  [Medium]

- **Find it:** LeetCode #701, search "Insert into a Binary Search Tree"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** A new value always becomes a new leaf.
- **First step:** Walk down as if searching for the value.
- **If stuck:** When you fall off the tree, that empty spot is where the new node goes.

### 12. Delete Node in a BST  [Medium]

- **Find it:** LeetCode #450, search "Delete Node in a BST"
- **Lists:** NeetCode 250, Striver A2Z
- **Notice:** Three cases: no child, one child, two children.
- **First step:** Find the node first using BST order.
- **If stuck:** With two children: copy the smallest value of the right subtree into the node, then delete that value from the right subtree.

### 13. Binary Tree Level Order Traversal  [Medium]

- **Find it:** LeetCode #102, search "Binary Tree Level Order Traversal"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Level by level means BFS with a queue.
- **First step:** Put the root in a queue.
- **If stuck:** For each level, record the current size of the queue and pop exactly that many nodes, pushing their children.

### 14. Binary Tree Right Side View  [Medium]

- **Find it:** LeetCode #199, search "Binary Tree Right Side View"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You see the last node of every level.
- **First step:** Do a level-order traversal.
- **If stuck:** Record the last node popped in each level.

### 15. Construct Quad Tree  [Medium]

- **Find it:** LeetCode #427, search "Construct Quad Tree"
- **Lists:** NeetCode 250
- **Notice:** If a square is all the same value it is a leaf; otherwise split it into four.
- **First step:** Write a recursive function (row, col, size).
- **If stuck:** Build the four children first; if all four are leaves with the same value, merge them into one leaf.

### 16. Count Good Nodes In Binary Tree  [Medium]

- **Find it:** LeetCode #1448, search "Count Good Nodes In Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250
- **Notice:** A node is good if nothing above it on its path is larger.
- **First step:** Carry the maximum value seen so far down the recursion.
- **If stuck:** Count the node if its value >= that maximum, then pass the updated maximum to the children.

### 17. Validate Binary Search Tree  [Medium]

- **Find it:** LeetCode #98, search "Validate Binary Search Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Checking only parent vs child is not enough.
- **First step:** Every node has an allowed range (low, high).
- **If stuck:** Going left tightens the upper bound; going right tightens the lower bound. (Or: inorder traversal must be strictly increasing.)

### 18. Kth Smallest Element In a Bst  [Medium]

- **Find it:** LeetCode #230, search "Kth Smallest Element In a Bst"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** Inorder traversal of a BST visits values in sorted order.
- **First step:** Do an inorder traversal.
- **If stuck:** Count nodes as you visit them and stop at the k-th.

### 19. Construct Binary Tree From Preorder And Inorder Traversal  [Medium]

- **Find it:** LeetCode #105, search "Construct Binary Tree From Preorder And Inorder Traversal"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** The first value of preorder is the root; inorder tells you what is left and right of it.
- **First step:** Find the position of the root in inorder.
- **If stuck:** The number of nodes to its left tells you how to split preorder; recurse. A value -> index dictionary makes it fast.

### 20. House Robber III  [Medium]

- **Find it:** LeetCode #337, search "House Robber III"
- **Lists:** NeetCode 250
- **Notice:** Robbing a node forbids robbing its children.
- **First step:** For each node return TWO answers: best if you rob it, best if you skip it.
- **If stuck:** rob = value + skip(left) + skip(right); skip = max of both options for left + max of both for right.

### 21. Delete Leaves With a Given Value  [Medium]

- **Find it:** LeetCode #1325, search "Delete Leaves With a Given Value"
- **Lists:** NeetCode 250
- **Notice:** Deleting a leaf can turn its parent into a new leaf.
- **First step:** Process children BEFORE the node (postorder).
- **If stuck:** After fixing both children, if the node is now a leaf with the target value, return None.

## Hard questions

### 22. Binary Tree Maximum Path Sum  [Hard]

- **Find it:** LeetCode #124, search "Binary Tree Maximum Path Sum"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** A path can bend at one node only.
- **First step:** For each node compute the best "one-sided" gain going down.
- **If stuck:** Update the global best with node + left gain + right gain; return node + max(left, right). Treat negative gains as 0.

### 23. Serialize And Deserialize Binary Tree  [Hard]

- **Find it:** LeetCode #297, search "Serialize And Deserialize Binary Tree"
- **Lists:** NeetCode 150, NeetCode 250, Striver A2Z
- **Notice:** You must record empty children or the shape is lost.
- **First step:** Use preorder and write a marker like "N" for empty.
- **If stuck:** Deserialize by reading values in the same order with a moving index: read one value, build the node, build left, build right.
