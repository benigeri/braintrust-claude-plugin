# Dual-Native Claude + Codex Runtime Design

**Date:** 2026-03-04  
**Repo:** `braintrust-claude-plugin`

## Goal

Make the repository runtime-agnostic with one shared CLI engine that works natively in both Claude and Codex, while preserving backward compatibility for existing Claude plugin users.

## Context

Current behavior is Claude-plugin-oriented, with core functionality implemented in `skills/braintrust/bt_cli.py` and wrappers/metadata in:

- `plugin.json`
- `.claude-plugin/marketplace.json`
- `commands/braintrust.md`
- `skills/braintrust/SKILL.md`

This project already has a working Python CLI engine. The gap is packaging, docs, and entrypoints for non-Claude use.

## Design Summary

### 1. Single Core Engine

Keep `skills/braintrust/bt_cli.py` as the only implementation engine.

- No command logic duplication in wrappers.
- All command behavior, env checks, and errors originate from this file.
- Command surface stays consistent across runtimes.

### 2. Dual-Native Entrypoints

Add a top-level shell entrypoint for Codex/plain terminal use and keep Claude adapter files for Claude-native use.

- New canonical shell command: `./braintrust <command> [options]`
- Claude-native command remains `/braintrust <command>`
- Both routes execute `skills/braintrust/bt_cli.py`

### 3. Canonical Command Surface

Document and support this canonical set across both runtimes:

- `list`
- `get`
- `invoke`
- `diff`
- `update`
- `test`
- `promote`

Additional commands (`create`, `delete`, `generate`) may remain available as extended commands, but docs must clearly separate core vs extended surface.

### 4. Env Validation (Fail-Fast)

Standardize runtime checks in core CLI:

- Required for all API-backed commands: `BRAINTRUST_API_KEY`
- Optional default project: `BRAINTRUST_PROJECT_NAME`
- Commands that require a concrete project (`invoke`, `test`, `promote`, `create`) should fail immediately with explicit guidance when neither `--project` nor `BRAINTRUST_PROJECT_NAME` is provided.

Error messages should include:

- Missing variable name
- How to set it
- Which command flag can override

### 5. Runtime-Agnostic Documentation

README becomes dual-native and runtime-agnostic:

- Claude setup path
- Codex/plain-shell setup path
- Same command examples for both runtimes
- Explicit statement that Claude plugin files are adapters, not the engine

Add migration doc:

- `docs/migration-claude-to-codex.md`
- Maps old `/braintrust` workflows to `./braintrust` equivalents
- Includes compatibility notes for teams keeping Claude plugin install

### 6. Smoke Verification Layer

Add a smoke script to quickly verify command wiring and fail-fast behavior without requiring live Braintrust credentials for every check.

Proposed script:

- `scripts/smoke.sh`

Checks include:

- Wrapper executable and delegates to CLI (`./braintrust --help`)
- Core command help surfaces exist
- Missing env produces expected fail-fast error text
- Missing project for project-required commands produces expected guidance

## Data and Control Flow

1. User runs `./braintrust ...` (Codex/shell) or `/braintrust ...` (Claude plugin).
2. Adapter forwards args to `skills/braintrust/bt_cli.py`.
3. Core CLI validates env/flags.
4. Core CLI calls Braintrust API and/or SDK.
5. Output/error returned to caller.

## Backward Compatibility

- Keep `plugin.json`, `.claude-plugin/marketplace.json`, and Claude skill/command wrappers.
- Mark them as runtime adapters in docs.
- Do not break existing `/braintrust` command usage.

## Risks and Mitigations

### Risk: Drift between adapters and core CLI

Mitigation:
- Keep wrappers minimal pass-through shims.
- Add smoke tests that exercise both wrapper and core help/command paths.

### Risk: Ambiguous docs between runtimes

Mitigation:
- README starts with runtime choice matrix and unified command examples.
- Migration guide provides 1:1 command mapping.

### Risk: Hidden env assumptions

Mitigation:
- Centralized fail-fast validation with explicit, actionable errors.

## Testing Strategy

- Smoke script for CLI surface and fail-fast checks.
- Manual verification commands documented in README and migration guide.
- Optional integration checks when real credentials are available.

## Out of Scope

- Rewriting Braintrust API behavior.
- Replacing Python CLI engine.
- Removing Claude support.

## Acceptance Criteria

- Shared core remains `skills/braintrust/bt_cli.py`.
- New top-level shell command works.
- Claude-native path still works.
- Canonical command surface documented and runnable in both runtimes.
- Env validation is clear and fail-fast.
- Migration doc exists.
- Smoke script exists and passes locally.
