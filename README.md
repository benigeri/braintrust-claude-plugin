# Braintrust Claude Plugin

A Claude Code plugin for managing Braintrust prompts via CLI.

## Features

- **List** prompts in your Braintrust project
- **Create** new prompts with system/user messages
- **Update** existing prompts (always diff first!)
- **Diff** changes before applying them
- **Generate** TypeScript invocation code

## Installation

```bash
/plugin install github:benigeri/braintrust-claude-plugin
```

Or add to `~/.claude/settings.json`:

```json
{
  "plugins": ["github:benigeri/braintrust-claude-plugin"]
}
```

## Setup

Set your Braintrust API key in your project's `.env`:

```bash
BRAINTRUST_API_KEY=sk-your-api-key
BRAINTRUST_PROJECT_NAME=Your_Project_Name  # optional default
```

Get your API key: https://www.braintrust.dev/app/settings/api-keys

## Usage

Run `/braintrust` in Claude Code to load the skill, then use commands like:

```bash
# List all prompts
/braintrust list

# View prompt details
/braintrust get --slug "email-draft"

# Always diff before updating!
/braintrust diff --slug "email-draft" --system "Updated prompt..."
/braintrust update --slug "email-draft" --system "Updated prompt..."

# Generate TypeScript code
/braintrust generate --slug "email-draft"
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all prompts in project |
| `get --slug X` | View prompt details |
| `create --slug X --system "..." --user "..."` | Create new prompt |
| `diff --slug X --system "..."` | Preview changes |
| `update --slug X --system "..."` | Apply changes |
| `generate --slug X` | Generate TypeScript code |
| `delete --slug X` | Delete prompt |

## Best Practices

1. **Always diff before updating** - Review changes before applying
2. **Use descriptive slugs** - `email-draft-v2` not `prompt-1`
3. **Test after updates** - Verify prompts work as expected

## Links

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust Dashboard](https://www.braintrust.dev)

## License

MIT
