from __future__ import annotations

import json
from statistics import median
from typing import Any


class Datum:
    """A labeled point stored in a KD-tree leaf."""

    def __init__(self, coords: tuple[int, ...], code: str):
        self.coords = coords
        self.code = code

    def to_json(self) -> dict[str, Any]:
        return {"code": self.code, "coords": self.coords}


class NodeInternal:
    """An internal KD-tree node that partitions one coordinate axis."""

    def __init__(
        self,
        splitindex: int,
        splitvalue: float,
        leftchild: NodeInternal | NodeLeaf,
        rightchild: NodeInternal | NodeLeaf,
    ):
        self.splitindex = splitindex
        self.splitvalue = splitvalue
        self.leftchild = leftchild
        self.rightchild = rightchild


class NodeLeaf:
    """A KD-tree leaf containing up to the configured bucket size."""

    def __init__(self, data: list[Datum]):
        self.data = data


class KDtree:
    """KD-tree supporting insertion, deletion, serialization, and nearest-neighbor search."""

    def __init__(
        self,
        splitmethod: str,
        k: int,
        m: int,
        root: NodeLeaf | NodeInternal | None = None,
    ):
        self.k = k
        self.m = m
        self.splitmethod = splitmethod
        self.root = root

    def dump(self) -> str:
        """Return the tree using the established JSON-compatible dump format."""

        def to_dict(node: NodeLeaf | NodeInternal) -> dict[str, Any]:
            if isinstance(node, NodeLeaf):
                return {
                    "p": str(
                        [
                            {"coords": datum.coords, "code": datum.code}
                            for datum in node.data
                        ]
                    )
                }

            return {
                "splitindex": node.splitindex,
                "splitvalue": node.splitvalue,
                "l": to_dict(node.leftchild),
                "r": to_dict(node.rightchild),
            }

        return json.dumps({} if self.root is None else to_dict(self.root), indent=2)

    def insert(self, point: tuple[int, ...], code: str) -> None:
        """Insert a labeled point into the tree."""
        if self.root is None:
            self.root = NodeLeaf([Datum(point, code)])
            return

        current = self.root
        parent: NodeInternal | None = None

        while isinstance(current, NodeInternal):
            parent = current
            if point[current.splitindex] < current.splitvalue:
                current = current.leftchild
            else:
                current = current.rightchild

        current.data.append(Datum(point, code))
        if len(current.data) > self.m:
            split(self, current, parent)

    def delete(self, point: tuple[int, ...]) -> None:
        """Delete the point with the requested coordinates."""
        if self.root is None:
            return

        current = self.root
        parent: NodeInternal | None = None
        grandparent: NodeInternal | None = None
        parent_direction: int | None = None
        direction: int | None = None

        while isinstance(current, NodeInternal):
            grandparent = parent
            parent = current
            parent_direction = direction

            if point[current.splitindex] < current.splitvalue:
                current = current.leftchild
                direction = 0
            else:
                current = current.rightchild
                direction = 1

        for index, datum in enumerate(current.data):
            if datum.coords == point:
                del current.data[index]
                break

        if current.data or parent is None:
            return

        sibling = parent.rightchild if direction == 0 else parent.leftchild
        if grandparent is None:
            self.root = sibling
        elif parent_direction == 0:
            grandparent.leftchild = sibling
        else:
            grandparent.rightchild = sibling

    def knn(self, k: int, point: tuple[int, ...]) -> str:
        """Return up to ``k`` nearest points and the number of searched leaves."""
        if self.root is None or k <= 0:
            return json.dumps({"leaveschecked": 0, "points": []}, indent=2)

        leaves_checked = [0]
        nearest: list[tuple[Datum, int]] = []
        recknn(self, self.root, k, point, leaves_checked, nearest)

        return json.dumps(
            {
                "leaveschecked": leaves_checked[0],
                "points": [datum.to_json() for datum, _ in nearest],
            },
            indent=2,
        )


