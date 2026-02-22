# Braintrust Claude Plugin

A Claude Code plugin for managing Braintrust prompts via CLI.

## Installation

```bash
claude plugin add github:benigeri/braintrust-claude-plugin
```

Or add to your project's `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["mcp", "Bash(python3 */bt_cli.py *)"]
  },
  "plugins": ["github:benigeri/braintrust-claude-plugin"]
}
```

## Setup

Add your Braintrust API key to your project's `.env`:

```bash
BRAINTRUST_API_KEY=sk-your-api-key
BRAINTRUST_PROJECT_NAME=Your_Project  # optional default
```

Get your API key at [braintrust.dev/app/settings/api-keys](https://www.braintrust.dev/app/settings/api-keys).

Install the SDK for invoke/test tracing:

```bash
pip install braintrust
```

## Usage

Use `/braintrust` in Claude Code:

```bash
/braintrust list
/braintrust get --slug "email-draft"
/braintrust invoke --slug "email-draft" --input '{"topic": "follow-up"}'
/braintrust test --slug "email-draft" --input '{"topic": "test"}' --system "New prompt..." --force
/braintrust diff --slug "email-draft" --system "Updated prompt..."
/braintrust update --slug "email-draft" --system "Updated prompt..."
/braintrust generate --slug "email-draft"
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | Lists all prompts |
| `get --slug X` | Views prompt details |
| `invoke --slug X --input '{...}'` | Runs prompt with tracing |
| `test --slug X --input '{...}'` | Tests prompt (simple or A/B) |
| `diff --slug X --system "..."` | Previews changes |
| `update --slug X --system "..."` | Applies changes |
| `create --slug X --system "..."` | Creates new prompt |
| `promote --from X --to Y` | Copies X content to Y |
| `generate --slug X` | Generates TypeScript code |
| `delete --slug X` | Deletes prompt |

## Links

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust Dashboard](https://www.braintrust.dev)

## License

MIT
