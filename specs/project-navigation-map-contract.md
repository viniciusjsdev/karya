# Project navigation map contract

## Goal and approved scope

Karya Harness projects use one JSON map at `.codex/references/project-map.json` for navigation. Original docs, ADRs, domain contracts and Spec references remain authoritative. The owner approved a live map maintained with changes and an optional offline interactive HTML using Karya branding. This contract records the resolved implementation scope; it does not dispatch an SDK thread or alter runtime manifests.

## Requirements

- REQ-001: New bootstrap generates the map from an accepted plan, copies its standalone Python 3.12+ maintenance tool into `scripts/harness/`, and directs new AGENTS instructions to it. Existing files and historical bootstrap decisions are preserved.
- REQ-002: Nodes have stable IDs, labels, kinds, summaries, paths, target types, planned/existing status and authority. Relations have endpoints, a bounded type and an explicit rationale. Bootstrap derives only structural containment from the plan, never inferred domain relationships.
- REQ-003: `check` validates schema, paths, endpoints and freshness. A content digest detects changes to the map; a project fingerprint detects edits, additions, renames and deletions in tracked and non-ignored files. Without Git, a bounded filesystem inventory is used. External references are never fetched; secrets, build/cache trees, the map itself and derived HTML are excluded. Explicit file/directory nodes are independently fingerprinted. Coverage is reported.
- REQ-004: `review --note` records the executor's reconciliation after source and map edits. It refuses broken structure or missing existing targets, updates fingerprints atomically, and does not invent relations, update domain docs or assert independent semantic approval. Ordinary `check`, `query` and `render` never acknowledge changes. Required Spec validation and Harness audit enforce freshness where a JSON map exists.
- REQ-005: `migrate` creates a JSON map from an accepted plan, keeps the old Markdown as a mapped source, and adds a bounded managed AGENTS block preserving owner instructions. Old projects remain supported until explicit migration. No mandatory duplicate Markdown is generated for JSON projects.
- REQ-006: `render` produces a standalone offline HTML snapshot on demand with generation time, map digest and freshness warnings, Karya colors and unmodified logo. Search, node/relation filters, neighbor focus, details, zoom, pan, dragging and keyboard selection work without a server or remote resources. Data remains text, not executable HTML or script. Rendering never changes the map.

## Boundaries and maintenance

The plan is historical bootstrap input; the JSON is the current map. Map edits accompany changed paths, responsibilities or relations; code-only changes may need review without a map edit. A fingerprint is a change detector, not semantic proof. The executor reads sources, reconciles the map, then records a note; review audits the actual evidence. No Graphify, database, daemon, automatic external access, global install, bulk project migration or git push is included.

The map is not an exhaustive function-call graph. Directory fingerprints cover their eligible contents, and the general project fingerprint detects new files outside mapped areas. Symlinks and special files are not followed. Generated map/HTML output does not invalidate itself. Read-only query/render may expose a stale snapshot with explicit warnings; required check/audit cannot silently accept it.

For conventional paired Harness Specs, lifecycle status fields are normalized and the Spec's execution `evidence/` subtree is excluded from the general fingerprint to avoid receipt/validation loops. Intent, commands and other contract fields remain covered; explicit evidence-file nodes remain fingerprinted. Other evidence directories remain covered. Coverage limits are part of the check report and maintenance reference.

## Acceptance and validation

- AC-001: Fresh bootstrap, dry-run, preservation and repeat runs are covered by real CLI tests.
- AC-002: Missing/moved paths, invalid/duplicate IDs, dangling edges, escaping paths and unsafe external schemes are rejected; planned and external nodes have explicit behavior.
- AC-003: A reviewed fixture becomes stale on code/doc/map changes, new or removed files, and is current only after explicit review; ignored/derived outputs do not cause loops.
- AC-004: Legacy migration preserves Markdown and owner instructions, is idempotent and installs a standalone tool; the auditor supports legacy and rejects stale JSON maps.
- AC-005: HTML snapshot has no network dependency or executable injected data, and primary controls work at desktop and mobile sizes.
- VAL-001: Run the bootstrap, project-map and applicable auditor/Spec validator Python tests.
- VAL-002: Run `quick_validate.py` for each changed skill and `git diff --check`.
- VAL-003: Inspect rendered HTML and exercise search, filters, selection, neighbor focus, zoom/reset and mobile layout in a browser; report the actual boundary of verification.

## Implementation ownership

`project-harness-architect` owns the schema, standalone CLI, renderer assets, bootstrap and maintenance instructions. `project-spec-architect` declares map review/check in new Specs when a map exists. `project-harness-auditor` checks freshness without modifying evidence. All writes in the current working tree remain sequential. Existing changes from earlier work are preserved. Validation and final review occur in the current authorized task; no model switch or independent SDK review is claimed.

