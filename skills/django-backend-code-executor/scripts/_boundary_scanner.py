#!/usr/bin/env python3
"""Audit Django backends against Karya architecture and documentation rules."""

from __future__ import annotations

import ast
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse


CWD = Path.cwd()
ROOT = CWD.parent if CWD.name == "backend" and (CWD.parent / "docs").exists() else CWD
BACKEND = CWD if CWD.name == "backend" else (ROOT / "backend" if (ROOT / "backend").exists() else ROOT)
WARNINGS: list[str] = []
ERRORS: list[str] = []

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
}
CAMEL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
MODEL_SPEC_KEYWORDS = {"max_length", "choices", "default", "validators", "db_column"}
PERSISTENCE_METHODS = {"save", "delete", "bulk_create", "bulk_update", "get_or_create", "update_or_create"}
MIN_MODULE_DOCSTRING_CHARS = 24
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
REQUIRED_LOCAL_SKILLS = (
    "backend-domain-skill-author",
    "django-backend-testing",
    "django-controller",
    "django-dto-mapper",
    "django-migration",
    "django-model-configuration",
    "django-repository",
    "django-service",
)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_py_files(base: Path, *, include_migrations: bool = False) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(base):
        dirs[:] = [
            name
            for name in dirs
            if name not in IGNORED_DIRS and (include_migrations or name != "migrations")
        ]
        files.extend(Path(current) / name for name in names if name.endswith(".py"))
    return files


def parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        ERRORS.append(f"{rel(path)}: invalid Python syntax.")
        return None


def check_module_docstring(path: Path, tree: ast.Module) -> None:
    value = ast.get_docstring(tree, clean=True)
    if value is None:
        ERRORS.append(
            f"{rel(path)}: missing required opening module docstring explaining what this file does."
        )
    elif len(value.strip()) < MIN_MODULE_DOCSTRING_CHARS:
        ERRORS.append(
            f"{rel(path)}: opening module docstring is too vague; describe the file's responsibility and boundary."
        )


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def imports(tree: ast.Module) -> set[str]:
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
        elif isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
    return result


def has_orm_access(tree: ast.Module, imported: set[str]) -> bool:
    if any(name == "django.db" or name.startswith("django.db.") for name in imported):
        return True

    model_symbols: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and (
            node.module.endswith(".models") or ".models." in node.module
        ):
            model_symbols.update(alias.asname or alias.name for alias in node.names)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.endswith(".models") or ".models." in alias.name:
                    model_symbols.add(alias.asname or alias.name.split(".", 1)[0])

    def is_model_manager(node: ast.AST) -> bool:
        if not isinstance(node, ast.Attribute) or node.attr != "objects":
            return False
        owner_path = dotted(node.value)
        owner = owner_path.rsplit(".", 1)[-1]
        root_owner = owner_path.split(".", 1)[0]
        return (bool(owner) and owner[0].isupper()) or root_owner in model_symbols

    return any(
        (is_model_manager(node) or (isinstance(node, ast.Attribute) and dotted(node).endswith("transaction.atomic")))
        or (isinstance(node, ast.Name) and node.id == "QuerySet")
        for node in ast.walk(tree)
    )


def has_persistence_call(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in PERSISTENCE_METHODS
        for node in ast.walk(tree)
    )


def path_has(path: Path, part: str) -> bool:
    return part in path.relative_to(BACKEND).parts


def is_repository(path: Path) -> bool:
    return path_has(path, "repositories") and not path_has(path, "tests")


def is_service(path: Path) -> bool:
    return path_has(path, "services") and not path_has(path, "tests")


def is_model_module(path: Path) -> bool:
    return path.parent.name == "models" and path.name != "__init__.py"


def is_configuration(path: Path) -> bool:
    return path.parent.name == "configurations" and path.name != "__init__.py"


def is_controller(path: Path) -> bool:
    if not path_has(path, "api") or path_has(path, "tests") or path.name == "__init__.py":
        return False
    return path.name in {"controllers.py", "views.py"} or path_has(path, "controllers")


def is_dto(path: Path) -> bool:
    return (path.name == "dtos.py" or path_has(path, "dtos")) and not path_has(path, "tests")


def is_mapper(path: Path) -> bool:
    return path_has(path, "mappers") and not path_has(path, "tests") and not is_repository(path)


def is_test(path: Path) -> bool:
    return path.name.startswith("test_") or path_has(path, "tests")


def imports_models(imported: set[str]) -> bool:
    return any(name == "models" or name.endswith(".models") or ".models." in name for name in imported)


def imports_repositories(imported: set[str]) -> bool:
    return any(name == "repositories" or name.endswith(".repositories") or ".repositories." in name for name in imported)


def check_required_contracts() -> None:
    for name in (
        "backend-plan.md",
        "domain-model.md",
        "api-contract.md",
        "security-contract.md",
        "backend-validation-plan.md",
        "backend-implementation-contract.md",
        "backend-contract-manifest.json",
    ):
        path = ROOT / "docs" / "architecture" / name
        if not path.exists():
            ERRORS.append(f"Missing backend contract: {rel(path)}.")


