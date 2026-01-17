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

Get your API key: [Braintrust API Keys](https://www.braintrust.dev/app/settings/api-keys)

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

## Use Cases

### 1. Iterate on an Email Draft Prompt

You have an email drafting prompt that's too formal. Use the plugin to iterate:

```bash
# See current prompt
/braintrust get --slug "email-draft"

# Preview your changes
/braintrust diff --slug "email-draft" --system "You are a friendly email assistant. Write concise, warm emails that get to the point quickly. Avoid corporate jargon."

# Apply the update
/braintrust update --slug "email-draft" --system "You are a friendly email assistant. Write concise, warm emails that get to the point quickly. Avoid corporate jargon."

# Generate code to test it
/braintrust generate --slug "email-draft"
```

### 2. Create a New Summarization Prompt

Build a prompt from scratch for summarizing meeting notes:

```bash
# Create the prompt
/braintrust create \
  --slug "meeting-summary" \
  --name "Meeting Summary Generator" \
  --description "Summarizes meeting notes into action items" \
  --system "You are a meeting assistant. Extract key decisions, action items with owners, and next steps. Be concise." \
  --user "Summarize this meeting:\n\n{{notes}}"

# Generate TypeScript code for your app
/braintrust generate --slug "meeting-summary"
```

### 3. Debug a Prompt That's Not Working

Your prompt returns malformed JSON. Debug it:

```bash
# Check the current prompt
/braintrust get --slug "data-extractor"

# Look for issues: missing JSON instructions? Wrong model?
# Fix by adding explicit JSON formatting
/braintrust diff --slug "data-extractor" --system "Extract data and return valid JSON. Always wrap response in ```json``` code blocks."

# Apply fix
/braintrust update --slug "data-extractor" --system "Extract data and return valid JSON. Always wrap response in ```json``` code blocks."
```

Then check the [Braintrust Dashboard](https://www.braintrust.dev) logs to verify traces show correct output.

## Template Variables

Use Handlebars syntax in user messages:

```
# Simple variable
Question: {{question}}

# Multiple variables
Subject: {{subject}}
From: {{sender}}
Body: {{body}}
```

## Testing Prompts

After creating or updating a prompt, test it:

**1. Generate TypeScript code:**

```bash
/braintrust generate --slug "my-prompt"
```

**2. Run with test input:**

```typescript
import { invoke, wrapTraced, initLogger } from 'braintrust';

const logger = initLogger({
  projectName: process.env.BRAINTRUST_PROJECT_NAME!,
  apiKey: process.env.BRAINTRUST_API_KEY,
  asyncFlush: false,  // Important for serverless
});

const testPrompt = wrapTraced(async function testPrompt(input: { question: string }) {
  return await invoke({
    projectName: process.env.BRAINTRUST_PROJECT_NAME,
    slug: 'my-prompt',
    input: { question: input.question },
  });
});

// Run test
const result = await testPrompt({ question: "Test input" });
console.log("Result:", result);
```

**3. Verify in Braintrust Dashboard:**

Check traces at `https://www.braintrust.dev/app/{org}/p/{project}/logs`

## Best Practices

1. **Always diff before updating** - Review changes before applying
2. **Use descriptive slugs** - `email-draft-v2` not `prompt-1`
3. **Test after updates** - Verify prompts work as expected
4. **Check traces** - Use Braintrust dashboard to debug issues

## Troubleshooting

**"Project not found"**
- Check `BRAINTRUST_PROJECT_NAME` is correct
- Run `list` to see available projects/prompts

**"Prompt not found"**
- Verify slug spelling (case-sensitive)
- Check you're in the right project

**No traces appearing in dashboard**
- Ensure `initLogger()` is called before invoke
- Use `asyncFlush: false` in serverless environments
- Verify API key is valid

**Validate API key:**

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
