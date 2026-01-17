# Braintrust CLI Reference

Detailed documentation for the Braintrust prompt management CLI.

## Contents

- [Testing Workflows](#testing-workflows)
- [TypeScript Integration](#typescript-integration)
- [Template Variables](#template-variables)
- [Debugging](#debugging)
- [Anti-Patterns](#anti-patterns)

## Testing Workflows

### Creating a New Prompt

1. Create the prompt:

```bash
python3 ./braintrust.py create \
  --slug "my-new-prompt" \
  --system "Your system message" \
  --user "Your user template with {{variables}}"
```

2. Generate TypeScript code:

```bash
python3 ./braintrust.py generate --slug "my-new-prompt" > invoke.ts
```

3. Test the prompt (see TypeScript Integration below)

### Updating a Prompt

1. Get current state:

```bash
python3 ./braintrust.py get --slug "my-prompt"
```

2. Diff changes:

```bash
python3 ./braintrust.py diff --slug "my-prompt" --system "New system message"
```

3. Apply update:

```bash
python3 ./braintrust.py update --slug "my-prompt" --system "New system message"
```

4. Test and verify in Braintrust dashboard

## TypeScript Integration

### Basic Invocation

```typescript
import { invoke, wrapTraced, initLogger } from 'braintrust';

const logger = initLogger({
  projectName: process.env.BRAINTRUST_PROJECT_NAME!,
  apiKey: process.env.BRAINTRUST_API_KEY,
  asyncFlush: false,  // Important for serverless environments
});

const myPrompt = wrapTraced(async function myPrompt(input: { question: string }) {
  return await invoke({
    projectName: process.env.BRAINTRUST_PROJECT_NAME,
    slug: 'my-prompt',
    input: { question: input.question },
  });
});

// Usage
const result = await myPrompt({ question: "Test input here" });
console.log("Result:", result);
```

Run with:

```bash
npx tsx invoke.ts
```

### Validating JSON Output

If your prompt returns structured JSON:

```typescript
import { z } from 'zod';

const OutputSchema = z.object({
  field1: z.string(),
  field2: z.array(z.string()),
});

const result = await myPrompt({ question: "Test" });
const validated = OutputSchema.safeParse(result);
if (!validated.success) {
  console.error("Validation failed:", validated.error.issues);
}
```

### Testing Checklist

- [ ] Test with minimal valid input
- [ ] Test with maximum complexity input
- [ ] Test with edge cases (empty strings, special characters)
- [ ] Verify JSON structure (if structured output)
- [ ] Check response time (should be < 5s for most prompts)
- [ ] Verify traces appear in Braintrust dashboard

## Template Variables

Use Handlebars syntax in user messages:

### Simple Variable

```
Question: {{question}}
```

### Multiple Variables

```
Subject: {{subject}}
From: {{sender}}
Body: {{body}}
```

### Loop Syntax

Note: Loops work in the Braintrust prompt UI but not in the CLI.

```
{{#each messages}}
From: {{this.from}}
Body: {{this.body}}
{{/each}}
```

## Debugging

### Check Braintrust Dashboard

View traces at: `https://www.braintrust.dev/app/{org}/p/{project}/logs`

Look for:
- New trace with your test timestamp
- Input/output logged correctly
- Duration reasonable (typically 1-5 seconds)
- No errors in trace

### Common Issues

**"Project not found"**
- Check BRAINTRUST_PROJECT_NAME is correct
- Run `list` to see available projects/prompts

**"Prompt not found"**
- Verify slug spelling (case-sensitive)
- Check you're in the right project

**No traces appearing**
- Ensure `initLogger()` is called before invoke
- Use `asyncFlush: false` in serverless environments
- Check API key is valid

### API Key Validation

```bash
curl -H "Authorization: Bearer $BRAINTRUST_API_KEY" \
  https://api.braintrust.dev/v1/project
```

## Anti-Patterns

### Never update without diffing first

```bash
# BAD - updating blind
python3 ./braintrust.py update --slug "my-prompt" --system "New content"

# GOOD - diff first
python3 ./braintrust.py diff --slug "my-prompt" --system "New content"
python3 ./braintrust.py update --slug "my-prompt" --system "New content"
```

### Never skip testing after updates

Always verify:
1. Output format is correct
2. Traces appear in dashboard
3. Response time is reasonable

### Never use vague slugs

```bash
# BAD
--slug "prompt-1"
--slug "test"

# GOOD
--slug "email-draft-v2"
--slug "user-summary-generator"
```

## External Resources

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust API Reference](https://www.braintrust.dev/docs/reference/api)
- [Braintrust Dashboard](https://www.braintrust.dev)
