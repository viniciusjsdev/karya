# npm Security Checklist

- [ ] Approved npm and Node versions used
- [ ] Direct dependencies use exact versions
- [ ] Lockfile v3 is committed and is the only lockfile
- [ ] Registry sources and SHA-512 integrity pass verification
- [ ] Install scripts remain disabled or a pinned exception is reviewed
- [ ] Seven-day release age remains enabled
- [ ] Git, remote tarball, file, and directory dependencies remain blocked
- [ ] Registry signatures/provenance checked after installation
- [ ] High and critical audit findings are absent
- [ ] SBOM generated for release evidence when applicable
