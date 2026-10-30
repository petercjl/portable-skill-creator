#!/usr/bin/env python3
"""Scan an Agent Skill for high-confidence privacy and portability problems."""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import socket
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    "", ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".json",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".sh", ".bash",
    ".zsh", ".fish", ".ps1", ".rb", ".go", ".rs", ".java", ".xml",
    ".html", ".css", ".sql", ".csv", ".env.example",
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
MAX_FILE_BYTES = 2 * 1024 * 1024
ALLOW_RE = re.compile(r"portable-scan:\s*allow\s+([a-z0-9-]+)\s+--\s+(.+)", re.I)
PLACEHOLDER_PARTS = ("${", "{{", "<", "example", "placeholder", "changeme", "redacted", "dummy")
NONSUPPRESSIBLE = {"private-key", "credential-value", "aws-access-key"}


@dataclass
class Finding:
    severity: str
    rule_id: str
    path: str
    line: int
    message: str
    suppressed: bool = False
    reason: str | None = None


def severity_for(profile: str, shareable_severity: str) -> str:
    if profile in {"local", "platform"} and shareable_severity == "error":
        return "warning"
    return shareable_severity


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(part.lower() in lowered for part in PLACEHOLDER_PARTS) or value.startswith("$")


def suppression(lines: list[str], index: int, rule_id: str) -> tuple[bool, str | None]:
    if rule_id in NONSUPPRESSIBLE:
        return False, None
    for candidate in (lines[index], lines[index - 1] if index > 0 else ""):
        match = ALLOW_RE.search(candidate)
        if match and match.group(1).lower() == rule_id and len(match.group(2).strip()) >= 8:
            return True, match.group(2).strip()
    return False, None


def add_finding(
    findings: list[Finding], lines: list[str], index: int, rule_id: str,
    severity: str, rel_path: str, message: str,
) -> None:
    allowed, reason = suppression(lines, index, rule_id)
    findings.append(Finding(severity, rule_id, rel_path, index + 1, message, allowed, reason))


def text_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and not path.name.endswith(".env.example"):
            continue
        data = path.read_bytes()
        if b"\x00" in data:
            continue
        try:
            yield path, data.decode("utf-8")
        except UnicodeDecodeError:
            continue


def scan_file(root: Path, path: Path, content: str, profile: str, identity_tokens: set[str]) -> list[Finding]:
    findings: list[Finding] = []
    rel_path = path.relative_to(root).as_posix()
    lines = content.splitlines()

    posix_home = re.compile((r"/" + "Users" + r"/[A-Za-z0-9._-]+(?:/|\b)") + "|" + (r"/" + "home" + r"/[A-Za-z0-9._-]+(?:/|\b)"))
    windows_home = re.compile(r"\b[A-Za-z]:\\Users\\[^\\\s]+", re.I)
    private_key = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
    aws_key = re.compile("AK" + r"IA[0-9A-Z]{16}")
    credential = re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|token|password|passwd|client[_-]?secret|cookie)\b"
        r"\s*[:=]\s*['\"]?([^\s'\",;#]+)"
    )
    email = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
    private_ip = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
    local_scheme = re.compile("file" + r":/{2,3}")
    platform_home = re.compile(r"~/(?:\.(?:codex|hermes|openclaw|sealseek|sealclaw|agents))(?:/|\b)", re.I)

    for index, line in enumerate(lines):
        if posix_home.search(line):
            add_finding(findings, lines, index, "home-posix", severity_for(profile, "error"), rel_path, "Author-style POSIX home path detected; use configuration or a relative path.")
        if windows_home.search(line):
            add_finding(findings, lines, index, "home-windows", severity_for(profile, "error"), rel_path, "Author-style Windows home path detected; use configuration or a relative path.")
        if private_key.search(line):
            add_finding(findings, lines, index, "private-key", "error", rel_path, "Private-key material detected; remove it and rotate if exposure is plausible.")
        if aws_key.search(line):
            add_finding(findings, lines, index, "aws-access-key", "error", rel_path, "Cloud access-key shaped value detected; remove it and rotate if real.")
        for match in credential.finditer(line):
            value = match.group(2)
            if not is_placeholder(value):
                add_finding(findings, lines, index, "credential-value", "error", rel_path, "Credential-like assigned value detected; use the runtime secret mechanism.")
                break
        if email.search(line) and "example." not in line.lower():
            add_finding(findings, lines, index, "email-address", severity_for(profile, "warning"), rel_path, "Non-example email address detected; verify that it is intended to ship.")
        if private_ip.search(line):
            add_finding(findings, lines, index, "private-ip", severity_for(profile, "warning"), rel_path, "Private network address detected; parameterize or isolate it.")
        if local_scheme.search(line):
            add_finding(findings, lines, index, "file-uri", severity_for(profile, "error"), rel_path, "Local file URI detected; use a relative path or configuration.")
        if platform_home.search(line):
            add_finding(findings, lines, index, "platform-home", severity_for(profile, "warning"), rel_path, "Platform-specific home location detected; isolate it in an adapter or configuration.")
        lowered = line.lower()
        for token in identity_tokens:
            if token and len(token) >= 4 and re.search(rf"(?<![A-Za-z0-9_.-]){re.escape(token.lower())}(?![A-Za-z0-9_.-])", lowered):
                add_finding(findings, lines, index, "author-identity", severity_for(profile, "error"), rel_path, "Current author username or hostname detected; replace it with a neutral placeholder.")
                break
    return findings


