# Braintrust CLI Reference

Complete documentation for the Braintrust prompt management CLI.

## Contents

- [Commands Overview](#commands-overview)
- [Invoke Command](#invoke-command)
- [Test Command (A/B Testing)](#test-command-ab-testing)
- [Promote Command](#promote-command)
- [TypeScript Integration](#typescript-integration)
- [Template Variables](#template-variables)
- [Debugging](#debugging)
- [Anti-Patterns](#anti-patterns)

## Commands Overview

| Command | Description | Side Effects |
|---------|-------------|--------------|
| `list` | List all prompts | None |
| `get --slug X` | View prompt details | None |
| `invoke --slug X` | Run prompt, see output | Creates trace |
| `test --slug X` | Test prompt (simple or A/B) | May create v2 prompt |
| `diff --slug X` | Preview changes | None |
| `update --slug X` | Apply changes | Modifies prompt |
| `create --slug X` | Create new prompt | Creates prompt |
| `generate --slug X` | Generate TypeScript | None |
| `delete --slug X` | Delete prompt | Deletes prompt |
| `promote --from X --to Y` | Copy X content to Y | Modifies Y |

## Invoke Command

Run a prompt with given input and see the result with full tracing.

### Syntax

```bash
python3 ./braintrust.py invoke \
  --slug "prompt-slug" \
  --input '{"variable": "value"}' \
  [--project "Project Name"] \
  [--verbose]
```

### Parameters

| Parameter | Short | Required | Description |
|-----------|-------|----------|-------------|
| `--slug` | | Yes | Prompt slug to invoke |
| `--input` | `-i` | No | JSON input data |
| `--input-file` | `-f` | No | Read input from JSON file |
| `--project` | | No | Project name (or use env var) |
| `--verbose` | `-v` | No | Show request details |

### Examples

```bash
# Basic invocation
python3 ./braintrust.py invoke --slug "summarizer" --input '{"text": "Hello world"}'

# With input file
python3 ./braintrust.py invoke --slug "summarizer" --input-file test-input.json

# Verbose mode
python3 ./braintrust.py invoke --slug "summarizer" -i '{"text": "test"}' -v
```

### Output

```
=== Output ===
This is the prompt response...

=== Metadata ===
Duration: 892ms
Trace: https://www.braintrust.dev/app/...
```

### Requirements

Install Braintrust SDK for full tracing:

```bash
pip install braintrust
```

## Test Command (A/B Testing)

Test a prompt with two modes:
1. **Simple test**: Just run the prompt and see output
2. **A/B test**: Compare current prompt with proposed changes

### Simple Test

```bash
python3 ./braintrust.py test --slug "my-prompt" --input '{"question": "test"}'
```

Same as invoke, but named `test` for clarity in workflows.

### A/B Test (Compare Changes)

When you provide `--system` or `--user`, the test command automatically:
1. Creates a `{slug}-v2` prompt with your changes
2. Runs both prompts with the same input
3. Shows side-by-side comparison
4. Asks if you want to promote v2 to the original

```bash
python3 ./braintrust.py test \
  --slug "email-draft" \
  --input '{"topic": "meeting follow-up"}' \
  --system "You are an expert email writer. Be concise and professional."
```

### A/B Test Output

```
🔬 A/B Test: email-draft vs email-draft-v2
==================================================

📝 Creating email-draft-v2 with proposed changes...
✓ Created email-draft-v2

Running both prompts with same input...
--------------------------------------------------

🅰️  ORIGINAL (email-draft):
------------------------------
Subject: Follow-up from our meeting

Dear Team,

Thank you for meeting with me today...

🅱️  V2 (email-draft-v2):
------------------------------
Subject: Meeting Follow-up

Hi Team,

Quick follow-up from today's discussion...

==================================================
📊 Comparison:
  Original: 1234ms
  V2:       1156ms

--------------------------------------------------
Promote email-draft-v2 → email-draft? [y/N]: y

✓ Promoted email-draft-v2 to email-draft
Delete email-draft-v2? [Y/n]: y
✓ Deleted email-draft-v2
```

### A/B Test Parameters

| Parameter | Description |
|-----------|-------------|
| `--slug` | Original prompt to test against |
| `--input` | Test input (JSON) |
| `--system` | Proposed system message (triggers A/B mode) |
| `--user` | Proposed user message (triggers A/B mode) |

### A/B Test Workflow

```bash
# 1. Check current prompt
python3 ./braintrust.py get --slug "my-prompt"

# 2. Run A/B test with changes
python3 ./braintrust.py test \
  --slug "my-prompt" \
  --input '{"question": "What is machine learning?"}' \
  --system "You are an expert teacher. Use analogies and examples."

# 3. Review outputs, decide to promote or not

# 4. If promoted, you're done!
# If not promoted, v2 remains for further iteration:
python3 ./braintrust.py test \
  --slug "my-prompt-v2" \
  --input '{"question": "different test"}'
```

## Promote Command

Manually promote changes from one prompt to another.

### Syntax

```bash
python3 ./braintrust.py promote \
  --from "source-slug" \
  --to "target-slug" \
  [--force] \
  [--keep]
```

### Parameters

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--from` | | Source prompt slug |
| `--to` | | Target prompt slug |
| `--force` | `-f` | Skip confirmation |
| `--keep` | | Keep source prompt after promotion |

### Example

```bash
# Promote after manual testing
python3 ./braintrust.py promote --from "email-draft-v2" --to "email-draft"

# Keep the v2 for reference
python3 ./braintrust.py promote --from "email-draft-v2" --to "email-draft" --keep
```

### Output

```
Promoting email-draft-v2 → email-draft

=== System Message Diff ===
--- current
+++ proposed
@@ -1,3 +1,3 @@
-You are an email assistant.
+You are an expert email writer. Be concise and professional.

=== User Message Diff ===
(no changes)

Apply these changes to email-draft? [y/N]: y

✓ Promoted email-draft-v2 → email-draft
Delete email-draft-v2? [Y/n]: y
✓ Deleted email-draft-v2
```

## TypeScript Integration

### Generated Code Pattern

```bash
python3 ./braintrust.py generate --slug "my-prompt"
```

Generates:

```typescript
import { invoke, wrapTraced, initLogger } from 'braintrust';

// Initialize logger ONCE at app startup
const logger = initLogger({
  projectName: process.env.BRAINTRUST_PROJECT_NAME!,
  apiKey: process.env.BRAINTRUST_API_KEY,
  asyncFlush: false, // CRITICAL for serverless
});

interface MyPromptInput {
  question: string;
}

export const myPrompt = wrapTraced(async function myPrompt(
  input: MyPromptInput
) {
  return await invoke({
    projectName: process.env.BRAINTRUST_PROJECT_NAME,
    slug: 'my-prompt',
    input,
  });
});
```

### Key Points

1. **initLogger once** - At app startup, not per-request
2. **asyncFlush: false** - Required for serverless (Vercel, Lambda)
3. **wrapTraced** - Automatic tracing for your function
4. **invoke** - Calls the prompt with variables

## Template Variables

Use Handlebars syntax in prompts:

```
Question: {{question}}
Context: {{context}}
```

Variables are automatically detected by `generate` command.

## Debugging

### View Traces

After invoke/test, click the trace URL or visit:
```
https://www.braintrust.dev/app/{org}/p/{project}/logs
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Prompt not found" | Check slug spelling, verify project |
| "Project not found" | Check BRAINTRUST_PROJECT_NAME |
| No tracing | Install SDK: `pip install braintrust` |
| Timeout | Check model config in dashboard |

### Validate API Key

```bash
curl -H "Authorization: Bearer $BRAINTRUST_API_KEY" \
  https://api.braintrust.dev/v1/project
```

## Anti-Patterns

### Never update without testing

```bash
# BAD
python3 ./braintrust.py update --slug "my-prompt" --system "New content"

# GOOD - A/B test first
python3 ./braintrust.py test \
  --slug "my-prompt" \
  --input '{"test": "input"}' \
  --system "New content"
```

### Never skip the comparison step

```bash
# BAD - blind update based on intuition
python3 ./braintrust.py update --slug "my-prompt" --system "I think this is better"

# GOOD - actually compare outputs
python3 ./braintrust.py test --slug "my-prompt" --input '{"q": "test"}' --system "New version"
# Review both outputs, THEN decide
```

### Never use vague slugs

```bash
# BAD
--slug "prompt-1"
--slug "test"

# GOOD
--slug "email-draft-v2"
--slug "deep-research-reduce-v2"
```

## External Resources

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust Python SDK](https://pypi.org/project/braintrust/)
- [Braintrust Dashboard](https://www.braintrust.dev)
