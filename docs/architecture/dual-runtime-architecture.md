# Dual Runtime Architecture

## Core Engine

`skills/braintrust/bt_cli.py` is the single implementation for all Braintrust prompt operations.

Responsibilities:

- command parsing and dispatch
- Braintrust API interactions
- SDK-backed invoke/test execution
- fail-fast validation (`BRAINTRUST_API_KEY`, project resolution)

## Runtime Adapters

Adapters call the same core engine and do not re-implement command logic.

Shell/Codex adapter:

- `./braintrust` -> `python3 skills/braintrust/bt_cli.py ...`

Claude adapters:

- `plugin.json`
- `.claude-plugin/marketplace.json`
- `commands/braintrust.md`
- `skills/braintrust/SKILL.md`

## Command Contract

Canonical commands across runtimes:

- `list`
- `get`
- `invoke`
- `diff`
- `update`
- `test`
- `promote`

Extended commands remain available: `create`, `delete`, `generate`.

## Validation Contract

- `BRAINTRUST_API_KEY` is required for API-backed operations.
- `BRAINTRUST_PROJECT_NAME` is optional default project context.
- Commands that require explicit project context fail fast if neither `--project` nor `BRAINTRUST_PROJECT_NAME` is provided.

## Drift Prevention

`scripts/smoke.sh` verifies:

- wrapper and canonical help surfaces
- missing API key guidance
- missing project guidance for project-required commands
