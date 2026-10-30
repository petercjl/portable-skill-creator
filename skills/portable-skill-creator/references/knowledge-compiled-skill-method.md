# Knowledge-Compiled Skill Method

Protocol version: `2026-09-01-v4`

This is the shared, platform-neutral method for building Skills that must use a strong, evolving body of domain knowledge without freezing the model into a rigid workflow.

## 1. Default Decision Policy

Choose a knowledge-compiled or hybrid design when all or most of these are true:

- the task depends on substantial domain judgment rather than a few stable rules;
- the source knowledge base is strong and will continue to evolve;
- different inputs need different frameworks, cases, or decision paths;
- a large one-time knowledge search produces much better work than an unaided prompt;
- the runtime Skill should reproduce that reasoning with less search and fewer tokens.

Use a direct Skill instead when the task is small, deterministic, stable, or adequately described by a short set of rules. Do not create a miniature Wiki as ceremony.

The user does not need to request this architecture by name. At creation or substantial update time, detect whether the current user has an accessible Wiki or equivalent structured knowledge source. When one is available, use knowledge-compiled or hybrid design by default for every non-trivial Skill, even when the user only says “create a Skill.” When no Wiki is available and the user did not request knowledge-based creation, use the ordinary direct method by default.

Treat a Skill as simple enough for direct internalization only when its method is short and stable, needs little input-dependent judgment, has no meaningful body of cases or trade-offs, is unlikely to evolve as knowledge changes, and is mostly mechanically verifiable. Do not use step count or file count as a proxy. If the classification is genuinely uncertain and an accessible Wiki exists, prefer hybrid.

If the user explicitly requests creation from a Wiki but no source is accessible, do not pretend to have used it. Report the missing capability or source and request the minimum information needed to continue.

## 2. Source Availability And Coverage Audit

Before choosing the final internalization mode, determine:

1. `source_status`: accessible, unavailable, or explicitly requested but unavailable;
2. `task_complexity`: simple or non-trivial, using the judgment criteria above;
3. `coverage`: sufficient, partial, none, or unknown;
4. `critical_gaps`: missing knowledge that would materially change strategy, facts, safety, or output.

Audit coverage with representative user questions and important decision nodes, not only the proposed Skill name. Merely finding a Wiki directory or search result is not evidence of relevant coverage.

Use this default matrix:

| Condition | Default internalization |
| --- | --- |
| Simple task, with or without a Wiki | direct |
| Non-trivial task, accessible Wiki, sufficient coverage | knowledge-compiled or hybrid |
| Non-trivial task, accessible Wiki, partial coverage | hybrid plus an explicit gap register |
| Non-trivial task, accessible Wiki, no relevant coverage | bootstrap a local knowledge layer from accepted design knowledge, while preserving gaps |
| No accessible Wiki and no knowledge-based request | direct |
| Knowledge-based request but source unavailable | explicit dependency blocker; do not fabricate provenance |

When relevant Wiki coverage is weak or absent, the new architecture may still be justified because the Skill-design process can produce reusable knowledge. Do not, however, invent domain facts. Resolve critical gaps through user confirmation or permitted authoritative research; otherwise keep them explicit and reduce the Skill’s claims.

## 3. Three-Layer Architecture

1. **Control layer — `SKILL.md`**: routing, I→S→O contract, main line, node contracts, hard constraints, branch triggers, tool contracts, failure behavior, and resource navigation.
2. **Knowledge layer — local mini LLM Wiki**: compact domain knowledge compiled from permitted sources, with query routes and topic pages. It supplies judgment at runtime without depending on the creator's private Wiki.
3. **Evaluation layer — development evidence**: test cases, acceptance criteria, clean regressions, comparison artifacts, and failure analysis used while creating, updating, recompiling, or releasing the Skill. It is not an ordinary runtime loop.

Keep these layers distinct. A runtime README or planning artifact may expose the Agent's reasoning path to the user, but it is an output contract, not the development evaluation suite.

Scripts, CLIs, MCPs, APIs, and assets are execution resources used by control-layer nodes. They are not a substitute for the third layer. If an architecture is presented as “three layers,” the third layer must be development evaluation, not tools or scripts.

## 4. Hard And Soft Internalization

**Hard-internalize** facts that should not vary with interpretation:

- input/output schemas and file contracts;
- safety, privacy, factual, and product-identity boundaries;
- deterministic tool, CLI, script, and dependency contracts;
- branch triggers, failure handlers, and return-to-main-line rules;
- mechanically verifiable completion conditions.

**Soft-internalize** knowledge that benefits from model judgment:

- business frameworks and diagnostic methods;
- audience, scenario, strategy, creative, and prioritization methods;
- cases, counterexamples, trade-offs, and domain heuristics;
- knowledge that will improve as the source Wiki evolves.

