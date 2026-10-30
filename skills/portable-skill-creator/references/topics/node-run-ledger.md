# Node run ledger

Read while designing execution observability (main-line step 4), then return with the node contract, storage choice and acceptance checks. Read during implementation only for the concrete template contract below.

## Responsibilities and records

The Creator defines the contract and provides generation assets. Each target Skill owns its workflow, strategies, acceptance criteria and run storage. Reuse its existing deterministic execution surface when available; otherwise the standalone Python template in `assets/node-ledger/ledger.py` can be copied as a generation asset into that target Skill's own scripts. It needs Python 3.10+ only and runs independently of this Creator after generation. Record the template version in development provenance; later changes are reviewed migrations, not hidden live dependencies.

Keep design decisions, actual run evidence, and development evaluation separate. Run records describe observable inputs, decisions/results, files and status; private model reasoning is outside this contract. Keep secrets out of summaries and parameters. Evidence snapshots can contain business-sensitive material: use the project's authorized private storage and retention policy; public packages exclude run data.

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
