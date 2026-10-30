# Capability Abstraction

Cross-Agent portability lives at the contract level. The core declares a logical capability and the exact features it needs; each platform adapter maps those requirements to a stable CLI/API/MCP/script or an Agent-native tool.

Do not force every native tool into a shell wrapper. A CLI wrapper is appropriate only when a real stable executable surface exists. For a native tool, the adapter is an execution instruction plus result normalization contract.

Four states prevent false compatibility: `tested`, `implemented`, `unresolved`, and `unsupported`. Missing required features produce `CAPABILITY_UNAVAILABLE` or `FEATURE_UNSUPPORTED`; they never trigger a silent downgrade.

During migration, inspect the target runtime's advertised capabilities and fill only the target adapter. During ordinary execution, load and use the adapter or report its gap. Runtime never rewrites itself.
