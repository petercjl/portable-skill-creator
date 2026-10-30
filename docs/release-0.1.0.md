# 0.1.0 release verification

Release: @petercjl/portable-skill-creator 0.1.0, stable latest. The exact public version and stable latest tag were verified, and the public package was installed through its real npm entry.

- Source tag: v0.1.0.
- OIDC release: https://github.com/petercjl/portable-skill-creator/actions/runs/40995942707
- All 12 package test groups passed on ubuntu-latest, macos-latest and windows-latest. These are OS/package results, not native-host certification for every Agent.
- Behavioral cases: strict parser/target validation, unmanaged and edited refusal, missing-file repair, no-op, custom metadata, physical isolation after bootstrap removal, lock handling, interrupted synchronization recovery, Python dependency failure, bounded cached registry checks, actual npm candidate acquisition/activation, same-version repair and local-edit protection.
- Bundled Python validator behavioral tests passed; base creator format validation passed on the source Skill. The release hook synchronized version manifests and reran tests/checks after the stable bump. Prepack independently verified release identity.
- Candidate audit matched every packed source file. Discovery witness and maintenance witness passed through a scripts-disabled isolated npm install. The latter performed no registry queries or installation and left all installed bytes/timestamps unchanged.
- Shared source audit has no failures. Three historical-updater coverage warnings are first-release non-applicable: no standalone historical updater existed before this publication. Current npm upgrade and recovery paths have real behavioral tests.
- Generic and arbitrary valid Agent identities use explicit exact destinations. Calling eligibility is capability-based. SealSeek native mapping remains unresolved and was not locally synchronized.
- Clean-context Skill regression was not requested and was not run. Packaging preserved the existing routed hybrid methodology; it added lifecycle guidance and generic host resolution.

Final public verification completed on 2026-10-30:

- The registry reports 0.1.0 and latest=0.1.0. Tarball integrity: sha512-AELoapjpYqH3DlXLuMiOOKW3nc92yCi+Znux10fa17I3AyMwqbjuOtt7d4BpCNE2bM1WaxtasQ8KU25Ez77Zxg==.
- Independent public-artifact audit verified registry/tarball integrity and matched all 40 packed files to the stable source. Read-only packed discovery probes passed.
- The exact global npm package reports 0.1.0. Its postinstall notice was skipped by npm script policy; the documented scripts-disabled installation handoff was executed explicitly.
- Only the current Codex target was migrated. The original complete Skill and a separately hash-verified snapshot were preserved outside the discovery directory before replacement.
- The managed physical target reports installed=true, managed=true, current=true, edited=[], missing=[], SHA-256 verified. Global bootstrap, target-owned runtime, canonical Skill manifest and install receipt all report 0.1.0.
- The current Codex session loaded the installed complete SKILL.md through the existing advertised logical identity/path. Its target-owned prepare entry executed successfully, found the real Python runtime, and verified latest=0.1.0. The current advertised base skill-creator was loaded in full during this task and its format validator passed.
- Read-only public-entry maintenance witness verified the actual Codex target with zero registry queries and zero installation operations; installed bytes and timestamps were unchanged.
- Native fresh-session behavioral regression was not run. The package CLI deliberately leaves host discovery authority with the host; current-session load evidence is recorded separately from that CLI field. Other Agents were not locally synchronized.

Host metadata is preserved independently from canonical file ownership.
