# Braintrust Prompt CLI (Claude + Codex)

A runtime-agnostic Braintrust prompt manager with one shared engine:

- Core engine: `skills/braintrust/bt_cli.py`
- Native shell/Codex entrypoint: `./braintrust`
- Native Claude entrypoint: `/braintrust` (via Claude plugin adapter files)

Both runtimes call the same CLI logic.

## Runtime Support

- `Codex / plain shell`: run `./braintrust <command>`
- `Claude Code plugin`: run `/braintrust <command>`

If you keep Claude plugin files (`plugin.json`, `.claude-plugin/*`, `commands/*`, `skills/*`), they act as adapters around the same core CLI.

## Setup

### 1) Configure environment

Add to `.env` (or export in shell):

```bash
BRAINTRUST_API_KEY=sk-your-api-key
BRAINTRUST_PROJECT_NAME=Your_Project_Name  # optional default project
```

Get API key: [braintrust.dev/app/settings/api-keys](https://www.braintrust.dev/app/settings/api-keys)

### 2) Install SDK for invoke/test tracing

```bash
pip install braintrust
```

### 3) Use the native shell entrypoint

```bash
chmod +x ./braintrust
./braintrust --help
```

## Claude Plugin Install (Optional Adapter)

Install in Claude Code:

```bash
claude plugin add github:benigeri/braintrust-claude-plugin
```

Or add in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["mcp", "Bash(python3 */bt_cli.py *)"]
  },
  "plugins": ["github:benigeri/braintrust-claude-plugin"]
}
```

Then use `/braintrust ...` commands in Claude.

## Canonical Command Surface

These commands are supported in both runtimes:

| Command | Shell/Codex | Claude |
|---|---|---|
| `list` | `./braintrust list` | `/braintrust list` |
| `get` | `./braintrust get --slug "x"` | `/braintrust get --slug "x"` |
| `invoke` | `./braintrust invoke --slug "x" --input '{"q":"..."}'` | `/braintrust invoke --slug "x" --input '{"q":"..."}'` |
| `diff` | `./braintrust diff --slug "x" --system "..."` | `/braintrust diff --slug "x" --system "..."` |
| `update` | `./braintrust update --slug "x" --system "..."` | `/braintrust update --slug "x" --system "..."` |
| `test` | `./braintrust test --slug "x" --input '{"q":"..."}' --system "..." --force` | `/braintrust test --slug "x" --input '{"q":"..."}' --system "..." --force` |
| `promote` | `./braintrust promote --from "x-v2" --to "x" --force` | `/braintrust promote --from "x-v2" --to "x" --force` |

Extended commands also available: `create`, `delete`, `generate`.

## Fail-Fast Validation

The shared CLI fails fast with explicit guidance when:

- `BRAINTRUST_API_KEY` is missing
- a command requires project context and neither `--project` nor `BRAINTRUST_PROJECT_NAME` is set

## Migration

Moving from plugin-only workflow to shell/Codex workflow:

- [Migration guide](docs/migration-claude-plugin-to-codex-workflow.md)

## Verification

Run smoke checks:

```bash
./scripts/smoke.sh
```

## Architecture

- [Dual runtime architecture note](docs/architecture/dual-runtime-architecture.md)

## Backward Compatibility

Claude plugin files are retained for native Claude usage. They are compatibility adapters around the same CLI core, not a separate implementation.

## Links

- [Braintrust Docs](https://www.braintrust.dev/docs)
- [Braintrust Dashboard](https://www.braintrust.dev)

## License

MIT
