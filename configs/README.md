# Config Layout

The canonical config tree is grouped into:

- `base/`
  - the five non-temporal baseline models
- `temporal/`
  - temporal sibling variants of those five models
  - placeholder router/additive/citation-only variants for temporal-citation integration experiments
- `plans/`
  - reporting and evaluation plans

Top-level config wrappers were removed to keep the tree compact. Use the subdirectories directly.
