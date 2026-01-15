---
name: braintrust
description: Manage Braintrust prompts via CLI
skill: braintrust
---

# /braintrust

Load the Braintrust skill for prompt management.

This skill provides a CLI for managing Braintrust prompts:
- **list** - List all prompts in a project
- **get** - View prompt details
- **create** - Create a new prompt
- **update** - Update an existing prompt
- **diff** - Preview changes before updating
- **generate** - Generate TypeScript invocation code
- **delete** - Delete a prompt

## Quick Start

```bash
# List prompts
python3 ~/.claude/plugins/*/braintrust-*/skills/braintrust/braintrust.py list

# Get prompt details
python3 ~/.claude/plugins/*/braintrust-*/skills/braintrust/braintrust.py get --slug "my-prompt"

# Always diff before updating
python3 ~/.claude/plugins/*/braintrust-*/skills/braintrust/braintrust.py diff --slug "my-prompt" --system "New content"
python3 ~/.claude/plugins/*/braintrust-*/skills/braintrust/braintrust.py update --slug "my-prompt" --system "New content"
```

See SKILL.md for full documentation.
