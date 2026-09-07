"""Project-map contracts, fingerprints and local rendering; no source mutation or network access."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

MAP_PATH = ".codex/references/project-map.json"
LEGACY_PATH = ".codex/references/project-harness.md"
TOOL_PATH = "scripts/harness/project_map.py"
HTML_PATH = ".harness/views/project-map.html"
EXCLUDED_DIRS = {".git", ".harness", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", "coverage", ".next"}
KINDS = {"domain_truth": "domain", "product": "product", "architecture": "architecture", "decision": "decision", "methodology": "methodology", "data": "data", "operation": "operation", "contract": "contract"}


def resource(name: str) -> Path:
    """Resolve identical resources from either the skill or generated-project kit."""
    here = Path(__file__).resolve().parent
    local = here / name
    return local if local.is_file() else here.parent / "assets" / name


def load_map(root: Path) -> dict:
    """Read the canonical map without allowing an escaped target."""
    return json.loads(local_path(root, MAP_PATH).read_text(encoding="utf-8-sig"))


def digest(value: object) -> str:
    """Hash a deterministic JSON representation."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    """Replace only the requested generated artifact after a complete UTF-8 write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def local_path(root: Path, relative: str) -> Path:
    """Reject absolute, traversal, stream and symlink paths outside project ownership."""
    if not relative or "\\" in relative or ":" in relative or relative.startswith("/"):
        raise ValueError(f"Expected project-relative POSIX path: {relative}")
    parts = PurePosixPath(relative).parts
    if ".." in parts:
        raise ValueError(f"Parent traversal is not allowed: {relative}")
    current = root.resolve()
    for part in parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError(f"Symlink/junction is not a map target: {relative}")
    current.resolve().relative_to(root.resolve())
    return current


def eligible(relative: str) -> bool:
    """Exclude sensitive files, generated outputs and conventional caches from hashing."""
    path = PurePosixPath(relative)
    name = path.name.lower()
    if any(part in EXCLUDED_DIRS for part in path.parts) or relative == MAP_PATH:
        return False
    if name == ".coverage" or name.endswith((".pyc", ".pem", ".key", ".pfx", ".p12")):
        return False
    if name.startswith(".env") and name not in {".env.example", ".env.sample", ".env.template"}:
        return False
    return not any(word in name for word in ("credentials", "secrets", "id_rsa", "id_ed25519"))


def harness_evidence(root: Path, relative: str) -> bool:
    """Exclude conventional Spec execution receipts, not arbitrary research evidence."""
    parts = PurePosixPath(relative).parts
    for index, part in enumerate(parts):
        if part == "evidence":
            parent = root.joinpath(*parts[:index])
            if (parent / "SPEC.md").is_file() and (parent / "SPEC.execution.json").is_file():
                return True
    return False


def inventory(root: Path) -> tuple[list[str], str]:
    """Inventory project-owned regular files, using Git ignore rules when available."""
    root = root.resolve()
    mode = "filesystem"
    candidates: list[str] = []
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True, timeout=10)
        if top.returncode == 0 and Path(top.stdout.strip()).resolve() == root:
            result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, capture_output=True, timeout=10)
            if result.returncode != 0:
                raise ValueError("Git inventory failed; review cannot establish project freshness.")
            candidates = result.stdout.decode("utf-8").split("\0")
            mode = "git tracked + non-ignored untracked"
    except subprocess.TimeoutExpired as error:
        raise ValueError("Git inventory timed out; project freshness could not be established.") from error
    except FileNotFoundError:
        pass
    if mode == "filesystem":
        for folder, dirs, files in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if name not in EXCLUDED_DIRS and not (Path(folder) / name).is_symlink() and not (hasattr(Path(folder) / name, "is_junction") and (Path(folder) / name).is_junction())]
            candidates.extend((Path(folder) / name).relative_to(root).as_posix() for name in files)
    found = []
    for relative in sorted(set(candidates)):
        if not relative or not eligible(relative) or harness_evidence(root, relative):
            continue
        try:
            path = local_path(root, relative)
        except ValueError:
            continue
        if path.exists() and stat.S_ISREG(path.stat().st_mode):
            found.append(relative)
    return found, mode


