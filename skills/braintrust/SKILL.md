---
name: braintrust
description: Manage Braintrust prompts via CLI. Create, update, delete, diff, and generate TypeScript code for prompts. Use when working with Braintrust prompts, LLM prompt management, or when the user mentions Braintrust, prompt iteration, or prompt versioning.
---

<objective>
Manage Braintrust prompts through a Python CLI. Supports listing, viewing, creating, updating, deleting, diffing, and generating TypeScript invocation code. The skill emphasizes safe iteration by always diffing prompts before updating.
</objective>

<quick_start>
Set environment variables:

```bash
export BRAINTRUST_API_KEY="sk-..."
export BRAINTRUST_PROJECT_NAME="Your_Project"
```

List prompts:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py list
```

Get prompt details:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py get --slug "my-prompt"
```

**Always diff before updating:**

```bash
python3 ~/.claude/skills/braintrust/braintrust.py diff --slug "my-prompt" --system "New content"
python3 ~/.claude/skills/braintrust/braintrust.py update --slug "my-prompt" --system "New content"
```

Generate TypeScript code:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py generate --slug "my-prompt"
```
</quick_start>

<success_criteria>
- Prompts listed from Braintrust project
- Prompt details displayed with system/user messages
- Diff shows unified diff output before updates
- Update applies changes to Braintrust
- Generated TypeScript code follows wrapTraced/initLogger pattern
- Traces appear in Braintrust dashboard after testing
</success_criteria>

<commands>
**list** - List all prompts in a project

```bash
python3 ~/.claude/skills/braintrust/braintrust.py list
python3 ~/.claude/skills/braintrust/braintrust.py list --project "My Project"
```

**get** - View prompt details including system and user messages

```bash
python3 ~/.claude/skills/braintrust/braintrust.py get --slug "email-draft"
```

**create** - Create a new prompt

```bash
python3 ~/.claude/skills/braintrust/braintrust.py create \
  --slug "email-draft" \
  --name "Email Draft Generator" \
  --description "Generates professional email drafts" \
  --system "You are an email assistant..." \
  --user "Write an email about: {{topic}}" \
  --model "claude-sonnet-4-5-20250929"
```

Parameters:
- `--slug` (required): URL-safe identifier
- `--name`: Human-readable name (defaults to slug)
- `--description`: What the prompt does
- `--system`: System message content
- `--user`: User message template (use `{{variable}}` for inputs)
- `--model`: Model name (default: claude-sonnet-4-5-20250929)
- `--project`: Project name (or use BRAINTRUST_PROJECT_NAME)

**diff** - **CRITICAL: Always diff before updating.** Shows what will change.

```bash
python3 ~/.claude/skills/braintrust/braintrust.py diff \
  --slug "my-prompt" \
  --system "New system message here"
```

Output shows unified diff:

```diff
--- current
+++ proposed
@@ -1,3 +1,3 @@
-You are helpful.
+New system message here.
```

**update** - Update an existing prompt

```bash
python3 ~/.claude/skills/braintrust/braintrust.py update \
  --slug "my-prompt" \
  --system "Updated system message" \
  --user "Updated user template: {{input}}"
```

**generate** - Generate TypeScript code for invoking the prompt

```bash
python3 ~/.claude/skills/braintrust/braintrust.py generate --slug "my-prompt"
```

Output follows the wrapTraced/initLogger pattern with proper serverless configuration.

**delete** - Delete a prompt (with confirmation)

```bash
python3 ~/.claude/skills/braintrust/braintrust.py delete --slug "my-prompt"
python3 ~/.claude/skills/braintrust/braintrust.py delete --slug "my-prompt" --force  # Skip confirmation
```
</commands>

<testing>
Standard workflow for testing prompts after changes:

**1. Run test script**

Create a test file or use the generated code:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py generate --slug "my-prompt" > /tmp/test-prompt.ts
```

**2. Execute with test input**

```typescript
// test-prompt.ts
import { invoke, wrapTraced, initLogger } from 'braintrust';

const logger = initLogger({
  projectName: process.env.BRAINTRUST_PROJECT_NAME!,
  apiKey: process.env.BRAINTRUST_API_KEY,
  asyncFlush: false,
});

const testPrompt = wrapTraced(async function testPrompt(input: { question: string }) {
  return await invoke({
    projectName: process.env.BRAINTRUST_PROJECT_NAME,
    slug: 'my-prompt',
    input: { question: input.question },
  });
});

// Run test
(async () => {
  const result = await testPrompt({ question: "Test input here" });
  console.log("Result:", result);
})();
```

