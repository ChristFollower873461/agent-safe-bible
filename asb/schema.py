"""Small JSON Schema checker for the contracts in schemas/."""

from __future__ import annotations

import re
from typing import Any


class SchemaError(ValueError):
    pass


def validate(instance: Any, schema: dict[str, Any], path: str = "$") -> None:
    if "const" in schema and instance != schema["const"]:
        raise SchemaError(f"{path}: expected {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        raise SchemaError(f"{path}: {instance!r} not in {schema['enum']!r}")
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            raise SchemaError(f"{path}: expected object")
        required = schema.get("required", [])
        missing = [key for key in required if key not in instance]
        if missing:
            raise SchemaError(f"{path}: missing {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = [key for key in instance if key not in properties]
            if extra:
                raise SchemaError(f"{path}: unexpected {extra}")
        for key, value in instance.items():
            if key in properties:
                validate(value, properties[key], f"{path}.{key}")
    elif expected_type == "array":
        if not isinstance(instance, list):
            raise SchemaError(f"{path}: expected array")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(instance):
                validate(value, item_schema, f"{path}[{index}]")
    elif expected_type == "string":
        if not isinstance(instance, str):
            raise SchemaError(f"{path}: expected string")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise SchemaError(f"{path}: shorter than {schema['minLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            raise SchemaError(f"{path}: {instance!r} does not match {schema['pattern']}")
    elif expected_type == "integer":
        if not isinstance(instance, int) or isinstance(instance, bool):
            raise SchemaError(f"{path}: expected integer")
        if "minimum" in schema and instance < schema["minimum"]:
            raise SchemaError(f"{path}: {instance} < {schema['minimum']}")
    elif expected_type == "boolean":
        if not isinstance(instance, bool):
            raise SchemaError(f"{path}: expected boolean")
