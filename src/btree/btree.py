from __future__ import annotations

import json
from bisect import bisect_left
from dataclasses import dataclass, field
from typing import Generic, List, Optional, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class Node(Generic[K, V]):
    keys: List[K] = field(default_factory=list)
    values: List[V] = field(default_factory=list)
    children: List["Node[K, V]"] = field(default_factory=list)
    leaf: bool = True


class BTree(Generic[K, V]):
    """A minimal B-tree map implementation.

    This implementation is independent of any course-specific interface.
    It stores key-value pairs in sorted order and supports search, insert,
    and delete for a configurable minimum degree ``t``.

    Invariants:
    - Each node stores between ``t - 1`` and ``2t - 1`` keys, except the root.
    - Internal nodes with ``n`` keys have ``n + 1`` children.
    - Keys within each node are sorted.
    """

    def __init__(self, minimum_degree: int = 2):
        if minimum_degree < 2:
            raise ValueError("minimum_degree must be at least 2")
        self.t = minimum_degree
        self.root: Node[K, V] = Node()

    def dump(self) -> str:
        def to_dict(node: Node[K, V]) -> dict:
            return {
                "keys": list(node.keys),
                "values": list(node.values),
                "children": [to_dict(child) for child in node.children],
            }

        if not self.root.keys and self.root.leaf:
            return json.dumps({}, indent=2)
        return json.dumps(to_dict(self.root), indent=2)

    def search(self, key: K) -> Optional[V]:
        node, index = self._search_node(self.root, key)
        if node is None:
            return None
        return node.values[index]

    def insert(self, key: K, value: V) -> None:
        root = self.root
        existing_node, existing_index = self._search_node(root, key)
        if existing_node is not None:
            existing_node.values[existing_index] = value
            return

        if len(root.keys) == self._max_keys:
            new_root = Node(keys=[], values=[], children=[root], leaf=False)
            self.root = new_root
            self._split_child(new_root, 0)
            self._insert_nonfull(new_root, key, value)
        else:
            self._insert_nonfull(root, key, value)

    def delete(self, key: K) -> bool:
        deleted = self._delete(self.root, key)
        if not self.root.leaf and not self.root.keys:
            self.root = self.root.children[0]
        if self.root.leaf and not self.root.keys:
            self.root = Node()
        return deleted

    @property
    def _max_keys(self) -> int:
        return 2 * self.t - 1

    @property
    def _min_keys(self) -> int:
        return self.t - 1

    def _search_node(
        self, node: Node[K, V], key: K
    ) -> Tuple[Optional[Node[K, V]], int]:
        index = bisect_left(node.keys, key)
        if index < len(node.keys) and node.keys[index] == key:
            return node, index
        if node.leaf:
            return None, -1
        return self._search_node(node.children[index], key)

    def _split_child(self, parent: Node[K, V], child_index: int) -> None:
        t = self.t
        child = parent.children[child_index]
        median_key = child.keys[t - 1]
        median_value = child.values[t - 1]

        right = Node(
            keys=child.keys[t:],
            values=child.values[t:],
            children=child.children[t:] if not child.leaf else [],
            leaf=child.leaf,
        )

        child.keys = child.keys[: t - 1]
        child.values = child.values[: t - 1]
        if not child.leaf:
            child.children = child.children[:t]

        parent.keys.insert(child_index, median_key)
        parent.values.insert(child_index, median_value)
        parent.children.insert(child_index + 1, right)

    def _insert_nonfull(self, node: Node[K, V], key: K, value: V) -> None:
        index = bisect_left(node.keys, key)

        if node.leaf:
            node.keys.insert(index, key)
            node.values.insert(index, value)
            return

        if len(node.children[index].keys) == self._max_keys:
            self._split_child(node, index)
            if key == node.keys[index]:
                node.values[index] = value
                return
            if key > node.keys[index]:
                index += 1
        self._insert_nonfull(node.children[index], key, value)

    def _delete(self, node: Node[K, V], key: K) -> bool:
        index = bisect_left(node.keys, key)

        if index < len(node.keys) and node.keys[index] == key:
            if node.leaf:
                del node.keys[index]
                del node.values[index]
                return True
            return self._delete_from_internal(node, index)

        if node.leaf:
            return False

        child = node.children[index]
        if len(child.keys) == self._min_keys:
            self._fill_child(node, index)
            if index > len(node.keys):
                index -= 1
        return self._delete(node.children[index], key)

    def _delete_from_internal(self, node: Node[K, V], index: int) -> bool:
        key = node.keys[index]
        left_child = node.children[index]
        right_child = node.children[index + 1]

        if len(left_child.keys) >= self.t:
            pred_key, pred_value = self._max_item(left_child)
            node.keys[index] = pred_key
            node.values[index] = pred_value
            return self._delete(left_child, pred_key)

        if len(right_child.keys) >= self.t:
            succ_key, succ_value = self._min_item(right_child)
            node.keys[index] = succ_key
            node.values[index] = succ_value
            return self._delete(right_child, succ_key)

        self._merge_children(node, index)
        return self._delete(left_child, key)

    def _fill_child(self, parent: Node[K, V], index: int) -> None:
        if index > 0 and len(parent.children[index - 1].keys) >= self.t:
            self._borrow_from_prev(parent, index)
        elif (
            index < len(parent.children) - 1
            and len(parent.children[index + 1].keys) >= self.t
        ):
            self._borrow_from_next(parent, index)
        else:
            if index < len(parent.children) - 1:
                self._merge_children(parent, index)
            else:
                self._merge_children(parent, index - 1)

    def _borrow_from_prev(self, parent: Node[K, V], index: int) -> None:
        child = parent.children[index]
        sibling = parent.children[index - 1]

        child.keys.insert(0, parent.keys[index - 1])
        child.values.insert(0, parent.values[index - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())

        parent.keys[index - 1] = sibling.keys.pop()
        parent.values[index - 1] = sibling.values.pop()

    def _borrow_from_next(self, parent: Node[K, V], index: int) -> None:
        child = parent.children[index]
        sibling = parent.children[index + 1]

        child.keys.append(parent.keys[index])
        child.values.append(parent.values[index])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))

        parent.keys[index] = sibling.keys.pop(0)
        parent.values[index] = sibling.values.pop(0)

    def _merge_children(self, parent: Node[K, V], index: int) -> None:
        left = parent.children[index]
        right = parent.children[index + 1]

        left.keys.append(parent.keys.pop(index))
        left.values.append(parent.values.pop(index))
        left.keys.extend(right.keys)
        left.values.extend(right.values)
        if not left.leaf:
            left.children.extend(right.children)

        parent.children.pop(index + 1)

    def _min_item(self, node: Node[K, V]) -> Tuple[K, V]:
        current = node
        while not current.leaf:
            current = current.children[0]
        return current.keys[0], current.values[0]

    def _max_item(self, node: Node[K, V]) -> Tuple[K, V]:
        current = node
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1], current.values[-1]
