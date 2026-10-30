# Business-flow ledger presentation

The Creator now requires user-facing run ledgers to follow the user’s familiar business flowchart. Business node names, sequence, branches and grouping are preserved, with explicit mappings to underlying execution records and result fields. Node-level status, results and input/output access are primary; strategies, evidence, history and technical details are progressively revealed. Jointly produced dimensions stay inside their owning business node. Strategy updates highlight affected nodes, regenerated downstream outputs and reused results on the same flow.

This patch changes authoring methods and QA requirements; deterministic ledger storage and CLI contracts remain compatible. Business status and reuse must derive from actual mapped evidence; views identify live versus snapshot state and remain read-only. A natural-language business flow is accepted, and the user need not supply a diagram file. Target Skills own their presentation.

Validation: existing 12 test groups, bundled version/privacy/knowledge/capability checks and base creator validation passed. Actual packed candidate bytes match the source. The previously created application demonstration provides three business nodes, jointly produced dimensions, node/result navigation, strategy-update/reuse markers, historical evidence links and unchanged run/output hashes; six panel transitions and all links passed. This is main-conversation evidence, not an independent clean-context evaluation or browser visual acceptance.

Publication and exact public-version/Codex-install verification are recorded after release.
