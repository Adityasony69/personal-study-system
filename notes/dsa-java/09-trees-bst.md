# Trees and binary search trees

## Words to know
- **Node:** holds a value and links to its children. **Root:** the top node. **Leaf:** a node with no children.
- **Binary tree:** each node has at most two children, left and right.
- **Height:** the number of nodes on the longest path from the root down to a leaf.
- **Subtree:** any node together with everything below it. Every subtree is itself a tree, which is why recursion fits so well.

```java
class TreeNode {
    int val;
    TreeNode left, right;

    TreeNode(int val) {
        this.val = val;
    }
}
```

Example tree used below:

```
        4
      /   \
     2     6
    / \   / \
   1   3 5   7
```

## Depth-first traversals
Three orders, named after when you visit the root.

| Order | Sequence | Result on the example | Used for |
|---|---|---|---|
| Inorder | left, root, right | 1 2 3 4 5 6 7 | Sorted output from a BST |
| Preorder | root, left, right | 4 2 1 3 6 5 7 | Copying or saving a tree |
| Postorder | left, right, root | 1 3 2 5 7 6 4 | Deleting, or computing from the children up |

```java
class Traversals {
    static void inorder(TreeNode node, List<Integer> out) {
        if (node == null) return;
        inorder(node.left, out);
        out.add(node.val);
        inorder(node.right, out);
    }

    static void preorder(TreeNode node, List<Integer> out) {
        if (node == null) return;
        out.add(node.val);
        preorder(node.left, out);
        preorder(node.right, out);
    }

    static void postorder(TreeNode node, List<Integer> out) {
        if (node == null) return;
        postorder(node.left, out);
        postorder(node.right, out);
        out.add(node.val);
    }
}
```

## Breadth-first: level order
Visit the tree one level at a time using a queue. Result on the example: `[[4], [2, 6], [1, 3, 5, 7]]`.

```java
class LevelOrder {
    static List<List<Integer>> levels(TreeNode root) {
        List<List<Integer>> out = new ArrayList<>();
        if (root == null) return out;
        Queue<TreeNode> queue = new ArrayDeque<>();
        queue.offer(root);
        while (!queue.isEmpty()) {
            int size = queue.size();                   // number of nodes on this level
            List<Integer> level = new ArrayList<>();
            for (int i = 0; i < size; i++) {
                TreeNode node = queue.poll();
                level.add(node.val);
                if (node.left != null) queue.offer(node.left);
                if (node.right != null) queue.offer(node.right);
            }
            out.add(level);
        }
        return out;
    }
}
```

## The recursive pattern for most tree questions
1. Base case: a null node.
2. Ask the left subtree, ask the right subtree.
3. Combine the two answers with the current node.

```java
class TreeQuestions {
    static int height(TreeNode node) {
        if (node == null) return 0;
        return 1 + Math.max(height(node.left), height(node.right));
    }

    static int countNodes(TreeNode node) {
        if (node == null) return 0;
        return 1 + countNodes(node.left) + countNodes(node.right);
    }

    static boolean isSameTree(TreeNode a, TreeNode b) {
        if (a == null && b == null) return true;
        if (a == null || b == null) return false;
        return a.val == b.val && isSameTree(a.left, b.left) && isSameTree(a.right, b.right);
    }

    static TreeNode invert(TreeNode node) {            // mirror image
        if (node == null) return null;
        TreeNode left = invert(node.left);
        node.left = invert(node.right);
        node.right = left;
        return node;
    }

    static boolean hasPathSum(TreeNode node, int target) {   // root-to-leaf path adding up to target
        if (node == null) return false;
        if (node.left == null && node.right == null) return node.val == target;
        return hasPathSum(node.left, target - node.val) || hasPathSum(node.right, target - node.val);
    }
}
```

## Binary search tree (BST)
A binary tree with one rule at every node: **everything in the left subtree is smaller, everything in the right subtree is larger.** The example tree above is a BST.

That rule lets you throw away half the tree at each step, like binary search.

```java
class Bst {
    static TreeNode search(TreeNode node, int target) {
        while (node != null && node.val != target) {
            node = target < node.val ? node.left : node.right;
        }
        return node;                                   // null if not found
    }

    static TreeNode insert(TreeNode node, int val) {
        if (node == null) return new TreeNode(val);    // found the empty spot
        if (val < node.val) node.left = insert(node.left, val);
        else if (val > node.val) node.right = insert(node.right, val);
        return node;                                   // duplicates are ignored
    }

    static boolean isValid(TreeNode node, long low, long high) {
        if (node == null) return true;
        if (node.val <= low || node.val >= high) return false;
        return isValid(node.left, low, node.val) && isValid(node.right, node.val, high);
    }

    static TreeNode lowestCommonAncestor(TreeNode node, int p, int q) {
        while (node != null) {
            if (p < node.val && q < node.val) node = node.left;         // both are on the left
            else if (p > node.val && q > node.val) node = node.right;   // both are on the right
            else return node;                                           // they split here
        }
        return null;
    }
}
```

Call `Bst.isValid(root, Long.MIN_VALUE, Long.MAX_VALUE)`. Checking only "left child smaller, right child larger" is not enough: a node deep in the left subtree must still be smaller than the root.

## BST complexity
| Operation | Balanced tree | Worst case (a chain) |
|---|---|---|
| Search, insert, delete | O(log n) | O(n) |

Inserting already sorted values into a plain BST gives a chain. Self-balancing trees fix this. In Java, `TreeMap` and `TreeSet` are balanced (red-black trees), so they guarantee O(log n).

## Mistakes to avoid
- Forgetting the null base case.
- Validating a BST by comparing only with the direct children.
- In level order, calling `queue.size()` inside the loop condition. It changes as you add children. Save it first.
- Mixing up height and depth: height is counted from the bottom, depth from the root.

## Check yourself
- Which traversal of a BST gives the values in sorted order, and why?
- Why does `isValid` pass a low and a high limit down the tree?
- When does a BST become as slow as a linked list?
