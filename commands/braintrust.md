---
name: braintrust
description: Manage Braintrust prompts via CLI
skill: braintrust
---

# /braintrust

Manage Braintrust prompts: list, create, update, diff, and generate TypeScript code.

## Quick Reference

| Command | Description |
|---------|-------------|
| `list` | List all prompts |
| `get --slug X` | View prompt details |
| `create --slug X --system "..." --user "..."` | Create prompt |
| `diff --slug X --system "..."` | Preview changes |
| `update --slug X --system "..."` | Apply changes |
| `generate --slug X` | Generate TypeScript |
| `delete --slug X` | Delete prompt |

## Setup

Requires `BRAINTRUST_API_KEY` in your `.env` file.

## Examples

```bash
# List prompts
python3 braintrust.py list

# Always diff before updating
python3 braintrust.py diff --slug "my-prompt" --system "New content"
python3 braintrust.py update --slug "my-prompt" --system "New content"
```
