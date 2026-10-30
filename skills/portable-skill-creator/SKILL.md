---
name: portable-skill-creator
description: Create, update, review, test, or port Agent Skills through the current base skill-creator plus a portable cross-Agent design protocol. Use by default for Skill authoring that needs explicit I→S→O contracts, knowledge internalization, main-line and branch design, capability contracts, Codex/SealSeek/OpenClaw adapters, privacy checks, user-approved standard answers, or honest compatibility evidence. Do not use only when the user explicitly requests the bundled/system skill-creator alone.
---

# Portable Skill Creator

Build maintainable Agent Skills without copying or shadowing the current platform's base creator. Treat a Skill as an executable knowledge manual: it may begin as a reusable prompt, but a mature Skill defines inputs, strategy, outputs, decision nodes, execution capabilities, failure behavior, QA, and evolution boundaries.

## Package Runtime

This Skill is distributed by `@petercjl/portable-skill-creator`. At ordinary task entry, run `node <this Skill directory>/.runtime/bin/portable-skill-creator.mjs prepare --json` for bounded update detection and dependency diagnosis, then return to Authority And Dynamic Composition below. A source checkout uses the package's `bin/portable-skill-creator.mjs` entry. Updates are advisory; installation requires explicit authorization. `PORTABLE_SKILL_UPDATE_CHECK=0` disables detection. The package does not supply or replace the host's base creator.

Bundled deterministic checks are available through `validate --path <absolute target Skill directory> --profile <profile> --mode <direct|hybrid|knowledge-compiled> --json`. The current Agent separately runs its dynamically resolved base creator's format validator. Required capabilities are base-creator resolution, safe filesystem access, command execution, Node.js 22+, and Python 3.10+. Any Agent satisfying these contracts may use the generic adapter; named adapters retain their own dated evidence. Resolve nested Skills by exact logical name from the current host's catalog/configured roots and read their complete instructions; missing dependencies return `DEPENDENCY_MISSING` and the required logical name.

## Authority And Dynamic Composition

1. Resolve the currently advertised base `skill-creator` or equivalent by exact logical name and read its complete current `SKILL.md`. Do not guess an installation path or use a remembered copy.
2. Use the base creator for current format, scaffolding, metadata, editing, and base validation.
3. Apply this Skill as the portability and method extension. Never copy the base creator into this package or create a writable Skill that shadows it.
4. At the first knowledge-dependent node, read [references/SCHEMA.md](references/SCHEMA.md), [references/index.md](references/index.md), the recent part of [references/log.md](references/log.md), and only the query route matching that node. Do not load the knowledge layer merely because the Skill was invoked. Directory placement is not lazy loading: never turn `references/` into a startup reading list.
5. Always read [references/unified-skill-design-protocol.md](references/unified-skill-design-protocol.md). For knowledge-based work also read [references/knowledge-compiled-skill-method.md](references/knowledge-compiled-skill-method.md). For cross-Agent tools or migration read [references/capability-contract-protocol.md](references/capability-contract-protocol.md), [references/platform-adapters.md](references/platform-adapters.md), and [references/portability-policy.md](references/portability-policy.md).

If the user explicitly asks to use only the bundled/system `skill-creator`, do not apply this extension. A generic request to create or update a Skill is not that exception.

## Main Line

### 1. Classify The Task And Target

Classify the task as `create`, `update`, `review`, `test`, or `port/migrate`. Preserve the difference between read-only review and authorized editing.

Classify the target profile:

- `shareable`: reusable across people and machines; default.
- `internal`: organization-specific but not author-machine-specific.
- `platform`: intentionally tied to one Agent/runtime.
- `local`: intentionally tied to the current machine.

Record intended Agents, operating systems, input/output expectations, external dependencies, permissions, paid actions, and compatibility claims. Never silently downgrade a target.

### 2. Define The Real Problem And I → S → O

Understand the recurring user problem before discussing files:

- who uses the Skill and why the task repeats;
- typical and optional inputs;
- business logic, judgment, tools, and branches;
- durable artifacts or state produced;
- observable success criteria and frequent failures;
- permissions, costs, and stopping conditions.

