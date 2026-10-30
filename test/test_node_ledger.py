import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/portable-skill-creator/assets/node-ledger/ledger.py"


class LedgerTest(unittest.TestCase):
    def setUp(self):
        if os.environ.get("LEDGER_EVIDENCE_DIR"):
            self.root = Path(tempfile.mkdtemp(prefix="run-", dir=os.environ["LEDGER_EVIDENCE_DIR"]))
        else:
            folder = tempfile.TemporaryDirectory()
            self.addCleanup(folder.cleanup)
            self.root = Path(folder.name)
        self.run = self.root / "ledger"
        self.count = 0
        self.put("reviews.txt", "用户希望清洁方便；小厨房需要节省空间。")
        self.put("strategy.md", "Identify needs with review evidence and distinguish inference.")
        self.flow = {"schemaVersion": 1, "nodes": [
            self.node("needs", [], ["reviews.txt"], ["strategy.md"]),
            self.node("portrait", [], ["reviews.txt"], []),
            self.node("report", ["needs"], [], [])]}
        self.call("init", data=self.flow, extra=["--workspace", str(self.root)])

    def node(self, key, deps, inputs, strategies):
        return {"id": key, "title": key, "dependsOn": deps, "inputs": inputs,
                "strategies": strategies, "outputKeys": ["result"], "checks": ["evidence"]}

    def put(self, relative, text):
        p = self.root / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def call(self, action, node=None, data=None, attempt=None, extra=None, ok=True):
        args = [sys.executable, str(SCRIPT), action, "--run", str(self.run)]
        if node:
            args += ["--node", node]
        if data is not None:
            self.count += 1
            p = self.root / f"request-{self.count}.json"
            p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            args += ["--data", str(p)]
        if attempt:
            args += ["--attempt", attempt]
        result = subprocess.run(args + (extra or []), capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONIOENCODING": "ascii"})
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return json.loads(result.stderr)

    def complete(self, node, text="verified result"):
        started = self.call("start", node)
        aid = started["node"]["attempt"]
        output = f"outputs/{node}-{aid}.txt"
        self.put(output, text)
        self.call("finish", node, attempt=aid, data={"status": "completed", "summary": text,
                  "outputs": {"result": output}, "checks": {"evidence": True}})
        return aid, output

    def test_trace_history_strategy_change_and_partial_rerun(self):
        old, output = self.complete("needs", "清洁便利与空间占用是两项需求；依据 reviews.txt。")
        independent, _ = self.complete("portrait", "画像证据不足，保留未知。")
        report, _ = self.complete("report", "需求报告已整理。")
        old_trace = self.call("inspect", "report", attempt=report)["trace"]
        self.assertEqual(old_trace["upstream"][0]["execution"]["id"], old)
        self.put("strategy.md", "Identify needs and map benefits using the applicable FABE evidence.")
        plan = self.call("plan")
        self.assertEqual(plan["reuse"], ["portrait"])
        self.assertEqual(plan["rerunOrder"], ["needs", "report"])
        self.call("start", "report", ok=False)
        new, _ = self.complete("needs", "新增方法下的需求解释及证据。")
        self.assertNotEqual(old, new)
        self.complete("report", "更新后的需求报告。")
        self.assertEqual(self.call("inspect")["nodes"]["portrait"]["attempt"], independent)
        self.put(output, "live file overwritten")
        trace = self.call("inspect", "needs", attempt=old)["trace"]
        snapshot = self.run / trace["execution"]["outputs"]["result"]["snapshot"]
        self.assertIn("清洁便利", snapshot.read_text(encoding="utf-8"))
        self.assertEqual(old_trace, self.call("inspect", "report", attempt=report)["trace"])
        self.put("trace-evidence.json", json.dumps(old_trace, ensure_ascii=False, indent=2))
        self.put("rerun-plan.json", json.dumps(plan, ensure_ascii=False, indent=2))

    def test_acceptance_failure_missing_output_and_interruption(self):
        started = self.call("start", "needs", data={"externalTask": {"id": "existing-task"}})
        aid = started["node"]["attempt"]
        self.call("start", "needs", ok=False)
        self.call("finish", "needs", attempt=aid, data={"status": "completed", "summary": "no file",
                  "outputs": {"result": "missing.txt"}, "checks": {"evidence": True}}, ok=False)
        self.put("output.txt", "result")
        self.call("finish", "needs", attempt=aid, data={"status": "completed", "summary": "bad check",
                  "outputs": {"result": "output.txt"}, "checks": {"evidence": False}}, ok=False)
        self.call("finish", "needs", attempt=aid, data={"status": "failed", "summary": "Existing external task inspected; failed."})
        new, output = self.complete("needs")
        self.assertNotEqual(aid, new)
        self.complete("report")
        (self.root / output).unlink()
        self.assertEqual(self.call("plan")["rerunOrder"], ["needs", "portrait", "report"])

    def test_changed_input_during_execution_and_exact_attempt(self):
        aid = self.call("start", "needs")["node"]["attempt"]
        self.put("reviews.txt", "changed")
        self.put("output.txt", "result")
        data = {"status": "completed", "summary": "result", "outputs": {"result": "output.txt"}, "checks": {"evidence": True}}
        self.call("finish", "needs", attempt=aid, data=data, ok=False)
        self.call("finish", "needs", attempt="wrong-id", data={"status": "failed", "summary": "wrong"}, ok=False)
        self.assertEqual(self.call("inspect")["nodes"]["needs"]["status"], "running")

    def test_revision_invalid_graph_history_and_read_only(self):
        self.complete("needs")
        self.complete("report")
        before = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.run.rglob("*") if p.is_file()}
        self.call("inspect", "report")
        self.call("plan")
        after = {str(p): (p.read_bytes(), p.stat().st_mtime_ns) for p in self.run.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        invalid = json.loads(json.dumps(self.flow))
        invalid["nodes"][0]["dependsOn"] = ["report"]
        self.call("revise", data=invalid, ok=False)
        new = {"schemaVersion": 1, "nodes": [self.flow["nodes"][0], self.node("review", ["needs"], [], []), self.node("report", ["review"], [], [])]}
        self.call("revise", data=new)
        self.assertEqual(self.call("plan")["rerunOrder"], ["review", "report"])
        self.call("inspect", "report")
        self.call("invalidate", "needs", data={"reason": "business acceptance revised"})
        self.assertEqual(self.call("plan")["rerunOrder"], ["needs", "review", "report"])

    def test_existing_run_lock_and_snapshot_corruption(self):
        self.call("init", data=self.flow, extra=["--workspace", str(self.root)], ok=False)
        (self.run / ".lock").mkdir()
        self.call("start", "needs", ok=False)
        self.assertTrue((self.run / ".lock").exists())
        (self.run / ".lock").rmdir()
        self.complete("needs")
        self.complete("report")
        details = self.call("inspect", "needs")["trace"]
        obj = self.run / details["execution"]["outputs"]["result"]["snapshot"]
        obj.write_text("corrupted", encoding="utf-8")
        self.assertFalse(self.call("inspect")["nodes"]["needs"]["current"])
        self.assertFalse(self.call("inspect", "needs")["trace"]["evidenceVerified"])
        self.assertFalse(self.call("inspect", "report")["trace"]["evidenceVerified"])

    def test_generated_template_runs_independently(self):
        copied = self.root / "generated-skill/scripts/ledger.py"
        copied.parent.mkdir(parents=True)
        copied.write_bytes(SCRIPT.read_bytes())
        result = subprocess.run([sys.executable, str(copied), "plan", "--run", str(self.run)],
                                capture_output=True, text=True, encoding="utf-8", cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["rerunOrder"], ["needs", "portrait", "report"])


if __name__ == "__main__":
    unittest.main()
