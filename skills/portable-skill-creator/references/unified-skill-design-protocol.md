# Unified Skill Design Protocol

Protocol version: `2026-09-18-v5`

Use this protocol as the platform-neutral design contract for creating, updating, reviewing, testing, and porting Agent Skills. Platform creators may add adapters, but must not replace or fork these core principles.

## 1. Task Modes

Classify the request before editing:

1. **Create**: build a new Skill from a recurring capability need.
2. **Update**: preserve the existing Skill and change only the affected main line, branch, resource, dependency, or output contract.
3. **Review**: inspect design and evidence; do not modify unless the user authorized changes.
4. **Test**: execute a realistic regression against the Skill on disk and classify the evidence.
5. **Port/migrate**: preserve one canonical core, map its logical capabilities to a target Agent, and report unresolved gaps without silently weakening the contract.

Do not treat review authorization as edit authorization. Do not treat a successful design-conversation run as a clean test.

For a new Skill, substantial redesign, creator enhancement, or cross-Agent migration, produce the design and validation plan first. Write only after user confirmation. A narrow correction within already authorized scope does not require repeating the full gate.

## 2. Definition Contract

Before implementation, define an explicit `I → S → O` contract:

- **I — Input**: user intent, required and optional inputs, accepted forms, facts, permissions, and missing-information policy.
- **S — Strategy**: business method, decision rules, main line, branches, deterministic tool nodes, error handling, QA gates, and return-to-main-line points.
- **O — Output**: artifacts, state changes, file/schema contract, user-facing report, and success/failure evidence.

Build that contract in two passes:

1. **Business flow:** from the user's task, identify accepted inputs, ordered work steps, decisions or hand-offs, and outputs. Keep this pass at the level of what must happen and what each step hands to the next; do not bury the business flow under tool commands or step-specific judgment rules.
2. **Strategy per step:** for each step requiring judgment, state the question to resolve, how evidence is used, the decision standard, failure or uncertainty branch, and completion check. A mechanical step may need only a deterministic contract rather than a long strategy.

Use three sources to develop a step's strategy: an Agent-proposed candidate reviewed by the user (`A` until accepted), relevant Wiki or other traceable enterprise knowledge (`W`, with scope and currency checked), and a method directly supplied or confirmed by the user (`U`). Verified platform or external evidence (`E`) may test or constrain any of them. Record which source supports each material rule, conflicts or missing coverage, and the point at which a proposed method becomes accepted. A reusable user-supplied method is a candidate for knowledge-base compilation, subject to the normal write authorization and provenance rules.

Also state:

- who uses the Skill and what recurring problem it solves;
- what is in scope and explicitly out of scope;
- what “success” means and how it can be checked;
- target profile and Agents/platforms;
- runtime, dependency, account, permission, and external-service requirements.

If a missing user choice would materially change the contract, ask. Otherwise make a bounded assumption, record it, and proceed under the host Agent's autonomy rules.

## 3. Knowledge Discovery And Internalization

Search available Skills, stable CLIs, APIs, schemas, SOPs, permitted knowledge bases, examples, and current platform documentation before inventing a new execution surface.

The user does not need to know or request the three-layer method. During every creation or substantial update, detect whether the current user has an accessible Wiki or equivalent structured knowledge source. If one exists, use knowledge-compiled or hybrid internalization by default for non-trivial Skills. Keep direct internalization for genuinely simple, stable, mostly mechanical Skills. If no Wiki is accessible and the user did not request knowledge-based creation, use the ordinary direct method by default.

Before finalizing the mode, record a compact knowledge decision:

- source status: accessible, unavailable, or requested-but-unavailable;
- task complexity: simple or non-trivial;
- coverage: sufficient, partial, none, or unknown;
- critical gaps that would change strategy, facts, safety, or output;
- selected mode and why the alternatives were rejected.

Judge coverage with realistic user tasks and important decision-node questions. A large Wiki can still have no relevant knowledge. When coverage is partial, use a hybrid design and preserve an explicit gap register. When an accessible Wiki has no relevant coverage but the Skill is non-trivial, bootstrap the local knowledge layer from accepted design knowledge, user confirmation, and permitted verified evidence; label provenance and gaps honestly. If knowledge-based creation was explicitly requested but no source is accessible, stop and report the dependency rather than fabricating a Wiki-derived method.

