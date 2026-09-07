# Whole-Karya navigation adoption

Status: accepted. Owner authorization: complete navigation integration and map Karya as a whole, including all Factories, not only Harness (2026-09-06).

## Existing mechanisms and disposition

| Mechanism | Disposition | Resolution |
| --- | --- | --- |
| AGENTS and concise repository/Harness Markdown | exists | Preserve owner rules and specialized orientation; add JSON routing and maintenance instructions. |
| Architecture, catalogue, workflow and handoff contracts | keep_specific | Remain authoritative; map their ownership and references without creating a merged domain document. |
| Skill folders, frontend/Django kits and specialized contracts | keep_specific | Preserve independent installability, rich contracts and generated-project assets. |
| JSON map, source fingerprints and offline view | generalize | Adopt the same standalone kit distributed to new Harness projects. |
| Mandatory executable Spec check | create_new | Shared validator rejects missing/optional/manual check in active Specs, before execution. |
| Local skill distribution | exists | Replace only Karya-owned packages from the approved working tree after backing up old installs; verify file hashes. |

## Ownership and scope

The accepted seed is `.codex/decisions/project-harness-bootstrap.json`. The maintained map is `.codex/references/project-map.json`; the seed is historical and is not repeatedly regenerated. Each installable skill is represented once as a package, with its SKILL.md as the entry point. Package membership comes from `specs/skill-catalog.md`; explicit contract relations preserve specialized ownership. Directory containment is structural, not inferred behavior.

The map covers MVP Factory, Research Factory, Marketing Factory, Project Harness Factory, the optional Karya coordinator, contracts, documentation, context/workflows, examples, templates, local maintenance scripts, brand and official website. Existing `project-harness.md` remains a specialized reference. Generated `.harness/views/project-map.html` is ignored and is not the website or a published artifact.

## Maintenance

Read affected original sources before implementation. Reconcile affected documentation, paths, responsibilities and relations after changes, then record an explicit `review --note` and rerun `check`. New skill packages or removed/moved areas must be reconciled against the catalogue and map. Full-source fingerprints flag new or removed eligible files even outside mapped areas. The map is navigation, not exhaustive code-call analysis or semantic approval.

Active contracts need the executable map check; completed historical contracts are preserved. Existing Factory approval and handoff boundaries remain in force. Adoption by Karya itself does not make Harness mandatory in projects created through another Factory.

The generic economic router cannot edit protected `.codex` files. For projects with the living map it returns Codex fallback before provider inspection or execution, preserving the same Spec and map validation. Explicitly forcing OpenCode returns unavailable; this does not weaken the Django-specific route's separate contracts.

No remote push, publication, SDK execution, paid provider call or migration of another user project is authorized by this adoption record.

## Observed local validation

- 67 Python tests passed across bootstrap, map, Spec validator, Codex router v2 and Harness auditor. They include rejection before SDK import, rejection of manual/optional checks, and canonical command replay replacing a false success claim with failure on stale sources.
- Two additional economic-router tests passed, including automatic fallback/forced-unavailable for a mapped project without running provider commands or changing source files.
- Independent read-only review reconciled Factory/skill membership and sampled semantic relations against sources. Its manual-check finding was corrected and reverified with seven focused tests; no blocking finding remained in that scope. This is not a live SDK or external-execution audit.
- The installed skill packages were exercised through a fresh temporary project: dry-run preservation, bootstrap, initial pending review, explicit review, new-file drift, reconciliation, render without invalidation and installed auditor approval all passed.
- All 23 installed packages passed skill validation. SHA-256 parity covered 374 distributed files; the six-file local map kit matches its owning skill resources. Previous packages are backed up under the local Codex backup directory.
- Chromium exercised the real 117-node/197-relation map offline at desktop and mobile sizes: Factory/skill presence, multiword search, empty state, filters, neighbor selection, zoom/fit and mobile overflow checks passed, with no JavaScript errors or remote HTTP requests. Screenshots were inspected. Final review/check and rendering refresh the derived snapshot after source reconciliation.
