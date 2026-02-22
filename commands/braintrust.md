---
name: braintrust
description: Manages Braintrust prompts via CLI
skill: braintrust
---

# /braintrust

Manages Braintrust prompts: list, get, invoke, test, create, update, diff, promote, generate, and delete.

## Setup

Requires `BRAINTRUST_API_KEY` in your `.env` file.

## Examples

```bash
# List prompts
python3 bt_cli.py list

# Run a prompt
python3 bt_cli.py invoke --slug "my-prompt" --input '{"question": "test"}'

# A/B test with changes (use --force in Claude Code)
python3 bt_cli.py test --slug "my-prompt" --input '{"q": "test"}' --system "New content" --force

# Always diff before updating
python3 bt_cli.py diff --slug "my-prompt" --system "New content"
python3 bt_cli.py update --slug "my-prompt" --system "New content"
```
