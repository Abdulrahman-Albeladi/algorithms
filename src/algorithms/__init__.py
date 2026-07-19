"""Unified algorithms package.

Exports core classes and helpers for convenient imports, e.g.::

    from algorithms import BTree, KDTree, ScapegoatTree, SkipList, Graph

The functional binary_search_tree helpers are also exposed with BST-prefixed
names to avoid collisions with class-based structures.
"""

from .btree import BTree
from .kd_tree import KDTree
from .scapegoat_tree import ScapegoatTree
from .skip_list import SkipList
from .clustering import Graph

# Functional BST module exports (prefixed to avoid name clashes)
from .binary_search_tree import Node as BSTNode
from .binary_search_tree import (
    dump as bst_dump,
    insert as bst_insert,
    delete as bst_delete,
    search as bst_search,
    inorder as bst_inorder,
    sorting as bst_sorting,
    restructure as bst_restructure,
)

__all__ = [
    "BTree",
    "KDTree",
    "ScapegoatTree",
    "SkipList",
    "Graph",
    "BSTNode",
    "bst_dump",
    "bst_insert",
    "bst_delete",
    "bst_search",
    "bst_inorder",
    "bst_sorting",
    "bst_restructure",
]
