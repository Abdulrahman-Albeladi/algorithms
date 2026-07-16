# Project Index

This index describes the recovered project artifacts and their relationship to the consolidated source tree. Archive identifiers are retained as provenance labels, not as descriptions of an original assignment or grading context.

## Consolidated rebuilds

| Project | Consolidated file | Related recovered artifact | Description | Data requirement | Known validation status | Limitations |
| --- | --- | --- | --- | --- | --- | --- |
| B-tree | `src/btree/btree.py` | `projects/241317538/btree.py` | Python implementation associated with a B-tree rebuild. | No dataset is indicated by the supplied file inventory. | No tests are listed; no successful validation is recorded. | API behavior, invariants, order configuration, duplicate handling, and deletion behavior require source review and tests. |
| Scapegoat tree | `src/scapegoat_tree/scapegoat_tree.py` | `projects/244252785/scapegoat.py` | Python implementation associated with a scapegoat-tree rebuild. | No dataset is indicated by the supplied file inventory. | No tests are listed; no successful validation is recorded. | Rebuild thresholds, balancing behavior, and boundary cases require source review and tests. |
| k-d tree | `src/kd_tree/kd_tree.py` | `projects/247391718/kd.py` | Python implementation associated with a k-d-tree rebuild. | No dataset is indicated by the supplied file inventory. Point inputs, if required at runtime, must be supplied by the caller. | No tests are listed; no successful validation is recorded. | Dimensionality assumptions, query semantics, and handling of ties or empty trees require source review and tests. |
| Skip list | `src/skip_list/skip_list.py` | `projects/250612490/skiplist.py` | Python implementation associated with a skip-list rebuild. | No dataset is indicated by the supplied file inventory. | No tests are listed; no successful validation is recorded. | Random-level behavior, reproducibility, duplicate handling, and deletion behavior require source review and tests. |

## Recovered project artifacts

| Archive ID | Files | Project description | Provenance | Data and privacy notes | Validation status |
| --- | --- | --- | --- | --- | --- |
| `234165456` | `bst.py`, `metadata.yml` | Binary-search-tree project. | Recovered project directory retained under its archive identifier. No matching file is listed under `src/`. | No dataset is included or indicated by the file inventory. | No tests are listed; no execution result is recorded. |
| `241317538` | `btree.py`, `metadata.yml` | B-tree project. | Recovered artifact with a related consolidated implementation at `src/btree/btree.py`. | No dataset is included or indicated by the file inventory. | No tests are listed; no execution result is recorded. |
| `244252785` | `scapegoat.py`, `metadata.yml` | Scapegoat-tree project. | Recovered artifact with a related consolidated implementation at `src/scapegoat_tree/scapegoat_tree.py`. | No dataset is included or indicated by the file inventory. | No tests are listed; no execution result is recorded. |
| `247391718` | `kd.py`, `metadata.yml` | k-d-tree project. | Recovered artifact with a related consolidated implementation at `src/kd_tree/kd_tree.py`. | No dataset is included or indicated by the file inventory. Runtime point data, if any, is not bundled. | No tests are listed; no execution result is recorded. |
| `250612490` | `skiplist.py`, `metadata.yml` | Skip-list project. | Recovered artifact with a related consolidated implementation at `src/skip_list/skip_list.py`. | No dataset is included or indicated by the file inventory. | No tests are listed; no execution result is recorded. |
| `253742914` | `cluster.py`, `metadata.yml` | Clustering project. | Recovered project directory retained under its archive identifier. No matching file is listed under `src/`. | No dataset is present in the repository inventory. Review source and metadata to determine the required input format. Keep private or restricted data outside version control. | No tests are listed; no execution result is recorded. |

## Suggested inspection order

1. Read the applicable `metadata.yml` file for each recovered artifact.
2. Compare a recovered implementation with its related `src/` rebuild where both are present.
3. Compile the relevant source file before making behavior claims.
4. Add focused tests for documented operations and edge cases.
5. For clustering, document a public or synthetic input fixture before adding a runnable example.

## Not included

The supplied file list does not include original assignment prompts, grading scripts, hidden tests, input datasets, benchmark outputs, or recorded test reports. This index therefore makes no claims about course requirements, grades, performance, or complete functional correctness.
