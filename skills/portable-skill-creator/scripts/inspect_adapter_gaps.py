#!/usr/bin/env python3
"""List unresolved, unsupported, missing, and feature-incomplete adapter mappings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def inspect(skill_dir: Path, platforms: list[str] | None = None) -> dict[str, Any]:
    manifest = load(skill_dir / "capabilities.json")
    declarations = {item["id"]: item for item in manifest["capabilities"]}
    selected = platforms or manifest["target_platforms"]
    gaps: list[dict[str, Any]] = []
    for platform in selected:
        adapter_path = skill_dir / "adapters" / f"{platform}.json"
        if not adapter_path.exists():
            for capability_id, declaration in declarations.items():
                gaps.append({"platform": platform, "capability_id": capability_id, "required": declaration["required"], "kind": "mapping-missing", "missing_features": declaration["required_features"]})
            continue
        adapter = load(adapter_path)
        mappings = {item.get("capability_id"): item for item in adapter.get("mappings", []) if isinstance(item, dict)}
        for capability_id, declaration in declarations.items():
            mapping = mappings.get(capability_id)
            if mapping is None:
                gaps.append({"platform": platform, "capability_id": capability_id, "required": declaration["required"], "kind": "mapping-missing", "missing_features": declaration["required_features"]})
                continue
            status = mapping.get("status")
            missing = sorted(set(declaration["required_features"]) - set(mapping.get("features", [])))
            if status in {"unresolved", "unsupported"}:
                gaps.append({"platform": platform, "capability_id": capability_id, "required": declaration["required"], "kind": status, "missing_features": missing})
            elif missing:
                gaps.append({"platform": platform, "capability_id": capability_id, "required": declaration["required"], "kind": "feature-gap", "missing_features": missing})
    return {"skill_directory": str(skill_dir), "platforms": selected, "gap_count": len(gaps), "gaps": gaps}


def render_text(report: dict[str, Any]) -> str:
    lines = [f"Adapter gaps: {report['gap_count']}"]
    for gap in report["gaps"]:
        required = "required" if gap["required"] else "optional"
        missing = ", ".join(gap["missing_features"]) or "none"
        lines.append(f"- {gap['platform']}/{gap['capability_id']}: {gap['kind']} ({required}); missing features: {missing}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--platform", action="append", dest="platforms")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        report = inspect(args.skill_directory.resolve(), args.platforms)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Cannot inspect adapter gaps: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
