# npm Supply-Chain Security

Require the project `.npmrc` policy:

```ini
ignore-scripts=true
min-release-age=7
allow-git=none
allow-remote=none
allow-file=none
allow-directory=none
save-exact=true
package-lock=true
strict-peer-deps=true
engine-strict=true
audit-level=high
```

Before adding a dependency, verify its exact name, purpose, ownership, repository, maintenance, transitive graph, install scripts, license, and advisories.

Use `npm ci`, never floating versions or forced audit remediation. Verify lockfile sources and integrity, registry signatures, vulnerability audit, and SBOM. Treat high and critical findings as release blockers.
