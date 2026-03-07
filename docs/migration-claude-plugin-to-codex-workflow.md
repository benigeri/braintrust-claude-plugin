# Migration: Claude Plugin Workflow -> Codex/Shell Workflow

This project now supports two native runtime paths that share the same core CLI:

- Claude plugin path: `/braintrust ...`
- Shell/Codex path: `./braintrust ...`

Both execute `skills/braintrust/bt_cli.py`.

## Why Migrate

Use shell/Codex workflow when you want:

- terminal-native automation/scripts
- runtime-agnostic usage outside Claude
- identical command behavior across tooling

## 1:1 Command Mapping

| Claude plugin command | Shell/Codex equivalent |
|---|---|
| `/braintrust list` | `./braintrust list` |
| `/braintrust get --slug "email-draft"` | `./braintrust get --slug "email-draft"` |
| `/braintrust invoke --slug "email-draft" --input '{"topic":"follow-up"}'` | `./braintrust invoke --slug "email-draft" --input '{"topic":"follow-up"}'` |
| `/braintrust diff --slug "email-draft" --system "Updated..."` | `./braintrust diff --slug "email-draft" --system "Updated..."` |
| `/braintrust update --slug "email-draft" --system "Updated..."` | `./braintrust update --slug "email-draft" --system "Updated..."` |
| `/braintrust test --slug "email-draft" --input '{"topic":"test"}' --system "New..." --force` | `./braintrust test --slug "email-draft" --input '{"topic":"test"}' --system "New..." --force` |
| `/braintrust promote --from "email-draft-v2" --to "email-draft" --force` | `./braintrust promote --from "email-draft-v2" --to "email-draft" --force` |

## Environment Setup (Same for Both)

```bash
BRAINTRUST_API_KEY=sk-your-api-key
BRAINTRUST_PROJECT_NAME=Your_Project_Name  # optional default
```

- `BRAINTRUST_API_KEY` is required.
- `BRAINTRUST_PROJECT_NAME` is optional but recommended.
- `invoke` and `test` require `pip install braintrust`.

## Adapter vs Core Files

Core implementation:

- `skills/braintrust/bt_cli.py`

Shell/Codex adapter:

- `./braintrust`
- `AGENTS.md` (Codex skill registration)

Claude adapters:

- `plugin.json`
- `.claude-plugin/marketplace.json`
- `commands/braintrust.md`
- `skills/braintrust/SKILL.md`

## Rollout Guidance for Teams

1. Keep Claude plugin installed for users who prefer `/braintrust`.
2. Introduce `./braintrust` in docs and scripts for runtime-agnostic automation.
3. Standardize runbooks on canonical commands (`list`, `get`, `invoke`, `diff`, `update`, `test`, `promote`).
4. Use `./scripts/smoke.sh` in CI/local checks to guard command-surface drift.