def check_contract_placeholders() -> None:
    for name in (
        "backend-plan.md",
        "domain-model.md",
        "api-contract.md",
        "security-contract.md",
        "backend-validation-plan.md",
        "backend-implementation-contract.md",
    ):
        path = ROOT / "docs" / "architecture" / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"\{\{|replace[_-]me", text, re.IGNORECASE):
            ERRORS.append(f"{rel(path)}: unresolved contract template value.")


def check_object_shape(
    value: object,
    label: str,
    required: set[str],
    allowed: set[str] | None = None,
) -> bool:
    if not isinstance(value, dict):
        ERRORS.append(f"backend-contract-manifest.json: {label} must be an object.")
        return False
    allowed_keys = allowed or required
    for key in sorted(required - value.keys()):
        ERRORS.append(f"backend-contract-manifest.json: {label} is missing required property {key}.")
    for key in sorted(value.keys() - allowed_keys):
        ERRORS.append(f"backend-contract-manifest.json: {label} has unsupported property {key}.")
    return True


def implementation_contract_version() -> int | None:
    path = ROOT / "docs" / "architecture" / "backend-implementation-contract.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"(?m)^contract_version:\s*([0-9]+)\s*$", text)
    return int(match.group(1)) if match else None


def manifest_object_path(value: str) -> tuple[Path, str] | None:
    parts = value.split(".")
    if len(parts) < 3 or "apps" not in parts:
        return None
    apps_index = parts.index("apps")
    module_parts = parts[apps_index:-1]
    if not module_parts:
        return None
    return BACKEND.joinpath(*module_parts).with_suffix(".py"), parts[-1]


def check_manifest_object(value: object, *, contract_id: str, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        ERRORS.append(f"backend-contract-manifest.json: {contract_id}.{field} must be a dotted path.")
        return
    resolved = manifest_object_path(value)
    if resolved is None:
        ERRORS.append(f"backend-contract-manifest.json: {contract_id}.{field} has an invalid dotted path.")
        return
    path, symbol = resolved
    if not path.is_file():
        ERRORS.append(f"backend-contract-manifest.json: {contract_id}.{field} file does not exist: {rel(path)}.")
        return
    tree = parse(path)
    if tree is None:
        return
    exported = any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == symbol
        for node in tree.body
    )
    if not exported:
        ERRORS.append(f"{rel(path)}: manifest symbol '{symbol}' for {contract_id}.{field} does not exist.")


