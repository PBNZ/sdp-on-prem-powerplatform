#!/usr/bin/env python3
"""
Check that every operation's "Learn more" wiring and per-action doc hold
together, across all four connectors:

  1. every operation carries externalDocs with the canonical action-doc URL
     (kebab of the operationId under connectors/<name>/actions/);
  2. the operation description ends with " Learn more: <that same URL>"
     (the flow designer's About tab shows the description text);
  3. the linked doc file exists;
  4. every file in actions/ (bar README.md) maps back to an operation — no
     orphaned docs;
  5. every parameter of the operation is mentioned in its doc (as `name`),
     so no parameter can go undocumented;
  6. the actions/README.md index links every action doc.

Run:  python tools/check_action_docs.py     (wired into validate.yml)
Exits non-zero listing each violation.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_swagger import action_doc_url, kebab  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    violations = []
    for def_path in sorted(glob.glob(os.path.join(ROOT, "connectors", "*",
                                                  "apiDefinition.swagger.json"))):
        cdir = os.path.dirname(def_path)
        cname = os.path.basename(cdir)
        rel = os.path.relpath(def_path, ROOT)
        with open(def_path, encoding="utf-8") as f:
            doc = json.load(f)

        adir = os.path.join(cdir, "actions")
        expected_files = set()
        for route, ops in (doc.get("paths") or {}).items():
            for verb, op in ops.items():
                if not isinstance(op, dict):
                    continue
                where = f"{rel}: {verb.upper()} {route} ({op.get('operationId')})"
                opid = op.get("operationId") or ""
                url = action_doc_url(cname, opid)
                fname = kebab(opid) + ".md"
                expected_files.add(fname)

                ed = op.get("externalDocs")
                if not ed:
                    violations.append(f"{where}: missing externalDocs")
                elif ed.get("url") != url:
                    violations.append(f"{where}: externalDocs.url is {ed.get('url')!r}, "
                                      f"expected {url!r}")
                desc = op.get("description") or ""
                if not desc.endswith(" Learn more: " + url):
                    violations.append(f"{where}: description does not end with the "
                                      f"'Learn more: {url}' suffix")

                doc_path = os.path.join(adir, fname)
                if not os.path.isfile(doc_path):
                    violations.append(f"{where}: action doc missing: "
                                      f"connectors/{cname}/actions/{fname}")
                    continue
                with open(doc_path, encoding="utf-8") as f:
                    text = f.read()
                for p in op.get("parameters") or []:
                    name = p.get("name")
                    if "$ref" in p:
                        name = p["$ref"].rsplit("/", 1)[-1]
                        name = (doc.get("parameters") or {}).get(name, {}).get("name")
                    if name and f"`{name}`" not in text:
                        violations.append(f"{where}: parameter '{name}' not documented in "
                                          f"actions/{fname}")

        # orphans + index coverage
        on_disk = {os.path.basename(p)
                   for p in glob.glob(os.path.join(adir, "*.md"))} - {"README.md"}
        for orphan in sorted(on_disk - expected_files):
            violations.append(f"connectors/{cname}/actions/{orphan}: no matching operation")
        index_path = os.path.join(adir, "README.md")
        if not os.path.isfile(index_path):
            violations.append(f"connectors/{cname}/actions/README.md: index missing")
        else:
            with open(index_path, encoding="utf-8") as f:
                index = f.read()
            for fname in sorted(expected_files):
                if f"({fname})" not in index:
                    violations.append(f"connectors/{cname}/actions/README.md: "
                                      f"does not link {fname}")

    for v in violations:
        print(v)
    if violations:
        sys.exit(1)
    print("Learn-more links & action-doc coverage: OK")


if __name__ == "__main__":
    main()
