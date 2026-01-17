---
name: braintrust
description: Manages Braintrust prompts via CLI. Lists, creates, updates, diffs, and generates TypeScript code for prompts. Use when working with Braintrust prompts, LLM prompt management, or when the user mentions Braintrust, prompt iteration, or prompt versioning.
---

# Braintrust Prompt Management

Manage Braintrust prompts through the CLI. Always diff before updating.

## Quick Start

```bash
# List prompts
python3 ./braintrust.py list

# View prompt details
python3 ./braintrust.py get --slug "my-prompt"

# Always diff before updating
python3 ./braintrust.py diff --slug "my-prompt" --system "New content"
python3 ./braintrust.py update --slug "my-prompt" --system "New content"

# Generate TypeScript invocation code
python3 ./braintrust.py generate --slug "my-prompt"
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all prompts in project |
| `get --slug X` | View prompt details |
| `create --slug X --system "..." --user "..."` | Create new prompt |
| `diff --slug X --system "..."` | Preview changes before applying |
| `update --slug X --system "..."` | Apply changes to prompt |
| `generate --slug X` | Generate TypeScript code |
| `delete --slug X` | Delete prompt |

## Create Command Parameters

```bash
python3 ./braintrust.py create \
  --slug "email-draft" \
  --name "Email Draft Generator" \
  --description "Generates professional emails" \
  --system "You are an email assistant..." \
  --user "Write an email about: {{topic}}" \
  --model "claude-sonnet-4-5-20250929"
```

- `--slug` (required): URL-safe identifier
- `--name`: Human-readable name (defaults to slug)
- `--description`: What the prompt does
- `--system`: System message content
- `--user`: User message template (use `{{variable}}` for inputs)
- `--model`: Model name (default: claude-sonnet-4-5-20250929)
- `--project`: Project name (or use BRAINTRUST_PROJECT_NAME env var)

## Environment Variables

```bash
BRAINTRUST_API_KEY=sk-your-api-key        # Required
BRAINTRUST_PROJECT_NAME=Your_Project      # Optional default
```

## Key Rules

1. **Always diff before updating** - Never update blind
2. **Use descriptive slugs** - `email-draft-v2` not `prompt-1`
3. **Test after changes** - Verify in Braintrust dashboard

## Additional Resources

- For detailed testing workflows, see [reference.md](reference.md)
- For TypeScript integration examples, see [reference.md](reference.md)
- For template variable syntax, see [reference.md](reference.md)
