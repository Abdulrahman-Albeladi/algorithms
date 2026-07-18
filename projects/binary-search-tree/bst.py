"""Binary search tree operations with JSON serialization support."""

from __future__ import annotations

import json
from typing import Optional


class Node:
    """A node in a binary search tree."""

    def __init__(
        self,
        key: Optional[int] = None,
        value: Optional[int] = None,
        leftchild: Optional["Node"] = None,
        rightchild: Optional["Node"] = None,
    ) -> None:
        self.key = key
        self.value = value
        self.leftchild = leftchild
        self.rightchild = rightchild


def dump(root: Optional[Node]) -> str:
    """Serialize a tree to an indented JSON object."""

    def to_dict(node: Node) -> dict:
        return {
            "key": node.key,
            "value": node.value,
            "leftchild": to_dict(node.leftchild) if node.leftchild else None,
            "rightchild": to_dict(node.rightchild) if node.rightchild else None,
        }

    return json.dumps({} if root is None else to_dict(root), indent=2)


def insert(root: Optional[Node], key: int, value: int) -> Node:
    """Insert a key-value pair and return the tree root."""
    if root is None:
        return Node(key, value)

    if key < root.key:
        root.leftchild = insert(root.leftchild, key, value)
    else:
        root.rightchild = insert(root.rightchild, key, value)
    return root


def delete(root: Optional[Node], key: int) -> Optional[Node]:
    """Delete a key, using the inorder successor for two-child nodes."""
    if root is None:
        return None

    if key < root.key:
        root.leftchild = delete(root.leftchild, key)
    elif key > root.key:
        root.rightchild = delete(root.rightchild, key)
    else:
        if root.leftchild is None:
            return root.rightchild
        if root.rightchild is None:
            return root.leftchild

        successor = root.rightchild
        while successor.leftchild is not None:
            successor = successor.leftchild

        root.key = successor.key
        root.value = successor.value
        root.rightchild = delete(root.rightchild, successor.key)

    return root


def pathing(node: Optional[Node], path: list[int], search_key: int) -> list[int]:
    """Return values along the root-to-key path, or an empty list if absent."""
    if node is None:
        return []

    path.append(node.value)
    if node.key == search_key:
        return path

    if search_key < node.key:
        return pathing(node.leftchild, path, search_key)
    return pathing(node.rightchild, path, search_key)


def search(root: Optional[Node], search_key: int) -> str:
    """Serialize the values on the path from the root to a search key."""
    return json.dumps(pathing(root, [], search_key), indent=2)


def inorder(
    root: Optional[Node], reach: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Collect tree entries in inorder traversal order."""
    if root is None:
        return reach

    inorder(root.leftchild, reach)
    reach.append((root.key, root.value))
    inorder(root.rightchild, reach)
    return reach


def sorting(root_list: list[tuple[int, int]]) -> Optional[Node]:
    """Build a balanced tree from entries in sorted key order."""
    if not root_list:
        return None

    midpoint = len(root_list) // 2
    key, value = root_list[midpoint]
    root = Node(key, value)
    root.leftchild = sorting(root_list[:midpoint])
    root.rightchild = sorting(root_list[midpoint + 1 :])
    return root


def restructure(root: Optional[Node]) -> Optional[Node]:
    """Rebuild a tree into a balanced form while preserving its entries."""
    return sorting(inorder(root, []))
