# Inspect results and rerun locally

Trigger: the user asks about a node's conclusion, output, error, or a partial rerun. Read the run-ledger contract only if the storage/operation interface is unknown. Return to the target Skill's execution node after resolving the issue.

1. Identify the run and business node, using stable ids and titles. Query its real attempt and output files. Report the concise conclusion first, then input sources, actual strategy references, output links and acceptance status. When the conclusion is unavailable, state the missing execution or evidence.
2. Trace the exact upstream attempt ids captured at execution. Historical conclusions use historical evidence snapshots, even when current files changed. Record revisions rather than rewriting old conclusions.
3. Find the earliest invalid node: changed/missing input, strategy or definition; failed acceptance; missing/changed output; changed upstream attempt; unresolved external task. Distinguish business strategy defects, execution failures and storage/contract defects.
4. Produce the dependency-based rerun plan, identifying reusable branches and affected descendants. Resolve running attempts by inspecting actual external task ids and artifacts. Explicitly close abandoned/failed attempts before retrying; a timeout alone is not proof an external action failed.
5. Within existing authorization, create a new attempt for each required node in topological order. Preserve prior results; recheck dependent nodes even if a replacement output appears similar. Keep paid actions, messages and external writes within their original permission boundaries.
6. Verify new output files and semantic acceptance, then summarize what is current, stale or unresolved. A green ledger status is evidence of satisfied declared checks, not a guarantee of analytical quality.

The file template conservatively invalidates downstream nodes whenever their upstream attempt changes. More selective reuse requires an explicit target-owned semantic equivalence rule with evidence. Independent branches remain reusable.
