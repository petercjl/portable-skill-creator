#!/usr/bin/env python3
"""Portable file-based node ledger template. Python 3.10+, standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone
from uuid import uuid4


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")


def write_new(path, data):
    require(not path.exists(), "Existing file is preserved: " + str(path))
    with path.open("xb") as out:
        out.write(encoded(data))
        out.flush()
        os.fsync(out.fileno())


def workflow(data):
    require(data.get("schemaVersion") == 1, "workflow schemaVersion must be 1")
    nodes = data.get("nodes")
    require(isinstance(nodes, list) and nodes, "nodes must be a non-empty array")
    mapped = {}
    for node in nodes:
        key = node.get("id")
        require(isinstance(key, str) and key and all(c.isalnum() or c in "-_" for c in key), "Invalid node id")
        require(key not in mapped, "Duplicate node id")
        require(isinstance(node.get("title"), str) and node["title"], "Node title required")
        for field in ["dependsOn", "inputs", "strategies", "outputKeys", "checks"]:
            values = node.get(field)
            require(isinstance(values, list) and all(isinstance(v, str) and v for v in values), field + " must be a string array")
            require(len(values) == len(set(values)), field + " contains duplicates")
        require(node["outputKeys"] and node["checks"], "Declare outputKeys and acceptance checks")
        mapped[key] = node
    ordered = []
    visiting = set()

    def visit(key):
        require(key in mapped, "Unknown dependency: " + key)
        require(key not in visiting, "Workflow cycle: " + key)
        if key in ordered:
            return
        visiting.add(key)
        for dep in mapped[key]["dependsOn"]:
            visit(dep)
        visiting.remove(key)
        ordered.append(key)
    for key in mapped:
        visit(key)
    return mapped, ordered


def safe_file(workspace, relative):
    require(isinstance(relative, str) and relative, "File reference required")
    p = Path(relative)
    require(not p.is_absolute() and ".." not in p.parts, "Use workspace-relative file references")
    result = (workspace / p).resolve()
    require(result.is_relative_to(workspace) and result.is_file(), "File missing or outside workspace: " + relative)
    return result


def snapshot(run, workspace, relative):
    p = safe_file(workspace, relative)
    data = p.read_bytes()
    sha = digest(data)
    obj = run / "objects" / sha
    if obj.exists():
        require(digest(obj.read_bytes()) == sha, "Corrupt evidence snapshot")
    else:
        with obj.open("xb") as out:
            out.write(data)
    return {"path": relative, "sha256": sha, "size": len(data), "snapshot": "objects/" + sha}


def load(run):
    state = read(run / "run.json")
    events = sorted((run / "events").glob("*.json"))
    previous = digest(encoded(state))
    for index, p in enumerate(events, 1):
        require(p.name == f"{index:06d}.json", "Incomplete event sequence; inspect before recovery")
        event = read(p)
        require(event["previous"] == previous, "Event history integrity mismatch")
        state = event["state"]
        previous = digest(encoded(event))
    return state, len(events), previous


def view(run, state):
    nodes, ordered = workflow(state["workflow"])
    workspace = Path(state["workspace"])
    rows = {}
    for key in ordered:
        node = nodes[key]
        history = state["attempts"].get(key, [])
        a = history[-1] if history else None
        reasons = []
        if a:
            if a["definition"] != digest(encoded(node)):
                reasons.append("node-definition-changed")
            if a["generation"] != state["generations"].get(key, 0):
                reasons.append("explicit-invalidation")
            for item in a["inputs"] + a["strategies"] + list(a.get("outputs", {}).values()):
                try:
                    require(digest(safe_file(workspace, item["path"]).read_bytes()) == item["sha256"], "changed")
                    require(digest((run / item["snapshot"]).read_bytes()) == item["sha256"], "corrupt")
                except (ValueError, OSError):
                    reasons.append("missing-or-changed:" + item["path"])
            for dep in node["dependsOn"]:
                if not rows[dep]["current"] or a["dependencies"].get(dep) != rows[dep]["attempt"]:
                    reasons.append("upstream-invalid:" + dep)
        blocked = [dep for dep in node["dependsOn"] if not rows[dep]["current"]]
        status = a["status"] if a else "pending"
        current = bool(a and status == "completed" and not reasons)
        rows[key] = {"node": key, "title": node["title"], "status": status,
                     "attempt": a["id"] if a else None, "current": current,
                     "stale": bool(a and reasons), "reasons": reasons, "blockedBy": blocked,
                     "summary": a.get("summary", "") if a else "", "outputs": a.get("outputs", {}) if a else {}}
    return rows, ordered


def trace(state, node, attempt=None, visited=None, run=None):
    history = state["attempts"].get(node, [])
    require(history, "Node has no execution history")
    a = next((x for x in history if x["id"] == attempt), None) if attempt else history[-1]
    require(a is not None, "Unknown attempt")
    visited = set() if visited is None else visited
    marker = (node, a["id"])
    require(marker not in visited, "Invalid history dependency cycle")
    visited = visited | {marker}
    issues = []
    for item in a["inputs"] + a["strategies"] + list(a.get("outputs", {}).values()):
        try:
            require(digest((run / item["snapshot"]).read_bytes()) == item["sha256"], "corrupt")
        except (ValueError, OSError):
            issues.append(item["snapshot"])
    return {"node": node, "execution": a, "evidenceVerified": not issues, "evidenceIssues": issues,
            "upstream": [trace(state, dep, aid, visited, run) for dep, aid in a["dependencies"].items()]}


def operate(run, action, node=None, payload=None, attempt=None):
    state, count, previous = load(run)
    rows, ordered = view(run, state)
    nodes, _ = workflow(state["workflow"])
    now = datetime.now(timezone.utc).isoformat()
    payload = payload or {}
    if action == "inspect":
        return {"ok": True, "runId": state["runId"], "nodes": rows,
                "trace": trace(state, node, attempt, run=run) if node else None}
    if action == "plan":
        return {"ok": True, "runId": state["runId"], "reuse": [k for k in ordered if rows[k]["current"]],
                "rerunOrder": [k for k in ordered if not rows[k]["current"]],
                "running": [k for k in ordered if rows[k]["status"] == "running"],
                "nodes": rows, "executionAuthorized": False}
    require(node in nodes or action == "revise", "Unknown workflow node")
    workspace = Path(state["workspace"])
    if action == "start":
        require(not rows[node]["blockedBy"], "Upstream nodes must have current accepted results")
        history = state["attempts"].setdefault(node, [])
        require(not history or history[-1]["status"] != "running", "Inspect interrupted execution and explicitly close it before retrying")
        definition = nodes[node]
        a = {"id": uuid4().hex, "node": node, "ordinal": len(history) + 1,
             "supersedes": history[-1]["id"] if history else None,
             "startedAt": now, "status": "running", "definition": digest(encoded(definition)),
             "nodeDefinition": definition, "generation": state["generations"].get(node, 0),
             "inputs": [snapshot(run, workspace, p) for p in definition["inputs"]],
             "strategies": [snapshot(run, workspace, p) for p in definition["strategies"]],
             "dependencies": {dep: rows[dep]["attempt"] for dep in definition["dependsOn"]},
             "parameters": payload.get("parameters", {}), "externalTask": payload.get("externalTask")}
        history.append(a)
    elif action == "finish":
        history = state["attempts"].get(node, [])
        require(history and history[-1]["status"] == "running", "Node is not running")
        a = history[-1]
        require(attempt == a["id"], "Supply the exact running --attempt id")
        status = payload.get("status")
        require(status in ["completed", "failed", "blocked", "skipped"], "Invalid terminal status")
        require(isinstance(payload.get("summary"), str) and payload["summary"].strip(), "Summary or failure/skip reason required")
        outputs = payload.get("outputs", {})
        checks = payload.get("checks", {})
        require(isinstance(outputs, dict) and isinstance(checks, dict), "outputs/checks must be objects")
        if status == "completed":
            require(not rows[node]["reasons"], "Inputs, strategies or upstream changed during execution")
            require(set(outputs) == set(nodes[node]["outputKeys"]), "Required outputs mismatch")
            require(set(checks) == set(nodes[node]["checks"]) and all(v is True for v in checks.values()), "All declared acceptance checks must pass")
        a.update({"status": status, "endedAt": now, "summary": payload["summary"], "checks": checks,
                  "outputs": {k: snapshot(run, workspace, p) for k, p in outputs.items()},
                  "externalTask": payload.get("externalTask", a.get("externalTask"))})
    elif action == "invalidate":
        require(isinstance(payload.get("reason"), str) and payload["reason"].strip(), "Invalidation reason required")
        state["generations"][node] = state["generations"].get(node, 0) + 1
    elif action == "revise":
        workflow(payload)
        require(not any(row["status"] == "running" for row in rows.values()), "Resolve running nodes before revising workflow")
        state["workflow"] = payload
    else:
        raise ValueError("Unsupported operation")
    event = {"schemaVersion": 1, "action": action, "node": node, "at": now, "previous": previous,
             "reason": payload.get("reason"), "state": state}
    destination = run / "events" / f"{count+1:06d}.json"
    require(not destination.exists(), "Event exists; reload before mutation")
    temp = run / (".pending-" + uuid4().hex)
    write_new(temp, event)
    os.rename(temp, destination)
    updated, _ = view(run, state)
    return {"ok": True, "event": destination.name, "node": updated.get(node), "runId": state["runId"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "start", "finish", "inspect", "plan", "invalidate", "revise"])
    parser.add_argument("--run", required=True)
    parser.add_argument("--workspace")
    parser.add_argument("--data", help="JSON input file; workflow for init/revise, operation data for other writes")
    parser.add_argument("--node")
    parser.add_argument("--attempt")
    args = parser.parse_args()
    run = Path(args.run).resolve()
    payload = read(args.data) if args.data else None
    if args.action == "init":
        workflow(payload or {})
        require(args.workspace is not None, "--workspace required")
        workspace = Path(args.workspace).resolve()
        require(workspace.is_dir(), "Workspace must exist")
        require(not run.exists(), "Existing run is preserved")
        run.mkdir(parents=True)
        (run / "objects").mkdir()
        (run / "events").mkdir()
        write_new(run / "run.json", {"schemaVersion": 1, "runId": uuid4().hex,
                  "workspace": str(workspace), "workflow": payload, "attempts": {}, "generations": {}})
        result = {"ok": True, "run": str(run), "runId": read(run / "run.json")["runId"]}
    elif args.action in ["inspect", "plan"]:
        result = operate(run, args.action, args.node, payload, args.attempt)
    else:
        require(run.is_dir(), "Run does not exist")
        lock = run / ".lock"
        lock.mkdir()  # Existing lock is never silently removed or stolen.
        try:
            result = operate(run, args.action, args.node, payload, args.attempt)
        finally:
            lock.rmdir()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