## Active execution and adoption

Active Specs (`ready`, `in_progress`, `implemented`, `review`, `changes_requested`) in adopted projects must include the canonical map check as `kind: test`, `required: true`, executed from the project root. The shared validator enforces this before Codex SDK and economic execution. Manual declarations are rejected. Completed historical Specs remain unchanged; resuming an older active Spec after adoption requires a normal contract revision. Removing JSON while AGENTS still references it is an error.

The generic economic executor protects `.codex` and cannot perform source/map reconciliation. Adopted projects therefore return Codex fallback before provider inspection; forced OpenCode requests return unavailable. Checks cannot be removed or automatically acknowledged to bypass this boundary.

Karya's own adoption covers the coordinator, four independent Factories, all 23 skill packages, contracts, workflows, examples, starters, tools, brand and site. Optional association never implies automatic invocation. Local installed skill updates preserve backups outside repositories and verify file parity; they do not publish remote content.

## Source-backed areas and dependencies

Schema 1.1 adds optional navigation root and areas with stable IDs, source node IDs, member node IDs and rationales. Version 1.0 remains supported. Membership comes from inspected architecture and ownership sources; multiple membership is permitted and displayed explicitly. Areas contain no coordinates or colors and do not propagate ownership through all descendants.

Record direct imports and resource consumption as `consumer -> dependency`, with the evidence in the rationale. References, containment, validation and optional workflow handoffs retain their distinct relation types. Dependency depth and cycles are derived from recorded edges, with absent evidence labeled as unrecorded dependency rather than independence. The map makes no claim to be a complete runtime call graph.

UTF-8 text fingerprints normalize CRLF to LF for portable Git checkouts. Substantive text changes remain detectable; binary files retain byte-level hashing. An existing review made with older fingerprint semantics needs one explicit reconciliation when the maintenance tool is upgraded.

## Interactive presentation

The default Atômico view has a compact center and two tilted orbital bands; Esfera, Camadas and 2D remain distinct options. Content bands organize types rather than dependency depth. Declared areas determine color families and actual folder paths determine related tones. Missing area membership remains neutral. Slot assignment brings connected records closer within each band, weighting dependencies; a bounded force solver serves 2D. These are visual heuristics, not additional project facts.

Every node can be dragged freely in every view. In 3D, dragging follows the screen plane at the node's depth; rotating first allows repositioning along another axis. Manual offsets survive filters, spacing, coloring, zoom and view switches within the current page session. Restore clears them; reloading resets them. Background drag rotates or pans separately. No coordinates are written to JSON or browser storage.

Continuous arrowed lines show dependencies; dashed lines show other relationships. Details show source paths, direction, rationale, dependency depth and cycle members. Screen height, orbit and manual proximity never redefine relationships. The viewer draws at most 200 nodes with the limit disclosed, and keeps a selected relation destination visible. Large-repository performance and graph completeness require separate evaluation.

## Website demonstration and release assets

The official website explains why navigation matters for clean Threads and application maintenance, and offers the real Karya map in an on-demand sandboxed iframe or a separate page. A Node build script reads the versioned JSON and canonical Harness template/logo. It omits maintenance attestations and node fingerprints from the public payload, safely escapes embedded JSON, and labels the result as a static demonstration without local source verification.

The site build regenerates that snapshot; it does not automatically review the project map. GitHub Pages watches the JSON, viewer assets and website source, runs site tests and builds the artifact. Generated HTML, local runtime state, construction screenshots and temporary helpers remain ignored. The source template and required brand assets are versioned.

## Release verification — 2026-09-07

- 83 Python tests passed across Harness architect, Spec architect, Harness auditor, Codex runtime router and economic executor, including bootstrap/migration preservation, freshness gates, portable fingerprints and viewer behavior in an isolated Node VM.
- Six website tests passed, including on-demand iframe behavior and safe snapshot generation. Typecheck, lint, formatting, lockfile checks and production build passed; clean dependency installation reported zero vulnerabilities.
- Browser checks on the integrated local site exercised open/close, search, Atômico/2D switching and the light theme at desktop and 390-pixel mobile widths. Screenshots were inspected without adding them to the release. No page horizontal overflow or browser warnings/errors were observed in those checks.
- The website retains its existing architecture exception. The general frontend scanner reports 27 baseline warnings about conventions/dependencies; this delivery does not claim a clean full-stack architecture audit.

These checks establish local implementation behavior, not complete semantic coverage of arbitrary projects, public deployment or independent domain approval. Source review and the map check remain required for each adopted project's own changes.
