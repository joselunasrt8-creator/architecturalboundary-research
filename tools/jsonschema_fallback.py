"""Restricted-environment fallback for current repository schema checks.

CI installs the declared jsonschema dependency. This fallback is used only when
that dependency cannot be imported in a local restricted environment, and only
implements keywords used by the repository's current schemas.
"""
from __future__ import annotations

import re
from collections.abc import Iterable


class ValidationError(Exception):
    def __init__(self, message: str, path=()):
        super().__init__(message)
        self.message = message
        self.path = tuple(path)


class Draft202012Validator:
    def __init__(self, schema):
        self.schema = schema or {}

    def iter_errors(self, instance):
        yield from self._validate(self.schema, instance, ())

    def _resolve_ref(self, ref: str):
        if not ref.startswith("#/"):
            return None
        target = self.schema
        for part in ref[2:].split("/"):
            if not isinstance(target, dict) or part not in target:
                return None
            target = target[part]
        return target

    def _validate(self, schema, instance, path):
        if not isinstance(schema, dict):
            return

        ref = schema.get("$ref")
        if isinstance(ref, str):
            target = self._resolve_ref(ref)
            if target is None:
                yield ValidationError(f"unresolvable $ref: {ref}", path)
            else:
                yield from self._validate(target, instance, path)
            return

        if "const" in schema and instance != schema["const"]:
            yield ValidationError(f"{instance!r} is not equal to const {schema['const']!r}", path)

        enum = schema.get("enum")
        if isinstance(enum, list) and instance not in enum:
            yield ValidationError(f"{instance!r} is not one of {enum!r}", path)

        typ = schema.get("type")
        if typ and not self._type_ok(typ, instance):
            yield ValidationError(f"{instance!r} is not of type {typ!r}", path)
            return

        if isinstance(instance, str):
            min_length = schema.get("minLength")
            if isinstance(min_length, int) and len(instance) < min_length:
                yield ValidationError(f"{instance!r} is shorter than {min_length}", path)
            pattern = schema.get("pattern")
            if isinstance(pattern, str) and re.search(pattern, instance) is None:
                yield ValidationError(f"{instance!r} does not match pattern {pattern!r}", path)

        if isinstance(instance, list):
            min_items = schema.get("minItems")
            if isinstance(min_items, int) and len(instance) < min_items:
                yield ValidationError(f"{instance!r} has fewer than {min_items} items", path)
            if schema.get("uniqueItems") is True and not self._items_unique(instance):
                yield ValidationError(f"{instance!r} has non-unique items", path)
            items = schema.get("items")
            if isinstance(items, dict):
                for index, value in enumerate(instance):
                    yield from self._validate(items, value, (*path, index))

        if isinstance(instance, dict):
            required = schema.get("required", [])
            if isinstance(required, list):
                for key in required:
                    if key not in instance:
                        yield ValidationError(f"{key!r} is a required property", (*path, key))

            props = schema.get("properties", {})
            if isinstance(props, dict):
                for key, subschema in props.items():
                    if key in instance:
                        yield from self._validate(subschema, instance[key], (*path, key))

            additional = schema.get("additionalProperties", True)
            if additional is False and isinstance(props, dict):
                for key in instance:
                    if key not in props:
                        yield ValidationError(f"additional property {key!r} is not allowed", (*path, key))
            elif isinstance(additional, dict) and isinstance(props, dict):
                for key, value in instance.items():
                    if key not in props:
                        yield from self._validate(additional, value, (*path, key))

    @staticmethod
    def _items_unique(items: Iterable[object]) -> bool:
        seen: list[object] = []
        for item in items:
            if any(item == prior for prior in seen):
                return False
            seen.append(item)
        return True

    @staticmethod
    def _type_ok(typ, instance):
        if isinstance(typ, list):
            return any(Draft202012Validator._type_ok(item, instance) for item in typ)
        if typ == "null":
            return instance is None
        if typ == "object":
            return isinstance(instance, dict)
        if typ == "array":
            return isinstance(instance, list)
        if typ == "string":
            return isinstance(instance, str)
        if typ == "boolean":
            return isinstance(instance, bool)
        if typ == "integer":
            return isinstance(instance, int) and not isinstance(instance, bool)
        if typ == "number":
            return isinstance(instance, (int, float)) and not isinstance(instance, bool)
        return True
