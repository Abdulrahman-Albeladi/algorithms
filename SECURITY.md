# Security policy

## Scope

This repository contains educational and comparative implementations of data structures. It is not presented as security-critical software.

## Reporting

If you find a security issue in repository infrastructure or dependency configuration, report it privately to the repository owner.

## Notes on current validation evidence

The available static-analysis log reported one low-severity Bandit finding for use of Python's standard pseudo-random generator in `src/skip_list/skip_list.py`.

That finding should be interpreted in context:

- pseudo-randomness may be appropriate for probabilistic balancing in a skip list
- pseudo-randomness is not appropriate for cryptographic purposes

If this repository later adds any authentication, secrets handling, or security-sensitive features, those features should use security-appropriate primitives and receive separate review.
