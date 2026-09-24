# Living project navigation

New Harness projects have `.codex/references/project-map.json`, a navigation graph owned by the project. Its schema and standalone CLI are distributed by this skill. There is no mandatory generated Markdown twin, graph database, daemon, external API or automatic model invocation.

## Ownership and life cycle

The accepted bootstrap plan is historical input. Original domain docs, decisions, contracts and code remain authoritative. The JSON records paths, brief responsibilities and explicit relations; it is not an exhaustive call graph. IDs remain stable when nodes move: edit the node path, do not replace its ID and orphan relations. Bootstrap creates deterministic IDs from initial paths; subsequent maintenance preserves them.

Before implementation, inspect `AGENTS.md`, run `python scripts/harness/project_map.py check --project-root .`, query relevant nodes and read original sources. Reconcile stale/invalid results; continue appropriate direct source investigation rather than relying on an outdated map.

Before completion, inspect the change and its documentation impact. Update docs, node paths/status/responsibilities and relations as needed. An internal implementation edit can leave map semantics unchanged, but the executor must still review its impact. Then explicitly run:

```bash
python scripts/harness/project_map.py review --project-root . --note "Reviewed changed module and source contracts; describe updates or why navigation remains accurate."
python scripts/harness/project_map.py check --project-root .
```

`review` is the executor's attestation. Never schedule it or call it automatically to clear a failing check. It refuses missing existing targets and newly created targets still labeled planned. The auditor independently checks facts and relationships; fingerprints establish change detection only. Run the check after all relevant changes. If the user chose a Spec, include it as a required VAL command; do not rewrite historical manifests merely to adopt this tool.

The Spec validator rejects active contracts without the canonical check declared as `kind: test`, `required: true`, or without the local tool, and requires execution from the project root. A manual declaration would not be executed by the router and is rejected. Completed historical Specs are preserved; resuming an older active Spec after adoption requires a normal contract revision adding the check. Removing JSON while AGENTS still routes to it is an error, even when legacy Markdown remains. Neither Spec design nor read-only queries automatically acknowledge current fingerprints.

## Schema and initial map

Version 1.0 maps remain supported. Version 1.1 adds optional `navigation`: a `root` node ID and an `areas` list. Each area has a stable `id`, human `label`, `rationale`, `sources` (existing map node IDs providing the evidence), and `members` (existing map node IDs). The project root is separate from area membership. IDs and references are validated; repeated members within one area are rejected. Membership in multiple areas is allowed when the sources support it. Areas contain no coordinates, colors, radii or camera state.

Do not regenerate areas from a generic reference edge or node kind. Read architecture, catalog and ownership sources, then author the membership. Areas describe navigation association, not automatic execution, handoff, hierarchy or transitive ownership of every child directory. Unmapped membership stays visibly unreviewed. Area edits invalidate the map fingerprint and require the same explicit source review as other semantic edits. `query` also matches area labels and includes the source-backed memberships for its selected nodes.

`assets/project-map.schema.json` defines metadata, nodes, relations and review state. Each node has a kind, target (`file`, `directory`, `pattern`, `external`), status (`existing`, `planned`), authority and fingerprint. Existing local targets must exist. Patterns are planned path shapes, not assertions of an active Spec. External targets are HTTP(S) URLs without credentials and are never fetched automatically. Secret material, generated output and symlink targets cannot be map sources.

Bootstrap seeds sources, mappings, workflows, decisions, Spec locations, policy and validation declarations from the plan. It derives structural path containment and references to stored declarations only. Author meaningful `governed_by`, `implements`, `validates`, `depends_on` and `supersedes` relations after inspecting the sources; every relation requires a rationale. Never infer test coverage from a validation command appearing in the plan.

The initial map requires review. Missing sources declared for preservation are errors; sources explicitly planned for creation may be absent. When planned files/directories are created, change their status and review. Adjust inferred file/directory target types when the plan could not determine them.

## Change detection and limits

`check` is read-only and fails on structure/path errors or pending review. It hashes map semantics and project contents, detecting same-size edits, additions, renames and deletions. In a Git root it inventories tracked and non-ignored untracked files; without Git it walks the project with conventional exclusions. Git subdirectories use the filesystem fallback, reported in coverage. Node file hashes also cover explicitly mapped ignored files. UTF-8 text fingerprints normalize CRLF to LF so a Git checkout on another operating system does not require a new review merely for line endings. Binary content retains byte-level hashing; substantive text changes still invalidate the map.

The map itself, `.harness/` outputs, secrets and conventional dependency/build/cache directories are excluded. Symlinks and special files are not followed; coverage reports these limits. Code or docs hidden in excluded trees require a deliberate coverage design, not a claim of complete freshness. This default trades a full content scan for reliable local change detection; evaluate cost before expanding to a very large corpus.

In conventional directories containing both `SPEC.md` and `SPEC.execution.json`, only lifecycle `status` fields are normalized and their `evidence/` subtree is excluded from the general project fingerprint. This prevents router receipts/status transitions after validation from invalidating the map indefinitely. Requirements, commands, versions and other Spec/manifest content still invalidate it; explicitly mapped evidence files are independently hashed. Other evidence directories remain covered. Alternate lifecycle layouts require a deliberate coverage design.

