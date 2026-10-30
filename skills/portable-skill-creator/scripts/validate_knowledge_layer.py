#!/usr/bin/env python3
"""Validate the structural and routing contract of a knowledge-compiled Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_FILES = (
    "SKILL.md",
    "references/SCHEMA.md",
    "references/index.md",
    "references/log.md",
    "references/source-manifest.md",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.md(?:#[^)]+)?)\)", re.I)
COVERAGE_RE = re.compile(
    r"\b(sufficient|partial|bootstrap|unknown)\b|"
    r"(?:覆盖(?:状态|程度)?|coverage)\s*[:：]?\s*(?:充分|部分|无|未知|引导)",
    re.I,
)
SOURCE_CLASS_RE = re.compile(
    r"W\s*(?:/|\||,)\s*U\s*(?:/|\||,)\s*E\s*(?:/|\||,)\s*A|"
    r"来源(?:类型|分级)|source\s+class",
    re.I,
)
ON_DEMAND_RE = re.compile(
    r"按需|对应节点|到此节点|知识依赖节点|first\s+knowledge-dependent\s+node|"
    r"only\s+when|on-demand|defer(?:red)?|延迟(?:加载|读取)?|后续节点",
    re.I,
)
EAGER_SCOPE_RE = re.compile(r"(?:all|every|whole|全部|所有|整个).{0,24}(?:references?|topics?|queries|知识(?:库|层)?)", re.I)
EAGER_ACTION_RE = re.compile(r"read|load|读取|加载|遍历", re.I)
NEGATION_RE = re.compile(r"do\s+not|don't|never|not\s+(?:read|load)|不得|不要|禁止|不(?:应|得|要)?(?:读取|加载|遍历)", re.I)


@dataclass
class Finding:
    severity: str
    rule: str
    path: str
    message: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def local_markdown_target(root: Path, source: Path, href: str) -> Path | None:
    target_text = href.split("#", 1)[0].strip()
    if not target_text or "://" in target_text or target_text.startswith("/"):
        return None
    target = (source.parent / target_text).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    return target


def eager_load_lines(text: str) -> list[tuple[int, str]]:
    findings = []
    for number, line in enumerate(text.splitlines(), 1):
        if EAGER_SCOPE_RE.search(line) and EAGER_ACTION_RE.search(line) and not NEGATION_RE.search(line):
            findings.append((number, line.strip()))
    return findings


def validate_route_manifest(root: Path, findings: list[Finding]) -> int:
    manifest = root / "references" / "routes.json"
    if not manifest.is_file():
        return 0
    try:
        data = json.loads(read_text(manifest))
    except json.JSONDecodeError as exc:
        findings.append(Finding("error", "invalid-route-manifest", "references/routes.json", f"Invalid JSON: {exc}"))
        return 0
    routes = data.get("routes")
    if not isinstance(routes, dict) or not routes:
        findings.append(Finding("error", "empty-route-manifest", "references/routes.json", "Declare at least one named runtime route."))
        return 0
    for name, spec in routes.items():
        files = spec.get("files") if isinstance(spec, dict) else None
        if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
            findings.append(Finding("error", "invalid-route-files", "references/routes.json", f"Route {name!r} needs a non-empty string file list."))
            continue
        for relative in files:
            target = local_markdown_target(root, manifest, relative)
            if target is None or not target.is_file():
                findings.append(Finding("error", "dead-route-file", "references/routes.json", f"Route {name!r} points to a missing or unsafe file: {relative}"))
            elif target.name == "source-manifest.md":
                findings.append(Finding("error", "maintenance-file-in-runtime-route", "references/routes.json", f"Route {name!r} must not load source-manifest.md during ordinary runtime."))
    return len(routes)


def validate(root: Path, mode: str) -> dict:
    root = root.expanduser().resolve()
    findings: list[Finding] = []
    if mode == "direct":
        return {
            "root": str(root),
            "mode": mode,
            "errors": 0,
            "warnings": 0,
            "findings": [],
        }

    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            findings.append(Finding("error", "missing-required-file", relative, "Required knowledge-layer file is missing."))
        elif not read_text(path).strip():
            findings.append(Finding("error", "empty-required-file", relative, "Required knowledge-layer file is empty."))

    queries_dir = root / "references" / "queries"
    queries = sorted(queries_dir.glob("*.md")) if queries_dir.is_dir() else []
    if not queries:
        findings.append(Finding("error", "missing-query-route", "references/queries", "At least one realistic Markdown query route is required."))

    reserved = {"SCHEMA.md", "index.md", "log.md", "source-manifest.md"}
    topic_pages = [
        path for path in (root / "references").rglob("*.md")
        if path.name not in reserved and "queries" not in path.relative_to(root / "references").parts
    ] if (root / "references").is_dir() else []
    if not topic_pages:
        findings.append(Finding("error", "missing-topic-page", "references", "At least one synthesized topic page is required."))

    for query in queries:
        content = read_text(query)
        links = LINK_RE.findall(content)
        valid_targets = []
        for href in links:
            target = local_markdown_target(root, query, href)
            if (
                target is not None
                and target.is_file()
                and "queries" not in target.relative_to(root / "references").parts
                and target.name not in reserved
            ):
                valid_targets.append(target)
            elif target is not None:
                findings.append(Finding(
                    "error", "dead-query-link", query.relative_to(root).as_posix(),
                    f"Query route points to a missing Markdown file: {href}",
                ))
        if not valid_targets:
            findings.append(Finding(
                "error", "query-without-topic-route", query.relative_to(root).as_posix(),
                "Query entry must link to at least one existing local Markdown topic page.",
            ))

    manifest = root / "references" / "source-manifest.md"
    manifest_text = read_text(manifest)
    if manifest.is_file() and not COVERAGE_RE.search(manifest_text):
        findings.append(Finding("error", "missing-coverage", "references/source-manifest.md", "Declare sufficient, partial, bootstrap, or unknown coverage and critical gaps."))
    if manifest.is_file() and not SOURCE_CLASS_RE.search(manifest_text):
        findings.append(Finding("error", "missing-source-classes", "references/source-manifest.md", "Declare W/U/E/A source classes or an equivalent explicit provenance legend."))
    if manifest.is_file() and not re.search(r"recompil|重新编译|重编译", manifest_text, re.I):
        findings.append(Finding("warning", "missing-recompile-boundary", "references/source-manifest.md", "State when the local knowledge layer must be recompiled."))

    skill_text = read_text(root / "SKILL.md")
    if skill_text and not re.search(r"SCHEMA\.md|queries/|knowledge|知识", skill_text, re.I):
        findings.append(Finding("warning", "missing-runtime-navigation", "SKILL.md", "Describe how runtime nodes enter the local knowledge layer."))
    if skill_text and not ON_DEMAND_RE.search(skill_text):
        findings.append(Finding("error", "missing-on-demand-loading-contract", "SKILL.md", "State that knowledge is loaded only at the current knowledge-dependent node and later-node pages remain deferred."))
    for number, line in eager_load_lines(skill_text):
        findings.append(Finding("error", "eager-full-knowledge-load", f"SKILL.md:{number}", f"Do not make the whole knowledge layer a startup reading list: {line}"))

    route_manifests = validate_route_manifest(root, findings)

    active_errors = sum(item.severity == "error" for item in findings)
    active_warnings = sum(item.severity == "warning" for item in findings)
    return {
        "root": str(root),
        "mode": mode,
        "errors": active_errors,
        "warnings": active_warnings,
        "queries": len(queries),
        "topic_pages": len(topic_pages),
        "route_manifests": route_manifests,
        "findings": [asdict(item) for item in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--mode", choices=("direct", "knowledge-compiled", "hybrid"), required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    root = args.skill_directory.expanduser().resolve()
    if not root.is_dir() or not (root / "SKILL.md").is_file():
        print("Target must be a Skill directory containing SKILL.md.", file=sys.stderr)
        return 2

    report = validate(root, args.mode)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Knowledge-layer validation: {report['root']}")
        print(f"Mode: {report['mode']} | errors: {report['errors']} | warnings: {report['warnings']}")
        for item in report["findings"]:
            print(f"[{item['severity'].upper()}] {item['rule']} {item['path']} - {item['message']}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
