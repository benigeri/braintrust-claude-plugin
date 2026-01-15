# Braintrust Claude Plugin

A Claude Code plugin for managing Braintrust prompts via CLI.

## Features

- **List** prompts in your Braintrust project
- **Create** new prompts with system/user messages
- **Update** existing prompts (always diff first!)
- **Diff** changes before applying them
- **Generate** TypeScript invocation code

## Installation

Add to your Claude Code settings (`~/.claude/settings.json`):

```json
{
  "plugins": ["github:YOUR_USERNAME/braintrust-claude-plugin"]
}
```

Or install via CLI:

```bash
/plugin install github:YOUR_USERNAME/braintrust-claude-plugin
```

## Setup

Set your Braintrust API key:

```bash
# Add to your .env file
BRAINTRUST_API_KEY=sk-your-api-key

# Optional: Set default project
BRAINTRUST_PROJECT_NAME=Your_Project_Name
```

Get your API key from: https://www.braintrust.dev/app/settings/api-keys

## Usage

Use the `/braintrust` command in Claude Code, or run the CLI directly:

```bash
# List all prompts
python3 braintrust.py list

# View prompt details
python3 braintrust.py get --slug "email-draft"

# Create a prompt
python3 braintrust.py create \
  --slug "email-draft" \
  --name "Email Draft Generator" \
  --system "You are an email assistant..." \
  --user "Write an email about: {{topic}}"

# Always diff before updating!
python3 braintrust.py diff --slug "email-draft" --system "Updated prompt..."
python3 braintrust.py update --slug "email-draft" --system "Updated prompt..."

# Generate TypeScript code
python3 braintrust.py generate --slug "email-draft"
```

## Best Practices

1. **Always diff before updating** - Review changes before applying
2. **Use descriptive slugs** - `email-draft-v2` not `prompt-1`
3. **Test after updates** - Verify prompts work as expected
4. **Check Braintrust dashboard** - Verify traces appear

## License

MIT
