#!/usr/bin/env python3

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_PATH = (Path(__file__).resolve().parents[1] / "skills" / "portable-skill-creator" / "scripts" / "validate_portability.py")
SPEC = importlib.util.spec_from_file_location("validate_portability", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PortabilityScannerTest(unittest.TestCase):
    def make_skill(self, body: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: Test skill.\n---\n\n" + body,
            encoding="utf-8",
        )
        return root

    def test_clean_skill_passes(self):
        report = MODULE.scan(self.make_skill("Use scripts/run.py relative to the Skill root."), "shareable", ["unlikely-author-token"])
        self.assertEqual(report["errors"], 0)

    def test_author_home_path_fails_shareable_profile(self):
        root = self.make_skill("Read /" + "Users" + "/alice/project/config.json.")
        report = MODULE.scan(root, "shareable", ["unlikely-author-token"])
        self.assertTrue(any(item["rule_id"] == "home-posix" and item["severity"] == "error" for item in report["findings"]))

    def test_placeholder_credential_passes(self):
        report = MODULE.scan(self.make_skill("api_key=${SERVICE_API_KEY}"), "shareable", ["unlikely-author-token"])
        self.assertFalse(any(item["rule_id"] == "credential-value" for item in report["findings"]))

    def test_real_credential_fails_without_echoing_value(self):
        secret = "sensitive-value-123"
        credential_line = "to" + f"ken={secret}"
        report = MODULE.scan(self.make_skill(credential_line), "shareable", ["unlikely-author-token"])
        credential_findings = [item for item in report["findings"] if item["rule_id"] == "credential-value"]
        self.assertEqual(len(credential_findings), 1)
        self.assertNotIn(secret, credential_findings[0]["message"])

    def test_local_profile_downgrades_home_path(self):
        root = self.make_skill("Read /" + "home" + "/alice/project/config.json.")
        report = MODULE.scan(root, "local", ["unlikely-author-token"])
        self.assertEqual(report["errors"], 0)
        self.assertGreaterEqual(report["warnings"], 1)


if __name__ == "__main__":
    unittest.main()
