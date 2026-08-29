"""Validate the strict JSON Schema subset accepted by Structured Outputs."""

from __future__ import annotations

from typing import Any

ALLOWED_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}
ALLOWED_KEYWORDS = {
    "$schema",
    "$defs",
    "$ref",
    "title",
    "description",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "items",
    "enum",
    "const",
    "anyOf",
    "pattern",
    "format",
    "multipleOf",
    "maximum",
    "exclusiveMaximum",
    "minimum",
    "exclusiveMinimum",
    "minItems",
    "maxItems",
}
UNSUPPORTED_KEYWORDS = {
    "oneOf",
    "allOf",
    "not",
    "if",
    "then",
    "else",
    "dependentRequired",
    "dependentSchemas",
    "patternProperties",
    "propertyNames",
    "contains",
    "minContains",
    "maxContains",
    "uniqueItems",
    "minLength",
    "maxLength",
}


def _types(node: dict[str, Any]) -> set[str]:
    value = node.get("type")
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    return set()


def _matches_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def validate_structured_output_schema(schema: Any) -> list[str]:
    """Return deterministic errors without importing the SDK or calling a model."""
    errors: list[str] = []
    property_count = 0
    string_budget = 0
    enum_count = 0
    if not isinstance(schema, dict):
        return ["output schema root must be an object"]
    if schema.get("type") != "object":
        errors.append("output schema root type must be object")
    if "anyOf" in schema:
        errors.append("output schema root must not use anyOf")

    def walk(node: Any, path: str, depth: int) -> None:
        nonlocal property_count, string_budget, enum_count
        if not isinstance(node, dict):
            errors.append(f"{path} must be a schema object")
            return
        if depth > 10:
            errors.append(f"{path} exceeds the maximum nesting depth of 10")
        for keyword in set(node) - ALLOWED_KEYWORDS:
            errors.append(f"{path} uses unsupported schema keyword {keyword}")
        for keyword in UNSUPPORTED_KEYWORDS.intersection(node):
            errors.append(
                f"{path} uses unsupported Structured Outputs keyword {keyword}"
            )
        node_types = _types(node)
        if "type" in node:
            if not node_types or not node_types.issubset(ALLOWED_TYPES):
                errors.append(f"{path}.type is invalid")
            if len(node_types) > 1 and (
                "null" not in node_types or len(node_types) != 2
            ):
                errors.append(
                    f"{path}.type unions may contain one value type plus null"
                )
        elif not any(key in node for key in ("$ref", "anyOf")):
            errors.append(f"{path} must declare type")
        if ("enum" in node or "const" in node) and not node_types:
            errors.append(f"{path} enum/const must declare type")
        if isinstance(node.get("enum"), list) and node_types:
            for value in node["enum"]:
                if not any(_matches_type(value, expected) for expected in node_types):
                    errors.append(
                        f"{path}.enum contains a value outside its declared type"
                    )
                    break
        if (
            "const" in node
            and node_types
            and not any(
                _matches_type(node["const"], expected) for expected in node_types
            )
        ):
            errors.append(f"{path}.const is outside its declared type")
        if "object" in node_types:
            properties = node.get("properties")
            if not isinstance(properties, dict):
                errors.append(f"{path}.properties must be an object")
                properties = {}
            if node.get("additionalProperties") is not False:
                errors.append(f"{path}.additionalProperties must be false")
            required = node.get("required")
            if not isinstance(required, list) or len(required) != len(set(required)):
                errors.append(f"{path}.required must be a duplicate-free array")
                required = []
            if set(required) != set(properties):
                errors.append(
                    f"{path}.required must contain every property exactly once"
                )
            property_count += len(properties)
            for name, child in properties.items():
                string_budget += len(str(name))
                walk(child, f"{path}.properties.{name}", depth + 1)
        if "array" in node_types:
            if "items" not in node:
                errors.append(f"{path}.items is required for arrays")
            else:
                walk(node["items"], f"{path}.items", depth + 1)
        any_of = node.get("anyOf")
        if any_of is not None:
            if not isinstance(any_of, list) or not any_of:
                errors.append(f"{path}.anyOf must be a non-empty array")
            else:
                for index, child in enumerate(any_of):
                    walk(child, f"{path}.anyOf[{index}]", depth + 1)
        definitions = node.get("$defs")
        if definitions is not None:
            if not isinstance(definitions, dict):
                errors.append(f"{path}.$defs must be an object")
            else:
                for name, child in definitions.items():
                    string_budget += len(str(name))
                    walk(child, f"{path}.$defs.{name}", depth + 1)
        values = node.get("enum")
        if isinstance(values, list):
            enum_count += len(values)
            enum_string_size = sum(len(str(value)) for value in values)
            string_budget += enum_string_size
            if len(values) > 250 and enum_string_size > 15000:
                errors.append(
                    f"{path}.enum exceeds the 15000 character budget for enums over 250 values"
                )
        if "const" in node:
            string_budget += len(str(node["const"]))

    walk(schema, "$", 1)
    if property_count > 5000:
        errors.append("output schema exceeds 5000 total object properties")
    if string_budget > 120000:
        errors.append(
            "output schema exceeds the 120000 character name/enum/const budget"
        )
    if enum_count > 1000:
        errors.append("output schema exceeds 1000 total enum values")
    return list(dict.fromkeys(errors))
