#!/usr/bin/env python3
"""Exercise both Django architecture scanners against valid and invalid fixtures."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FACTORY_ROOT = SCRIPT_DIR.parents[2]
SCANNERS = (
    SCRIPT_DIR / "scan-django-architecture.py",
    FACTORY_ROOT / "skills" / "django-backend-code-executor" / "scripts" / "scan-django-boundaries.py",
)
LOCAL_SKILLS = (
    "backend-domain-skill-author",
    "django-backend-testing",
    "django-controller",
    "django-dto-mapper",
    "django-migration",
    "django-model-configuration",
    "django-repository",
    "django-service",
)


def write(root: Path, relative: str, content: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".py" and "migrations" not in path.parts:
        stripped = content.lstrip()
        if not stripped.startswith(('"""', "'''")):
            purpose = relative.replace("/", " ").replace("_", " ")
            content = f'"""Exercise the {purpose} responsibility in the scanner fixture."""\n\n{content}'
    path.write_text(content, encoding="utf-8")


def write_local_skill(root: Path, name: str) -> None:
    write(
        root,
        f".agents/skills/{name}/SKILL.md",
        "---\n"
        f"name: {name}\n"
        f"description: Exercise the approved {name} capability when its project-local backend workflow is required.\n"
        "---\n\n"
        f"# {name}\n\n"
        "Read docs/architecture/backend-implementation-contract.md and relevant .codex/references/ before work.\n",
    )
    write(
        root,
        f".agents/skills/{name}/agents/openai.yaml",
        "interface:\n"
        f"  display_name: \"{name}\"\n"
        '  short_description: "Exercise a project backend capability"\n'
        f'  default_prompt: "Use ${name} for the approved project workflow."\n',
    )