def file_digest(path: Path) -> str:
    """Hash content with portable UTF-8 line endings and paired Spec lifecycle handling."""
    if path.name == "SPEC.execution.json" and path.with_name("SPEC.md").is_file():
        try:
            value = json.loads(path.read_text(encoding="utf-8-sig"))
            if isinstance(value, dict) and value.get("schema_version") in {"1.0", "2.0"}:
                return digest({key: item for key, item in value.items() if key != "status"})
        except (ValueError, UnicodeError):
            pass
    if path.name == "SPEC.md" and path.with_name("SPEC.execution.json").is_file():
        try:
            text = path.read_text(encoding="utf-8-sig")
            if text.startswith("---\n") and "\n---" in text[4:]:
                frontmatter, body = text[4:].split("\n---", 1)
                normalized = re.sub(r"^status:.*$", "status: lifecycle", frontmatter, flags=re.MULTILINE)
                return digest(normalized + "\n---" + body)
        except UnicodeError:
            pass
    content = path.read_bytes()
    if b"\0" not in content:
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            # Git may check text out as CRLF on Windows and LF on Linux.
            # That alone must not invalidate a committed source review.
            content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


def fingerprints(root: Path, data: dict) -> tuple[str, dict[str, str | None], dict]:
    """Compare actual contents rather than mtimes, including explicit ignored sources."""
    files, mode = inventory(root)
    hashes = {name: file_digest(local_path(root, name)) for name in files}
    node_hashes: dict[str, str | None] = {}
    for node in data["nodes"]:
        if node["target"] == "file" and node["status"] == "existing":
            node_hashes[node["id"]] = file_digest(local_path(root, node["path"]))
        elif node["target"] == "directory" and node["status"] == "existing":
            prefix = node["path"].rstrip("/") + "/"
            node_hashes[node["id"]] = digest({name: value for name, value in hashes.items() if name.startswith(prefix) or node["path"] == "."})
        else:
            node_hashes[node["id"]] = None
    return digest(hashes), node_hashes, {"mode": mode, "file_count": len(files), "exclusions": sorted(EXCLUDED_DIRS), "note": "Secrets and special/symlink files excluded; external URLs are not fetched. Conventional paired Spec evidence is excluded and lifecycle status normalized. Explicit existing files are hashed even when Git-ignored."}