def recknn(
    tree: KDtree,
    current: NodeLeaf | NodeInternal,
    k: int,
    point: tuple[int, ...],
    leaves_checked: list[int],
    nearest: list[tuple[Datum, int]],
) -> None:
    if isinstance(current, NodeLeaf):
        leaves_checked[0] += 1
        for candidate in calculateds(current, point):
            nearest.append(candidate)
            nearest.sort(key=lambda item: (item[1], item[0].code))
            if len(nearest) > k:
                nearest.pop()
        return

    left_distance = boxd(tree, current.leftchild, point)
    right_distance = boxd(tree, current.rightchild, point)

    if left_distance <= right_distance:
        first_node, first_distance = current.leftchild, left_distance
        second_node, second_distance = current.rightchild, right_distance
    else:
        first_node, first_distance = current.rightchild, right_distance
        second_node, second_distance = current.leftchild, left_distance

    if len(nearest) < k or first_distance <= nearest[-1][1]:
        recknn(tree, first_node, k, point, leaves_checked, nearest)

    if len(nearest) < k or second_distance <= nearest[-1][1]:
        recknn(tree, second_node, k, point, leaves_checked, nearest)


def calculateds(current: NodeLeaf, point: tuple[int, ...]) -> list[tuple[Datum, int]]:
    """Calculate squared Euclidean distances for points in one leaf."""
    distances = []
    for datum in current.data:
        distance = sum(
            (point[index] - datum.coords[index]) ** 2
            for index in range(len(datum.coords))
        )
        distances.append((datum, distance))

    return sorted(distances, key=lambda item: (item[1], item[0].code))


def boxd(
    tree: KDtree, current: NodeLeaf | NodeInternal, point: tuple[int, ...]
) -> int | float:
    """Return squared distance from a point to a subtree bounding box."""
    box = boxit(tree, current, [])
    if not box:
        return float("inf")

    distance = 0
    for index in range(tree.k):
        lower, upper = box[index]
        if point[index] > upper:
            distance += (point[index] - upper) ** 2
        elif point[index] < lower:
            distance += (lower - point[index]) ** 2

    return distance


def boxit(
    tree: KDtree,
    current: NodeLeaf | NodeInternal,
    bounds: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Compute coordinate bounds for every datum below ``current``."""
    if isinstance(current, NodeInternal):
        bounds = boxit(tree, current.leftchild, bounds)
        return boxit(tree, current.rightchild, bounds)

    for datum in current.data:
        if not bounds:
            bounds = [(coordinate, coordinate) for coordinate in datum.coords]
            continue

        for index in range(tree.k):
            lower, upper = bounds[index]
            bounds[index] = (
                min(lower, datum.coords[index]),
                max(upper, datum.coords[index]),
            )

    return bounds


def split(tree: KDtree, current: NodeLeaf, parent: NodeInternal | None) -> None:
    """Replace an overflowing leaf with an internal partition node."""
    split_axis = splitindex(tree, current, parent)
    split_value, left_data, right_data = _partition_data(current.data, split_axis)

    # A cyclic axis can contain identical values; use a varying axis if needed.
    if not left_data:
        split_axis = _widest_axis(tree, current.data)
        split_value, left_data, right_data = _partition_data(current.data, split_axis)

    replacement = NodeInternal(
        split_axis,
        split_value,
        NodeLeaf(left_data),
        NodeLeaf(right_data),
    )

    if parent is None:
        tree.root = replacement
    elif parent.leftchild is current:
        parent.leftchild = replacement
    else:
        parent.rightchild = replacement


def _partition_data(
    data: list[Datum], axis: int
) -> tuple[float, list[Datum], list[Datum]]:
    values = [datum.coords[axis] for datum in data]
    split_value = float(median(values))
    left_data = [datum for datum in data if datum.coords[axis] < split_value]
    right_data = [datum for datum in data if datum.coords[axis] >= split_value]
    return split_value, left_data, right_data


def _widest_axis(tree: KDtree, data: list[Datum]) -> int:
    spreads = []
    for index in range(tree.k):
        coordinates = [datum.coords[index] for datum in data]
        spreads.append(max(coordinates) - min(coordinates))
    return spreads.index(max(spreads))


def splitindex(tree: KDtree, current: NodeLeaf, parent: NodeInternal | None) -> int:
    """Choose a split axis using spread-based or cyclic selection."""
    if tree.splitmethod == "spread":
        return _widest_axis(tree, current.data)

    if parent is None:
        return 0
    return (parent.splitindex + 1) % tree.k