def build_fixture(root: Path) -> None:
    for name in (
        "backend-plan.md",
        "domain-model.md",
        "api-contract.md",
        "security-contract.md",
        "backend-validation-plan.md",
        "backend-implementation-contract.md",
    ):
        write(root, f"docs/architecture/{name}", f"# {name}\n")
    write(
        root,
        "docs/architecture/backend-implementation-contract.md",
        "---\nstatus: approved\ncontract_version: 1\napproved_at: 2026-07-13\n---\n\n"
        "# Backend implementation contract\n",
    )
    write(
        root,
        "docs/architecture/backend-validation-plan.md",
        "# Backend validation plan\n\n```bash\npython manage.py test\n```\n",
    )
    write(
        root,
        "docs/architecture/backend-contract-manifest.json",
        json.dumps(
            {
                "contract_version": 1,
                "status": "approved",
                "services": [
                    {
                        "id": "django",
                        "runtime": "django",
                        "local_port": 8000,
                        "root_urlconf": "config.urls",
                    }
                ],
                "environment_bindings": [
                    {
                        "variable": "DJANGO_PUBLIC_URL",
                        "target_service": "django",
                        "url_role": "public_url",
                        "expected_url": "http://127.0.0.1:8000",
                        "env_files": ["backend/.env.example"],
                    }
                ],
                "invariants": [
                    {
                        "id": "BR-001",
                        "statement": "Every order requires a non-empty name.",
                        "enforcement": ["apps.orders.services.create_order.CreateOrderService"],
                        "required_tests": ["test_order_name_is_required"],
                    }
                ],
                "endpoints": [
                    {
                        "id": "API-001",
                        "method": "POST",
                        "path": "/api/orders/",
                        "controller": (
                            "apps.orders.api.controllers.create_order.CreateOrderController"
                        ),
                        "request_dto": "apps.orders.dtos.create_order.CreateOrderRequestDTO",
                        "response_dto": None,
                        "mapper": "apps.orders.mappers.create_order.to_service_input",
                        "service": "apps.orders.services.create_order.CreateOrderService",
                        "repositories": ["apps.orders.repositories.contracts.OrderRepository"],
                        "required_tests": ["test_create_order_endpoint_contract"],
                    }
                ],
                "allowed_execution_commands": ["python manage.py makemigrations orders"],
                "required_validations": [
                    {
                        "id": "VAL-001",
                        "kind": "test",
                        "command": "python manage.py test",
                        "required": True,
                    }
                ],
            },
            indent=2,
        )
        + "\n",
    )

    for relative in (
        ".codex/references/backend-architecture.md",
        ".codex/references/domain-boundaries.md",
        ".codex/references/domain-skill-policy.md",
        ".codex/references/mapping-policy.md",
        ".codex/references/module-documentation.md",
        ".codex/references/migration-policy.md",
        ".codex/references/repository-policy.md",
        ".codex/workflows/backend-validation.md",
        ".codex/checklists/backend-validation.md",
    ):
        write(root, relative, "# Context\n")

    for name in LOCAL_SKILLS:
        write_local_skill(root, name)
    write_local_skill(root, "order-lifecycle")

    app = "backend/apps/orders"
    for package in (
        "configurations",
        "models",
        "dtos",
        "mappers",
        "repositories",
        "services",
        "api",
        "api/controllers",
        "tests",
        "migrations",
    ):
        write(root, f"{app}/{package}/__init__.py")
    for layer in ("dtos", "mappers", "repositories", "services", "api"):
        write(root, f"{app}/tests/{layer}/__init__.py")

    write(
        root,
        f"{app}/configurations/order.py",
        "class OrderConfiguration:\n"
        "    NAME_MAX_LENGTH = 120\n"
        "    TABLE_NAME = 'orders'\n",
    )
    write(
        root,
        f"{app}/models/order.py",
        "from django.db import models\n"
        "from apps.orders.configurations.order import OrderConfiguration\n\n"
        "class Order(models.Model):\n"
        "    name = models.CharField(max_length=OrderConfiguration.NAME_MAX_LENGTH)\n\n"
        "    class Meta:\n"
        "        db_table = OrderConfiguration.TABLE_NAME\n",
    )
    write(root, f"{app}/models/__init__.py", "from .order import Order\n\n__all__ = ['Order']\n")
    write(
        root,
        f"{app}/dtos/create_order.py",
        "from dataclasses import dataclass\n\n"
        "@dataclass(frozen=True)\n"
        "class CreateOrderRequestDTO:\n"
        "    name: str\n\n"
        "@dataclass(frozen=True)\n"
        "class CreateOrderInput:\n"
        "    name: str\n",
    )
    write(
        root,
        f"{app}/mappers/create_order.py",
        "from apps.orders.dtos.create_order import CreateOrderInput, CreateOrderRequestDTO\n\n"
        "def to_service_input(payload: CreateOrderRequestDTO) -> CreateOrderInput:\n"
        "    return CreateOrderInput(name=payload.name)\n",
    )
    write(
        root,
        f"{app}/repositories/contracts.py",
        "from typing import Protocol\n\n"
        "class OrderRepository(Protocol):\n"
        "    def create(self, *, name: str) -> object: ...\n",
    )
    write(
        root,
        f"{app}/repositories/mappers.py",
        "from apps.orders.models.order import Order\n\n"
        "def to_record(instance: Order) -> dict[str, object]:\n"
        "    return {'id': instance.pk, 'name': instance.name}\n",
    )
    write(
        root,
        f"{app}/repositories/django_repository.py",
        "from apps.orders.models.order import Order\n\n"
        "class DjangoOrderRepository:\n"
        "    def create(self, *, name: str) -> Order:\n"
        "        return Order.objects.create(name=name)\n",
    )
    write(
        root,
        f"{app}/services/create_order.py",
        "from apps.orders.dtos.create_order import CreateOrderInput\n"
        "from apps.orders.repositories.contracts import OrderRepository\n\n"
        "class CreateOrderService:\n"
        "    def __init__(self, repository: OrderRepository) -> None:\n"
        "        self._repository = repository\n\n"
        "    def execute(self, payload: CreateOrderInput) -> object:\n"
        "        return self._repository.create(name=payload.name)\n",
    )
    write(
        root,
        f"{app}/api/controllers/create_order.py",
        "from apps.orders.dtos.create_order import CreateOrderRequestDTO\n"
        "from apps.orders.mappers.create_order import to_service_input\n"
        "from apps.orders.services.create_order import CreateOrderService\n\n"
        "class CreateOrderController:\n"
        "    def post(self, request, service: CreateOrderService):\n"
        "        payload = CreateOrderRequestDTO(**request.data)\n"
        "        return service.execute(to_service_input(payload))\n",
    )
    write(root, f"{app}/api/permissions.py")
    write(
        root,
        f"{app}/api/urls.py",
        "from django.urls import path\n"
        "from apps.orders.api.controllers.create_order import CreateOrderController\n\n"
        "urlpatterns = [path('orders/', CreateOrderController.as_view())]\n",
    )
    write(root, f"{app}/composition.py")
    write(
        root,
        f"{app}/tests/services/test_create_order.py",
        "def test_order_name_is_required():\n"
        "    assert True\n",
    )
    write(
        root,
        f"{app}/tests/api/test_create_order.py",
        "def test_create_order_endpoint_contract():\n"
        "    assert True\n",
    )
    write(root, f"{app}/migrations/0001_initial.py", "# Generated by Django 5.0 on 2026-07-13\n")
    write(root, "backend/.env.example", "DJANGO_PUBLIC_URL=http://127.0.0.1:8000\n")
    write(root, "backend/config/__init__.py")
    write(root, "backend/config/settings.py", "ROOT_URLCONF = 'config.urls'\n")
    write(
        root,
        "backend/config/urls.py",
        "from django.urls import include, path\n\n"
        "urlpatterns = [path('api/', include('apps.orders.api.urls'))]\n",
    )


