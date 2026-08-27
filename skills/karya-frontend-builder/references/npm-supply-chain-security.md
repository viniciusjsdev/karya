# npm Supply-Chain Security

## Policy

Treat every new dependency as executable third-party code. Minimize the dependency graph and require a product or engineering reason for every added package.

Use Node.js 24 LTS with npm 11.18.x for the current baseline. Pin the approved npm CLI through `packageManager` and require it through `engines.npm` so install-script policy behaves consistently.

## Before Adding a Package

Review:

- whether platform or existing dependencies already solve the problem
- package ownership, repository, maintenance activity, and release history
- unpacked size and transitive dependency count
- install scripts and native binaries
- known vulnerabilities and recent ownership changes
- whether the requested package name could be a typo or dependency-confusion risk
- license compatibility

Never install a package only because generated code imported it. Verify the package name and purpose first.

## Deterministic Installation

Require:

- exact direct dependency versions in `package.json`
- committed `package-lock.json` using lockfile version 3
- `sha512` integrity for registry artifacts
- only `https://registry.npmjs.org/` as the default registry unless an approved scoped registry is documented
- `npm ci` for clean installs and CI
- no manual edits inside `node_modules`

Do not use floating tags such as `latest`, wildcard versions, Git URLs, arbitrary tarball URLs, or unreviewed local paths in product dependencies.

Run `npm run security:lockfile` before installation to check exact versions, registry hosts, integrity metadata, and approved lifecycle scripts.

## Install Scripts

Set `ignore-scripts=true` by default so dependency `preinstall`, `install`, and `postinstall` scripts never execute during installation. Keep `strict-allow-scripts=true` and version-pinned `allowScripts` entries as reviewed documentation for a future controlled exception; `ignore-scripts` takes precedence and blocks them in the default factory profile.

If a verified package cannot function without its install script, do not bypass protections ad hoc. Review the exact package and version, record the reason, set `ignore-scripts=false` deliberately, and approve only the required pinned package:

```bash
npm install-scripts ls
npm install-scripts approve <package>
```

Keep approvals pinned as `package@version`. Re-review when the lockfile changes the version. Never use `dangerously-allow-all-scripts` in factory projects.

Restore `ignore-scripts=true` when the exception is no longer required. Never disable it globally or at the user level to solve one project dependency.

## Release-Age and Source Restrictions

Set `min-release-age=7` so newly published versions must age for seven days before npm can select them. This reduces exposure to fast-moving account takeovers and malicious releases.

The release-age window can temporarily block a newly published security fix. In that situation, investigate the advisory and exempt only the reviewed package temporarily; do not remove the policy for the entire graph.

Set these source restrictions:

```ini
allow-git=none
allow-remote=none
allow-file=none
allow-directory=none
```

Factory dependencies must resolve by exact version from the approved registry. Document and review any project that genuinely needs a Git, tarball, file, or directory dependency before relaxing one restriction.

## Verification After Installation

Run:

```bash
npm audit signatures
npm audit --audit-level=high
npm sbom --sbom-format=cyclonedx
```

`npm audit signatures` verifies registry signatures and available provenance attestations. Treat missing or invalid signatures from a registry that advertises signing keys as a blocking supply-chain signal until investigated.

Treat high and critical vulnerabilities as release blockers. Review moderate findings based on reachability and exposure. Do not run `npm audit fix --force` automatically because it can introduce unreviewed major-version changes.

Generate an SBOM for release artifacts and retain it with CI/release evidence when the project has a delivery pipeline.

## Updating Dependencies

Update deliberately in small groups. For each update:

1. Inspect the manifest and lockfile diff.
2. Confirm registry source and integrity changes.
3. Review new transitive packages and install scripts.
4. Run signature and vulnerability checks.
5. Run typecheck, tests, build, browser smoke checks, and architecture scan.
6. Record any temporary override and its removal condition.

Never hide an audit finding with an override unless the advisory has been reviewed and the decision is documented with owner, rationale, scope, and expiry.
