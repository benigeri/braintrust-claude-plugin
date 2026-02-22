---
name: braintrust
description: Manages Braintrust prompts via CLI
skill: braintrust
---

# /braintrust

Manage Braintrust prompts: list, create, update, diff, invoke, test, and generate TypeScript code.

## Quick Reference

| Command | Description |
|---------|-------------|
| `list` | List all prompts |
| `get --slug X` | View prompt details |
| `invoke --slug X --input '{...}'` | Run prompt with tracing |
| `test --slug X --input '{...}'` | Simple test or A/B comparison |
| `create --slug X --system "..." --user "..."` | Create prompt |
| `diff --slug X --system "..."` | Preview changes |
| `update --slug X --system "..."` | Apply changes |
| `promote --from X --to Y` | Copy X content to Y |
| `generate --slug X` | Generate TypeScript |
| `delete --slug X` | Delete prompt |

## Setup

Requires `BRAINTRUST_API_KEY` in your `.env` file. Install SDK for invoke/test: `pip install braintrust`

## Examples

```bash
# List prompts
/braintrust list

# Always diff before updating
/braintrust diff --slug "my-prompt" --system "New content"
/braintrust update --slug "my-prompt" --system "New content"

# A/B test a change
/braintrust test --slug "my-prompt" --input '{"q": "test"}' --system "New version"
```