Do not flatten soft knowledge into one permanently fixed sequence. Do not leave hard constraints buried in reference prose.

## 5. Design Knowledge Ledger

During requirement discovery and design discussion, maintain a temporary design knowledge ledger. Capture reusable cognition that would otherwise disappear when the final workflow is shortened:

- the recurring problem, user intent, and representative situations;
- candidate methods, accepted decisions, rejected alternatives, and reasons;
- cases, counterexamples, trade-offs, evidence boundaries, and uncertainty;
- user-confirmed facts and methods;
- external verified knowledge when permitted;
- Agent-derived hypotheses that still require evidence;
- critical and non-critical knowledge gaps;
- natural evaluation cases and acceptance criteria.

Use source classes consistently:

- `W`: compiled from the user’s accessible Wiki or equivalent source;
- `U`: explicitly confirmed by the user during design;
- `E`: verified external or platform evidence;
- `A`: Agent-derived method, inference, or hypothesis.

`A` material may support exploration or a provisional method, but it must not silently become a business fact. Resolve material conflicts by source authority and preserve unresolved disagreement.

At implementation time, synthesize rather than dump the conversation:

```text
hard contracts and stable boundaries → control layer
reusable methods, cases, reasons, trade-offs, and open gaps → knowledge layer
tests, benchmarks, candidate outputs, and failure analysis → development evaluation layer
```

Do not package raw chat history, private reasoning traces, temporary brainstorming, or superseded claims merely to avoid losing information.

## 6. Node Contracts

Each important judgment node should define:

- input;
- goal;
- retrieval question;
- required output;
- hard constraints;
- completion condition;
- return-to-main-line point or terminal result.

The retrieval question is essential: it tells the Agent what it needs to learn from the local Wiki without prescribing the answer in advance.

## 7. Compilation From Sources

1. Read the source Wiki's structure, index, recent log, and search/query instructions when a Wiki is accessible.
2. Query it with realistic user tasks and important node questions, not only abstract topic names.
3. Read the formal pages that support important business decisions and record uncovered nodes.
4. Merge accepted items from the design knowledge ledger without promoting hypotheses to facts.
5. Classify findings as hard constraints, soft methods, cases, counterexamples, source facts, accepted design decisions, hypotheses, or unresolved gaps.
6. Synthesize the minimum sufficient local Wiki. Preserve useful nuance, disagreements, reasons, evidence boundaries, and navigation; do not blindly copy source pages or chat transcripts.
7. Remove secrets, personal paths, private facts, copyrighted bulk text, and author-machine assumptions.
8. Record a sanitized source manifest with source class (`W/U/E/A`), stable page identifier or title when applicable, compile date, coverage, confidence or status, and hashes when appropriate.
9. Test retrieval with real questions. A pile of reference files without working routes is not a compiled knowledge layer.

For a shareable Skill, the compiled local Wiki must be self-contained. The private source Wiki may be used at creation or maintenance time but must not be a hidden runtime dependency.

When the large Wiki has partial or no relevant coverage, label the local layer as bootstrap or partial coverage. Include accepted design knowledge and explicit gaps; do not claim that the large Wiki supplied what it did not contain.

## 8. Minimum Mini-Wiki Structure

Use this structure when a knowledge layer is justified:

```text
references/
  SCHEMA.md
  index.md
  log.md
  source-manifest.md
  queries/
    <real-task-entry>.md
  topics/
    <synthesized-methods-cases-and-boundaries>.md
```

- `SCHEMA.md`: how to navigate and what each area means.
- `index.md`: compact map of topics and common entry points.
- `log.md`: recent knowledge-layer changes that can affect execution.
- `source-manifest.md`: maintenance provenance, not a runtime reading list.
- `queries/`: routes from realistic task questions to the minimum required pages.
- topic pages: synthesized methods, rules, cases, and evidence boundaries.

The source manifest must include overall coverage (`sufficient`, `partial`, `bootstrap`, or `unknown`), critical gaps, source classes, and a recompilation boundary. It must not contain private absolute Wiki paths in a shareable Skill.

The runtime should follow query routes and read only what the current task needs. It should not read every topic page or the source manifest by default.

### 8.1 Lazy Loading Is A Control-Layer Contract

Putting files under `references/` only separates storage; it does not make retrieval lazy. The control layer must prevent eager loading explicitly:

- do not read the mini Wiki when the Skill is merely selected or invoked;
- enter it only when the current strategy reaches a knowledge-dependent node;
- give each node a named route, trigger/retrieval question, minimum pages, required output, and return point;
- keep later-node topics and maintenance files deferred; `source-manifest.md` is never a default runtime page;
- do not write a global startup instruction to read all references, all queries, or all topics;
- when a route contains several files, load them in one parallel read or deterministic route-loader call where the host supports it, while preserving the knowledge-orientation barrier before expensive analysis.

