#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path

from validate_capability_contract import validate


def manifest() -> dict:
    return {
        "schema": "portable-skill-capabilities",
        "schema_version": "1.0.0",
        "skill": "fixture",
        "target_platforms": ["alpha"],
        "capabilities": [
            {
                "id": "media.image.generate",
                "purpose": "Generate an image.",
                "required": True,
                "required_features": ["reference-image", "local-artifact"],
                "input_fields": ["prompt"],
                "output_fields": ["artifacts"],
                "side_effects": {"external_mutation": True, "may_cost_money": True, "authorization": "task-scope"},
            }
        ],
    }


def adapter(status: str = "tested", features: list[str] | None = None) -> dict:
    value = {
        "schema": "portable-skill-adapter",
        "schema_version": "1.0.0",
        "platform": "alpha",
        "mappings": [
            {
                "capability_id": "media.image.generate",
                "status": status,
                "implementation": {"kind": "agent-native", "capability": "image generation"} if status in {"tested", "implemented"} else None,
                "features": features if features is not None else ["reference-image", "local-artifact"],
                "permissions": [],
                "normalization": "Return local artifacts.",
            }
        ],
    }
    if status == "tested":
        value["mappings"][0]["tested_date"] = "2026-08-29"
        value["mappings"][0]["evidence"] = ["Fixture execution passed."]
    return value


class CapabilityContractTests(unittest.TestCase):
    def fixture(self, adapter_value: dict | None = None) -> tuple[tempfile.TemporaryDirectory, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "adapters").mkdir()
        (root / "capabilities.json").write_text(json.dumps(manifest()), encoding="utf-8")
        if adapter_value is not None:
            (root / "adapters" / "alpha.json").write_text(json.dumps(adapter_value), encoding="utf-8")
        return temporary, root

    def test_valid_contract_passes(self) -> None:
        temporary, root = self.fixture(adapter())
        self.addCleanup(temporary.cleanup)
        report = validate(root, require_ready=True)
        self.assertEqual(report["errors"], 0)
        self.assertEqual(report["warnings"], 0)

    def test_missing_adapter_is_error(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        report = validate(root)
        self.assertGreater(report["errors"], 0)
        self.assertIn("adapter-invalid", {item["code"] for item in report["issues"]})

    def test_unresolved_required_is_warning_then_error(self) -> None:
        temporary, root = self.fixture(adapter("unresolved", []))
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate(root)["errors"], 0)
        self.assertGreater(validate(root)["warnings"], 0)
        self.assertGreater(validate(root, require_ready=True)["errors"], 0)

    def test_tested_mapping_requires_evidence(self) -> None:
        value = adapter()
        del value["mappings"][0]["evidence"]
        temporary, root = self.fixture(value)
        self.addCleanup(temporary.cleanup)
        codes = {item["code"] for item in validate(root)["issues"]}
        self.assertIn("mapping-tested-evidence", codes)

    def test_feature_gap_is_error(self) -> None:
        temporary, root = self.fixture(adapter("implemented", ["reference-image"]))
        self.addCleanup(temporary.cleanup)
        codes = {item["code"] for item in validate(root)["issues"]}
        self.assertIn("mapping-feature-gap", codes)


if __name__ == "__main__":
    unittest.main()
