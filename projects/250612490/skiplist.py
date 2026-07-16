from __future__ import annotations

import json
import math
from typing import List, Optional


class Node:
    """A skip-list node with forward pointers through its top level."""

    def __init__(
        self,
        key: int,
        value: Optional[str],
        toplevel: int,
        pointers: Optional[List[Optional["Node"]]] = None,
    ) -> None:
        self.key = key
        self.value = value
        self.toplevel = toplevel
        self.pointers = pointers


class SkipList:
    """Deterministic skip list with sentinel head and tail nodes.

    Call :meth:`initialize` before inserting, deleting, or searching. Inserted
    keys are expected to be unique, and deletion/search keys are expected to
    exist in the list.
    """

    def __init__(
        self,
        maxlevel: Optional[int] = None,
        nodecount: Optional[int] = None,
        headnode: Optional[Node] = None,
        tailnode: Optional[Node] = None,
    ) -> None:
        self.maxlevel = maxlevel
        self.nodecount = nodecount
        self.headnode = headnode
        self.tailnode = tailnode

    def dump(self) -> str:
        """Return a JSON representation of nodes and their forward pointers."""
        self._require_initialized()

        current_node = self.headnode
        node_list = []
        while current_node is not self.tailnode:
            pointer_list = str([node.key for node in current_node.pointers])
            node_list.append(
                {
                    "key": current_node.key,
                    "value": current_node.value,
                    "pointers": pointer_list,
                }
            )
            current_node = current_node.pointers[0]

        pointer_list = str([None for _ in current_node.pointers])
        node_list.append(
            {
                "key": current_node.key,
                "value": current_node.value,
                "pointers": pointer_list,
            }
        )
        return json.dumps(node_list, indent=2)

    def pretty(self) -> str:
        """Return a vertical, human-readable representation of the list."""
        self._require_initialized()

        current_node = self.headnode
        longest_key = 0
        while current_node is not None:
            longest_key = max(longest_key, len(str(current_node.key)))
            current_node = current_node.pointers[0]
        column_width = longest_key + 2

        result = ""
        current_node = self.headnode
        while current_node is not None:
            result += f"Key = {current_node.key}, Value = {current_node.value}"
            if current_node is not self.tailnode:
                pointers = ""
                for pointer in current_node.pointers:
                    if pointer is not None:
                        pointers += f"({pointer.key})".ljust(column_width)
                    else:
                        pointers += "".ljust(column_width)
                result += f"\n{pointers}\n\n"
            current_node = current_node.pointers[0]
        return result

    def initialize(self, maxlevel: int) -> None:
        """Create empty sentinel nodes for a skip list of ``maxlevel``."""
        if maxlevel < 0:
            raise ValueError("maxlevel must be non-negative")

        tailnode = Node(
            key=float("inf"),
            value=None,
            toplevel=maxlevel,
            pointers=[None] * (maxlevel + 1),
        )
        headnode = Node(
            key=float("-inf"),
            value=None,
            toplevel=maxlevel,
            pointers=[tailnode] * (maxlevel + 1),
        )
        self.headnode = headnode
        self.tailnode = tailnode
        self.maxlevel = maxlevel
        self.nodecount = 0

    def insert(self, key: int, value: str, toplevel: int) -> None:
        """Insert a unique key/value pair with the supplied top level."""
        self._require_initialized()

        predecessors = []
        current_node = self.headnode
        current_level = self.maxlevel
        while current_level != -1:
            if current_node.pointers[current_level].key < key:
                current_node = current_node.pointers[current_level]
            else:
                predecessors.append((current_level, current_node))
                current_level -= 1

        inserted = Node(key, value, toplevel, [None] * (toplevel + 1))
        for level, predecessor in predecessors:
            if level <= toplevel:
                inserted.pointers[level] = predecessor.pointers[level]
                predecessor.pointers[level] = inserted

        self.nodecount += 1
        if math.log2(self.nodecount) + 1 > self.maxlevel:
            self._rebuild()

    def delete(self, key: int) -> None:
        """Remove the node associated with ``key``."""
        self._require_initialized()

        predecessors = []
        current_node = self.headnode
        current_level = self.maxlevel
        while current_level != -1:
            next_node = current_node.pointers[current_level]
            if next_node.key < key:
                current_node = next_node
            elif next_node.key > key:
                current_level -= 1
            else:
                predecessors.append((current_node, current_level))
                current_level -= 1

        if not predecessors:
            raise KeyError(key)

        target = predecessors[0][0].pointers[predecessors[0][1]]
        for predecessor, level in predecessors:
            predecessor.pointers[level] = target.pointers[level]
        self.nodecount -= 1

    def search(self, key: int) -> str:
        """Return visited keys followed by the matching value as formatted JSON."""
        self._require_initialized()

        visited = [self.headnode.key]
        current_node = self.headnode
        current_level = self.maxlevel
        while current_level != -1:
            next_node = current_node.pointers[current_level]
            if next_node.key < key:
                if next_node.key not in visited:
                    visited.append(next_node.key)
                current_node = next_node
            elif next_node.key > key:
                current_level -= 1
            else:
                visited.append(next_node.key)
                visited.append(next_node.value)
                return json.dumps(visited, indent=2)

        raise KeyError(key)

    def _rebuild(self) -> None:
        """Rebuild deterministic tower heights after the level bound grows."""
        self.maxlevel = max(1, self.maxlevel * 2)

        existing_nodes = []
        current_node = self.headnode.pointers[0]
        while current_node is not self.tailnode:
            existing_nodes.append(current_node)
            current_node = current_node.pointers[0]

        tailnode = Node(
            float("inf"),
            None,
            self.maxlevel,
            [None] * (self.maxlevel + 1),
        )
        nodes = [tailnode]

        for index in range(self.nodecount - 1, -1, -1):
            rank = index + 1
            toplevel = 0
            while rank % 2 == 0:
                toplevel += 1
                rank //= 2
            toplevel = min(toplevel, self.maxlevel)

            old_node = existing_nodes[index]
            node = Node(
                old_node.key,
                old_node.value,
                toplevel,
                [None] * (toplevel + 1),
            )
            for level in range(toplevel + 1):
                node.pointers[level] = (
                    nodes[-1 - 2**level] if len(nodes) > 2**level else tailnode
                )
            nodes.append(node)

        headnode = Node(
            float("-inf"),
            None,
            self.maxlevel,
            [None] * (self.maxlevel + 1),
        )
        for level in range(self.maxlevel + 1):
            headnode.pointers[level] = (
                nodes[-1 - 2**level] if len(nodes) > 2**level else tailnode
            )

        self.headnode = headnode
        self.tailnode = tailnode

    def _require_initialized(self) -> None:
        if (
            self.maxlevel is None
            or self.nodecount is None
            or self.headnode is None
            or self.tailnode is None
        ):
            raise RuntimeError("initialize the skip list before use")
