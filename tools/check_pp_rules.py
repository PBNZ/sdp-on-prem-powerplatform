#!/usr/bin/env python3
"""
Check the connector definitions against Power Platform x-ms-* rules that
generic Swagger 2.0 validators (swagger-cli) do not know about.

Rules enforced (both from the portal's Swagger Validator / openapi-extensions
docs, https://learn.microsoft.com/connectors/custom-connectors/):
  - PropertyMustBeRequired: a parameter with x-ms-visibility "internal" and a
    default value must be required — optional internal fields are silently
    dropped from requests, and the portal wizard refuses to save.
  - An internal *required* parameter must have a default value (the user can
    never see it to fill it in).

Run:  python tools/check_pp_rules.py
Exits non-zero listing each violation.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def iter_parameters(doc):
    """Yield (location, parameter) for shared and inline operation parameters."""
    for name, param in (doc.get("parameters") or {}).items():
        yield f"parameters/{name}", param
    for route, ops in (doc.get("paths") or {}).items():
        for verb, op in ops.items():
            if not isinstance(op, dict):
                continue
            for param in op.get("parameters") or []:
                if "$ref" not in param:
                    yield f"{verb.upper()} {route} -> {param.get('name')}", param


def main():
    violations = []
    for path in sorted(glob.glob(os.path.join(ROOT, "connectors", "*", "apiDefinition.swagger.json"))):
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for where, param in iter_parameters(doc):
            if param.get("x-ms-visibility") != "internal":
                continue
            if "default" in param and not param.get("required"):
                violations.append(
                    f"{rel}: {where}: internal parameter with a default value must be "
                    "required (PropertyMustBeRequired); optional internal fields are ignored"
                )
            if param.get("required") and "default" not in param:
                violations.append(
                    f"{rel}: {where}: internal required parameter must have a default value"
                )
    for v in violations:
        print(v)
    if violations:
        sys.exit(1)
    print("Power Platform x-ms rules: OK")


if __name__ == "__main__":
    main()
