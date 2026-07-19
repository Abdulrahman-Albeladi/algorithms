from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple
import heapq
import json

Point = Tuple[float, ...]


@dataclass(frozen=True)
class Datum:
    """Stored point payload."""

    coords: Point
    code: str

    def to_dict(self) -> dict:
        return {"code": self.code, "coords": self.coords}


@dataclass
class LeafNode:
    items: List[Datum]


@dataclass
class InternalNode:
    axis: int
    split_value: float
    left: "KDNode"
    right: "KDNode"


KDNode = LeafNode | InternalNode


class KDTree:
    """KD-tree with bucketed leaves and exact k-nearest-neighbor search.

    This implementation is an independent reconstruction intended for a
    comparative data-structures repository. It supports insertion, deletion,
    JSON dumping, and exact k-NN queries using subtree bounding boxes for
    pruning.
    """

    def __init__(
        self, dimensions: int, leaf_capacity: int = 8, split_method: str = "spread"
    ):
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if leaf_capacity <= 0:
            raise ValueError("leaf_capacity must be positive")
        if split_method not in {"spread", "cycle"}:
            raise ValueError("split_method must be 'spread' or 'cycle'")

        self.dimensions = dimensions
        self.leaf_capacity = leaf_capacity
        self.split_method = split_method
        self.root: Optional[KDNode] = None

    def insert(self, coords: Sequence[float], code: str) -> None:
        point = self._normalize_point(coords)
        datum = Datum(point, code)

        if self.root is None:
            self.root = LeafNode([datum])
            return

        self.root = self._insert(self.root, datum, depth=0)

    def delete(self, coords: Sequence[float], code: Optional[str] = None) -> bool:
        """Delete one matching datum.

        If code is provided, both coordinates and code must match. Otherwise the
        first datum with matching coordinates is removed.
        """

        if self.root is None:
            return False

        point = self._normalize_point(coords)
        self.root, deleted = self._delete(self.root, point, code)
        return deleted

    def knn(self, k: int, coords: Sequence[float]) -> str:
        point = self._normalize_point(coords)
        result = self.query_knn(k, point)
        return json.dumps(
            {
                "leaveschecked": result["leaves_checked"],
                "points": [datum.to_dict() for datum in result["points"]],
            },
            indent=2,
        )

    def query_knn(self, k: int, coords: Sequence[float]) -> dict:
        if k < 0:
            raise ValueError("k must be non-negative")
        point = self._normalize_point(coords)

        if self.root is None or k == 0:
            return {"leaves_checked": 0, "points": []}

        heap: List[Tuple[float, str, Datum]] = []
        leaves_checked = 0

        def search(node: KDNode, bounds: List[Tuple[float, float]]) -> None:
            nonlocal leaves_checked

            if isinstance(node, LeafNode):
                leaves_checked += 1
                for datum in node.items:
                    dist2 = self._distance_squared(point, datum.coords)
                    entry = (-dist2, self._invert_string_for_heap(datum.code), datum)
                    if len(heap) < k:
                        heapq.heappush(heap, entry)
                    else:
                        worst_dist2 = -heap[0][0]
                        worst_code = self._restore_inverted_string(heap[0][1])
                        if (dist2, datum.code) < (worst_dist2, worst_code):
                            heapq.heapreplace(heap, entry)
                return

            left_bounds = self._child_bounds(
                bounds, node.axis, bounds[node.axis][0], node.split_value, left=True
            )
            right_bounds = self._child_bounds(
                bounds, node.axis, node.split_value, bounds[node.axis][1], left=False
            )

            left_distance = self._box_distance_squared(point, left_bounds)
            right_distance = self._box_distance_squared(point, right_bounds)

            first_node, first_bounds, _first_distance = (
                node.left,
                left_bounds,
                left_distance,
            )
            second_node, second_bounds, second_distance = (
                node.right,
                right_bounds,
                right_distance,
            )
            if right_distance < left_distance:
                (
                    first_node,
                    first_bounds,
                    _first_distance,
                    second_node,
                    second_bounds,
                    second_distance,
                ) = (
                    node.right,
                    right_bounds,
                    right_distance,
                    node.left,
                    left_bounds,
                    left_distance,
                )

            search(first_node, first_bounds)

            if len(heap) < k:
                search(second_node, second_bounds)
            else:
                worst_dist2 = -heap[0][0]
                if second_distance <= worst_dist2:
                    search(second_node, second_bounds)

        initial_bounds = self._subtree_bounds(self.root)
        search(self.root, initial_bounds)

        ordered = sorted(
            (
                (-dist2, self._restore_inverted_string(code_key), datum)
                for dist2, code_key, datum in heap
            ),
            key=lambda x: (x[0], x[1]),
        )
        return {
            "leaves_checked": leaves_checked,
            "points": [datum for _, _, datum in ordered],
        }

    def dump(self) -> str:
        def to_dict(node: Optional[KDNode]) -> dict | None:
            if node is None:
                return None
            if isinstance(node, LeafNode):
                return {"points": [item.to_dict() for item in node.items]}
            return {
                "axis": node.axis,
                "split_value": node.split_value,
                "left": to_dict(node.left),
                "right": to_dict(node.right),
            }

        return json.dumps({} if self.root is None else to_dict(self.root), indent=2)

    def build(self, items: Iterable[tuple[Sequence[float], str]]) -> None:
        self.root = None
        for coords, code in items:
            self.insert(coords, code)

    def _insert(self, node: KDNode, datum: Datum, depth: int) -> KDNode:
        if isinstance(node, LeafNode):
            node.items.append(datum)
            if len(node.items) <= self.leaf_capacity:
                return node
            return self._split_leaf(node, depth)

        if datum.coords[node.axis] < node.split_value:
            node.left = self._insert(node.left, datum, depth + 1)
        else:
            node.right = self._insert(node.right, datum, depth + 1)
        return node

    def _delete(
        self, node: KDNode, point: Point, code: Optional[str]
    ) -> tuple[Optional[KDNode], bool]:
        if isinstance(node, LeafNode):
            for index, datum in enumerate(node.items):
                if datum.coords == point and (code is None or datum.code == code):
                    del node.items[index]
                    if not node.items:
                        return None, True
                    return node, True
            return node, False

        if point[node.axis] < node.split_value:
            node.left, deleted = (
                self._delete(node.left, point, code)
                if node.left is not None
                else (None, False)
            )
        else:
            node.right, deleted = (
                self._delete(node.right, point, code)
                if node.right is not None
                else (None, False)
            )

        if not deleted:
            return node, False

        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True
        return node, True

    def _split_leaf(self, leaf: LeafNode, depth: int) -> KDNode:
        axis = self._choose_split_axis(leaf.items, depth)
        values = sorted(item.coords[axis] for item in leaf.items)
        split_value = values[len(values) // 2]

        left_items = [item for item in leaf.items if item.coords[axis] < split_value]
        right_items = [item for item in leaf.items if item.coords[axis] >= split_value]

        # If all values on the chosen axis are identical, try other axes before
        # giving up and keeping the bucket unsplit.
        if not left_items or not right_items:
            for fallback_axis in range(self.dimensions):
                if fallback_axis == axis:
                    continue
                values = sorted(item.coords[fallback_axis] for item in leaf.items)
                candidate = values[len(values) // 2]
                candidate_left = [
                    item
                    for item in leaf.items
                    if item.coords[fallback_axis] < candidate
                ]
                candidate_right = [
                    item
                    for item in leaf.items
                    if item.coords[fallback_axis] >= candidate
                ]
                if candidate_left and candidate_right:
                    axis = fallback_axis
                    split_value = candidate
                    left_items = candidate_left
                    right_items = candidate_right
                    break

        if not left_items or not right_items:
            return leaf

        return InternalNode(
            axis, float(split_value), LeafNode(left_items), LeafNode(right_items)
        )

    def _choose_split_axis(self, items: List[Datum], depth: int) -> int:
        if self.split_method == "cycle":
            return depth % self.dimensions

        spreads = []
        for axis in range(self.dimensions):
            axis_values = [item.coords[axis] for item in items]
            spreads.append(max(axis_values) - min(axis_values))
        return max(range(self.dimensions), key=lambda axis: spreads[axis])

    def _subtree_bounds(self, node: KDNode) -> List[Tuple[float, float]]:
        if isinstance(node, LeafNode):
            mins = list(node.items[0].coords)
            maxs = list(node.items[0].coords)
            for datum in node.items[1:]:
                for axis, value in enumerate(datum.coords):
                    mins[axis] = min(mins[axis], value)
                    maxs[axis] = max(maxs[axis], value)
            return list(zip(mins, maxs))

        left_bounds = self._subtree_bounds(node.left)
        right_bounds = self._subtree_bounds(node.right)
        return [
            (
                min(left_bounds[axis][0], right_bounds[axis][0]),
                max(left_bounds[axis][1], right_bounds[axis][1]),
            )
            for axis in range(self.dimensions)
        ]

    def _child_bounds(
        self,
        bounds: List[Tuple[float, float]],
        axis: int,
        low: float,
        high: float,
        left: bool,
    ) -> List[Tuple[float, float]]:
        child_bounds = list(bounds)
        current_low, current_high = child_bounds[axis]
        if left:
            child_bounds[axis] = (current_low, min(current_high, high))
        else:
            child_bounds[axis] = (max(current_low, low), current_high)
        return child_bounds

    def _box_distance_squared(
        self, point: Point, bounds: List[Tuple[float, float]]
    ) -> float:
        total = 0.0
        for axis, value in enumerate(point):
            low, high = bounds[axis]
            if value < low:
                total += (low - value) ** 2
            elif value > high:
                total += (value - high) ** 2
        return total

    @staticmethod
    def _distance_squared(a: Point, b: Point) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b))

    def _normalize_point(self, coords: Sequence[float]) -> Point:
        point = tuple(float(value) for value in coords)
        if len(point) != self.dimensions:
            raise ValueError(f"expected {self.dimensions} dimensions, got {len(point)}")
        return point

    @staticmethod
    def _invert_string_for_heap(value: str) -> str:
        return "".join(chr(0x10FFFF - ord(ch)) for ch in value)

    @staticmethod
    def _restore_inverted_string(value: str) -> str:
        return "".join(chr(0x10FFFF - ord(ch)) for ch in value)