def schema_errors(value: object, schema: dict, path: str = "map") -> list[str]:
    """Validate the deliberately small JSON Schema subset used by this standalone kit."""
    errors: list[str] = []
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: unsupported value")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: unsupported value")
    types = schema.get("type", [])
    types = [types] if isinstance(types, str) else types
    checks = {"object": isinstance(value, dict), "array": isinstance(value, list), "string": isinstance(value, str), "null": value is None}
    if types and not any(checks.get(kind, False) for kind in types):
        return errors + [f"{path}: expected {'/'.join(types)}"]
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or ("pattern" in schema and not re.fullmatch(schema["pattern"], value)):
            errors.append(f"{path}: empty or invalid text")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: missing")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            errors.extend(f"{path}.{key}: unknown field" for key in value if key not in props)
        for key in value.keys() & props.keys():
            errors.extend(schema_errors(value[key], props[key], f"{path}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: insufficient items")
        for index, item in enumerate(value):
            errors.extend(schema_errors(item, schema.get("items", {}), f"{path}[{index}]"))
    return errors


def validate_map(root: Path, data: object, *, check_paths: bool = True) -> list[str]:
    """Validate map shape and reference integrity, never executing declared commands."""
    errors = schema_errors(data, json.loads(resource("project-map.schema.json").read_text(encoding="utf-8")))
    if errors:
        return errors
    ids: set[str] = set()
    for node in data["nodes"]:
        label = node["id"]
        if label in ids:
            errors.append(f"Duplicate node ID: {label}")
        ids.add(label)
        if node["target"] == "external":
            url = urlsplit(node["path"])
            if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
                errors.append(f"{label}: external target must be an HTTP(S) URL without credentials")
            continue
        try:
            path = local_path(root, node["path"])
            if not eligible(node["path"]):
                raise ValueError("sensitive, generated or excluded map target")
            if node["target"] == "pattern":
                if node["status"] != "planned":
                    errors.append(f"{label}: patterns describe planned locations, not existing artifacts")
                continue
            if check_paths and node["status"] == "existing":
                if node["target"] == "file" and not (path.is_file() and stat.S_ISREG(path.stat().st_mode)):
                    errors.append(f"{label}: missing regular file {node['path']}")
                elif node["target"] == "directory" and not path.is_dir():
                    errors.append(f"{label}: missing directory {node['path']}")
        except (ValueError, OSError) as error:
            errors.append(f"{label}: {error}")
    seen = set()
    for edge in data["relations"]:
        key = (edge["from"], edge["type"], edge["to"])
        if edge["from"] not in ids or edge["to"] not in ids:
            errors.append(f"Dangling relation: {key}")
        if key in seen or edge["from"] == edge["to"]:
            errors.append(f"Duplicate or self relation: {key}")
        seen.add(key)
    navigation = data.get("navigation")
    if navigation is not None:
        if data["schema_version"] != "1.1":
            errors.append("Navigation areas require schema_version 1.1")
        if navigation["root"] not in ids:
            errors.append("Dangling navigation root")
        area_ids: set[str] = set()
        for area in navigation["areas"]:
            if area["id"] in area_ids:
                errors.append(f"Duplicate area ID: {area['id']}")
            area_ids.add(area["id"])
            for field in ("sources", "members"):
                references = area[field]
                if len(references) != len(set(references)):
                    errors.append(f"Duplicate area {field}: {area['id']}")
                if any(reference not in ids for reference in references):
                    errors.append(f"Dangling area {field}: {area['id']}")
            if navigation["root"] in area["members"]:
                errors.append(f"Navigation root cannot be an area member: {area['id']}")
    return errors


def map_digest(data: dict) -> str:
    """Digest semantics and node fingerprints; maintenance cannot validate itself."""
    return digest({key: value for key, value in data.items() if key != "maintenance"})


def check_map(root: Path, data: object) -> dict:
    """Report structural failures and unacknowledged project/map changes read-only."""
    errors = validate_map(root, data)
    if errors:
        return {"status": "invalid", "errors": errors, "pending": [], "coverage": {}}
    project_hash, node_hashes, coverage = fingerprints(root, data)
    state = data["maintenance"]
    pending = []
    if not state["reviewed_at"] or not state["review_note"].strip():
        pending.append("Initial source and relationship review is required.")
    if state["map_fingerprint"] != map_digest(data):
        pending.append("Map content changed or has not been reviewed.")
    if state["project_fingerprint"] != project_hash:
        pending.append("Project files changed or have not been reviewed (including additions/deletions).")
    for node in data["nodes"]:
        if node["fingerprint"] != node_hashes[node["id"]]:
            pending.append(f"Source changed: {node['id']} ({node['path']})")
        if node["status"] == "planned" and node["target"] in {"file", "directory"} and local_path(root, node["path"]).exists():
            pending.append(f"Planned target now exists; reconcile its status: {node['id']}")
    return {"status": "review_required" if pending else "current", "errors": [], "pending": pending, "coverage": coverage}


def review_map(root: Path, data: dict, note: str) -> dict:
    """Record an explicit executor attestation; does not prove semantic correctness."""
    if not note.strip():
        raise ValueError("Review requires a meaningful --note about source/map reconciliation.")
    errors = validate_map(root, data)
    if errors:
        raise ValueError("; ".join(errors))
    for node in data["nodes"]:
        if node["status"] == "planned" and node["target"] in {"file", "directory"} and local_path(root, node["path"]).exists():
            raise ValueError(f"Reconcile planned status before review: {node['id']}")
    result = copy.deepcopy(data)
    project_hash, node_hashes, _ = fingerprints(root, result)
    for node in result["nodes"]:
        node["fingerprint"] = node_hashes[node["id"]]
    result["maintenance"] = {"reviewed_at": datetime.now(timezone.utc).isoformat(), "review_note": note.strip(), "project_fingerprint": project_hash, "map_fingerprint": map_digest(result)}
    return result


def map_from_plan(root: Path, plan: dict) -> dict:
    """Create conservative navigation from plan declarations, retaining legacy sources."""
    nodes: list[dict] = []
    by_path: dict[str, dict] = {}

    def add(path: str, label: str, kind: str, summary: str, *, target: str | None = None, action: str = "preserve", authority: str = "supporting") -> dict:
        path = path.replace("\\", "/")
        if path in by_path:
            return by_path[path]
        external = urlsplit(path).scheme in {"http", "https"}
        local = None if external else local_path(root, path)
        target = "external" if external else target or ("directory" if local.is_dir() else "file")
        status = "planned" if action == "create" or target == "pattern" or (local is not None and not local.exists()) else "existing"
        node = {"id": "n-" + hashlib.sha256(path.encode()).hexdigest()[:12], "label": label, "kind": kind, "summary": summary, "path": path, "target": target, "status": status, "authority": authority, "fingerprint": None}
        nodes.append(node)
        by_path[path] = node
        return node

    for source in plan["sources_of_truth"]:
        node = add(source["path"], source["path"], KINDS.get(source["kind"], "other"), "Source declared in the accepted Harness plan.", action=source["action"], authority=source["authority"])
        if source["action"] != "create":
            node["status"] = "existing"
    for item in plan["documentation"]["path_mappings"]:
        node = add(item["existing_path"], item["generic_role"], "reference", "Path mapping from accepted plan.")
        node["label"] = item["generic_role"]
        node["status"] = "existing"
    for item in plan["documentation"]["create"]:
        node = add(item["path"], item["path"], "reference", item["purpose"], action="create")
        node["summary"] = item["purpose"]
    for item in plan["workflows"]:
        node = add(item["path"], item["name"], "workflow", "Workflow declared in accepted plan.", action=item["action"])
        if item["action"] != "create":
            node["status"] = "existing"
    add(plan["decisions"]["durable_path"], "Decisions", "decision", "Durable decisions. Open at bootstrap: " + json.dumps(plan["decisions"]["open"], ensure_ascii=False), target="directory")
    add(plan["spec_strategy"]["root"], "Specs", "spec", "Bounded project changes.", target="directory")
    add(plan["spec_strategy"]["active_pattern"], "Active Spec path pattern", "spec", "Pattern only, not a selected active Spec.", target="pattern")
    add(plan["runtime_policy"]["project_path"], "Runtime policy", "runtime", "Policy path declared in accepted plan.")
    archive = add(".codex/decisions/project-harness-bootstrap.json", "Accepted bootstrap plan", "reference", "Historical input; validation commands are declarations, not proof of execution.")
    validation_edges = []
    for item in plan["validation"]:
        node = {**archive, "id": "v-" + hashlib.sha256(item["id"].encode()).hexdigest()[:12], "label": item["id"], "kind": "validation", "summary": "Declared command (not executed): " + item["command"] + (" [required]" if item["required"] else " [optional]")}
        nodes.append(node)
        validation_edges.append({"from": node["id"], "to": archive["id"], "type": "references", "rationale": "Validation declaration is stored in the accepted bootstrap plan; this is not proof of test coverage."})
    if (root / LEGACY_PATH).is_file():
        add(LEGACY_PATH, "Legacy navigation", "reference", "Preserved owner-authored navigation; reconcile its links during migration.")
    edges = validation_edges
    for parent in nodes:
        if parent["target"] != "directory":
            continue
        for child in nodes:
            if child is not parent and child["target"] != "external" and child["path"].startswith(parent["path"].rstrip("/") + "/"):
                edges.append({"from": parent["id"], "to": child["id"], "type": "contains", "rationale": "Explicit path containment; not an inferred business dependency."})
    return {"schema_version": "1.0", "project": {"name": plan["project"]["name"], "objective": plan["project"]["objective"]}, "nodes": nodes, "relations": edges, "maintenance": {"reviewed_at": None, "review_note": "", "map_fingerprint": None, "project_fingerprint": None}}


def render_html(root: Path, data: dict) -> str:
    """Embed a read-only snapshot in a self-contained branded, network-free viewer."""
    report = check_map(root, data)
    if report["errors"]:
        raise ValueError("; ".join(report["errors"]))
    payload = {"map": data, "check": report, "generated_at": datetime.now(timezone.utc).isoformat(), "digest": map_digest(data)}
    encoded = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = resource("project-map.html").read_text(encoding="utf-8")
    logo = base64.b64encode(resource("karya-icon.png").read_bytes()).decode("ascii")
    return template.replace("__KARYA_LOGO__", logo).replace("__MAP_DATA__", encoded)
