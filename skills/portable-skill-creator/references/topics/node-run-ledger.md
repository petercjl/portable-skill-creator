# Node run ledger

Read while designing execution observability (main-line step 4), then return with the node contract, storage choice and acceptance checks. Read during implementation only for the concrete template contract below.

## Responsibilities and records

The Creator defines the contract and provides generation assets. Each target Skill owns its workflow, strategies, acceptance criteria and run storage. Reuse its existing deterministic execution surface when available; otherwise the standalone Python template in `assets/node-ledger/ledger.py` can be copied as a generation asset into that target Skill's own scripts. It needs Python 3.10+ only and runs independently of this Creator after generation. Record the template version in development provenance; later changes are reviewed migrations, not hidden live dependencies.

Keep design decisions, actual run evidence, and development evaluation separate. Run records describe observable inputs, decisions/results, files and status; private model reasoning is outside this contract. Keep secrets out of summaries and parameters. Evidence snapshots can contain business-sensitive material: use the project's authorized private storage and retention policy; public packages exclude run data.

## Business-flow presentation contract

Every user-facing run ledger follows the user's business flowchart. Retain the user's familiar node names, sequence, branches and grouping. A business flow described in natural language is sufficient; a mind map or diagram file is optional. A simple task may have one business node. Keep an explicit mapping from stable business node ids to execution records, output sections or result fields. Several implementation steps may belong to one business node; several result dimensions may be produced by one joint operation. Present those dimensions within that business node, preserving actual concurrency and hand-offs.

At each business node show the current status/freshness, a short result and access to its inputs/outputs. Selecting or expanding it reveals actual strategies, source evidence, acceptance and historical results. Put attempt ids, hashes, tool calls and implementation-node graphs in expandable technical evidence. This preserves the user's business navigation while retaining full audit detail. The target Skill owns its presentation and mapping; the file-ledger asset supplies records and does not generate a user interface by itself.

When a strategy changes, highlight the affected business node or result dimension, the downstream business outputs regenerated, and the unaffected results retained. Derive reuse claims from actual attempt/field identities and content evidence. Preserve historical business views or reconstruct them from exact historical records. Do not label an old result as using a new strategy.

Derive business status from all required mapped execution records, their freshness, acceptance and output evidence. Surface pending, running, failed, blocked, missing, stale and unverified conditions; a completed low-level action alone does not establish business completion. Keep terminal state and freshness distinguishable. Label whether the view is live or an explicitly dated/versioned snapshot. Viewing, expanding or switching history is read-only and does not trigger reruns or external actions.

Validate the projection with a real run: compare the shown nodes/edges/groupings with the agreed business flow; open each node's results, inputs/outputs and evidence; change a strategy and inspect affected/reused markers; confirm that failures or stale results cannot appear complete; verify historical links and that inspection leaves records unchanged. Check the rendered presentation when the host supports it, and report visual inspection separately from static/link/interaction checks.

## Node definition

Use stable ids, readable titles, upstream node ids, accepted input references, strategy references, output keys and explicit acceptance check names. The file template uses `{schemaVersion:1,nodes:[{id,title,dependsOn,inputs,strategies,outputKeys,checks}]}`. Paths are workspace-relative. Its validator rejects duplicate ids, missing dependencies and cycles. `outputKeys` and `checks` are nonempty. Strategy pages carry evolving judgment; workflow definitions carry execution contracts. Small flows may have one strategy page and a single node.

## One execution

Create a run id and immutable workflow baseline. Each node attempt records id/ordinal, its predecessor, node definition, actual input and strategy content hashes/snapshots, upstream attempt ids, parameters, external task identifiers when applicable, timestamps, terminal state, output paths/hashes/snapshots, a concise result summary and check results.

Record at business-node granularity. Small transient tool calls need evidence only when they affect verification or recovery. A document can combine several output sections if each node has a stable section/result reference. The file template requires file outputs; targets with databases, document APIs or external objects must implement equivalent revision-aware evidence adapters rather than pretend a local path proves an external write.

Lifecycle: pending → running → completed/failed/blocked/skipped. Freshness is a separate current/stale property. Completed requires every declared output to exist and every declared acceptance check to pass. The Agent/business validator supplies truthful semantic checks; the ledger checks structure, bytes and dependencies, not the correctness of a natural-language conclusion. Failed, blocked and skipped require reasons. A skipped node does not satisfy downstream dependencies automatically; revise the branch contract explicitly when omission is valid.

## Template operations

Run `python scripts/ledger.py ACTION --run RUN` in the generated target's environment. These are developer/Agent operations, not instructions for end users to type.

- `init --workspace PROJECT --data workflow.json`: create a new run, refusing an existing directory.
- `start --node ID [--data context.json]`: verify current upstream results, snapshot inputs/strategies and append a running attempt; returns the attempt id. Context may include parameters and an existing externalTask id.
- `finish --node ID --attempt EXACT_ID --data result.json`: result contains status, summary, outputs (key→workspace-relative path), checks (name→boolean), and optional externalTask. Completion refuses changed inputs/upstream or failing checks. A rejected finish leaves the attempt running for inspection and correction.
- `inspect [--node ID] [--attempt ID]`: read current freshness and recursively trace the exact historical upstream attempts. Evidence objects remain available when live files are edited or removed.
- `plan`: read-only topological rerun order, reusable nodes, reasons, blocked dependencies and running attempts. It does not execute or authorize work.
- `invalidate --node ID --data reason.json`: preserve history and mark this node and dependent results stale; reason is required.
- `revise --data workflow.json`: validate and append a new workflow revision; preserve removed nodes' history; resolve running attempts first.

Store run.json as the baseline, immutable sequence/hash-linked events under events/, and content-addressed evidence under objects/. A mutation acquires .lock and publishes a new event only after the evidence is ready. Read-only operations do not alter state. Interrupted writes may leave unreferenced objects or .pending files; the last committed event remains authoritative. A surviving lock requires checking the actual process before an authorized removal. External actions are never retried by the ledger.

Return from implementation with a real run showing inspect/trace/plan and verified artifacts, not only a schema file.
