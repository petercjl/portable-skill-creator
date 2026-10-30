# Logical Capability Contract Protocol

Use this protocol when a Skill needs execution surfaces whose native names or semantics can vary by Agent.

## Files And Roles

- `capabilities.json`: canonical platform-neutral requirements.
- `adapters/<platform>.json`: one target platform's native mappings and evidence.
- `references/capability-contract.schema.json`: structural schema for tooling and maintainers.

The portable core may refer to logical IDs such as `media.image.generate`, `command.execute`, or `agent.isolated-run`. It must not embed a vendor tool name when the capability is intended to move across Agents.

## Capability Declaration

Every declaration contains:

- stable dot-separated `id`;
- human-readable `purpose`;
- `required` boolean;
- feature-level `required_features`;
- named `input_fields` and `output_fields`;
- `side_effects`, including external mutation, cost, and user-authorization boundaries;
- standard errors the caller must handle.

Feature-level requirements matter. “Can generate an image” is insufficient when the workflow also requires reference-image editing, exact aspect ratio, or local artifact delivery.

## Normalized Result

Adapters normalize successful execution to:

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

Adapters normalize failure to `ok: false`, a standard error code, a human-readable message, and the missing capability or feature when applicable.

Standard codes:

- `CAPABILITY_UNAVAILABLE`
- `FEATURE_UNSUPPORTED`
- `AUTH_REQUIRED`
- `PERMISSION_REQUIRED`
- `PAID_ACTION_NOT_AUTHORIZED`
- `PROVIDER_FAILURE`
- `OUTPUT_CONTRACT_FAILED`

## Adapter Requirements

Mappings use one of `tested`, `implemented`, `unresolved`, or `unsupported`. A `tested` mapping requires `tested_date` and evidence. `tested` and `implemented` mappings must cover every required feature before they can satisfy a required capability.

For a stable CLI/API/MCP/script, identify its discovery and version/capability probing rules. For an Agent-native tool, describe how the host should invoke its advertised capability and normalize the returned artifacts; do not invent an executable wrapper.

Resolve platforms and native tools from the target runtime's advertised catalog, configured platform identifier, or explicit migration target. Do not infer them from an author's private path.

## Runtime And Evolution Boundary

At runtime:

1. determine the current target platform through advertised/configured context;
2. load its adapter;
3. verify required mapping status and feature coverage;
4. execute and normalize the result;
5. return a standard error if the contract is not satisfied.

Runtime execution must never create, patch, or guess a missing adapter. During a separately authorized port/update cycle, inspect the target platform, implement the adapter, validate it, collect evidence, and return to the creator's validation main line.

Nested Skill dependencies follow the same rule: resolve the callee by exact logical Skill name from the target catalog, read its complete current instructions and resources, execute its declared input/output handoff, and return to the caller's named main-line point. Do not use fuzzy matching or copied fallback instructions.
