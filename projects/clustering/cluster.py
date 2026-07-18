"""Spectral graph partitioning using the Fiedler vector."""

from __future__ import annotations

from typing import Sequence

import numpy as np


class Graph:
    """Undirected, unweighted graph represented by its Laplacian matrix."""

    def __init__(self, nodecount: int):
        if nodecount < 0:
            raise ValueError("nodecount must be non-negative")

        self.nodecount = nodecount
        self.laplacian = np.zeros((nodecount, nodecount))

    def addedge(self, edge: Sequence[int]) -> None:
        """Add an undirected edge and update the graph Laplacian."""
        if len(edge) != 2:
            raise ValueError("edge must contain exactly two node indices")

        source, target = edge
        if not 0 <= source < self.nodecount or not 0 <= target < self.nodecount:
            raise IndexError("edge node indices must be within the graph")

        self.laplacian[source, target] = -1
        self.laplacian[target, source] = -1
        self.laplacian[source, source] += 1
        self.laplacian[target, target] += 1

    def laplacianmatrix(self) -> np.ndarray:
        """Return the graph Laplacian matrix."""
        return self.laplacian

    def fiedlervector(self) -> np.ndarray:
        """Return the eigenvector associated with the second-smallest eigenvalue."""
        if self.nodecount < 2:
            raise ValueError("at least two nodes are required for a Fiedler vector")

        eigenvalues, eigenvectors = np.linalg.eigh(self.laplacian)
        fiedler_vector = eigenvectors[:, np.argsort(eigenvalues)[1]]

        if fiedler_vector[0] < 0:
            fiedler_vector = -fiedler_vector

        return fiedler_vector

    def clustersign(self) -> list[list[int]]:
        """Partition nodes by the sign of their Fiedler-vector entries."""
        fiedler_vector = self.fiedlervector()
        nonnegative = [
            index for index, value in enumerate(fiedler_vector) if value >= 0
        ]
        negative = [index for index, value in enumerate(fiedler_vector) if value < 0]
        return [nonnegative, negative]