Classify each important method source:

- user-confirmed requirement;
- bundled/shareable reference;
- verified external or platform documentation;
- deterministic tool or observed runtime behavior;
- Agent-derived method or hypothesis.

Convert useful knowledge into executable instructions:

```text
input → action/decision → output → validation
```

Internalize frameworks as decisions and steps, rules as branch or QA conditions, and tables as concise decision logic. Do not copy large source documents merely to prove provenance.

For shareable Skills:

- package the generalizable method, not the creator's private context;
- include only sanitized references that the Skill genuinely needs at runtime or for future maintenance;
- never require an author-only Wiki or absolute private path;
- preserve source attribution at the method/section level when it helps future evolution.

Private source material may inform the design but must not become a hidden runtime dependency. Do not copy private pages verbatim into a shareable Skill unless the user explicitly authorizes redistribution and the content passes privacy/copyright review.

Choose the internalization mode explicitly:

- **direct**: encode a small, stable mechanical method as executable contracts; core domain judgment uses a compact separate strategy reference;
- **knowledge-compiled**: compile an evolving body of judgment into a routed local mini Wiki;
- **hybrid**: keep hard contracts in `SKILL.md` and soft domain judgment in the local Wiki.

For knowledge-compiled and hybrid designs, read and follow `knowledge-compiled-skill-method.md` protocol version `2026-09-01-v4`. Do not flatten all knowledge into fixed steps merely to make execution look deterministic.

During requirement discovery and design discussion, maintain a temporary design knowledge ledger containing accepted decisions, rejected alternatives and reasons, cases, counterexamples, trade-offs, evidence boundaries, hypotheses, gaps, and candidate evaluation cases. At implementation time, synthesize ledger content into the correct layer: hard contracts into `SKILL.md`, reusable soft knowledge into the mini Wiki, and tests/benchmarks/failure analysis into development evaluation. Do not ship raw chat history or private reasoning traces.

Classify source contributions as `W` (accessible Wiki), `U` (user-confirmed), `E` (verified external/platform evidence), or `A` (Agent-derived method or hypothesis). Agent-derived material must not silently become a business fact.

## 4. Skill Topology

A Skill is an execution manual for an LLM, not just a prompt and not merely a rigid workflow.

Every non-trivial Skill should make these structures explicit:

- goal and main line;
- branch trigger and branch-specific action;
- deterministic tool/script/CLI/MCP/API nodes;
- failure and dependency handlers;
- patch areas for known recurring exceptions;
- QA and output gates;
- return-to-main-line points;
- evolution rule describing how a reported failure enters a separately authorized update cycle.

The main line remains stable while the Agent may adapt low-risk details to the current input. A branch must either return to a named main-line point or end with an explicit terminal result.

Use deterministic code for fixed, important, high-risk, repetitive, or mechanically verifiable work. Keep judgment-heavy business decisions in instructions backed by references and observable evidence.

## 4.1 Logical Capability Contracts

When native tools differ across Agents, keep the portable core expressed in logical capabilities and feature requirements. Declare those requirements in `capabilities.json`; put native mappings in `adapters/<platform>.json`.

A capability declaration must identify its logical ID, required features, input fields, output fields, side effects, authorization boundary, and whether it is required. An adapter mapping must identify the platform implementation, implemented features, status, and test evidence when status is `tested`.

Do not equate an Agent-native tool with a portable executable wrapper. A stable CLI may expose one cross-platform executable contract. An Agent-native generator, browser, or delegation function instead needs an instruction-level adapter that normalizes results to the declared output contract. Runtime execution must never edit its own adapter; unresolved mappings are completed only in an authorized port or update cycle.

## 4.2 Observable execution and local reruns

Use stable business node ids and target-owned run records. Record actual inputs, strategy identities, upstream attempt ids, output evidence, summaries and acceptance. Preserve historical attempts and snapshots; derive freshness from changed contracts, inputs, strategies, artifacts and dependencies. Flow edits reconnect contracts, and strategy edits preserve or migrate output interfaces. Enter `queries/design-node-observability.md` for the recording and recovery method; return to step 4, then validate real node outputs at step 7. Design discussion records and evaluation reports serve separate purposes from runtime evidence.

