# ADR-004: Equal timestamp ordering

Status: accepted.

When two normalized samples have the same timestamp, preserve their original input order. Adding a value-based tie-breaker would silently change source semantics and is outside SPEC-023.
