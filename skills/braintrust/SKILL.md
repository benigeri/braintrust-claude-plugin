---
name: braintrust
description: Claude adapter for the shared Braintrust prompt CLI. Use for prompt listing, retrieval, invoke/testing, diff/update, and promotion.
argument-hint: <command> [options]
allowed-tools: Bash(python3 */bt_cli.py *)
---

# Braintrust Prompt Management

This skill is the Claude adapter for the shared CLI engine at `SKILL_DIR/bt_cli.py`.

- Claude runtime command: `/braintrust <command>`
- Shell/Codex equivalent: `./braintrust <command>`

Both call the same core engine.

## Canonical Commands

| Command | Description | Side Effects |
|---|---|---|
| `list` | List prompts | None |
| `get --slug X` | View prompt details | None |
| `invoke --slug X --input '{...}'` | Run prompt with tracing | Creates trace |
| `diff --slug X --system "..."` | Preview message changes | None |
| `update --slug X --system "..."` | Apply message changes | Modifies prompt |
| `test --slug X --input '{...}' [--system "..."]` | Simple run or A/B test | May create/promote/delete v2 |
| `promote --from X --to Y` | Copy X content into Y | Modifies Y |

Extended commands: `create`, `delete`, `generate`.

## Usage

```bash
python3 SKILL_DIR/bt_cli.py list
python3 SKILL_DIR/bt_cli.py get --slug "my-prompt"
python3 SKILL_DIR/bt_cli.py invoke --slug "my-prompt" --input '{"question":"test"}'
python3 SKILL_DIR/bt_cli.py diff --slug "my-prompt" --system "New content"
python3 SKILL_DIR/bt_cli.py update --slug "my-prompt" --system "New content"
python3 SKILL_DIR/bt_cli.py test --slug "my-prompt" --input '{"q":"test"}' --system "New instructions" --force
python3 SKILL_DIR/bt_cli.py promote --from "my-prompt-v2" --to "my-prompt" --force
```

## Non-Interactive Mode

Commands with confirmation prompts (`test` in A/B mode, `promote`, `delete`) support `--force` (`-y`). Use `--force` for automation and Claude Code execution.

## Environment

```bash
BRAINTRUST_API_KEY=sk-your-api-key        # Required
BRAINTRUST_PROJECT_NAME=Your_Project_Name # Optional default project
```

The `braintrust` Python SDK is required for `invoke` and `test`:

```bash
pip install braintrust
```

## Key Rules

1. Always run `diff` before `update`.
2. Use `--force` in non-interactive/automated workflows.
3. Use A/B test mode for significant prompt changes.
4. Keep prompt slugs explicit and versioned (`my-prompt-v2`).

## Reference

See [reference.md](reference.md) for detailed examples and command options.