## 5. Resource Distribution

Place information according to how it is used:

- `SKILL.md`: routing, core contract, main line, branches, tool contracts, QA, and resource navigation.
- `references/`: schemas, domain rules, maintenance sources, detailed variants, and templates that must be read.
- `scripts/`: deterministic repeated operations with declared inputs, outputs, dependencies, and errors.
- `assets/`: files copied or transformed into outputs.
- platform metadata/adapters: discovery, UI, permission, installation, and native tool mappings.

Avoid duplicate sources of truth. The base/system creator is always loaded dynamically; never copy it into a custom enhancement Skill.

Design reviews and regression reports are validation evidence, not automatic runtime dependencies. Do not ship `DESIGN-REVIEW.md`, changelogs, or test reports inside every Skill by default. Include a maintenance artifact only when the target runtime or user explicitly requires it and it passes the output/package policy.

When a local mini Wiki is justified, its minimum navigation surface is `SCHEMA.md`, `index.md`, `log.md`, `source-manifest.md`, realistic `queries/` entries, and synthesized topic pages. The source manifest records `W/U/E/A` provenance, coverage, critical gaps, and recompilation boundaries. The runtime follows query routes and reads only the minimum needed pages; the source manifest is maintenance provenance rather than a default runtime reading list.

Physical separation under `references/` does not provide lazy loading. Each knowledge-dependent main-line node must name its trigger or retrieval question, the minimum route/pages it loads, and its return point. Do not create a global startup step that reads the whole mini Wiki. Later-node knowledge and maintenance pages remain deferred until needed. For multi-file routes on high-latency Agents, prefer one batched read or a deterministic route loader over one model turn per file.

## 6. Implementation Rules

- Inspect existing files and preserve user-owned content before writing.
- New Skills use the current base creator's scaffold and metadata mechanisms.
- Updates patch the smallest correct surface and verify the actual disk state.
- Use relative paths for bundled resources and semantic runtime configuration for external locations.
- Declare supported environments honestly; do not claim untested compatibility.
- Extend an intended stable CLI or script interface when a recurring need appears instead of leaving a one-off workaround.
- Keep platform-specific commands in adapters; keep the core capability and contracts platform-neutral.
- Do not silently substitute a weaker capability. Return `CAPABILITY_UNAVAILABLE` or `FEATURE_UNSUPPORTED` with the missing logical ID and feature set.

## 7. Validation Ladder

Run the applicable layers separately and report each result:

1. **Disk evidence**: expected content exists in the real target files; inspect with reads, search, metadata, checksum, or diff.
2. **Format validation**: frontmatter, naming, structure, and referenced resources.
3. **Privacy/portability validation**: no secrets, private machine leakage, undeclared coupling, or dead references.
4. **Dependency validation**: runtimes, packages, CLIs, accounts, permissions, and installation/discovery paths.
5. **Script/tool validation**: representative real inputs and failure paths.
6. **Main-run validation**: a small realistic task produces a real artifact or state result.
7. **Clean-context regression, when authorized**: one fresh evaluator receives a natural user request without the Skill name/path, tool route, design rationale, suspected bug, expected answer, scoring rubric, or temporary hints.
8. **Independent artifact audit**: inspect the produced files/state against the formal output contract.

For knowledge-compiled/hybrid Skills, validation also includes a runtime read-set audit for one realistic path: record every reference loaded before the first expensive analysis call, justify it by the current node, and confirm that later-node topics and `source-manifest.md` were not eagerly loaded.

Clean regression is not an automatic completion step. Run it only when a user-approved standard answer/artifact exists, the current iteration is complete, and the user explicitly requests the regression. Use one new evaluator per run. If isolation is unavailable or would cause unapproved cost/live mutation, run the strongest safe evidence layers and report `clean-regression-not-run` rather than fabricating a pass.

Test sets, acceptance standards, independent review, and expensive model-based QA belong to creation, update, recompilation, and release by default. Ordinary runtime should retain deterministic contract checks and task-required safeguards, not rerun the full development evaluation suite.

