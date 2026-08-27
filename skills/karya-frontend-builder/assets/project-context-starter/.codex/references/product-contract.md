# Product Contract

Read product truth from `docs/product/` before changing behavior.

Small products may use `product-brief.md`. Modular products use `prd.md`, `screen-map.md`, `business-rules.md`, `data-contract.md`, `visual-direction.md`, and `acceptance-criteria.md`.

- Preserve explicit scope and non-scope.
- Reference `BR-###` rules in implementation notes and focused tests when applicable.
- Keep frontend DTOs compatible with `data-contract.md`.
- Record implementation assumptions and contract variances; do not silently change product semantics.