Design in two passes. First write the business main line from the user's perspective: accepted inputs, the work to perform in order, decision/hand-off points, and outputs. This pass specifies **what happens**, not the method for every judgment. Then, for each step that needs judgment, define **how to do it**: the strategy question, decision standard, evidence, and QA. Draw strategies from three explicit sources—Agent proposals for user review, relevant Wiki or other traceable enterprise knowledge, and methods supplied by the user. Record provenance and unresolved gaps; an Agent proposal is not a confirmed business rule. Read [Business flow and strategy sources](references/topics/business-flow-and-strategy-sources.md) when creating or substantially redesigning a business Skill, via the current knowledge route.

Define:

- **I — Input:** intent, accepted forms, facts, permissions, and missing-information policy.
- **S — Strategy:** method, main line, decisions, knowledge retrieval, capabilities, error handling, QA, and return points.
- **O — Output:** artifacts/state, schema, user report, and completion evidence.

### 3. Inspect Existing Knowledge And Execution Surfaces

Search for existing Skills, stable CLIs, scripts, MCPs, APIs, schemas, SOPs, examples, and permitted knowledge sources before inventing a new surface. Extend the intended stable CLI or Skill when a reusable need belongs there.

For an existing Skill, inspect its actual `SKILL.md`, referenced resources, scripts, capability declarations, adapters, metadata, and validation evidence before planning changes.

Detect an accessible Wiki or equivalent source. Query it with realistic tasks and decision-node questions, then record:

- source status: accessible, unavailable, or requested-but-unavailable;
- complexity: simple or non-trivial;
- coverage: sufficient, partial, none, or unknown;
- critical gaps;
- selected internalization mode: direct, knowledge-compiled, or hybrid.

Maintain a temporary design knowledge ledger using `W` (Wiki/traceable source), `U` (user-confirmed), `E` (verified execution evidence), and `A` (Agent hypothesis). Record accepted decisions, rejected alternatives, cases, counterexamples, trade-offs, gaps, and candidate evaluations. Synthesize it; never ship raw conversation history.

### 4. Design Control, Knowledge, Evaluation, And Capabilities

For non-trivial Skills, make the topology explicit:

- stable main line;
- branch triggers and named return points;
- node contracts with input, goal, retrieval question, output, constraints, and completion condition;
- deterministic execution resources for fixed or verifiable work;
- QA gates, failure handlers, terminal outcomes, and evolution rules.

Keep the three responsibilities distinct:

1. control layer in `SKILL.md`;
2. optional task mini Wiki in `references/`;
3. development evaluation outside ordinary runtime.

For every knowledge-dependent node, record its trigger, retrieval question, minimum route/pages, completion output, and return point. Also record what remains deferred. A global instruction to read all references or all topics at startup is a design error. When a route needs several files or the target Agent incurs high per-call latency, use one batched read or a small deterministic route loader; do not spend one model turn per file.

Scripts, CLIs, MCPs, APIs, browsers, and native Agent tools are execution resources, not the third layer.

When the Skill targets multiple Agents or uses platform-specific tools, define logical capabilities rather than naming a native tool in the portable core. Use `capabilities.json` and per-platform adapter files as specified in `references/capability-contract-protocol.md`.

### 5. Planning And Confirmation Gate

For a new Skill, a substantial redesign, a creator enhancement, or a cross-Agent migration, the first pass is planning only:

- proposed target and location;
- I → S → O;
- knowledge decision and gaps;
- control, knowledge, execution, capability, and evaluation structure;
- files to create or update;
- validation plan;
- `READY` or `BLOCKED`.

Do not write, install, change routing rules, or mutate external systems until the user confirms the plan. A narrow, already-authorized correction may proceed without repeating a full planning gate.

### 6. Implement Without Leakage Or Silent Degradation

After confirmation:

- use the current base creator's scaffold for new Skills;
- preserve existing files and patch the smallest correct surface for updates;
- use relative paths for bundled resources and semantic configuration for external locations;
- keep secrets in the target runtime's secret mechanism;
- reload applicable file-delivery rules before creating durable artifacts;
- use deterministic scripts for fixed, fragile, high-risk, or mechanically verifiable steps;
- never claim a missing capability is satisfied by an unverified substitute.

For nested Skill dependencies, resolve the exact logical name from the target runtime, read the callee's current complete instructions, execute its documented contract, and return to the caller's named main-line point. Naming another Skill in prose is not dependency injection.

