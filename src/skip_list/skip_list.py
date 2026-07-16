from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Generic, Iterable, Iterator, List, Optional, Tuple, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Node(Generic[K, V]):
    key: Optional[K]
    value: Optional[V]
    level: int
    forward: List[Optional["_Node[K, V]"]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.forward:
            self.forward = [None] * (self.level + 1)


class SkipList(Generic[K, V]):
    """Probabilistic ordered map implemented as a skip list.

    This implementation is independent of any coursework interface. It exposes a
    small dictionary-like API for insertion, lookup, deletion, and iteration over
    sorted keys.
    """

    def __init__(
        self, max_level: int = 16, p: float = 0.5, seed: Optional[int] = None
    ) -> None:
        if max_level < 0:
            raise ValueError("max_level must be non-negative")
        if not 0.0 < p < 1.0:
            raise ValueError("p must be between 0 and 1")

        self._max_level = max_level
        self._p = p
        self._rng = random.Random(seed)  # nosec B311
        self._level = 0
        self._size = 0
        self._head: _Node[K, V] = _Node(key=None, value=None, level=max_level)

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: K) -> bool:
        return self.get(key) is not None

    def __iter__(self) -> Iterator[Tuple[K, V]]:
        current = self._head.forward[0]
        while current is not None:
            yield current.key, current.value  # type: ignore[misc]
            current = current.forward[0]

    def items(self) -> Iterator[Tuple[K, V]]:
        return iter(self)

    def keys(self) -> Iterator[K]:
        for key, _ in self:
            yield key

    def values(self) -> Iterator[V]:
        for _, value in self:
            yield value

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        node = self._find_node(key)
        return default if node is None else node.value

    def search_path(self, key: K) -> List[K]:
        """Return the sequence of keys visited while descending toward key.

        The path is useful for examples and debugging without exposing internal
        node objects.
        """

        path: List[K] = []
        current = self._head
        for level in range(self._level, -1, -1):
            while (
                current.forward[level] is not None and current.forward[level].key < key
            ):
                current = current.forward[level]
                if current.key is not None:
                    path.append(current.key)
        candidate = current.forward[0]
        if candidate is not None and candidate.key == key:
            path.append(candidate.key)
        return path

    def insert(self, key: K, value: V) -> None:
        update = self._locate_predecessors(key)
        candidate = update[0].forward[0]

        if candidate is not None and candidate.key == key:
            candidate.value = value
            return

        node_level = self._random_level()
        if node_level > self._level:
            for level in range(self._level + 1, node_level + 1):
                update[level] = self._head
            self._level = node_level

        new_node = _Node(key=key, value=value, level=node_level)
        for level in range(node_level + 1):
            new_node.forward[level] = update[level].forward[level]
            update[level].forward[level] = new_node
        self._size += 1

    def delete(self, key: K) -> bool:
        update = self._locate_predecessors(key)
        candidate = update[0].forward[0]

        if candidate is None or candidate.key != key:
            return False

        for level in range(self._level + 1):
            if update[level].forward[level] is not candidate:
                continue
            update[level].forward[level] = candidate.forward[level]

        while self._level > 0 and self._head.forward[self._level] is None:
            self._level -= 1

        self._size -= 1
        return True

    def clear(self) -> None:
        self._head = _Node(key=None, value=None, level=self._max_level)
        self._level = 0
        self._size = 0

    def to_list(self) -> List[Tuple[K, V]]:
        return list(self)

    @classmethod
    def from_items(
        cls,
        items: Iterable[Tuple[K, V]],
        max_level: int = 16,
        p: float = 0.5,
        seed: Optional[int] = None,
    ) -> "SkipList[K, V]":
        skip_list = cls(max_level=max_level, p=p, seed=seed)
        for key, value in items:
            skip_list.insert(key, value)
        return skip_list

    def _find_node(self, key: K) -> Optional[_Node[K, V]]:
        current = self._head
        for level in range(self._level, -1, -1):
            while (
                current.forward[level] is not None and current.forward[level].key < key
            ):
                current = current.forward[level]
        current = current.forward[0]
        if current is not None and current.key == key:
            return current
        return None

    def _locate_predecessors(self, key: K) -> List[_Node[K, V]]:
        update: List[_Node[K, V]] = [self._head] * (self._max_level + 1)
        current = self._head
        for level in range(self._level, -1, -1):
            while (
                current.forward[level] is not None and current.forward[level].key < key
            ):
                current = current.forward[level]
            update[level] = current
        return update

    def _random_level(self) -> int:
        level = 0
        while level < self._max_level and self._rng.random() < self._p:
            level += 1
        return level
