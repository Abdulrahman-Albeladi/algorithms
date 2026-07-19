from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class Node(Generic[K, V]):
    key: K
    value: V
    left: Optional["Node[K, V]"] = None
    right: Optional["Node[K, V]"] = None
    parent: Optional["Node[K, V]"] = None


class ScapegoatTree(Generic[K, V]):
    """Scapegoat tree with subtree rebuilding.

    The tree maintains binary-search-tree ordering and uses partial rebuilds
    instead of per-node balance metadata. The `alpha` parameter must satisfy
    0.5 < alpha < 1.0.
    """

    def __init__(self, alpha: float = 2.0 / 3.0) -> None:
        if not (0.5 < alpha < 1.0):
            raise ValueError("alpha must satisfy 0.5 < alpha < 1.0")
        self.alpha = alpha
        self.root: Optional[Node[K, V]] = None
        self.size = 0
        self.max_size = 0

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: K) -> bool:
        return self._find_node(key) is not None

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._find_node(key)
        return default if node is None else node.value

    def search_path(self, key: K) -> list[V]:
        path: list[V] = []
        current = self.root
        while current is not None:
            path.append(current.value)
            if key == current.key:
                return path
            current = current.left if key < current.key else current.right
        return []

    def insert(self, key: K, value: V) -> None:
        if self.root is None:
            self.root = Node(key=key, value=value)
            self.size = 1
            self.max_size = 1
            return

        current = self.root
        depth = 0
        while True:
            if key == current.key:
                current.value = value
                return
            if key < current.key:
                if current.left is None:
                    current.left = Node(key=key, value=value, parent=current)
                    inserted = current.left
                    depth += 1
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = Node(key=key, value=value, parent=current)
                    inserted = current.right
                    depth += 1
                    break
                current = current.right
            depth += 1

        self.size += 1
        self.max_size = max(self.max_size, self.size)

        if depth > self._max_allowed_depth(self.size):
            scapegoat = self._find_scapegoat(inserted)
            if scapegoat is not None:
                self._rebuild_subtree(scapegoat)

    def delete(self, key: K) -> bool:
        node = self._find_node(key)
        if node is None:
            return False

        if node.left is not None and node.right is not None:
            successor = self._minimum(node.right)
            node.key, successor.key = successor.key, node.key
            node.value, successor.value = successor.value, node.value
            node = successor

        child = node.left if node.left is not None else node.right
        self._replace_node(node, child)
        self.size -= 1

        if self.size == 0:
            self.root = None
            self.max_size = 0
        elif self.size < self.alpha * self.max_size:
            self.root = self._build_balanced(list(self._inorder_nodes(self.root)), None)
            self.max_size = self.size
        return True

    def items(self) -> Iterator[tuple[K, V]]:
        for node in self._inorder_nodes(self.root):
            yield node.key, node.value

    def dump(self) -> str:
        def to_dict(node: Optional[Node[K, V]]) -> Optional[dict]:
            if node is None:
                return None
            return {
                "k": node.key,
                "v": node.value,
                "l": to_dict(node.left),
                "r": to_dict(node.right),
            }

        return json.dumps({} if self.root is None else to_dict(self.root), indent=2)

    def _find_node(self, key: K) -> Optional[Node[K, V]]:
        current = self.root
        while current is not None:
            if key == current.key:
                return current
            current = current.left if key < current.key else current.right
        return None

    def _max_allowed_depth(self, n: int) -> int:
        return math.floor(math.log(n, 1.0 / self.alpha)) if n > 1 else 0

    def _find_scapegoat(self, node: Node[K, V]) -> Optional[Node[K, V]]:
        current = node.parent
        while current is not None:
            left_size = self._subtree_size(current.left)
            right_size = self._subtree_size(current.right)
            if max(left_size, right_size) > self.alpha * (1 + left_size + right_size):
                return current
            current = current.parent
        return None

    def _rebuild_subtree(self, root: Node[K, V]) -> None:
        parent = root.parent
        rebuilt = self._build_balanced(list(self._inorder_nodes(root)), parent)
        if parent is None:
            self.root = rebuilt
        elif parent.left is root:
            parent.left = rebuilt
        else:
            parent.right = rebuilt

    def _replace_node(
        self, node: Node[K, V], replacement: Optional[Node[K, V]]
    ) -> None:
        if node.parent is None:
            self.root = replacement
        elif node.parent.left is node:
            node.parent.left = replacement
        else:
            node.parent.right = replacement
        if replacement is not None:
            replacement.parent = node.parent

    def _minimum(self, node: Node[K, V]) -> Node[K, V]:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _subtree_size(self, node: Optional[Node[K, V]]) -> int:
        if node is None:
            return 0
        return 1 + self._subtree_size(node.left) + self._subtree_size(node.right)

    def _inorder_nodes(self, node: Optional[Node[K, V]]) -> Iterator[Node[K, V]]:
        if node is None:
            return
        yield from self._inorder_nodes(node.left)
        yield Node(key=node.key, value=node.value)
        yield from self._inorder_nodes(node.right)

    def _build_balanced(
        self,
        nodes: list[Node[K, V]],
        parent: Optional[Node[K, V]],
    ) -> Optional[Node[K, V]]:
        if not nodes:
            return None
        mid = len(nodes) // 2
        root = nodes[mid]
        root.parent = parent
        root.left = self._build_balanced(nodes[:mid], root)
        root.right = self._build_balanced(nodes[mid + 1 :], root)
        return root
