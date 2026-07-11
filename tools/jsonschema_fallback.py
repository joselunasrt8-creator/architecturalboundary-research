"""Restricted-environment fallback for current repository schema checks.

CI installs the declared jsonschema dependency. This fallback is used only when
that dependency cannot be imported in a local restricted environment, and only
implements keywords used by the repository's current schemas.
"""
from __future__ import annotations


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

    def _validate(self, schema, instance, path):
        if not isinstance(schema, dict):
            return
        typ = schema.get("type")
        if typ and not self._type_ok(typ, instance):
            yield ValidationError(f"{instance!r} is not of type {typ!r}", path)
            return
        required = schema.get("required", [])
        if isinstance(required, list) and isinstance(instance, dict):
            for key in required:
                if key not in instance:
                    yield ValidationError(f"{key!r} is a required property", (*path, key))
        props = schema.get("properties", {})
        if isinstance(props, dict) and isinstance(instance, dict):
            for key, subschema in props.items():
                if key in instance:
                    yield from self._validate(subschema, instance[key], (*path, key))
        items = schema.get("items")
        if isinstance(items, dict) and isinstance(instance, list):
            for index, value in enumerate(instance):
                yield from self._validate(items, value, (*path, index))

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