Run with:

```bash
npx tsx /tmp/test-prompt.ts
```

**3. Verify in Braintrust dashboard**

Check traces at: `https://www.braintrust.dev/app/{org}/p/{project}/logs`

Look for:
- New trace with your test timestamp
- Input/output logged correctly
- Duration reasonable (typically 1-5 seconds)
- No errors in trace

**4. Validate output format**

If expecting JSON:

```typescript
import { z } from 'zod';

const OutputSchema = z.object({
  field1: z.string(),
  field2: z.array(z.string()),
});

const result = await testPrompt({ question: "Test" });
const validated = OutputSchema.safeParse(result);
if (!validated.success) {
  console.error("Validation failed:", validated.error.issues);
}
```

**Testing checklist:**
- [ ] Test with minimal valid input
- [ ] Test with maximum complexity input
- [ ] Test with edge cases (empty strings, special characters)
- [ ] Verify JSON structure (if structured output)
- [ ] Check response time (should be < 5s for most prompts)
- [ ] Verify traces appear in Braintrust dashboard
</testing>

<workflow>
**Creating a New Prompt**

1. Create prompt:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py create \
  --slug "my-new-prompt" \
  --system "..." \
  --user "..."
```

2. Generate code:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py generate \
  --slug "my-new-prompt" > invoke.ts
```

3. Test the prompt (see testing section)

**Updating a Prompt**

1. Get current state:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py get --slug "my-prompt"
```

2. Diff changes:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py diff \
  --slug "my-prompt" \
  --system "New system message"
```

3. Apply update:

```bash
python3 ~/.claude/skills/braintrust/braintrust.py update \
  --slug "my-prompt" \
  --system "New system message"
```

4. Test and verify (see testing section)
</workflow>

<environment_variables>
```bash
# Required
BRAINTRUST_API_KEY=sk-your-api-key

# Optional (can use --project flag instead)
BRAINTRUST_PROJECT_NAME=Your_Project_Name
```

Add to `.env` or export in shell.
</environment_variables>

<template_variables>
Use Handlebars syntax in user messages:

```
# Simple variable
Question: {{question}}

# Multiple variables
Subject: {{subject}}
From: {{sender}}
Body: {{body}}

# Loop (in prompt UI, not CLI)
{{#each messages}}
From: {{this.from}}
Body: {{this.body}}
{{/each}}
```
</template_variables>

<debugging>
**Check Braintrust Dashboard**

View traces at: `https://www.braintrust.dev/app/{org}/p/{project}/logs`

**Common Issues**

"Project not found"
- Check BRAINTRUST_PROJECT_NAME is correct
- Run `list` to see available projects/prompts

"Prompt not found"
- Verify slug spelling
- Check you're in the right project

No traces appearing
- Ensure `initLogger()` is called before invoke
- Use `asyncFlush: false` in serverless environments
- Check API key is valid

**API Key Validation**

```bash
curl -H "Authorization: Bearer $BRAINTRUST_API_KEY" \
  https://api.braintrust.dev/v1/project
```
</debugging>

<anti_patterns>
**Never update without diffing first**

```bash
# BAD - updating blind
python3 braintrust.py update --slug "my-prompt" --system "New content"

# GOOD - diff first
python3 braintrust.py diff --slug "my-prompt" --system "New content"
python3 braintrust.py update --slug "my-prompt" --system "New content"
```

**Never skip testing after updates**

Always verify:
1. Output format is correct
2. Traces appear in dashboard
3. Response time is reasonable

**Never use vague slugs**

```bash
# BAD
--slug "prompt-1"
--slug "test"

# GOOD
--slug "email-draft-v2"
--slug "user-summary-generator"
```
</anti_patterns>

<reference_guides>
- [Braintrust Docs](https://www.braintrust.dev/docs) - Official documentation
- [Braintrust API Reference](https://www.braintrust.dev/docs/reference/api) - API documentation
</reference_guides>