### 7. Validate Disk, Format, Knowledge, Portability, And Capabilities

Run applicable gates separately:

1. inspect real disk content and diff/metadata evidence;
2. run the current platform's base Skill validator;
3. run `scripts/validate_portability.py TARGET --profile PROFILE`;
4. for knowledge-compiled/hybrid Skills, run `scripts/validate_knowledge_layer.py TARGET --mode MODE`;
5. when `capabilities.json` exists, run `scripts/validate_capability_contract.py TARGET` and inspect target-platform gaps with `scripts/inspect_adapter_gaps.py`;
6. test every changed script with representative success and failure cases;
7. validate dependencies, permissions, accounts, and paid-action boundaries;
8. run a realistic main task when the Skill produces artifacts or state;
9. inspect the real artifact against the output contract.

For knowledge-compiled/hybrid Skills, additionally audit the runtime read set: list the files loaded before the first expensive analysis call, verify that each belongs to the current node, and verify that later-node topics and maintenance files remain unloaded. Treat eager full-layer loading as a validation failure even when every file is valid individually.

Static success is not runtime success. Report `spec-compatible`, `adapter-required`, `tested`, `platform-specific`, or `local-only` precisely.

### 8. Main-Run And Standard Answer

Use the main conversation to perform a realistic task and inspect its actual process and artifacts. A candidate output becomes a development standard answer only after the user accepts it and the relevant facts, logic, evidence, file quality, and delivery contract have been checked.

Do not place the standard answer, private acceptance notes, expected conclusions, or failure hints into the ordinary Skill runtime.

### 9. User-Gated Clean Regression

Do not automatically start an isolated subagent or clean-context regression after creation, editing, validation, or a main run.

Run one isolated evaluator only when all are true:

1. a user-approved standard answer or standard artifact exists;
2. the current iteration is complete;
3. the user explicitly asks for clean regression.

The evaluator receives only a natural user request, representative input, ordinary delivery requirements, and safety boundaries. It must not receive the Skill name/path, tool route, design history, standard answer, expected result, suspected gap, or scoring rubric. Use a fresh evaluator for each regression and do not rescue it with follow-up hints.

After regression, report evidence, differences, classification, and recommended changes only. Do not modify the Skill or start another regression unless the user separately authorizes the next update cycle.

### 10. Report Completion Honestly

Report:

- task mode and target profile;
- base creator actually loaded;
- knowledge sources, coverage, and mode;
- files created or changed and disk evidence;
- format, portability, knowledge, capability, dependency, and script results;
- main-run and artifact-audit result;
- clean-regression state;
- platforms and operating systems actually tested;
- unresolved adapters and other limitations.

Use `main-run-pass` when the main task passed but clean regression has not run. Use `clean-regression-not-run` when its three gates are not satisfied or the user has not requested it.

## Branches And Return Rules

### Port Or Migrate A Skill

Keep one canonical portable core. Extract native tool names into capability adapters, inventory required features, create a target-platform gap report, implement only authorized adapters, validate them, and return to Main Line Step 7. Do not copy the core method into each platform adapter.

### Missing Target Capability

Do not invent a tool or silently reduce requirements. Return `CAPABILITY_UNAVAILABLE` or `FEATURE_UNSUPPORTED` with the logical capability, required features, expected input/output, target platform, and validation needed. During an authorized port/update cycle, add or repair only the adapter and return to Step 7.

### Base Creator Changes

Adopt useful current scaffolding, validation, or metadata behavior dynamically. Do not copy it into this Skill. Recheck compatibility and return to Step 7.

### User Requests Platform Or Local Coupling

Honor the narrower target, isolate the coupling, keep secrets external, and label the result accurately. Return to Step 7.

### Regression Finds A Gap

Classify the gap and submit an evaluation report. Stop. Only after user authorization begin a new update cycle at Step 1; do not patch during the regression turn.

## Completion Gate

Do not claim completion until the authorized scope has real disk evidence; current base creator composition, I → S → O, knowledge decision, main line, branches, capability contracts, failure behavior, QA, and output contract are explicit in proportion to complexity; required validators and changed-script tests pass; compatibility claims match evidence; and clean regression is either user-requested and completed or explicitly reported as not run.
