# Contributing

## Before contributing

This repository is intended as a clean-room reconstruction project. Do not contribute any of the following:

- course submission files
- assignment handouts
- instructor tests
- autograder files
- grading metadata
- copied starter code

Contributions should be original implementations or documentation updates.

## Development expectations

1. Keep interfaces and naming consistent across data-structure modules where practical.
2. Add focused tests for behavior, not course-specific outputs.
3. Prefer small, reviewable pull requests.
4. Document any algorithmic tradeoff claims in plain technical language.
5. Do not add benchmark claims unless benchmark code, environment, and results are included and reproducible.

## Validation expectations

Based on current repository evidence, contributors should expect to address:

- `ruff` findings in `src/kd_tree/kd_tree.py`
- formatting issues reported by `black --check .`
- missing automated test execution evidence

## Style

- Use direct docstrings and comments only where they add information.
- Avoid comments that restate code line by line.
- Keep examples minimal and executable.
