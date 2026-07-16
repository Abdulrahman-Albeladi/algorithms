# Data Structures and Algorithms Rebuilds

This repository collects recovered, publish-eligible Python projects from a course/archive labeled `420`. It contains two related views of the recovered work:

- `src/`: consolidated rebuilds for four data-structure implementations.
- `projects/<id>/`: preserved recovered project directories, each with its original source filename and `metadata.yml` record.

The repository is organized as a code archive and rebuild effort. It does not claim benchmark results, complete test coverage, or equivalence to any original assignment environment.

## Contents

| Area | Description |
| --- | --- |
| `src/btree/btree.py` | Consolidated B-tree implementation. |
| `src/scapegoat_tree/scapegoat_tree.py` | Consolidated scapegoat-tree implementation. |
| `src/kd_tree/kd_tree.py` | Consolidated k-d tree implementation. |
| `src/skip_list/skip_list.py` | Consolidated skip-list implementation. |
| `projects/234165456/` | Recovered binary-search-tree project. |
| `projects/241317538/` | Recovered B-tree project. |
| `projects/244252785/` | Recovered scapegoat-tree project. |
| `projects/247391718/` | Recovered k-d-tree project. |
| `projects/250612490/` | Recovered skip-list project. |
| `projects/253742914/` | Recovered clustering project. |

See [Project Index](#project-index) for provenance, source locations, data notes, and validation status.

## Setup

The repository contains Python source and a `pyproject.toml` file. Create an isolated environment before installing or running tools:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

If editable installation is not needed, the individual files can be inspected or compiled directly from the repository root.

## Validation status

No test suite is present in the supplied file list, and no test execution result is recorded here. The presence of `.ruff_cache/` indicates that Ruff has been used in the working tree at some point, but cached files are not validation evidence.

The available validation actions are static and structural unless additional tests are added:

```bash
python -m compileall src projects
python -m ruff check .
```

Run the Ruff command only after installing the project tooling or Ruff itself. A command listed in this README is a recommended action, not a claim that it has been run successfully.

## Data and privacy

The tree implementations are algorithmic code and do not require a bundled dataset to inspect or compile.

The clustering project has no dataset in the supplied file list. Its runtime input format, expected source, and any original course-data dependency must be determined from `projects/253742914/cluster.py` and its metadata before execution. Do not add private course files, personal records, credentials, or nonredistributable datasets to this repository. Use configuration, a documented public dataset, or a synthetic example when adding runnable clustering instructions.

## Limitations

- No automated tests are included in the listed repository contents.
- Correctness, complexity, balancing behavior, duplicate-key policy, deletion behavior, and edge-case handling have not been independently verified in this README.
- The recovered project directories may retain historical structure that differs from the consolidated `src/` rebuilds.
- `metadata.yml` files are preserved as recovery metadata; their contents should be reviewed before treating them as user-facing documentation.
- Licensing and publication status should be reviewed against `LICENSE_REVIEW.md` before distributing code beyond this repository.

## Provenance

The `projects/<id>/` directories preserve recovered project artifacts using their archive identifiers. The `src/` directory contains corresponding consolidated implementations for B-tree, scapegoat tree, k-d tree, and skip list. The binary-search-tree and clustering projects are currently represented only in their recovered project directories.

This organization preserves the distinction between recovered artifacts and rebuilt source. It does not attribute the original course material, prompts, tests, or grading infrastructure to this repository.

## Project Index

| Recovered ID | Project | Recovered source | Consolidated source | Data requirement | Validation status |
| --- | --- | --- | --- | --- | --- |
| `234165456` | Binary search tree | `projects/234165456/bst.py` | None listed | No dataset indicated by the file inventory. | No tests or recorded validation result. |
| `241317538` | B-tree | `projects/241317538/btree.py` | `src/btree/btree.py` | No dataset indicated by the file inventory. | No tests or recorded validation result. |
| `244252785` | Scapegoat tree | `projects/244252785/scapegoat.py` | `src/scapegoat_tree/scapegoat_tree.py` | No dataset indicated by the file inventory. | No tests or recorded validation result. |
| `247391718` | k-d tree | `projects/247391718/kd.py` | `src/kd_tree/kd_tree.py` | No dataset indicated by the file inventory. | No tests or recorded validation result. |
| `250612490` | Skip list | `projects/250612490/skiplist.py` | `src/skip_list/skip_list.py` | No dataset indicated by the file inventory. | No tests or recorded validation result. |
| `253742914` | Clustering | `projects/253742914/cluster.py` | None listed | No dataset is included. Determine required inputs from source and metadata; keep private inputs external. | No tests or recorded validation result. |

## Repository maintenance

- Keep generated caches, virtual environments, local datasets, and machine-specific paths out of version control.
- Keep recovery metadata with its corresponding recovered project.
- Add tests beside new or modified behavior and record actual validation results in pull requests rather than in retrospective claims.
- Review `SECURITY.md`, `CONTRIBUTING.md`, and `LICENSE_REVIEW.md` before publishing changes.