def test_function_names(files: list[Path]) -> set[str]:
    names: set[str] = set()
    for path in files:
        if not is_test(path):
            continue
        tree = parse(path)
        if tree is None:
            continue
        names.update(
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
    return names


def read_env_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values


def check_environment_binding(binding: dict, services: dict[str, dict]) -> None:
    variable = binding.get("variable")
    target_id = binding.get("target_service")
    expected_url = binding.get("expected_url")
    env_files = binding.get("env_files")
    if not isinstance(variable, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]*", variable):
        ERRORS.append("backend-contract-manifest.json: environment binding has an invalid variable.")
        return
    if target_id not in services:
        ERRORS.append(
            f"backend-contract-manifest.json: {variable} targets unknown service '{target_id}'."
        )
        return
    if not isinstance(env_files, list) or not env_files:
        ERRORS.append(f"backend-contract-manifest.json: {variable} requires env_files.")
        return
    if not isinstance(expected_url, str):
        ERRORS.append(f"backend-contract-manifest.json: {variable} requires expected_url.")
        return
    parsed_expected = urlparse(expected_url)
    if parsed_expected.scheme not in {"http", "https"} or not parsed_expected.hostname:
        ERRORS.append(f"backend-contract-manifest.json: {variable} expected_url must be absolute HTTP(S).")
        return

    target_port = services[target_id].get("local_port")
    for relative in env_files:
        if not isinstance(relative, str):
            ERRORS.append(f"backend-contract-manifest.json: {variable} has an invalid env file path.")
            continue
        env_path = ROOT / relative
        if not env_path.is_file():
            ERRORS.append(f"{relative}: missing environment example required for {variable}.")
            continue
        value = read_env_values(env_path).get(variable)
        if not value:
            ERRORS.append(f"{relative}: missing required environment binding {variable}.")
            continue
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            ERRORS.append(f"{relative}: {variable} must be an absolute HTTP(S) URL.")
            continue
        try:
            actual_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        except ValueError:
            ERRORS.append(f"{relative}: {variable} contains an invalid port.")
            continue
        if isinstance(target_port, int) and actual_port != target_port:
            ERRORS.append(
                f"{relative}: {variable} uses port {actual_port}, but manifest target "
                f"service '{target_id}' uses {target_port}."
            )
        if value.rstrip("/") != expected_url.rstrip("/"):
            ERRORS.append(
                f"{relative}: {variable} is '{value}', but the approved manifest expects "
                f"'{expected_url}'."
            )


def resolved_import_module(node: ast.ImportFrom, url_path: Path) -> str:
    if node.level == 0:
        return node.module or ""
    module_parts = list(url_path.relative_to(BACKEND).with_suffix("").parts[:-1])
    keep = max(0, len(module_parts) - (node.level - 1))
    suffix = (node.module or "").split(".") if node.module else []
    return ".".join(module_parts[:keep] + suffix)


def url_module_name(url_path: Path) -> str:
    return ".".join(url_path.relative_to(BACKEND).with_suffix("").parts)


def import_bindings(tree: ast.Module, url_path: Path) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = resolved_import_module(node, url_path)
            for alias in node.names:
                bindings[alias.asname or alias.name] = f"{module}.{alias.name}" if module else alias.name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                local_name = alias.asname or alias.name.split(".", 1)[0]
                bindings[local_name] = alias.name if alias.asname else local_name
    return bindings


def resolve_bound_name(node: ast.AST, bindings: dict[str, str]) -> str:
    value = dotted(node)
    if not value:
        return ""
    root, *suffix = value.split(".")
    resolved_root = bindings.get(root, root)
    return ".".join([resolved_root, *suffix])


def include_target(node: ast.AST, bindings: dict[str, str]) -> str:
    if not isinstance(node, ast.Call) or dotted(node.func).rsplit(".", 1)[-1] != "include" or not node.args:
        return ""
    target = node.args[0]
    if isinstance(target, ast.Constant) and isinstance(target.value, str):
        return target.value
    return resolve_bound_name(target, bindings)


def join_url_path(prefix: str, route: str) -> str:
    parts = [value.strip("/") for value in (prefix, route) if value.strip("/")]
    return "/".join(parts)


def controller_routes(module_name: str, symbol: str, active_roots: set[str]) -> list[str]:
    modules: set[str] = set()
    includes: dict[str, list[tuple[str, str]]] = {}
    direct_routes: dict[str, list[str]] = {}
    for url_path in BACKEND.rglob("urls.py"):
        tree = parse(url_path)
        if tree is None:
            continue
        current_module = url_module_name(url_path)
        modules.add(current_module)
        bindings = import_bindings(tree, url_path)
        local_names: set[str] = set()
        for node in tree.body:
            if not isinstance(node, ast.ImportFrom) or resolved_import_module(node, url_path) != module_name:
                continue
            local_names.update(alias.asname or alias.name for alias in node.names if alias.name == symbol)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or dotted(node.func).rsplit(".", 1)[-1] not in {"path", "re_path"}:
                continue
            if len(node.args) < 2 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                continue
            route = node.args[0].value
            view = node.args[1]
            target_module = include_target(view, bindings)
            if target_module:
                includes.setdefault(current_module, []).append((route, target_module))
                continue
            if (
                isinstance(view, ast.Call)
                and isinstance(view.func, ast.Attribute)
                and view.func.attr == "as_view"
                and isinstance(view.func.value, ast.Name)
                and view.func.value.id in local_names
            ):
                direct_routes.setdefault(current_module, []).append(route)

    roots = active_roots & modules
    effective_routes: list[str] = []

    def walk(current: str, prefix: str, seen: set[str]) -> None:
        if current in seen:
            return
        next_seen = {*seen, current}
        for route in direct_routes.get(current, []):
            effective_routes.append(join_url_path(prefix, route))
        for route, child in includes.get(current, []):
            if child in modules:
                walk(child, join_url_path(prefix, route), next_seen)

    for root in roots:
        walk(root, "", set())
    return effective_routes


def manifest_path_matches_route(manifest_path: str, route: str) -> bool:
    normalized_manifest = manifest_path.strip("/")
    normalized_route = route.strip("/")
    return normalized_manifest == normalized_route


def check_manifest_controller(
    controller: str,
    declared_methods: set[str],
    endpoint_ids: list[str],
    declared_paths: set[str],
    active_roots: set[str],
) -> None:
    resolved = manifest_object_path(controller)
    if resolved is None:
        ERRORS.append(
            "backend-contract-manifest.json: "
            f"{', '.join(endpoint_ids)} has an invalid Controller path."
        )
        return
    path, symbol = resolved
    if not path.is_file():
        ERRORS.append(
            "backend-contract-manifest.json: "
            f"{', '.join(endpoint_ids)} Controller file does not exist: {rel(path)}."
        )
        return
    tree = parse(path)
    if tree is None:
        return
    controller_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == symbol),
        None,
    )
    if controller_class is None:
        ERRORS.append(f"{rel(path)}: manifest Controller class '{symbol}' does not exist.")
        return
    methods = {
        node.name
        for node in controller_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in HTTP_METHODS
    }
    if methods != declared_methods:
        ERRORS.append(
            f"{rel(path)}:{controller_class.lineno}: manifest endpoint(s) {', '.join(endpoint_ids)} "
            f"declare HTTP methods {sorted(declared_methods)}, found {sorted(methods)}."
        )
    module_name = controller.rsplit(".", 1)[0]
    routes = controller_routes(module_name, symbol, active_roots)
    if not routes:
        ERRORS.append(
            f"{rel(path)}: manifest Controller '{symbol}' is not wired by any urls.py path()."
        )
    else:
        for declared_path in declared_paths:
            if not any(manifest_path_matches_route(declared_path, route) for route in routes):
                ERRORS.append(
                    f"{rel(path)}: manifest path '{declared_path}' for Controller '{symbol}' "
                    f"does not match wired route(s) {sorted(routes)}."
                )