`query --project-root . --text "topic" --limit 20` selects matching node metadata and a bounded set of related edges. It reports pending review without changing fingerprints. Relations may name neighbors outside the selected subset; query those IDs or inspect the JSON as needed.

## Existing projects

Repeated bootstrap preserves existing JSON maps and tool files. A project with only `project-harness.md` stays in legacy mode; its Markdown is not overwritten. When migration is in scope:

```bash
python scripts/project_map.py migrate --project-root <root> --plan <accepted-plan.json> --dry-run
python scripts/project_map.py migrate --project-root <root> --plan <accepted-plan.json>
```

These commands are relative to this skill; installed project tools live at `scripts/harness/project_map.py`. Migration preserves the legacy Markdown as a mapped source, preserves owner AGENTS content and adds an explicitly managed navigation block. Review the legacy links and transfer the useful structure into JSON; parsing Markdown is not an automatic semantic migration. Existing tools are preserved, so reconcile version upgrades separately.

When the historical bootstrap archive exists, use it as the accepted seed plan. A differing input cannot be attributed to that preserved archive: initial migration refuses it before writes. After seeding, reconcile current sources and relationships directly in the map. This keeps bootstrap history distinct from living navigation.

## Show the map

Run `python scripts/harness/project_map.py render --project-root .` when the user requests a visualization. The output `.harness/views/project-map.html` is an offline read-only snapshot with generation time and freshness status. Regenerate after source/map review. It never edits JSON, fetches sources, invokes a model or writes coordinates/colors to durable truth.

The default **Atômico** view restores one compact center and two tilted orbital bands. **Esfera** distributes the same nodes over spherical surfaces; **Camadas** separates the content bands, and **2D** uses a finite relation-based force layout. Areas never create separate spatial domains. Initial atomic/spherical slot assignment minimizes recorded connection length within each content band, weighting dependencies more strongly; the 2D solver also attracts linked nodes. This is a bounded visual heuristic, not a guarantee that every connected pair is adjacent. Work is bounded to 200 nodes for slot optimization/force solving; other records retain deterministic initial positions.

The three visual bands group product/domain/decision/methodology, architecture/contract/workflow/reference/Spec, and code/validation/operation/runtime/data/other. They are presentation categories, not dependency depth or authority. The complete-project root starts at the center and can also be moved. Nodes without recorded dependencies stay in the same map, not a separate lateral region. Recorded dependency depth and strongly connected components remain available in details: `consumer -> dependency`, cycles disclosed with their members, and no edge reported as **Sem dependência registrada**, not as independence. Manual height, radius and proximity never redefine these facts.

Drag any node in any view to reposition it freely, even outside its original band. In 3D the movement follows the screen plane at the node's depth; rotate the scene before dragging to change placement along other world axes. Background dragging separately rotates or pans; Shift pans and touch pinch zooms. A click selects, while a drag does not trigger an accidental click. Connections follow the moved node without changing other nodes or the camera. Offsets are held per view for the current page session and survive filters, coloring, zoom, spacing controls and view switches. **Restaurar** clears all manual offsets and restores the initial spacing/orientation; **Enquadrar** fits the visible positions, including moved nodes. Reloading or regenerating HTML resets offsets. No positions are written to JSON or browser storage.

Colors default to declared areas, with related tones for actual directory paths. Skill packages belonging to the same Factory share a color family even when they are sibling folders under `skills/`. A project's own area names are used; no Karya Factory names are hardcoded. Multiple membership uses a split color and lists every association/source; unassigned records stay neutral. Without declared areas, colors fall back to actual top-level folders and do not imply reviewed ownership. Node details identify the folder behind the tone. Colors alone are insufficient: labels, paths and provenance remain available. Content-type coloring/filtering is optional and independent of position.

Continuous arrowed edges are dependencies; dashed edges are containment, references, governance, implementation, validation or supersession. Dependencies remain visible by default; other relations can be shown together or on node selection. Direction and rationale are displayed in details. A document referencing modules must not become their runtime prerequisite. Map direct imports or resource consumption only after source inspection, with rationales naming the evidence; do not convert optional Factory handoffs or workflow ordering into mandatory dependencies.

The spacing controls adjust orbital/separated-band distance and node spread; manual offsets remain applied. Search, source details, neighbor focus, label density, keyboard selection, zoom, pan and touch pinch remain available. Background rotation and arrow keys apply to 3D; 2D supports free node dragging and background pan. Drawing runs on interaction, with no idle animation, WebGL, server or remote library. The 200-node draw cap is disclosed; selecting a relation destination beyond the cap keeps it visible. Node size reflects connection count and perspective, not architectural authority. Geometry does not guarantee no projected overlap at every angle.

The installed kit and bootstrap use this same template. Existing project tools are preserved by bootstrap and need an explicit upgrade; new projects are initialized from the accepted plan and require source review to enrich dependencies and optional areas. The HTML cannot infer a complete graph from the initial plan. The logo and palette remain part of Karya's bundled visual identity; the repository license applies.

## Public website demonstration

Karya's website builds `project-map.html` from the repository JSON and this same viewer template. The public payload omits maintenance attestations and fingerprints and explicitly identifies itself as a static demonstration without local source verification. Rebuild the site to refresh that snapshot. This does not replace the project CLI review/check cycle, and construction screenshots are not release assets.