Do not require byte-for-byte identical natural-language results. Compare routing, facts, business logic, tool usage, output contract, and artifact quality.

## 8. Regression Prompt Integrity

A clean regression should receive:

- a natural user request;
- real or representative input;
- ordinary delivery requirements;
- an isolated write scope and safety boundary when artifacts are produced.

Do not give it:

- the intended fix or suspected gap;
- expected answer or reference artifact;
- prior design conversation;
- private acceptance notes;
- platform routing hints unless the user would naturally provide them.
- the Skill name or path, native tool route, design history, scoring rubric, or known failure classification.

The evaluator must discover ordinary routing from the natural request. Verify afterward, through execution evidence where available, whether the intended Skill and capabilities were used. Do not contaminate the prompt to force that result.

## 9. Failure Taxonomy And Write-Back

Classify failures before patching:

| Classification | Meaning |
|---|---|
| `pass` | Required routing, execution, artifact, and evidence passed |
| `partial-pass` | Useful result, but a required layer or branch was not exercised |
| `false-pass` | Success was claimed without relying on the target Skill or without real evidence |
| `skill-gap` | Main line, branch, method, tool contract, QA, or return rule is incomplete |
| `disk-gap` | Intended changes are absent from the actual Skill files |
| `trigger-gap` | A natural request did not reliably load the target Skill |
| `timeout-gap` | The Skill was loaded but the run did not finish within a justified window |
| `runtime-gap` | Platform/runtime failed before the Skill actually began |
| `output-gap` | Execution completed but the artifact/state violates the output contract |
| `context-leak` | Success depends on design history, hidden hints, or expected answers |
| `test-gap` | The test does not cover the changed user-level path |
| `tool-gap` | Required capability, dependency, account, or permission is unavailable |
| `capability-gap` | Logical capability or required feature has no valid target-platform mapping |
| `adapter-gap` | A target mapping is unresolved, unsupported, stale, or lacks evidence |
| `main-run-pass` | The realistic main task passed; clean regression has not run |
| `clean-regression-not-run` | The clean-regression gates were not all satisfied or the user did not request it |

Write reusable fixes back to the correct layer:

- routing/trigger problem → frontmatter description or platform registration;
- main-line problem → main flow;
- input variation → branch;
- recurring exception → patch/error handler;
- tool confusion → deterministic tool contract or adapter;
- weak output → output schema or QA gate;
- environment issue → dependency detection and failure behavior.

For knowledge-compiled Skills, also classify the failing layer before editing:

- routing, node order, hard boundary, or output contract → control layer;
- missing, stale, weak, or badly routed domain method → knowledge layer;
- repeatable mechanical failure → script/tool layer;
- weak test or acceptance standard → evaluation layer;
- host model, permission, or service behavior → platform/runtime layer.

After an ordinary authorized patch, re-read the disk files and rerun deterministic and main-run checks as appropriate. A clean regression only reports evidence and recommended changes; it must not patch the Skill or start another regression. If the user authorizes changes, begin a new update cycle and use a new evaluator for any later regression.

## 10. Cross-Agent Parity

Keep Agents unified at the contract level:

- same task modes;
- same `I → S → O` definition;
- same knowledge-internalization rules;
- same knowledge-compiled protocol version and three-layer architecture;
- same Skill topology;
- same validation ladder and failure meanings;
- same logical capability and output contracts;
- same privacy and compatibility claims.

Keep these platform-specific:

- Skill discovery and registration;
- UI metadata;
- tool and session/subagent command names;
- sandbox and approval behavior;
- secret injection and installation locations.

Do not synchronize by copying one platform creator wholesale into another. Synchronize the core protocol, then maintain small platform adapters and test each platform independently.

## 11. Completion Report

Report separately:

- task mode and target profile;
- base/system creator actually loaded;
- files created or changed;
- disk and format evidence;
- privacy/portability result;
- dependency and script result;
- main-run result;
- clean-context result;
- Agents/operating systems actually tested;
- remaining untested scope or known limitations.

Compatibility labels must distinguish `tested`, `spec-compatible`, `adapter-required`, `platform-specific`, and `local-only`. An unresolved required adapter is never a tested compatibility claim.
