---
name: braintrust
description: Manage Braintrust prompts. Use when working with LLM prompts, prompt versioning, A/B testing prompts, or when user mentions Braintrust. Supports list, get, invoke, test, create, update, diff, delete, and generate commands.
argument-hint: <command> [options]
allowed-tools: Bash(python3 *)
---

# Braintrust Prompt Management

Manage Braintrust prompts through the CLI.

## Quick Reference

| Command | Description |
|---------|-------------|
| `list` | List all prompts |
| `get --slug X` | View prompt details |
| `invoke --slug X --input '{...}'` | Run prompt, see output with tracing |
| `test --slug X --input '{...}'` | Test prompt (simple or A/B comparison) |
| `diff --slug X --system "..."` | Preview changes before applying |
| `update --slug X --system "..."` | Apply changes to prompt |
| `create --slug X --system "..."` | Create new prompt |
| `generate --slug X` | Generate TypeScript invocation code |
| `delete --slug X` | Delete prompt |

## Essential Commands

### Invoke (Run a prompt)

```bash
python3 ./bt_cli.py invoke --slug "my-prompt" --input '{"question": "test"}'
```

Shows output, token usage, and trace URL for Braintrust dashboard.

### Test (Simple or A/B comparison)

**Simple test:**
```bash
python3 ./bt_cli.py test --slug "my-prompt" --input '{"q": "test"}'
```

**A/B test with changes:**
```bash
python3 ./bt_cli.py test --slug "my-prompt" \
  --input '{"q": "test"}' \
  --system "New improved instructions..."
```

This will:
1. Create `my-prompt-v2` with your changes
2. Run both prompts with same input
3. Show side-by-side comparison
4. Ask if you want to promote v2

### Always Diff Before Update

```bash
# Preview changes
python3 ./bt_cli.py diff --slug "my-prompt" --system "New content"

# Apply changes
python3 ./bt_cli.py update --slug "my-prompt" --system "New content"
```

## Environment Setup

```bash
# Required
BRAINTRUST_API_KEY=sk-your-api-key

# Optional (default project)
BRAINTRUST_PROJECT_NAME=Your_Project
```

## Key Rules

1. **Always diff before updating** - never update blind
2. **Use invoke to test** - faster than writing code
3. **A/B test significant changes** - compare before committing
4. **Use descriptive slugs** - `email-draft-v2` not `prompt-1`

## Additional Resources

For detailed documentation:
- [reference.md](reference.md) - Complete command reference, A/B testing workflows, TypeScript integration
