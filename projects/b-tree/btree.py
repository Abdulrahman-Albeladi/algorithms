from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Iterator, Optional


@dataclass
class Node:
    """A node in a B-tree.

    Leaf nodes retain ``None`` child slots so ``dump()`` produces the same
    explicit leaf representation used by the original implementation.
    """

    keys: list[int] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    children: list[Optional["Node"]] = field(default_factory=list)
    order: list[int] = field(default_factory=list)
    parent: Optional["Node"] = None


class Btree:
    """An in-memory B-tree mapping integer keys to string values.

    ``m`` is the maximum number of children in an internal node. A node may
    therefore contain at most ``m - 1`` keys.
    """

    def __init__(self, m: int = 3, root: Optional[Node] = None):
        if not isinstance(m, int) or m < 3:
            raise ValueError("m must be an integer greater than or equal to 3")

        self.m = m
        self.root = root
        if self.root is not None:
            self._refresh_metadata(self.root, None)

    @property
    def _max_keys(self) -> int:
        return self.m - 1

    def dump(self) -> str:
        """Return a JSON representation of the tree."""

        def to_dict(node: Node) -> dict[str, object]:
            return {
                "keys": node.keys,
                "values": node.values,
                "children": [
                    to_dict(child) if child is not None else None
                    for child in node.children
                ],
            }

        return json.dumps({} if self.root is None else to_dict(self.root), indent=2)

    def insert(self, key: int, value: str) -> None:
        """Insert a key/value pair.

        Duplicate keys are retained; searches return the first matching key
        encountered while descending from the root.
        """
        if self.root is None:
            self.root = Node(keys=[key], values=[value])
            self._refresh_metadata(self.root, None)
            return

        leaf = self._find_leaf(key)
        index = self._position(key, leaf.keys)
        leaf.keys.insert(index, key)
        leaf.values.insert(index, value)

        self._split_overfull_nodes(leaf)
        self._refresh_metadata(self.root, None)

    def delete(self, key: int) -> None:
        """Remove one occurrence of ``key`` when it exists.

        Rebuilding from the remaining sorted entries keeps deletion correct for
        every supported tree order, including odd orders where a direct merge
        can temporarily exceed the configured node capacity.
        """
        entries = list(self._entries())
        for index, (entry_key, _) in enumerate(entries):
            if entry_key == key:
                del entries[index]
                self.root = None
                for remaining_key, remaining_value in entries:
                    self.insert(remaining_key, remaining_value)
                return

    def search(self, key: int) -> Optional[str]:
        """Return the value associated with ``key``, or ``None`` if absent."""
        current = self.root
        while current is not None:
            index = self._position(key, current.keys)
            if index < len(current.keys) and current.keys[index] == key:
                return current.values[index]

            if self._is_leaf(current):
                return None
            current = current.children[index]

        return None

    def _find_leaf(self, key: int) -> Node:
        current = self.root
        assert current is not None  # nosec B101

        while not self._is_leaf(current):
            current = current.children[self._position(key, current.keys)]
            assert current is not None  # nosec B101
        return current

    def _split_overfull_nodes(self, node: Node) -> None:
        current = node
        while len(current.keys) > self._max_keys:
            middle = len(current.keys) // 2
            promoted_key = current.keys[middle]
            promoted_value = current.values[middle]

            left = Node(
                keys=current.keys[:middle],
                values=current.values[:middle],
            )
            right = Node(
                keys=current.keys[middle + 1 :],
                values=current.values[middle + 1 :],
            )

            if not self._is_leaf(current):
                left.children = current.children[: middle + 1]
                right.children = current.children[middle + 1 :]

            parent = current.parent
            if parent is None:
                self.root = Node(
                    keys=[promoted_key],
                    values=[promoted_value],
                    children=[left, right],
                )
                current = self.root
                continue

            child_index = parent.children.index(current)
            parent.keys.insert(child_index, promoted_key)
            parent.values.insert(child_index, promoted_value)
            parent.children[child_index : child_index + 1] = [left, right]
            current = parent

    def _entries(self) -> Iterator[tuple[int, str]]:
        def visit(node: Node) -> Iterator[tuple[int, str]]:
            if self._is_leaf(node):
                yield from zip(node.keys, node.values)
                return

            for index, (key, value) in enumerate(zip(node.keys, node.values)):
                child = node.children[index]
                assert child is not None  # nosec B101
                yield from visit(child)
                yield key, value

            final_child = node.children[-1]
            assert final_child is not None  # nosec B101
            yield from visit(final_child)

        if self.root is not None:
            yield from visit(self.root)

    @staticmethod
    def _position(key: int, keys: list[int]) -> int:
        """Return the insertion position before the first key not less than key."""
        low = 0
        high = len(keys)
        while low < high:
            middle = (low + high) // 2
            if keys[middle] < key:
                low = middle + 1
            else:
                high = middle
        return low

    @staticmethod
    def _is_leaf(node: Node) -> bool:
        return not node.children or node.children[0] is None

    def _refresh_metadata(self, node: Node, parent: Optional[Node]) -> None:
        node.parent = parent
        if self._is_leaf(node):
            node.children = [None] * (len(node.keys) + 1)
            node.order = []
            return

        if len(node.children) != len(node.keys) + 1:
            raise ValueError("internal node child count does not match its keys")

        node.order = list(range(len(node.children)))
        for child in node.children:
            if child is None:
                raise ValueError("internal nodes cannot contain empty child slots")
            self._refresh_metadata(child, node)