def scan_symlinks(root: Path, profile: str) -> list[Finding]:
    findings: list[Finding] = []
    resolved_root = root.resolve()
    for path in root.rglob("*"):
        if not path.is_symlink():
            continue
        try:
            target = path.resolve(strict=True)
            target.relative_to(resolved_root)
        except (FileNotFoundError, ValueError):
            findings.append(Finding(severity_for(profile, "error"), "external-symlink", path.relative_to(root).as_posix(), 0, "Symlink is broken or resolves outside the Skill root."))
    return findings


def scan(root: Path, profile: str, extra_tokens: list[str]) -> dict:
    identity_tokens = {getpass.getuser().lower(), socket.gethostname().split(".")[0].lower()}
    identity_tokens.update(token.lower() for token in extra_tokens if token)
    findings = scan_symlinks(root, profile)
    scanned_files = 0
    for path, content in text_files(root):
        scanned_files += 1
        findings.extend(scan_file(root, path, content, profile, identity_tokens))
    active = [finding for finding in findings if not finding.suppressed]
    return {
        "root": str(root),
        "profile": profile,
        "scanned_files": scanned_files,
        "errors": sum(item.severity == "error" for item in active),
        "warnings": sum(item.severity == "warning" for item in active),
        "suppressed": sum(item.suppressed for item in findings),
        "findings": [asdict(item) for item in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--profile", choices=("shareable", "internal", "platform", "local"), default="shareable")
    parser.add_argument("--author-token", action="append", default=[], help="Additional author-specific token to detect; repeatable.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    root = args.skill_directory.expanduser().resolve()
    if not root.is_dir() or not (root / "SKILL.md").is_file():
        print("Target must be a Skill directory containing SKILL.md.", file=sys.stderr)
        return 2

    report = scan(root, args.profile, args.author_token)
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Portability scan: {report['root']}")
        print(f"Profile: {report['profile']} | files: {report['scanned_files']} | errors: {report['errors']} | warnings: {report['warnings']} | suppressed: {report['suppressed']}")
        for item in report["findings"]:
            state = "SUPPRESSED" if item["suppressed"] else item["severity"].upper()
            location = f"{item['path']}:{item['line']}" if item["line"] else item["path"]
            print(f"[{state}] {item['rule_id']} {location} - {item['message']}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
