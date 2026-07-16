from __future__ import annotations

import json
import math


class Node:
    """A node in a binary search tree."""

    def __init__(
        self,
        key=None,
        value=None,
        leftchild=None,
        rightchild=None,
        parent=None,
    ):
        self.key = key
        self.value = value
        self.leftchild = leftchild
        self.rightchild = rightchild
        self.parent = parent


class SGtree:
    """Scapegoat tree parameterized by alpha = a / b."""

    def __init__(
        self,
        a: int | None = None,
        b: int | None = None,
        m: int | None = None,
        n: int | None = None,
        root: Node | None = None,
    ):
        if a is None or b is None or not 0 < a < b:
            raise ValueError("scapegoat tree parameters must satisfy 0 < a < b")

        self.m = 0
        self.n = 0
        self.a = a
        self.b = b
        self.root = None

    @property
    def alpha(self) -> float:
        return self.a / self.b

    def dump(self) -> str:
        """Return a JSON representation of the tree."""

        def to_dict(node: Node) -> dict:
            return {
                "k": node.key,
                "v": node.value,
                "l": to_dict(node.leftchild) if node.leftchild is not None else None,
                "r": to_dict(node.rightchild) if node.rightchild is not None else None,
            }

        return json.dumps({} if self.root is None else to_dict(self.root), indent=2)

    def insert(self, key: int, value: str) -> None:
        """Insert a key-value pair, rebuilding an unbalanced ancestor if needed."""
        if self.root is None:
            self.root = Node(key, value)
            self.n = 1
            self.m = 1
            return

        current = self.root
        depth = 0
        while True:
            if key > current.key:
                if current.rightchild is None:
                    current.rightchild = Node(key, value, parent=current)
                    current = current.rightchild
                    depth += 1
                    break
                current = current.rightchild
            else:
                if current.leftchild is None:
                    current.leftchild = Node(key, value, parent=current)
                    current = current.leftchild
                    depth += 1
                    break
                current = current.leftchild
            depth += 1

        self.n += 1
        self.m = max(self.m, self.n)

        if depth > math.log(self.n, self.b / self.a):
            scape(self, current)
            self.m = self.n

    def delete(self, key: int) -> None:
        """Delete the first node matching *key*."""
        current = self.root
        while current is not None and current.key != key:
            current = current.rightchild if key > current.key else current.leftchild

        if current is None:
            raise KeyError(key)

        if current.leftchild is not None and current.rightchild is not None:
            successor = current.rightchild
            while successor.leftchild is not None:
                successor = successor.leftchild
            current.key = successor.key
            current.value = successor.value
            current = successor

        replacement = current.leftchild or current.rightchild
        if replacement is not None:
            replacement.parent = current.parent

        if current.parent is None:
            self.root = replacement
        elif current.parent.leftchild is current:
            current.parent.leftchild = replacement
        else:
            current.parent.rightchild = replacement

        self.n -= 1

        if self.n < self.alpha * self.m:
            self.root = restructure(self.root)
            self.m = self.n

    def search(self, search_key: int) -> str:
        """Return the JSON-encoded sequence of values visited during a search."""
        current = self.root
        path = []

        while current is not None:
            path.append(current.value)
            if search_key == current.key:
                return json.dumps(path)
            current = (
                current.rightchild if search_key > current.key else current.leftchild
            )

        raise KeyError(search_key)


def scape(tree: SGtree, node: Node) -> None:
    """Rebuild the first ancestor that violates the scapegoat balance bound."""
    current = node
    while current.parent is not None:
        parent = current.parent
        if size(current) > tree.alpha * size(parent):
            grandparent = parent.parent
            rebuilt = restructure(parent)

            if grandparent is None:
                tree.root = rebuilt
                if rebuilt is not None:
                    rebuilt.parent = None
            elif grandparent.leftchild is parent:
                grandparent.leftchild = rebuilt
                rebuilt.parent = grandparent
            else:
                grandparent.rightchild = rebuilt
                rebuilt.parent = grandparent
            return
        current = parent


def size(node: Node | None) -> int:
    """Return the number of nodes in the subtree rooted at *node*."""
    if node is None:
        return 0
    return 1 + size(node.leftchild) + size(node.rightchild)


def inorder(root: Node | None, reach: list[Node]) -> list[Node]:
    """Collect copies of nodes in in-order traversal order."""
    if root is None:
        return reach

    inorder(root.leftchild, reach)
    reach.append(Node(root.key, root.value))
    inorder(root.rightchild, reach)
    return reach


def sorting(root_list: list[Node]) -> Node | None:
    """Build a balanced tree from an in-order list of nodes."""
    if not root_list:
        return None

    midpoint = len(root_list) // 2
    root = root_list[midpoint]
    root.leftchild = sorting(root_list[:midpoint])
    root.rightchild = sorting(root_list[midpoint + 1 :])

    if root.leftchild is not None:
        root.leftchild.parent = root
    if root.rightchild is not None:
        root.rightchild.parent = root

    return root


def restructure(root: Node | None) -> Node | None:
    """Rebuild a subtree into a balanced binary search tree."""
    return sorting(inorder(root, []))
