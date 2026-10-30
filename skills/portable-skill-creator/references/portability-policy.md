# Portability And Privacy Policy

Use this reference while designing, reviewing, and validating a Skill.

## Target Profiles

| Profile | Allowed coupling | Required label |
| --- | --- | --- |
| `shareable` | Declared cross-machine dependencies only | Spec-compatible and tested platforms |
| `internal` | Organization services and schemas | Internal; list access requirements |
| `platform` | One Agent's tools, metadata, or runtime | Platform-specific; name the platform |
| `local` | Authorized current-machine resources | Local-only; not shareable as-is |

Default to `shareable`. A narrower profile requires an explicit user request or an unavoidable requirement that is reported before finalizing the artifact.

## Portable Core Rules

- Keep `SKILL.md` and its instructions usable without platform UI metadata.
- Use relative paths for bundled scripts, references, assets, and templates.
- Use semantic configuration names for external roots and executables.
- State capabilities such as terminal execution, web access, file editing, browser control, or message delivery before giving a platform-specific tool mapping.
- Prefer stable CLI, MCP, API, or script contracts when tool names vary across Agents.
- Detect dependencies and permissions at runtime.
- Keep references one level from `SKILL.md` when practical.
- Avoid copying methods into multiple platform files; keep one core rule and small adapters.
- Declare cross-Agent execution needs as logical capabilities with feature-level requirements, normalized inputs/outputs, side effects, permissions, and failure codes.
- Resolve the current platform from its advertised runtime/catalog or explicit target configuration, not author-machine path heuristics.
- Refuse silent degradation when a required capability or feature is absent.

## Information That Must Not Ship

Remove or parameterize:

- author usernames, hostnames, device names, home directories, and personal workspace locations;
- real email addresses, internal addresses, private domains, account identifiers, and private repository locations unless the target is explicitly internal;
- credentials, tokens, session data, cookies, passwords, private keys, and real configuration values;
- hidden wiki notes, private conversation context, and files not included in the Skill;
- undeclared binary locations, application bundles, browser profiles, or local services.

Never downgrade a secret finding to an accepted portability warning. Remove the value and use the target environment's credential mechanism.

## Configuration Pattern

Use names that describe meaning rather than the author's filesystem. Examples include `${WORKSPACE_ROOT}`, `${SKILL_ROOT}`, `${CONFIG_PATH}`, `${TOOL_BIN}`, and `${SERVICE_URL}`. Document who provides each value, whether it is required, and how the Skill behaves when it is absent.

Do not assume environment-variable syntax is interpreted inside `SKILL.md`; it is a contract for the executing Agent or script. Resolve values explicitly at runtime.

## Platform Isolation

Keep platform-specific material in an optional metadata file or a directly linked adapter reference. Each adapter should declare:

- platform and tested version/date;
- capability mapping;
- installation/discovery location as a platform convention, not an author path;
- required permissions and dependencies;
- fallback or unsupported behavior;
- whether the adapter changes the core output contract.

If the core cannot run without the adapter, label the Skill `adapter-required` rather than fully portable.

Keep `capabilities.json` and `adapters/<platform>.json` machine-readable when the Skill has cross-Agent execution dependencies. A mapping is `tested` only with dated evidence; `implemented` means the mapping exists but lacks target-runtime evidence; `unresolved` and `unsupported` remain visible gaps. Runtime execution may report a gap but must not fill or rewrite adapters itself.

## Scanner Suppression

The portability scanner supports a narrow suppression for suppressible machine/platform findings. Put this marker on the same line or the immediately preceding line:

```text
portable-scan: allow <rule-id> -- <specific reason>
```

Use it only when the selected `internal`, `platform`, or `local` profile authorizes the dependency. Do not use broad, unexplained, or repeated suppressions. Secret and private-key rules cannot be suppressed.

## Compatibility Evidence

Maintain separate claims:

- Format evidence: validator result.
- Static portability evidence: scanner result and dependency inventory.
- Script evidence: commands/tests and representative results.
- Runtime evidence: Agent/runtime, version or date, request exercised, and artifact inspected.

Absence of runtime evidence means `spec-compatible`, not `tested`.

Record operating-system evidence separately from Agent evidence. A Skill tested on one Agent/OS combination is not automatically tested on another OS, even if the adapter schema validates.
