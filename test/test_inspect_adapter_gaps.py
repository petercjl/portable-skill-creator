#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

from inspect_adapter_gaps import inspect


class AdapterGapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "adapters").mkdir()
        manifest = {
            "schema": "portable-skill-capabilities",
            "schema_version": "1.0.0",
            "skill": "fixture",
            "target_platforms": ["alpha"],
            "capabilities": [
                {"id": "media.image.generate", "required": True, "required_features": ["generate", "edit"]},
                {"id": "agent.isolated-run", "required": False, "required_features": ["fresh-context"]},
            ],
        }
        (self.root / "capabilities.json").write_text(json.dumps(manifest), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_detects_unresolved_and_feature_gap(self) -> None:
        adapter = {
            "schema": "portable-skill-adapter",
            "platform": "alpha",
            "mappings": [
                {"capability_id": "media.image.generate", "status": "implemented", "features": ["generate"]},
                {"capability_id": "agent.isolated-run", "status": "unresolved", "features": []},
            ],
        }
        (self.root / "adapters" / "alpha.json").write_text(json.dumps(adapter), encoding="utf-8")
        report = inspect(self.root)
        self.assertEqual(report["gap_count"], 2)
        self.assertEqual({gap["kind"] for gap in report["gaps"]}, {"feature-gap", "unresolved"})

    def test_missing_adapter_lists_every_capability(self) -> None:
        report = inspect(self.root)
        self.assertEqual(report["gap_count"], 2)
        self.assertTrue(all(gap["kind"] == "mapping-missing" for gap in report["gaps"]))


if __name__ == "__main__":
    unittest.main()
