# Business Flow And Strategy Sources

Use this topic when a business Skill must translate a recurring job into a reliable Agent workflow. The business flow and its strategies are separate design passes; both eventually contribute to the `I → S → O` contract.

## Pass 1: Business Flow

Describe the job as the user experiences it:

```text
accepted input → ordered work steps and decision/hand-off points → observable outputs
```

For each step, name its purpose, required input, hand-off output, and completion condition. This pass answers **what work is done and in what order**. It is not yet a list of tool calls, prompts, analytic techniques, or domain conclusions. Keep the flow short enough that the user can check whether it matches the actual business job. Leave a branch or a named gap where a missing input materially changes the work.

## Pass 2: Strategy For Each Step

For every judgment-heavy step, ask: What question must be answered? Which evidence is relevant? By what standard is a decision made? What happens if evidence is missing or conflicting? What output lets the next step proceed? Mechanical steps can use a deterministic CLI/script/API contract instead of a prose-heavy strategy.

Develop candidate strategies from three sources:

| Source | Use | Boundary |
| --- | --- | --- |
| Agent proposal (`A`) | Suggest a method, comparison, branch, or quality standard for user review. | Keep it provisional until evidence or the user validates it; do not present it as an enterprise rule. |
| Enterprise Wiki or other traceable knowledge (`W`) | Retrieve the relevant SOP, framework, case, or prior decision by the current step's question. | Check coverage, applicability, and currency; cite the actual page or source in the design ledger. |
| User-supplied method (`U`) | Translate the user's business judgment and accepted standards into a reusable decision rule. | Preserve scope and intent; with authorization, compile reusable knowledge into the appropriate Wiki rather than leaving it only in conversation. |

Verified platform behavior or external evidence (`E`) may validate, limit, or contradict a candidate from any source. When sources disagree, record the conflict and its scope; resolve material choices with the user or an authorized evidence check. Source labels describe provenance, not a blanket ranking of truth.

Use a compact strategy ledger during design:

| Step and hand-off | Strategy question | Candidate rule and source | Evidence/acceptance standard | Gap or branch |
| --- | --- | --- | --- | --- |
| One business step | One decision to make | `W`, `U`, `E`, or provisional `A` | What would verify the decision and output | What to do when it cannot be decided |

Synthesize the accepted result into the correct layer: stable order, hard boundaries, and output contracts in `SKILL.md`; evolving domain judgment in routed knowledge references when warranted; repeatable calculations or integrations in scripts/CLI; and candidate examples, quality baselines, and failures in development evaluation. The strategy-source choice does not by itself require a mini Wiki: simple stable Skills may remain direct, while knowledge-heavy Skills may be hybrid or knowledge-compiled.

Before implementation, verify that every business step has a hand-off and that every judgment-heavy step has a strategy source or an explicit gap. The final design should read as a current, self-contained execution manual, not as a record of the discussion that produced it.