def check_contract_manifest(files: list[Path]) -> None:
    path = ROOT / "docs" / "architecture" / "backend-contract-manifest.json"
    if not path.is_file():
        return
    try:
        raw = path.read_text(encoding="utf-8")
        manifest = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        ERRORS.append(f"{rel(path)}: invalid JSON: {error}.")
        return
    if not isinstance(manifest, dict):
        ERRORS.append(f"{rel(path)}: manifest root must be an object.")
        return
    check_object_shape(
        manifest,
        "manifest",
        {
            "contract_version",
            "status",
            "services",
            "environment_bindings",
            "invariants",
            "endpoints",
            "allowed_execution_commands",
            "required_validations",
        },
        {
            "$schema",
            "contract_version",
            "status",
            "services",
            "environment_bindings",
            "invariants",
            "endpoints",
            "allowed_execution_commands",
            "required_validations",
        },
    )
    if manifest.get("status") != "approved":
        ERRORS.append(f"{rel(path)}: manifest status must be approved before implementation or audit.")
    version = manifest.get("contract_version")
    approved_version = implementation_contract_version()
    if not isinstance(version, int) or version < 1:
        ERRORS.append(f"{rel(path)}: contract_version must be a positive integer.")
    elif approved_version is None or version != approved_version:
        ERRORS.append(f"{rel(path)}: contract_version must match backend-implementation-contract.md.")
    if re.search(r"\{\{|replace[_-]me", raw, re.IGNORECASE):
        ERRORS.append(f"{rel(path)}: unresolved contract template value.")

    services_list = manifest.get("services")
    if not isinstance(services_list, list) or not services_list:
        ERRORS.append(f"{rel(path)}: services must be a non-empty array.")
        services_list = []
    services: dict[str, dict] = {}
    manifest_root_urlconfs: set[str] = set()
    for service in services_list:
        if not check_object_shape(service, "service", {"id", "runtime", "local_port", "root_urlconf"}):
            continue
        if not isinstance(service.get("id"), str) or not re.fullmatch(r"[a-z][a-z0-9_-]*", service["id"]):
            ERRORS.append(f"{rel(path)}: every service requires a string id.")
            continue
        service_id = service["id"]
        if service_id in services:
            ERRORS.append(f"{rel(path)}: duplicate service id {service_id}.")
        services[service_id] = service
        if not isinstance(service.get("runtime"), str) or not service["runtime"].strip():
            ERRORS.append(f"{rel(path)}: service {service_id} requires a non-empty runtime.")
        elif "django" in service["runtime"].lower():
            root_urlconf = service.get("root_urlconf")
            if not isinstance(root_urlconf, str) or not re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_.]*\.urls",
                root_urlconf,
            ):
                ERRORS.append(f"{rel(path)}: Django service {service_id} requires root_urlconf.")
            else:
                manifest_root_urlconfs.add(root_urlconf)
        elif service.get("root_urlconf") is not None:
            ERRORS.append(f"{rel(path)}: non-Django service {service_id} must use root_urlconf null.")
        port = service.get("local_port")
        if port is not None and (not isinstance(port, int) or not 1 <= port <= 65535):
            ERRORS.append(f"{rel(path)}: service {service_id} has an invalid local_port.")

    configured_root_urlconfs: list[tuple[Path, str]] = []
    for settings_path in files:
        relative_parts = settings_path.relative_to(BACKEND).parts
        if settings_path.name != "settings.py" and "settings" not in relative_parts[:-1]:
            continue
        tree = parse(settings_path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            value: ast.AST | None = None
            targets: list[ast.AST] = []
            if isinstance(node, ast.Assign):
                value = node.value
                targets = node.targets
            elif isinstance(node, ast.AnnAssign):
                value = node.value
                targets = [node.target]
            if (
                value is not None
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
                and any(isinstance(target, ast.Name) and target.id == "ROOT_URLCONF" for target in targets)
            ):
                configured_root_urlconfs.append((settings_path, value.value))
    if manifest_root_urlconfs and not configured_root_urlconfs:
        ERRORS.append(f"{rel(path)}: no literal ROOT_URLCONF setting matches the manifest.")
    for settings_path, configured in configured_root_urlconfs:
        if configured not in manifest_root_urlconfs:
            ERRORS.append(
                f"{rel(settings_path)}: ROOT_URLCONF '{configured}' is absent from manifest Django services."
            )

    bindings = manifest.get("environment_bindings", [])
    if not isinstance(bindings, list):
        ERRORS.append(f"{rel(path)}: environment_bindings must be an array.")
    else:
        for binding in bindings:
            if not check_object_shape(
                binding,
                "environment binding",
                {"variable", "target_service", "url_role", "expected_url", "env_files"},
            ):
                continue
            if binding.get("url_role") not in {"base_url", "callback_url", "public_url", "internal_url"}:
                ERRORS.append(f"{rel(path)}: environment binding has an invalid url_role.")
            check_environment_binding(binding, services)

    names = test_function_names(files)
    invariants = manifest.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        ERRORS.append(f"{rel(path)}: invariants must be a non-empty array.")
        invariants = []
    seen_ids: set[str] = set()
    for invariant in invariants:
        if not check_object_shape(invariant, "invariant", {"id", "statement", "enforcement", "required_tests"}):
            continue
        if not isinstance(invariant.get("id"), str) or not re.fullmatch(r"[A-Z][A-Z0-9_-]*-[0-9]{3}", invariant["id"]):
            ERRORS.append(f"{rel(path)}: every invariant requires a string id.")
            continue
        invariant_id = invariant["id"]
        if invariant_id in seen_ids:
            ERRORS.append(f"{rel(path)}: duplicate contract id {invariant_id}.")
        seen_ids.add(invariant_id)
        if not isinstance(invariant.get("statement"), str) or len(invariant["statement"]) < 12:
            ERRORS.append(f"{rel(path)}: invariant {invariant_id} needs a meaningful statement.")
        enforcement = invariant.get("enforcement")
        if not isinstance(enforcement, list) or not enforcement:
            ERRORS.append(f"{rel(path)}: invariant {invariant_id} requires enforcement paths.")
        else:
            for value in enforcement:
                check_manifest_object(value, contract_id=invariant_id, field="enforcement")
        required_tests = invariant.get("required_tests")
        if not isinstance(required_tests, list) or not required_tests:
            ERRORS.append(f"{rel(path)}: invariant {invariant_id} requires exact test names.")
            continue
        for name in required_tests:
            if not isinstance(name, str) or not name.startswith("test_"):
                ERRORS.append(f"{rel(path)}: invariant {invariant_id} has an invalid test name.")
            elif name not in names:
                ERRORS.append(f"{rel(path)}: invariant {invariant_id} is missing required test {name}.")

    endpoints = manifest.get("endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        ERRORS.append(f"{rel(path)}: endpoints must be a non-empty array.")
        endpoints = []
    controller_groups: dict[str, tuple[set[str], list[str], set[str]]] = {}
    for endpoint in endpoints:
        if not check_object_shape(
            endpoint,
            "endpoint",
            {"id", "method", "path", "controller", "request_dto", "response_dto", "mapper", "service", "repositories", "required_tests"},
        ):
            continue
        if not isinstance(endpoint.get("id"), str) or not re.fullmatch(r"API-[0-9]{3}", endpoint["id"]):
            ERRORS.append(f"{rel(path)}: every endpoint requires a string id.")
            continue
        endpoint_id = endpoint["id"]
        if endpoint_id in seen_ids:
            ERRORS.append(f"{rel(path)}: duplicate contract id {endpoint_id}.")
        seen_ids.add(endpoint_id)
        controller = endpoint.get("controller")
        method = endpoint.get("method")
        if not isinstance(controller, str):
            ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} requires a Controller class path.")
            continue
        if method not in {value.upper() for value in HTTP_METHODS}:
            ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} has an invalid HTTP method.")
            continue
        if not isinstance(endpoint.get("path"), str) or not endpoint["path"].startswith("/"):
            ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} has an invalid path.")
            continue
        methods, ids, paths = controller_groups.setdefault(controller, (set(), [], set()))
        if method.lower() in methods:
            ERRORS.append(
                f"{rel(path)}: Controller {controller} has duplicate manifest method {method}."
            )
        methods.add(method.lower())
        ids.append(endpoint_id)
        if isinstance(endpoint.get("path"), str):
            paths.add(endpoint["path"])
        for field in ("request_dto", "response_dto", "mapper", "service"):
            check_manifest_object(endpoint.get(field), contract_id=endpoint_id, field=field)
        repositories = endpoint.get("repositories")
        if not isinstance(repositories, list):
            ERRORS.append(f"{rel(path)}: endpoint {endpoint_id}.repositories must be an array.")
        else:
            for value in repositories:
                check_manifest_object(value, contract_id=endpoint_id, field="repositories")
        endpoint_tests = endpoint.get("required_tests")
        if not isinstance(endpoint_tests, list) or not endpoint_tests:
            ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} requires exact test names.")
        else:
            for name in endpoint_tests:
                if not isinstance(name, str) or not re.fullmatch(r"test_[a-z0-9_]+", name):
                    ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} has an invalid test name.")
                elif name not in names:
                    ERRORS.append(f"{rel(path)}: endpoint {endpoint_id} is missing required test {name}.")

    for controller, (methods, ids, paths) in controller_groups.items():
        if len(paths) > 1:
            ERRORS.append(
                f"{rel(path)}: shared Controller {controller} spans multiple URL paths {sorted(paths)}; "
                "use a separate use-case/resource Controller."
            )
        check_manifest_controller(controller, methods, ids, paths, manifest_root_urlconfs)

    allowed_commands = manifest.get("allowed_execution_commands")
    if not isinstance(allowed_commands, list):
        ERRORS.append(f"{rel(path)}: allowed_execution_commands must be an array.")
    else:
        for command in allowed_commands:
            if (
                not isinstance(command, str)
                or not re.fullmatch(
                    r"(?:python3?|py) manage\.py makemigrations(?: [A-Za-z0-9_.=:/-]+)+",
                    command,
                )
                or re.search(r"[;&|><`\r\n]|\$\(", command)
            ):
                ERRORS.append(
                    f"{rel(path)}: allowed_execution_commands may contain only exact, "
                    "non-compound Django makemigrations commands."
                )

    validations = manifest.get("required_validations")
    if not isinstance(validations, list) or not validations:
        ERRORS.append(f"{rel(path)}: required_validations must be a non-empty array.")
    else:
        validation_ids: set[str] = set()
        validation_commands: set[str] = set()
        for validation in validations:
            if not check_object_shape(validation, "validation", {"id", "kind", "command", "required"}):
                continue
            validation_id = validation.get("id")
            if not isinstance(validation_id, str) or not re.fullmatch(r"VAL-[0-9]{3}", validation_id):
                ERRORS.append(f"{rel(path)}: every required validation needs an id.")
            elif validation_id in validation_ids:
                ERRORS.append(f"{rel(path)}: duplicate validation id {validation_id}.")
            else:
                validation_ids.add(validation_id)
            if validation.get("kind") not in {"check", "test", "scan", "migration", "integration", "browser"}:
                ERRORS.append(f"{rel(path)}: validation {validation_id} has an invalid kind.")
            if not isinstance(validation.get("command"), str) or not validation["command"].strip():
                ERRORS.append(f"{rel(path)}: validation {validation_id} requires a command.")
            elif re.search(r"[;&|><`\r\n]|\$\(", validation["command"]):
                ERRORS.append(f"{rel(path)}: validation {validation_id} command contains shell control operators.")
            else:
                validation_commands.add(validation["command"].strip())
            if not isinstance(validation.get("required"), bool):
                ERRORS.append(f"{rel(path)}: validation {validation_id} requires a boolean required flag.")

        plan_path = ROOT / "docs" / "architecture" / "backend-validation-plan.md"
        if plan_path.is_file():
            plan_text = plan_path.read_text(encoding="utf-8", errors="ignore")
            planned_commands = {
                line.strip()
                for block in re.findall(r"```(?:bash|powershell)\s*\n([\s\S]*?)```", plan_text, re.IGNORECASE)
                for line in block.splitlines()
                if line.strip() and not line.strip().startswith("#")
            }
            for command in sorted(validation_commands - planned_commands):
                ERRORS.append(f"{rel(plan_path)}: missing manifest command: {command}.")
            for command in sorted(planned_commands - validation_commands):
                ERRORS.append(f"{rel(plan_path)}: command absent from manifest: {command}.")


