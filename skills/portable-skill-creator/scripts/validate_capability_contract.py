#!/usr/bin/env python3
"""Validate a portable Skill capability manifest and platform adapters."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PLATFORM_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
STATUSES = {"tested", "implemented", "unresolved", "unsupported"}


def issue(level: str, code: str, message: str, **context: Any) -> dict[str, Any]:
    value = {"level": level, "code": code, "message": message}
    value.update({key: item for key, item in context.items() if item is not None})
    return value


def load_json(path: Path, issues: list[dict[str, Any]], code: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(issue("error", code, f"Missing file: {path}"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(issue("error", code, f"Cannot read valid JSON from {path}: {exc}"))
    return None


def string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value)


def validate(skill_dir: Path, platforms: list[str] | None = None, require_ready: bool = False) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    manifest_path = skill_dir / "capabilities.json"
    if not manifest_path.exists():
        return {
            "applicable": False,
            "skill_directory": str(skill_dir),
            "platforms": [],
            "errors": 0,
            "warnings": 0,
            "issues": [],
        }

    manifest = load_json(manifest_path, issues, "manifest-invalid")
    if not isinstance(manifest, dict):
        return summarize(skill_dir, [], issues, applicable=True)

    if manifest.get("schema") != "portable-skill-capabilities":
        issues.append(issue("error", "manifest-schema", "Manifest schema must be portable-skill-capabilities."))
    if not isinstance(manifest.get("schema_version"), str) or not SEMVER.fullmatch(manifest["schema_version"]):
        issues.append(issue("error", "manifest-version", "Manifest schema_version must be semantic version text."))

    target_platforms = manifest.get("target_platforms")
    if not string_list(target_platforms) or not target_platforms:
        issues.append(issue("error", "target-platforms", "target_platforms must be a non-empty string list."))
        target_platforms = []
    elif len(target_platforms) != len(set(target_platforms)) or any(not PLATFORM_ID.fullmatch(item) for item in target_platforms):
        issues.append(issue("error", "target-platforms", "target_platforms must contain unique portable platform IDs."))

    selected = platforms if platforms else list(target_platforms)
    unknown_selected = sorted(set(selected) - set(target_platforms))
    for platform in unknown_selected:
        issues.append(issue("error", "platform-not-targeted", f"Selected platform is not declared: {platform}", platform=platform))

    capabilities = manifest.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        issues.append(issue("error", "capabilities-empty", "capabilities must be a non-empty list."))
        capabilities = []

    declarations: dict[str, dict[str, Any]] = {}
    for position, declaration in enumerate(capabilities):
        if not isinstance(declaration, dict):
            issues.append(issue("error", "capability-invalid", f"Capability at index {position} must be an object."))
            continue
        capability_id = declaration.get("id")
        if not isinstance(capability_id, str) or not CAPABILITY_ID.fullmatch(capability_id):
            issues.append(issue("error", "capability-id", f"Invalid capability ID at index {position}."))
            continue
        if capability_id in declarations:
            issues.append(issue("error", "capability-duplicate", f"Duplicate capability ID: {capability_id}", capability_id=capability_id))
            continue
        declarations[capability_id] = declaration
        if not isinstance(declaration.get("purpose"), str) or not declaration["purpose"].strip():
            issues.append(issue("error", "capability-purpose", f"Capability {capability_id} needs a purpose.", capability_id=capability_id))
        if not isinstance(declaration.get("required"), bool):
            issues.append(issue("error", "capability-required", f"Capability {capability_id} needs a required boolean.", capability_id=capability_id))
        for field in ("required_features", "input_fields", "output_fields"):
            value = declaration.get(field)
            if not string_list(value) or (field != "required_features" and not value):
                issues.append(issue("error", f"capability-{field}", f"Capability {capability_id} has invalid {field}.", capability_id=capability_id))
            elif len(value) != len(set(value)):
                issues.append(issue("error", f"capability-{field}-duplicate", f"Capability {capability_id} has duplicate {field}.", capability_id=capability_id))
        side_effects = declaration.get("side_effects")
        if not isinstance(side_effects, dict) or not {"external_mutation", "may_cost_money", "authorization"}.issubset(side_effects):
            issues.append(issue("error", "capability-side-effects", f"Capability {capability_id} needs complete side_effects.", capability_id=capability_id))

    for platform in selected:
        if platform not in target_platforms:
            continue
        adapter_path = skill_dir / "adapters" / f"{platform}.json"
        adapter = load_json(adapter_path, issues, "adapter-invalid")
        if not isinstance(adapter, dict):
            continue
        if adapter.get("schema") != "portable-skill-adapter":
            issues.append(issue("error", "adapter-schema", f"Adapter {platform} has the wrong schema.", platform=platform))
        if adapter.get("platform") != platform:
            issues.append(issue("error", "adapter-platform", f"Adapter platform must equal {platform}.", platform=platform))
        mappings = adapter.get("mappings")
        if not isinstance(mappings, list):
            issues.append(issue("error", "adapter-mappings", f"Adapter {platform} mappings must be a list.", platform=platform))
            continue
        mapped: dict[str, dict[str, Any]] = {}
        for position, mapping in enumerate(mappings):
            if not isinstance(mapping, dict):
                issues.append(issue("error", "mapping-invalid", f"Adapter {platform} mapping {position} must be an object.", platform=platform))
                continue
            capability_id = mapping.get("capability_id")
            if capability_id not in declarations:
                issues.append(issue("error", "mapping-unknown-capability", f"Adapter {platform} maps unknown capability {capability_id}.", platform=platform, capability_id=capability_id))
                continue
            if capability_id in mapped:
                issues.append(issue("error", "mapping-duplicate", f"Adapter {platform} maps {capability_id} more than once.", platform=platform, capability_id=capability_id))
                continue
            mapped[capability_id] = mapping
            status = mapping.get("status")
            if status not in STATUSES:
                issues.append(issue("error", "mapping-status", f"Adapter {platform} capability {capability_id} has invalid status.", platform=platform, capability_id=capability_id))
                continue
            features = mapping.get("features")
            if not string_list(features):
                issues.append(issue("error", "mapping-features", f"Adapter {platform} capability {capability_id} needs a feature list.", platform=platform, capability_id=capability_id))
                features = []
            required_features = set(declarations[capability_id].get("required_features", []))
            if status in {"tested", "implemented"}:
                if not isinstance(mapping.get("implementation"), dict):
                    issues.append(issue("error", "mapping-implementation", f"Ready mapping {platform}/{capability_id} needs an implementation object.", platform=platform, capability_id=capability_id))
                missing_features = sorted(required_features - set(features))
                if missing_features:
                    issues.append(issue("error", "mapping-feature-gap", f"Adapter {platform} capability {capability_id} lacks features: {', '.join(missing_features)}", platform=platform, capability_id=capability_id))
            if status == "tested":
                if not isinstance(mapping.get("tested_date"), str) or not mapping["tested_date"].strip():
                    issues.append(issue("error", "mapping-tested-date", f"Tested mapping {platform}/{capability_id} needs tested_date.", platform=platform, capability_id=capability_id))
                if not string_list(mapping.get("evidence")) or not mapping.get("evidence"):
                    issues.append(issue("error", "mapping-tested-evidence", f"Tested mapping {platform}/{capability_id} needs evidence.", platform=platform, capability_id=capability_id))
            if status in {"unresolved", "unsupported"}:
                required = declarations[capability_id].get("required") is True
                level = "error" if require_ready and required else "warning"
                issues.append(issue(level, f"mapping-{status}", f"Adapter {platform} capability {capability_id} is {status}.", platform=platform, capability_id=capability_id))

        for capability_id, declaration in declarations.items():
            if capability_id in mapped:
                continue
            required = declaration.get("required") is True
            level = "error" if require_ready and required else "warning"
            issues.append(issue(level, "mapping-missing", f"Adapter {platform} has no mapping for {capability_id}.", platform=platform, capability_id=capability_id))

    return summarize(skill_dir, selected, issues, applicable=True)


def summarize(skill_dir: Path, platforms: list[str], issues: list[dict[str, Any]], applicable: bool) -> dict[str, Any]:
    return {
        "applicable": applicable,
        "skill_directory": str(skill_dir),
        "platforms": platforms,
        "errors": sum(item["level"] == "error" for item in issues),
        "warnings": sum(item["level"] == "warning" for item in issues),
        "issues": issues,
    }


def render_text(report: dict[str, Any]) -> str:
    if not report["applicable"]:
        return "Capability contract: not applicable (no capabilities.json)."
    lines = [f"Capability contract: {report['errors']} error(s), {report['warnings']} warning(s)."]
    for item in report["issues"]:
        location = "/".join(filter(None, [item.get("platform"), item.get("capability_id")]))
        prefix = f" [{location}]" if location else ""
        lines.append(f"- {item['level'].upper()} {item['code']}{prefix}: {item['message']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--platform", action="append", dest="platforms")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    report = validate(args.skill_directory.resolve(), args.platforms, args.require_ready)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else render_text(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