def run(scanner: Path, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(scanner)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def main() -> int:
    executor_scanner = FACTORY_ROOT / "skills" / "django-backend-code-executor" / "scripts" / "_boundary_scanner.py"
    if SCRIPT_DIR.joinpath("scan-django-architecture.py").read_bytes() != executor_scanner.read_bytes():
        raise AssertionError("architect and executor scanner implementations have drifted")

    with tempfile.TemporaryDirectory(prefix="karya-django-scan-") as value:
        root = Path(value)
        build_fixture(root)

        for scanner in SCANNERS:
            result = run(scanner, root)
            if result.returncode != 0:
                raise AssertionError(f"valid scalable fixture failed {scanner}:\n{result.stdout}\n{result.stderr}")

        manifest_path = root / "docs/architecture/backend-contract-manifest.json"
        manifest_text = manifest_path.read_text(encoding="utf-8")
        shared_manifest = json.loads(manifest_text)
        shared_endpoint = dict(shared_manifest["endpoints"][0])
        shared_endpoint.update({"id": "API-002", "method": "GET", "request_dto": None})
        shared_manifest["endpoints"].append(shared_endpoint)
        manifest_path.write_text(json.dumps(shared_manifest, indent=2) + "\n", encoding="utf-8")
        shared_controller = root / "backend/apps/orders/api/controllers/create_order.py"
        shared_controller_text = shared_controller.read_text(encoding="utf-8")
        shared_controller.write_text(
            shared_controller_text.replace(
                "class CreateOrderController:\n",
                "class CreateOrderController:\n    def get(self, request):\n        return None\n\n",
            ),
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode != 0:
            raise AssertionError(f"explicit same-route Controller method grouping failed:\n{result.stdout}")
        manifest_path.write_text(manifest_text, encoding="utf-8")
        shared_controller.write_text(shared_controller_text, encoding="utf-8")

        env_example = root / "backend/.env.example"
        env_example.write_text("DJANGO_PUBLIC_URL=http://127.0.0.1:8001\n", encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "uses port 8001" not in result.stdout:
            raise AssertionError(f"reversed service port was not rejected:\n{result.stdout}")
        env_example.write_text("DJANGO_PUBLIC_URL=http://127.0.0.1:8000\n", encoding="utf-8")

        env_example.write_text("DJANGO_PUBLIC_URL=http://wrong-service.example:8000\n", encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "approved manifest expects" not in result.stdout:
            raise AssertionError(f"wrong environment hostname was not rejected:\n{result.stdout}")
        env_example.write_text("DJANGO_PUBLIC_URL=http://127.0.0.1:8000\n", encoding="utf-8")

        urls = root / "backend/apps/orders/api/urls.py"
        urls_text = urls.read_text(encoding="utf-8")
        write(root, "backend/apps/orders/api/urls.py")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "not wired by any urls.py path()" not in result.stdout:
            raise AssertionError(f"unwired manifest Controller was not rejected:\n{result.stdout}")
        urls.write_text(urls_text, encoding="utf-8")

        root_urls = root / "backend/config/urls.py"
        root_urls_text = root_urls.read_text(encoding="utf-8")
        root_urls.write_text(root_urls_text.replace("path('api/'", "path('wrong/'"), encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "does not match wired route" not in result.stdout:
            raise AssertionError(f"wrong root include URL prefix was not rejected:\n{result.stdout}")
        root_urls.write_text(root_urls_text, encoding="utf-8")

        write(root, "backend/alt/__init__.py")
        write(
            root,
            "backend/alt/urls.py",
            "from django.urls import include, path\n\n"
            "urlpatterns = [path('wrong/', include('apps.orders.api.urls'))]\n",
        )
        settings = root / "backend/config/settings.py"
        settings_text = settings.read_text(encoding="utf-8")
        settings.write_text(settings_text.replace("config.urls", "alt.urls"), encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "ROOT_URLCONF 'alt.urls' is absent from manifest" not in result.stdout:
            raise AssertionError(f"inactive manifest URLconf was accepted:\n{result.stdout}")
        settings.write_text(settings_text, encoding="utf-8")

        relative_urls_text = urls_text.replace(
            "from apps.orders.api.controllers.create_order import CreateOrderController",
            "from .controllers.create_order import CreateOrderController",
        )
        urls.write_text(relative_urls_text, encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode != 0:
            raise AssertionError(f"relative Controller import was not resolved:\n{result.stdout}")
        urls.write_text(urls_text, encoding="utf-8")

        urls.write_text(urls_text.replace("path('orders/'", "path('wrong/'"), encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "does not match wired route" not in result.stdout:
            raise AssertionError(f"wrong manifest URL path was not rejected:\n{result.stdout}")
        urls.write_text(urls_text, encoding="utf-8")

        invariant_test = root / "backend/apps/orders/tests/services/test_create_order.py"
        invariant_test.unlink()
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "missing required test test_order_name_is_required" not in result.stdout:
            raise AssertionError(f"missing invariant test was not rejected:\n{result.stdout}")
        write(
            root,
            "backend/apps/orders/tests/services/test_create_order.py",
            "def test_order_name_is_required():\n    assert True\n",
        )

        controller = root / "backend/apps/orders/api/controllers/create_order.py"
        controller_text = controller.read_text(encoding="utf-8")
        controller.write_text(
            controller_text.replace(
                "class CreateOrderController:\n",
                "class CreateOrderController:\n    def get(self, request):\n        return None\n\n",
            ),
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "declare HTTP methods ['post'], found ['get', 'post']" not in result.stdout:
            raise AssertionError(f"uncontracted Controller method was not rejected:\n{result.stdout}")
        controller.write_text(controller_text, encoding="utf-8")

        service = root / "backend/apps/orders/services/create_order.py"
        service_text = service.read_text(encoding="utf-8")
        service.write_text(
            service_text.replace(
                "from apps.orders.dtos.create_order import CreateOrderInput\n",
                "from django.http import HttpResponse\n"
                "from apps.orders.dtos.create_order import CreateOrderInput\n",
            ).replace(
                "return self._repository.create(name=payload.name)",
                "payload.save()\n        return HttpResponse()",
            ),
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "Service imports endpoint/HTTP code" not in result.stdout or "persistence calls are exclusive to repositories" not in result.stdout:
            raise AssertionError(f"HTTP/persistence-coupled Service was not rejected:\n{result.stdout}")
        service.write_text(service_text, encoding="utf-8")

        mapper_payload_objects = root / "backend/apps/orders/mappers/create_order.py"
        mapper_payload_objects_text = mapper_payload_objects.read_text(encoding="utf-8")
        mapper_payload_objects.write_text(
            mapper_payload_objects_text.replace("return CreateOrderInput(name=payload.name)", "_ = payload.objects\n    return CreateOrderInput(name=payload.name)"),
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode != 0:
            raise AssertionError(f"non-ORM lowercase .objects produced a false positive:\n{result.stdout}")
        mapper_payload_objects.write_text(mapper_payload_objects_text, encoding="utf-8")

        composition = root / "backend/apps/orders/composition.py"
        composition_text = composition.read_text(encoding="utf-8")
        composition.write_text(
            composition_text
            + "\nfrom apps.orders.models.order import Order as order_model\n"
            + "QUERY = order_model.objects.all()\n",
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "ORM/database access is exclusive to repositories" not in result.stdout:
            raise AssertionError(f"lowercase imported Model manager was not rejected:\n{result.stdout}")
        composition.write_text(composition_text, encoding="utf-8")

        missing_skill = root / ".agents/skills/django-service/SKILL.md"
        missing_skill.unlink()
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "project-local skill requires SKILL.md" not in result.stdout:
            raise AssertionError(f"incomplete project-local skill kit was not rejected:\n{result.stdout}")
        write_local_skill(root, "django-service")

        write(root, "backend/apps/orders/models.py", "# forbidden aggregate\n")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "aggregate layer file is forbidden" not in result.stdout:
            raise AssertionError(f"legacy models.py was not rejected:\n{result.stdout}")
        (root / "backend/apps/orders/models.py").unlink()

        undocumented = root / "backend/apps/orders/composition.py"
        undocumented.write_text("VALUE = 1\n", encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "missing required opening module docstring" not in result.stdout:
            raise AssertionError(f"undocumented Python module was not rejected:\n{result.stdout}")

        undocumented.write_text('"""Utility."""\n\nVALUE = 1\n', encoding="utf-8")
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "opening module docstring is too vague" not in result.stdout:
            raise AssertionError(f"vague module documentation was not rejected:\n{result.stdout}")
        write(root, "backend/apps/orders/composition.py")

        mapper = root / "backend/apps/orders/mappers/create_order.py"
        mapper.write_text(
            mapper.read_text(encoding="utf-8") + "\nfrom apps.orders.models.order import Order\n",
            encoding="utf-8",
        )
        result = run(SCANNERS[0], root)
        if result.returncode == 0 or "application mapper must not import or access persistence" not in result.stdout:
            raise AssertionError(f"persistence-coupled mapper was not rejected:\n{result.stdout}")

    print("Django scalable architecture scanner tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