def check_project_context() -> None:
    required = (
        ".codex/references/backend-architecture.md",
        ".codex/references/domain-boundaries.md",
        ".codex/references/domain-skill-policy.md",
        ".codex/references/mapping-policy.md",
        ".codex/references/module-documentation.md",
        ".codex/references/migration-policy.md",
        ".codex/references/repository-policy.md",
        ".codex/workflows/backend-validation.md",
        ".codex/checklists/backend-validation.md",
    )
    for value in required:
        if not (ROOT / value).exists():
            WARNINGS.append(f"Missing resolved backend project context: {value}.")


def skill_frontmatter(path: Path, text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        ERRORS.append(f"{rel(path)}: skill must start with YAML frontmatter.")
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        ERRORS.append(f"{rel(path)}: skill frontmatter is not closed.")
        return None

    values: dict[str, str] = {}
    for line in lines[1:end]:
        match = re.fullmatch(r"([a-z_]+):\s*(.+)", line.strip())
        if not match:
            ERRORS.append(f"{rel(path)}: skill frontmatter must use simple name and description fields.")
            return None
        values[match.group(1)] = match.group(2).strip().strip('"\'')
    return values


def check_project_skills() -> None:
    root = ROOT / ".agents" / "skills"
    if not root.is_dir():
        ERRORS.append("Missing project-local backend architecture skill kit: .agents/skills/.")
        return

    for name in REQUIRED_LOCAL_SKILLS:
        if not (root / name).is_dir():
            ERRORS.append(f"Missing required project-local backend skill: .agents/skills/{name}/.")

    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        skill_path = directory / "SKILL.md"
        agent_path = directory / "agents" / "openai.yaml"
        if not skill_path.is_file():
            ERRORS.append(f"{rel(directory)}: project-local skill requires SKILL.md.")
            continue

        text = skill_path.read_text(encoding="utf-8", errors="ignore")
        if "TODO" in text:
            ERRORS.append(f"{rel(skill_path)}: project-local skill contains unresolved TODO placeholders.")
        values = skill_frontmatter(skill_path, text)
        if values is not None:
            unexpected = set(values) - {"name", "description"}
            if unexpected or set(values) != {"name", "description"}:
                ERRORS.append(f"{rel(skill_path)}: frontmatter must contain only name and description.")
            if values.get("name") != directory.name:
                ERRORS.append(f"{rel(skill_path)}: skill name must match directory '{directory.name}'.")
            if len(values.get("description", "")) < 40:
                ERRORS.append(f"{rel(skill_path)}: skill description must explain capability and triggers.")
        if "docs/architecture/backend-implementation-contract.md" not in text:
            ERRORS.append(f"{rel(skill_path)}: skill must defer to the approved implementation contract.")
        if ".codex/" not in text:
            ERRORS.append(f"{rel(skill_path)}: skill must read project-local .codex context.")

        if not agent_path.is_file():
            ERRORS.append(f"{rel(directory)}: project-local skill requires agents/openai.yaml.")
        else:
            agent_text = agent_path.read_text(encoding="utf-8", errors="ignore")
            if f"${directory.name}" not in agent_text:
                ERRORS.append(f"{rel(agent_path)}: default_prompt must explicitly invoke ${directory.name}.")


def model_classes(tree: ast.Module) -> list[ast.ClassDef]:
    return [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and any(dotted(base).endswith("Model") for base in node.bases)
    ]


def model_app_dir(path: Path) -> Path:
    return path.parent.parent if path.parent.name == "models" else path.parent


def check_model_file(path: Path, tree: ast.Module, imported: set[str]) -> None:
    classes = model_classes(tree)
    if not classes:
        return

    app_dir = model_app_dir(path)
    if not is_model_module(path):
        ERRORS.append(f"{rel(path)}: ORM Models must live one-per-module under models/; aggregate models.py is forbidden.")
    if len(classes) != 1:
        ERRORS.append(f"{rel(path)}: expected exactly one ORM Model per module, found {len(classes)}.")

    configuration_path = app_dir / "configurations" / f"{path.stem}.py"
    if not configuration_path.exists():
        ERRORS.append(
            f"{rel(path)}: missing matching configuration module "
            f"{configuration_path.relative_to(app_dir).as_posix()}."
        )
    if not any("configurations" in name for name in imported):
        ERRORS.append(f"{rel(path)}: Model must import specifications from its matching configurations/ module.")

    for node in classes:
        if not CAMEL_CASE.fullmatch(node.name):
            ERRORS.append(f"{rel(path)}:{node.lineno}: ORM Model '{node.name}' is not CamelCase.")
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name != "__str__":
                ERRORS.append(
                    f"{rel(path)}:{child.lineno}: ORM Model '{node.name}' contains non-entity method "
                    f"'{child.name}'."
                )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg in MODEL_SPEC_KEYWORDS and isinstance(keyword.value, ast.Constant):
                ERRORS.append(
                    f"{rel(path)}:{node.lineno}: literal {keyword.arg} belongs in the matching configurations/ module."
                )


def check_layer_file(path: Path, tree: ast.Module, imported: set[str]) -> None:
    normalized = rel(path)
    orm_access = has_orm_access(tree, imported)

    if is_repository(path):
        if "contracts" in path.stem and orm_access:
            ERRORS.append(f"{normalized}: repository contracts must not depend on Django ORM.")
        if path.stem in {"mapper", "mappers"} and (orm_access or has_persistence_call(tree)):
            ERRORS.append(f"{normalized}: repository mapper may transform ORM objects but must not query or persist.")
        return

    exempt = is_model_module(path) or is_configuration(path) or path.name in {"admin.py", "apps.py"} or is_test(path)
    if orm_access and not exempt:
        ERRORS.append(f"{normalized}: ORM/database access is exclusive to repositories.")
    if has_persistence_call(tree) and not exempt:
        ERRORS.append(f"{normalized}: persistence calls are exclusive to repositories.")

    if is_service(path):
        if any(
            name == "django.http"
            or name.startswith("django.http.")
            or name.startswith("rest_framework")
            or ".api" in name
            for name in imported
        ):
            ERRORS.append(f"{normalized}: Service imports endpoint/HTTP code.")
        if imports_models(imported):
            ERRORS.append(f"{normalized}: Service imports ORM Models directly.")
        if any(name == "mappers" or name.endswith(".mappers") or ".mappers." in name for name in imported):
            ERRORS.append(f"{normalized}: Service must not depend on Controller/application mappers.")

    if is_controller(path):
        if path.name == "views.py":
            WARNINGS.append(f"{normalized}: prefer api/controllers/<use_case>.py for the Controller layer.")
        if imports_repositories(imported) or imports_models(imported):
            ERRORS.append(f"{normalized}: Controller must not import repositories or ORM Models.")
        text = path.read_text(encoding="utf-8", errors="ignore")
        uses_request_payload = "request.data" in text or "request.query_params" in text
        uses_dto = any(name == "dtos" or name.endswith(".dtos") or ".dtos." in name for name in imported)
        uses_mapper = any(name == "mappers" or name.endswith(".mappers") or ".mappers." in name for name in imported)
        if uses_request_payload and not uses_dto:
            ERRORS.append(f"{normalized}: Controller payload must be defined and validated by a DTO.")
        if uses_request_payload and not uses_mapper:
            ERRORS.append(f"{normalized}: Controller must delegate representation mapping to an explicit mapper.")

    if is_dto(path) and (imports_repositories(imported) or imports_models(imported)):
        ERRORS.append(f"{normalized}: DTO must not import repositories or ORM Models.")

    if is_mapper(path):
        if orm_access or imports_repositories(imported) or imports_models(imported):
            ERRORS.append(f"{normalized}: application mapper must not import or access persistence.")
        if any(name.startswith("rest_framework") or ".services" in name for name in imported):
            ERRORS.append(f"{normalized}: application mapper must depend on DTO types, not HTTP or Service implementations.")


def require_package(path: Path, app_dir: Path) -> None:
    if not path.is_dir():
        ERRORS.append(f"{rel(app_dir)}: missing required package {path.relative_to(app_dir).as_posix()}/.")
    elif not (path / "__init__.py").exists():
        ERRORS.append(f"{rel(path)}: Python package requires __init__.py.")


def check_app_shape(files: list[Path]) -> None:
    app_dirs: set[Path] = set()
    model_modules: dict[Path, list[Path]] = {}

    for path in files:
        tree = parse(path)
        if tree is None or not model_classes(tree):
            continue
        app_dir = model_app_dir(path)
        app_dirs.add(app_dir)
        model_modules.setdefault(app_dir, []).append(path)

    for app_dir in sorted(app_dirs):
        for package in (
            app_dir / "configurations",
            app_dir / "models",
            app_dir / "dtos",
            app_dir / "mappers",
            app_dir / "repositories",
            app_dir / "services",
            app_dir / "api",
            app_dir / "api" / "controllers",
            app_dir / "tests",
            app_dir / "migrations",
        ):
            require_package(package, app_dir)

        for test_layer in ("dtos", "mappers", "repositories", "services", "api"):
            layer = app_dir / "tests" / test_layer
            if not layer.is_dir():
                ERRORS.append(f"{rel(app_dir)}: missing layered test directory tests/{test_layer}/.")

        for legacy in (
            app_dir / "models.py",
            app_dir / "configurations.py",
            app_dir / "dtos.py",
            app_dir / "api" / "controllers.py",
        ):
            if legacy.exists():
                ERRORS.append(f"{rel(legacy)}: aggregate layer file is forbidden; use the corresponding package.")

        models_init = app_dir / "models" / "__init__.py"
        init_text = models_init.read_text(encoding="utf-8", errors="ignore") if models_init.exists() else ""
        for module in model_modules.get(app_dir, []):
            if module.parent.name != "models":
                continue
            pattern = rf"from\s+\.{re.escape(module.stem)}\s+import\s+"
            if not re.search(pattern, init_text):
                ERRORS.append(
                    f"{rel(models_init)}: explicitly import ORM Model(s) from .{module.stem} for Django discovery."
                )

        selectors = app_dir / "selectors"
        if selectors.exists():
            ERRORS.append(f"{rel(selectors)}: selectors are not allowed; move reads into repositories.")


def check_migration_provenance() -> None:
    for path in iter_py_files(BACKEND, include_migrations=True):
        if "migrations" not in path.parts or path.name == "__init__.py":
            continue
        header = "\n".join(path.read_text(encoding="utf-8", errors="ignore").splitlines()[:5])
        if "Generated by Django" not in header:
            ERRORS.append(f"{rel(path)}: migration lacks Django-generated provenance; do not handwrite migrations.")


def main() -> int:
    print("Django backend boundary scan")
    print("============================")
    files = iter_py_files(BACKEND) if BACKEND.exists() else []
    if not BACKEND.exists():
        ERRORS.append("Backend directory does not exist.")

    check_required_contracts()
    check_contract_placeholders()
    check_contract_manifest(files)
    check_project_context()
    check_project_skills()
    check_app_shape(files)
    check_migration_provenance()

    for path in files:
        tree = parse(path)
        if tree is None:
            continue
        check_module_docstring(path, tree)
        imported = imports(tree)
        if model_classes(tree):
            check_model_file(path, tree, imported)
        check_layer_file(path, tree, imported)

    for warning in WARNINGS:
        print(f"warning: {warning}")
    for error in ERRORS:
        print(f"error: {error}")

    if ERRORS:
        print(f"failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s)")
        return 1
    if WARNINGS:
        print(f"ok with warnings: {len(WARNINGS)} warning(s)")
        return 0
    print("ok: no architecture boundary violations found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
