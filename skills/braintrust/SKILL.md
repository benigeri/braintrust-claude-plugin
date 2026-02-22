---
name: braintrust
description: Manages Braintrust prompts via CLI. Use when working with LLM prompts, prompt versioning, A/B testing prompts, or when the user mentions Braintrust. Supports list, get, invoke, test, create, update, diff, delete, promote, and generate commands.
argument-hint: <command> [options]
allowed-tools: Bash(python3 */bt_cli.py *)
---

# Braintrust Prompt Management

Manages Braintrust prompts through the CLI tool at `SKILL_DIR/bt_cli.py`.

## Commands

| Command | Description | Side Effects |
|---------|-------------|--------------|
| `list` | Lists all prompts | None |
| `get --slug X` | Views prompt details | None |
| `invoke --slug X --input '{...}'` | Runs prompt with tracing | Creates trace |
| `test --slug X --input '{...}'` | Tests prompt (simple or A/B) | May create v2 prompt |
| `diff --slug X --system "..."` | Previews changes | None |
| `update --slug X --system "..."` | Applies changes | Modifies prompt |
| `create --slug X --system "..."` | Creates new prompt | Creates prompt |
| `promote --from X --to Y` | Copies X content to Y | Modifies Y |
| `generate --slug X` | Generates TypeScript code | None |
| `delete --slug X` | Deletes prompt | Deletes prompt |

## Usage

```bash
# List prompts
python3 SKILL_DIR/bt_cli.py list

# View prompt details
python3 SKILL_DIR/bt_cli.py get --slug "my-prompt"

# Run a prompt
python3 SKILL_DIR/bt_cli.py invoke --slug "my-prompt" --input '{"question": "test"}'

# A/B test with proposed changes
python3 SKILL_DIR/bt_cli.py test --slug "my-prompt" \
  --input '{"q": "test"}' \
  --system "New instructions..." \
  --force

# Preview then apply changes
python3 SKILL_DIR/bt_cli.py diff --slug "my-prompt" --system "New content"
python3 SKILL_DIR/bt_cli.py update --slug "my-prompt" --system "New content"

# Promote and clean up
python3 SKILL_DIR/bt_cli.py promote --from "slug-v2" --to "slug" --force
```

## Non-Interactive Mode

Commands that normally prompt for confirmation (`test` with A/B, `promote`, `delete`) accept `--force` / `-f` to skip all interactive prompts. Always use `--force` when running from Claude Code.

## Environment

```bash
BRAINTRUST_API_KEY=sk-your-api-key        # Required
BRAINTRUST_PROJECT_NAME=Your_Project      # Optional default
```

## Key Rules

1. Always diff before updating — never update blind.
2. Use `--force` for all interactive commands in Claude Code.
3. A/B test significant changes — compare before committing.
4. Use descriptive slugs — `email-draft-v2` not `prompt-1`.

## Reference

See [reference.md](reference.md) for detailed parameter docs, A/B testing workflows, and TypeScript integration.
