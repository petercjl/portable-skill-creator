# Skill Worldview

A Skill is an execution manual for an LLM, not merely a prompt and not merely a fixed workflow. Its unit of design is a reusable task-specific knowledge system:

```text
Input → Strategy → Output
```

The strategy contains a stable main line, judgment nodes, branches, deterministic execution resources, failure handlers, QA gates, terminal conditions, and named returns to the main line. The Agent may improvise low-risk local details, but exceptions may not dissolve the main line.

For complex work, separate:

1. control in `SKILL.md`;
2. soft, evolving judgment in a routed local mini Wiki;
3. development evaluation outside ordinary runtime.

Scripts and tools are execution resources, not the evaluation layer. A one-time successful conversation is evidence for design, not proof that the installed Skill works independently.

Place recurring, fixed, fragile, high-risk, or mechanically checkable actions behind deterministic contracts. Keep semantic judgment with the Agent, supported by concise knowledge and observable evidence.
