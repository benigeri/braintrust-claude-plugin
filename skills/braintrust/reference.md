# Braintrust CLI Reference

Detailed parameter docs for the shared CLI engine. Run examples from repo root using `./braintrust` (or `/braintrust` in Claude).

## invoke

Runs a prompt and displays the result with tracing.

```bash
./braintrust invoke --slug "my-prompt" --input '{"key": "value"}' [--project "Name"] [--verbose]
```

| Parameter | Short | Required | Description |
|-----------|-------|----------|-------------|
| `--slug` | | Yes | Prompt slug |
| `--input` | `-i` | No | JSON input |
| `--input-file` | `-f` | No | Read input from JSON file |
| `--project` | | No | Project name (or env var) |
| `--verbose` | `-v` | No | Show request details |

Requires `pip install braintrust` for SDK tracing.

## test

Runs a prompt (simple) or compares original vs proposed changes (A/B).

**Simple test** — just runs the prompt:
```bash
./braintrust test --slug "my-prompt" --input '{"q": "test"}'
```

**A/B test** — pass `--system` or `--user` to trigger comparison:
```bash
./braintrust test --slug "my-prompt" \
  --input '{"q": "test"}' \
  --system "New instructions" \
  --force
```

A/B mode automatically:
1. Creates `{slug}-v2` with your changes
2. Runs both prompts with the same input
3. Shows side-by-side comparison
4. With `--force`: auto-promotes and cleans up v2

| Parameter | Description |
|-----------|-------------|
| `--slug` | Original prompt to test against |
| `--input` / `-i` | Test input (JSON) |
| `--system` | Proposed system message (triggers A/B) |
| `--user` | Proposed user message (triggers A/B) |
| `--force` / `-y` | Skip interactive prompts (auto-promotes in A/B mode) |

## promote

Copies content from one prompt to another.

```bash
./braintrust promote --from "slug-v2" --to "slug" [--force] [--keep]
```

| Parameter | Short | Description |
|-----------|-------|-------------|
| `--from` | | Source prompt slug |
| `--to` | | Target prompt slug |
| `--force` | `-y` | Skip all confirmations |
| `--keep` | | Keep source prompt after promotion |

## generate

Generates TypeScript invocation code with `wrapTraced` and `initLogger`.

```bash
./braintrust generate --slug "my-prompt"
```

Key points for generated code:
- Call `initLogger` once at app startup, not per-request
- Use `asyncFlush: false` in serverless environments (Vercel, Lambda)
- `wrapTraced` provides automatic tracing

## Template Variables

Use Handlebars syntax in user messages: `{{variable_name}}`. Variables are auto-detected by the `generate` command.

## Debugging

After invoke/test, check traces at `https://www.braintrust.dev/app/{org}/p/{project}/logs`.

| Issue | Fix |
|-------|-----|
| "Prompt not found" | Check slug spelling and project |
| "Project not found" | Check `BRAINTRUST_PROJECT_NAME` |
| No tracing | `pip install braintrust` |
