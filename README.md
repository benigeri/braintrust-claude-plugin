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

### 1. Iterate on an Email Draft Prompt (Full Workflow)

You have an email drafting prompt that's too formal. Here's the proper workflow to safely iterate:

**Step 1: Review the current prompt**
```bash
python3 ./braintrust.py get --slug "email-draft"
```

**Step 2: Create a test version with your changes**
```bash
python3 ./braintrust.py create \
  --slug "email-draft-v2-test" \
  --name "Email Draft (Test)" \
  --system "You are a friendly email assistant. Write concise, warm emails. Avoid corporate jargon." \
  --user "{{email_context}}"
```

**Step 3: Test both versions side-by-side**

Generate test code and run both prompts with the same input:

```bash
python3 ./braintrust.py generate --slug "email-draft"
python3 ./braintrust.py generate --slug "email-draft-v2-test"
```

Run the generated code to invoke both prompts. The `wrapTraced` pattern ensures all calls are logged.

**Step 4: Compare outputs in Braintrust Dashboard**

Check traces at `https://www.braintrust.dev/app/{org}/p/{project}/logs`

Compare:
- Output quality between original and test version
- Response times
- Any errors or edge cases

**Step 5: Update the original once confirmed**
```bash
python3 ./braintrust.py diff --slug "email-draft" --system "You are a friendly email assistant..."
python3 ./braintrust.py update --slug "email-draft" --system "You are a friendly email assistant..."
```

**Step 6: Delete the test version**
```bash
python3 ./braintrust.py delete --slug "email-draft-v2-test" --force
```

### 2. Create a New Summarization Prompt

Build a prompt from scratch for summarizing meeting notes:

```bash
# Create the prompt
python3 ./braintrust.py create \
  --slug "meeting-summary" \
  --name "Meeting Summary Generator" \
  --description "Summarizes meeting notes into action items" \
  --system "You are a meeting assistant. Extract key decisions, action items with owners, and next steps. Be concise." \
  --user "Summarize this meeting:\n\n{{notes}}"

# Generate TypeScript code for your app
python3 ./braintrust.py generate --slug "meeting-summary"

# Test it, check logs, iterate as needed
```

### 3. Debug a Prompt That's Not Working

Your prompt returns malformed JSON. Debug it using the test version workflow:

```bash
# 1. Check the current prompt
python3 ./braintrust.py get --slug "data-extractor"

# 2. Create a test version with the fix
python3 ./braintrust.py create \
  --slug "data-extractor-debug" \
  --system "Extract data and return valid JSON. Always wrap response in ```json``` code blocks."

# 3. Test both versions, compare logs
python3 ./braintrust.py generate --slug "data-extractor"
python3 ./braintrust.py generate --slug "data-extractor-debug"

# 4. Check Braintrust logs to verify the fix works
# 5. Update original once confirmed
python3 ./braintrust.py update --slug "data-extractor" --system "..."

# 6. Delete debug version
python3 ./braintrust.py delete --slug "data-extractor-debug" --force
```

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
