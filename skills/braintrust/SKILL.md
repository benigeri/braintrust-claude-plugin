---
name: braintrust
description: Manages Braintrust prompts via CLI. Use when working with LLM prompts, prompt versioning, A/B testing prompts, or when user mentions Braintrust. Supports list, get, invoke, test, create, update, diff, delete, and generate commands.
argument-hint: <command> [options]
allowed-tools: Bash(python3 *)
---

# Braintrust Prompt Management

Manage Braintrust prompts through the CLI. The script is at `skills/braintrust/braintrust.py` relative to the plugin install directory.

Run commands with:

```bash
python3 SKILL_DIR/braintrust.py <command> [options]
```

Replace `SKILL_DIR` with the actual path to this skill's directory.

## Quick Reference

| Command | Description |
|---------|-------------|
| `list` | List all prompts |
| `get --slug X` | View prompt details |
| `invoke --slug X --input '{...}'` | Run prompt with tracing |
| `test --slug X --input '{...}'` | Test prompt (simple or A/B comparison) |
| `diff --slug X --system "..."` | Preview changes before applying |
| `update --slug X --system "..."` | Apply changes to prompt |
| `create --slug X --system "..."` | Create new prompt |
| `promote --from X --to Y` | Copy X content to Y |
| `generate --slug X` | Generate TypeScript invocation code |
| `delete --slug X` | Delete prompt |

## Invoke and Test

```bash
python3 SKILL_DIR/braintrust.py invoke --slug "my-prompt" --input '{"question": "test"}'
```

**A/B test** -- provide `--system` or `--user` to compare current vs proposed:

```bash
python3 SKILL_DIR/braintrust.py test --slug "my-prompt" \
  --input '{"q": "test"}' \
  --system "New improved instructions..."
```

This creates `my-prompt-v2`, runs both, shows side-by-side comparison, and offers to promote.

## Always Diff Before Update

```bash
python3 SKILL_DIR/braintrust.py diff --slug "my-prompt" --system "New content"
python3 SKILL_DIR/braintrust.py update --slug "my-prompt" --system "New content"
```

## Environment

Requires `BRAINTRUST_API_KEY` in `.env`. Optional: `BRAINTRUST_PROJECT_NAME` for default project.

The `braintrust` Python SDK is needed for invoke/test: `pip install braintrust`

## Key Rules

1. **Always diff before updating** -- never update blind
2. **Use invoke to test** -- faster than writing code
3. **A/B test significant changes** -- compare before committing
4. **Use descriptive slugs** -- `email-draft-v2` not `prompt-1`

## Additional Resources

For detailed documentation: [reference.md](reference.md) -- complete command reference, A/B testing workflows, TypeScript integration
