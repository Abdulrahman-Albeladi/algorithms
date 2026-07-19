# Algorithms: Data Structures and Spectral Clustering in Python


Self-implemented B-tree, KD-tree, Scapegoat tree, Skip list, and spectral clustering, organized as a clean Python package for quick review.

Technologies: Python • Algorithms • Data Structures

## Overview
- Canonical implementations in a single importable package: `src/algorithms`.
- Typed, readable code with simple JSON serialization for demos/debugging.
- KD-tree supports exact k-NN with bounding-box pruning; Scapegoat tree rebalances via subtree rebuilds.

## Package structure
- `algorithms.btree.BTree` — generic B-tree map (search/insert/delete, JSON dump)
- `algorithms.kd_tree.KDTree` — bucketed leaves, exact k-NN with box pruning
- `algorithms.scapegoat_tree.ScapegoatTree` — alpha-balanced via subtree rebuilds
- `algorithms.skip_list.SkipList` — probabilistic ordered map
- `algorithms.binary_search_tree` — functional BST helpers (Node, insert/delete/restructure)
- `algorithms.clustering.Graph` — undirected graph Laplacian + Fiedler-vector partitioning

## Install
1) Create a Python 3.10+ environment.
2) Install in editable mode:

   ```bash
   python -m pip install -e .
   ```

Runtime dependency: NumPy (declared in `pyproject.toml`). The package uses a standard `src/` layout and is discovered via setuptools.

## Quickstart

### B-tree
```python
from algorithms import BTree

bt = BTree(minimum_degree=2)
bt.insert(10, "ten")
bt.insert(5, "five")
print(bt.search(10))   # -> "ten" (or None if absent)
print(bt.dump())       # JSON representation
```

### KD-tree (exact k-NN)
```python
from algorithms import KDTree

kd = KDTree(dimensions=2, leaf_capacity=2)
kd.insert((0.0, 0.0), "A")
kd.insert((1.0, 1.0), "B")
kd.insert((0.5, 0.2), "C")

# JSON with keys: "leaveschecked" and "points" (each point has code and coords)
print(kd.knn(2, (0.6, 0.4)))
```

### Scapegoat tree
```python
from algorithms import ScapegoatTree

sg = ScapegoatTree(alpha=2/3)
sg.insert(10, "root")
sg.insert(5, "left")
sg.insert(15, "right")
print(sg.search_path(5))  # values along the search path
print(sg.dump())          # JSON representation
```

### Skip list
```python
from algorithms import SkipList

sl = SkipList(seed=42)
sl.insert(10, "ten")
sl.insert(5, "five")
print(sl.get(10))       # -> "ten"
print(list(sl.items())) # -> [(5, "five"), (10, "ten")]
```

### Spectral clustering (Fiedler vector)
```python
from algorithms import Graph

g = Graph(4)
g.addedge((0, 1))
g.addedge((1, 2))
g.addedge((2, 3))
print(g.clustersign())  # [[nonnegative indices], [negative indices]]
```

## Legacy coursework (archived)
Earlier coursework-style sources are retained for reference under:
- `archive/legacy-coursework/b-tree/`
- `archive/legacy-coursework/kd-tree/`
- `archive/legacy-coursework/scapegoat-tree/`
- `archive/legacy-coursework/skip-list/`

These are archived to reduce duplication; the canonical interfaces live in `src/algorithms`.

## License
Use and redistribution are governed by this repository’s [LICENSE](LICENSE).
