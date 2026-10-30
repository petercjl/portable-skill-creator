# Platform Adapter Design

Read this reference when a Skill uses native tools, differs across Agents, or is being ported.

## Capability-First Boundary

The portable core names what must happen, not which vendor tool performs it. Put required logical IDs and features in `capabilities.json`; put each Agent's implementation in `adapters/<platform>.json`.

Create an adapter when tool names, feature sets, Skill discovery, UI metadata, permissions, secrets, browser control, messaging, scheduling, media generation, or isolated-agent invocation differ. Do not create an adapter merely to repeat the core workflow.

## Two Execution Shapes

1. **Stable executable surface**: a CLI, API, MCP, or bundled script can expose a deterministic contract. The adapter records discovery, version/capability probing, inputs, outputs, permissions, and errors.
2. **Agent-native surface**: image generation, browser control, delegation, or similar functionality may exist only as a host tool. The adapter gives the executing Agent an instruction mapping and normalization contract. It is not a fake shell wrapper.

In both cases, the core consumes the same normalized result. Example:

```json
{
  "ok": true,
  "artifacts": [],
  "metadata": {},
  "task_id": null,
  "cost": null,
  "warnings": []
}
```

## Mapping States

- `tested`: implemented and exercised on the named target, with date and evidence.
- `implemented`: mapping exists and passes static checks, but target-runtime evidence is absent.
- `unresolved`: the target capability has not yet been identified or wired.
- `unsupported`: the target is known not to provide the required feature.

Never translate `unresolved` or `unsupported` into success. Return the standard capability error and keep the core output contract unchanged.

## Resolution And Migration

During an authorized port/update cycle:

1. load the canonical core and capability manifest;
2. inspect the target Agent's advertised Skills, tools, schemas, and stable CLIs;
3. match exact features, permissions, side effects, and result fields;
4. write only the target adapter;
5. validate feature coverage and failure behavior;
6. run target-specific evidence and update status honestly;
7. return to the creator's validation main line.

Ordinary runtime may detect and report a missing adapter. It must not self-modify the Skill, guess a native tool, or weaken required features.

## Adapter Record

Each mapping records the logical capability ID, native implementation, implemented features, status, required configuration and permissions, normalized-output behavior, output-contract differences, and evidence. `tested` records require a test date and non-empty evidence.

Platform metadata under `agents/` may improve discovery but cannot be a runtime dependency of the portable core. Keep one canonical method and small platform mappings; test every distribution independently.
