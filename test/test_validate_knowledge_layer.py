#!/usr/bin/env python3
"""Regression tests for validate_knowledge_layer.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1] / "skills" / "portable-skill-creator" / "scripts" / "validate_knowledge_layer.py")
SPEC = importlib.util.spec_from_file_location("knowledge_validator", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class KnowledgeLayerValidatorTest(unittest.TestCase):
    def make_valid_skill(self, root: Path) -> None:
        write(root / "SKILL.md", "---\nname: demo\ndescription: demo\n---\nAt the current knowledge-dependent node, load only its route under references/queries/; later-node knowledge remains deferred.\n")
        write(root / "references/SCHEMA.md", "# Schema\n")
        write(root / "references/index.md", "# Index\n")
        write(root / "references/log.md", "# Log\n")
        write(
            root / "references/source-manifest.md",
            "# Sources\nCoverage: partial\nCritical gaps: one\nSource classes: W/U/E/A\nRecompile when sources change.\n",
        )
        write(root / "references/topics/method.md", "# Method\n")
        write(root / "references/queries/how-to.md", "# How to\nUse [method](../topics/method.md).\n")

    def test_valid_knowledge_layer_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_valid_skill(root)
            report = MODULE.validate(root, "hybrid")
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 0)

    def test_dead_or_recursive_query_route_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_valid_skill(root)
            write(root / "references/queries/how-to.md", "# How to\nUse [another query](other.md).\n")
            write(root / "references/queries/other.md", "# Other\n")
            report = MODULE.validate(root, "knowledge-compiled")
            rules = {item["rule"] for item in report["findings"]}
            self.assertGreater(report["errors"], 0)
            self.assertIn("query-without-topic-route", rules)

    def test_direct_mode_skips_knowledge_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report = MODULE.validate(Path(directory), "direct")
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["findings"], [])

    def test_eager_full_layer_loading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_valid_skill(root)
            write(root / "SKILL.md", "---\nname: demo\ndescription: demo\n---\nAt startup, read all references and every knowledge topic.\n")
            report = MODULE.validate(root, "hybrid")
            rules = {item["rule"] for item in report["findings"]}
            self.assertIn("eager-full-knowledge-load", rules)
            self.assertIn("missing-on-demand-loading-contract", rules)

    def test_runtime_route_cannot_load_source_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_valid_skill(root)
            write(
                root / "references/routes.json",
                '{"routes":{"startup":{"files":["source-manifest.md"]}}}',
            )
            report = MODULE.validate(root, "knowledge-compiled")
            rules = {item["rule"] for item in report["findings"]}
            self.assertIn("maintenance-file-in-runtime-route", rules)


if __name__ == "__main__":
    unittest.main()