Creation and substantial updates must include a **runtime read-set audit**. For a realistic task, list (a) files loaded before the first expensive analysis call, (b) the current node that justifies each file, and (c) files intentionally deferred to later nodes. If the startup set includes unrelated topics or maintenance provenance, the knowledge routing fails even if the final answer is good.

## 9. Runtime Retrieval Protocol

At a knowledge-dependent node, not at unconditional Skill startup:

1. read `SCHEMA.md`, `index.md`, and the relevant recent portion of `log.md`;
2. formulate the current retrieval question from the actual input;
3. select a matching `queries/` entry;
4. read its required topic pages and only then apply the method;
5. distinguish visible evidence, user-provided facts, external evidence, inference, and unsupported claims;
6. produce the node's required output and return to the main line.

When domain knowledge is intended to shape what the Agent notices in an image, document, trace, or other expensive analysis, enforce a **knowledge-orientation barrier**: the structural files, relevant query entry, and required pages must return before the first analysis call. Do not launch knowledge retrieval and the first analysis call in the same parallel batch.

When useful for transparency or Skill evolution, require a user-facing planning artifact to record the retrieval question, access path, adopted methods, rejected or overridden rules, evidence gaps, decisions, and final prompts or tool inputs.

## 10. Evaluation Belongs To Development

Use test sets and acceptance criteria during creation, update, knowledge recompilation, and release. Do not make expensive AI self-review a mandatory step in every ordinary user run unless the task itself requires high-stakes runtime verification.

Ordinary runtime QA should focus on deterministic contracts, explicit factual boundaries, required files, tool success, and lightweight checks. Development evaluation may use independent models, human review, visual comparison, adversarial cases, and clean conversations.

Store development reports outside the distributable Skill by default. Include them only when the user or target platform explicitly requires a maintenance artifact.

When a source Wiki provides a strong answer, use it as evidence while developing the main run, not as an automatically approved standard answer. A candidate becomes the development standard answer only after it is produced or inspected in the main conversation, checked against facts, logic, evidence, artifact quality, and delivery requirements, and explicitly accepted by the user. When the source Wiki lacks the answer, use user-confirmed design decisions, verified evidence, and explicit acceptance criteria as provisional guidance; never manufacture a “Wiki standard answer.”

Do not package a standard answer, private acceptance notes, expected conclusions, or known failure hints into ordinary runtime references. They belong to development evaluation outside the distributable runtime.

## 11. Evolution Loop

Use this user-gated loop:

```text
real user run
→ inspect reasoning artifact and output
→ user accepts a standard answer/artifact when appropriate
→ complete the current iteration
→ if the user explicitly requests it, run one fresh clean regression
→ report differences and classify the failing layer
→ stop
→ if the user authorizes changes, begin a new update/recompilation cycle
→ validate and release the authorized change
```

Classify fixes accurately:

- routing, node order, hard boundary, output contract → control layer;
- missing, weak, stale, or badly routed domain method → knowledge layer;
- repeatable mechanical failure → script/tool layer;
- weak test or acceptance rule → evaluation layer;
- host model, image model, permission, or service problem → platform/runtime layer.

Do not compensate for a weak knowledge layer by adding more rigid steps. Do not compensate for a tool failure by rewriting business knowledge. Do not patch or retest automatically inside a clean-regression turn.

Recompile the knowledge layer when relevant source pages, accepted design decisions, evidence, or critical gaps materially change. Recompile knowledge without rewriting the control layer when the runtime contract is still correct. Update the control layer only when routing, node order, hard boundaries, tool contracts, or outputs change.

## 12. Completion Checks

A knowledge-compiled Skill is not complete until:

- the direct, knowledge-compiled, or hybrid design choice is explicit;
- source availability, task complexity, coverage, and critical gaps were assessed;
- a simple Skill did not receive a ceremonial mini Wiki;
- hard and soft internalization are separated;
- reusable conclusions from design discussion were synthesized through the design knowledge ledger instead of being discarded or copied as raw chat;
- important nodes have retrieval-aware contracts;
- the local Wiki has working structure and realistic query routes;
- source classes, coverage, gaps, provenance, privacy boundaries, and recompilation conditions are recorded;
- runtime does not depend on the creator's private Wiki;
- references are not treated as a startup reading list; every runtime page is justified by the current node and later-node knowledge remains deferred;
- a runtime read-set audit verifies the files loaded before the first expensive analysis call;
- knowledge is retrieved before the analysis it is meant to orient;
- development evaluation is separate from ordinary runtime;
- any “three-layer” description names evaluation as the third layer and treats scripts/tools as execution resources;
- the main run and actual artifacts have been inspected;
- a user-approved standard answer exists when clean regression is intended;
- clean regression has either been explicitly requested and reported, or is honestly marked `clean-regression-not-run`;
- reported failures enter the correct layer only in a separately authorized update cycle.
