# Braintrust Claude Plugin

A Claude Code plugin for managing Braintrust prompts. List, create, update, diff, invoke, A/B test, and generate TypeScript code for your prompts.

## Installation

Add the marketplace, then install the plugin:

```
/plugin marketplace add benigeri/braintrust-claude-plugin
/plugin install braintrust@benigeri-braintrust-claude-plugin
```

Restart Claude Code after installing.

### Manual install

If the marketplace install doesn't work, clone and copy manually:

```bash
git clone https://github.com/benigeri/braintrust-claude-plugin.git /tmp/braintrust-claude-plugin
mkdir -p ~/.claude/plugins/cache/local/braintrust/1.0.0
cp -r /tmp/braintrust-claude-plugin/* ~/.claude/plugins/cache/local/braintrust/1.0.0/
```

Then add to `~/.claude/plugins/installed_plugins.json` (merge into existing `plugins` object):

```json
"braintrust@local": [
  {
    "scope": "user",
    "installPath": "~/.claude/plugins/cache/local/braintrust/1.0.0",
    "version": "1.0.0",
    "installedAt": "2025-01-01T00:00:00.000Z",
    "lastUpdated": "2025-01-01T00:00:00.000Z"
  }
]
```

Restart Claude Code after installing.

## Setup

Set your Braintrust API key in your project's `.env`:

```bash
BRAINTRUST_API_KEY=sk-your-api-key
BRAINTRUST_PROJECT_NAME=Your_Project_Name  # optional default
```

The `braintrust` Python SDK is required for invoke/test commands:

```bash
pip install braintrust
```

Get your API key: [Braintrust API Keys](https://www.braintrust.dev/app/settings/api-keys)

## Usage

Use `/braintrust` in Claude Code followed by a command:

```bash
/braintrust list
/braintrust get --slug "email-draft"
/braintrust diff --slug "email-draft" --system "Updated prompt..."
/braintrust update --slug "email-draft" --system "Updated prompt..."
/braintrust invoke --slug "email-draft" --input '{"topic": "follow-up"}'
/braintrust generate --slug "email-draft"
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all prompts in project |
| `get --slug X` | View prompt details |
| `invoke --slug X --input '{...}'` | Run prompt with tracing |
| `test --slug X --input '{...}'` | Simple test or A/B comparison |
| `diff --slug X --system "..."` | Preview changes |
| `update --slug X --system "..."` | Apply changes |
| `create --slug X --system "..." --user "..."` | Create new prompt |
| `promote --from X --to Y` | Copy prompt content from X to Y |
| `generate --slug X` | Generate TypeScript invocation code |
| `delete --slug X` | Delete prompt |

## Workflows

### A/B test a prompt change

The `test` command with `--system` or `--user` flags automatically creates a v2 copy, runs both, and shows a side-by-side comparison:

```bash
/braintrust test --slug "email-draft" \
  --input '{"topic": "meeting follow-up"}' \
  --system "You are an expert email writer. Be concise and professional."
```

This will:
1. Create `email-draft-v2` with your changes
2. Run both prompts with the same input
3. Show side-by-side comparison with timing
4. Ask if you want to promote v2 to the original

### Iterate on a prompt safely

```bash
# 1. Review current state
/braintrust get --slug "email-draft"

# 2. A/B test your change
/braintrust test --slug "email-draft" \
  --input '{"topic": "test"}' \
  --system "New improved instructions..."

# 3. If not promoted during test, promote manually later
/braintrust promote --from "email-draft-v2" --to "email-draft"
```

### Create and test a new prompt

```bash
# Create it
/braintrust create --slug "meeting-summary" \
  --name "Meeting Summary Generator" \
  --system "Extract key decisions and action items. Be concise." \
  --user "Summarize this meeting:\n\n{{notes}}"

# Test it
/braintrust invoke --slug "meeting-summary" \
  --input '{"notes": "We discussed the Q4 roadmap..."}'

# Generate TypeScript code for your app
/braintrust generate --slug "meeting-summary"
```

## Template Variables

Use Handlebars syntax in user messages:

```
Question: {{question}}
Subject: {{subject}}
Body: {{body}}
```

Variables are auto-detected by the `generate` command for TypeScript type generation.

## Best Practices

1. **Always diff before updating** -- review changes before applying
2. **Use A/B test for significant changes** -- compare outputs before committing
3. **Use descriptive slugs** -- `email-draft-v2` not `prompt-1`
4. **Check traces** -- use the Braintrust dashboard to debug issues

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Project not found" | Check `BRAINTRUST_PROJECT_NAME` is correct. Run `list` to see available projects. |
| "Prompt not found" | Verify slug spelling (case-sensitive). Check you're in the right project. |
| No traces in dashboard | Install SDK: `pip install braintrust`. Verify API key is valid. |
| "BRAINTRUST_API_KEY not set" | Add `BRAINTRUST_API_KEY=sk-...` to your `.env` file. |

Validate your API key:

```bash
curl -H "Authorization: Bearer $BRAINTRUST_API_KEY" \
  https://api.braintrust.dev/v1/project
```

## Links

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust Dashboard](https://www.braintrust.dev)
- [Braintrust API Reference](https://www.braintrust.dev/docs/reference/api)

## License

MIT
