#!/usr/bin/env python3
"""Validate the public scientific GeoJSON catalogs against their JSON Schemas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def format_error(error: Any) -> str:
    location = "$"
    for part in error.absolute_path:
        location += f"[{part}]" if isinstance(part, int) else f".{part}"
    return f"{location}: {error.message}"


def validate_catalog(schema_path: Path, data_path: Path) -> list[str]:
    schema = read_json(schema_path)
    document = read_json(data_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        format_error(error)
        for error in sorted(
            validator.iter_errors(document),
            key=lambda item: tuple(str(part) for part in item.absolute_path),
        )
    ]

    feature_count = document.get("metadata", {}).get("feature_count")
    actual_count = len(document.get("features", []))
    if feature_count != actual_count:
        errors.append(
            f"$.metadata.feature_count: declares {feature_count!r}, but the document contains {actual_count} features"
        )
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Ecuador Vivo GeoJSON catalogs with JSON Schema Draft 2020-12."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root containing data/schemas and data/geojson.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalogs = (
        (args.root / "data/schemas/fallas.schema.json", args.root / "data/geojson/fallas.geojson"),
        (
            args.root / "data/schemas/estructuras.schema.json",
            args.root / "data/geojson/estructuras.geojson",
        ),
    )
    failed = False
    for schema_path, data_path in catalogs:
        errors = validate_catalog(schema_path, data_path)
        if errors:
            failed = True
            print(f"ERROR: {data_path.relative_to(args.root)} does not satisfy {schema_path.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"Schema validation passed: {data_path.relative_to(args.root)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
