# Dual-Native Claude + Codex Compatibility Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the repo runtime-agnostic with one shared CLI engine that works natively in Claude and Codex, while preserving Claude plugin compatibility.

**Architecture:** Keep `skills/braintrust/bt_cli.py` as the single source of command behavior. Add thin runtime adapters (`./braintrust` for shell/Codex and existing Claude plugin wrappers) that only forward arguments into the same core engine. Centralize env/project validation in the core so both runtimes get identical fail-fast behavior.

**Tech Stack:** Python 3, Bash, Braintrust API/SDK, Claude plugin metadata files, Markdown docs.

---

### Task 1: Add Runtime-Agnostic Shell Entrypoint

**Files:**
- Create: `braintrust`
- Modify: `.gitignore` (only if needed for local artifacts)
- Test: `braintrust` execution + help output

**Step 1: Write the failing check for missing wrapper**

Run:

```bash
ls -l braintrust
```

Expected: file not found.

**Step 2: Create minimal wrapper implementation**

Create `braintrust` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/skills/braintrust/bt_cli.py" "$@"
```

**Step 3: Make wrapper executable**

Run:

```bash
chmod +x braintrust
```

Expected: no output, exit 0.

**Step 4: Verify wrapper delegates to core CLI**

Run:

```bash
./braintrust --help
./braintrust list --help
```

Expected: both commands print argparse help and exit 0.

**Step 5: Commit**

```bash
git add braintrust
git commit -m "feat: add runtime-agnostic braintrust wrapper"
```

---

### Task 2: Centralize Fail-Fast Env and Project Validation in Core CLI

**Files:**
- Modify: `skills/braintrust/bt_cli.py`
- Test: command-level error checks

**Step 1: Write failing/behavior checks for current validation contract**

Run:

```bash
env -u BRAINTRUST_API_KEY ./braintrust list
./braintrust invoke --slug test-slug
```

Expected:
- First command fails with clear missing `BRAINTRUST_API_KEY` message.
- Second command fails with clear missing project (`--project` or `BRAINTRUST_PROJECT_NAME`) message.

**Step 2: Add reusable validation helpers (minimal implementation)**

In `skills/braintrust/bt_cli.py`, add helpers:

```python
def require_api_key() -> str:
    ...

def resolve_project(project_arg: str | None, *, required: bool, command_name: str) -> str | None:
    ...
```

Behavior:
- `require_api_key()` fails fast with actionable instructions.
- `resolve_project(...)` returns explicit project or env default.
- If required and missing, fail with command-specific guidance.

**Step 3: Route command handlers through helpers**

Update command handlers (`cmd_list`, `cmd_get`, `cmd_invoke`, `cmd_diff`, `cmd_update`, `cmd_test`, `cmd_promote`, plus `cmd_create`) so they:
- validate API key once at command entry
- resolve project consistently
- emit standardized errors

**Step 4: Verify fail-fast behavior after refactor**

Run:

```bash
env -u BRAINTRUST_API_KEY ./braintrust list || true
./braintrust invoke --slug test-slug || true
./braintrust test --slug test-slug || true
./braintrust promote --from a --to b || true
```

Expected:
- Each failing command prints explicit, non-ambiguous guidance.
- No stack traces for expected validation failures.

**Step 5: Commit**

```bash
git add skills/braintrust/bt_cli.py
git commit -m "refactor: centralize env and project validation"
```

---

### Task 3: Keep Claude Native While Making Workflow Runtime-Agnostic

**Files:**
- Modify: `README.md`
- Modify: `commands/braintrust.md`
- Modify: `skills/braintrust/SKILL.md`
- Modify: `plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Create: `docs/migration-claude-plugin-to-codex-workflow.md`

**Step 1: Write README failing check (Codex entrypoint absent in docs)**

Run:

```bash
rg -n "\./braintrust|Codex|runtime-agnostic" README.md
```

Expected: missing or insufficient coverage before edit.

**Step 2: Update README to dual-native structure**

Add:
- Runtime overview (Claude and Codex both supported)
- Codex/plain-shell setup using `./braintrust`
- Claude plugin setup using existing plugin files
- Canonical command surface examples: `list|get|invoke|diff|update|test|promote`
- Backward compatibility notes for retained Claude files

**Step 3: Add migration document**

Create `docs/migration-claude-plugin-to-codex-workflow.md` containing:
- 1:1 mapping table (`/braintrust ...` -> `./braintrust ...`)
- env setup differences
- which files are adapters vs core engine
- rollout guidance for teams using both runtimes

**Step 4: Update Claude adapter docs/metadata to reflect shared engine**

- `commands/braintrust.md`: clarify this is a Claude runtime adapter.
- `skills/braintrust/SKILL.md`: point to `SKILL_DIR/bt_cli.py` and non-interactive usage notes.
- `plugin.json` / `.claude-plugin/marketplace.json`: update descriptions to emphasize compatibility adapter role.

**Step 5: Verify documentation coverage**

Run:

```bash
rg -n "runtime-agnostic|Codex|migration|adapter|\./braintrust" README.md docs/migration-claude-plugin-to-codex-workflow.md commands/braintrust.md skills/braintrust/SKILL.md
```

Expected: all key terms present in the new docs.

**Step 6: Commit**

```bash
git add README.md commands/braintrust.md skills/braintrust/SKILL.md plugin.json .claude-plugin/marketplace.json docs/migration-claude-plugin-to-codex-workflow.md
git commit -m "docs: make workflow dual-native for Claude and Codex"
```

---

### Task 4: Add Smoke Test Script for Basic Command Surface

**Files:**
- Create: `scripts/smoke.sh`
- Modify: `README.md` (add test invocation section)

**Step 1: Write failing check for missing smoke script**

Run:

```bash
ls -l scripts/smoke.sh
```

Expected: file not found.

**Step 2: Implement smoke script**

Create `scripts/smoke.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[smoke] wrapper help"
./braintrust --help >/dev/null

echo "[smoke] canonical command help"
for cmd in list get invoke diff update test promote; do
  ./braintrust "$cmd" --help >/dev/null
done

echo "[smoke] missing API key fails fast"
if env -u BRAINTRUST_API_KEY ./braintrust list 2>&1 | rg -q "BRAINTRUST_API_KEY"; then
  :
else
  echo "Expected missing API key guidance" >&2
  exit 1
fi

echo "[smoke] missing project fails fast on project-required command"
if ./braintrust invoke --slug test-slug 2>&1 | rg -q "--project\|BRAINTRUST_PROJECT_NAME"; then
  :
else
  echo "Expected missing project guidance" >&2
  exit 1
fi

echo "[smoke] OK"
```

**Step 3: Make script executable and run it**

Run:

```bash
chmod +x scripts/smoke.sh
./scripts/smoke.sh
```

Expected: all smoke checks pass and script ends with `[smoke] OK`.

**Step 4: Document smoke command in README**

Add verification section with:

```bash
./scripts/smoke.sh
```

**Step 5: Commit**

```bash
git add scripts/smoke.sh README.md
git commit -m "test: add smoke verification for dual-runtime CLI"
```

---

### Task 5: Add Short Architecture Note and Final Verification Bundle

**Files:**
- Create: `docs/architecture/dual-runtime-architecture.md`
- Modify: `README.md` (link architecture note)

**Step 1: Add architecture note**

Create `docs/architecture/dual-runtime-architecture.md` with:
- core engine responsibility (`bt_cli.py`)
- adapter responsibilities (shell wrapper + Claude plugin wrappers)
- command-surface contract
- validation/error-handling contract

**Step 2: Link architecture note from README**

Add a short “Architecture” section with pointer to the new doc.

**Step 3: Run final verification commands**

Run:

```bash
./braintrust --help
./braintrust list --help
./braintrust get --help
./braintrust invoke --help
./braintrust diff --help
./braintrust update --help
./braintrust test --help
./braintrust promote --help
./scripts/smoke.sh
```

Expected:
- help commands exit 0
- smoke script exits 0 and prints success marker

**Step 4: Review final diff for deliverables**

Run:

```bash
git status --short
git diff --stat
```

Expected:
- includes wrapper, docs updates, migration doc, architecture note, smoke script, and CLI validation changes.

**Step 5: Commit**

```bash
git add docs/architecture/dual-runtime-architecture.md README.md
git commit -m "docs: add dual-runtime architecture note"
```

---

## Final Deliverable Checklist

- [ ] `skills/braintrust/bt_cli.py` remains core engine
- [ ] Claude runtime remains supported (native adapter)
- [ ] Codex/plain shell native entrypoint (`./braintrust`) works
- [ ] Canonical command surface implemented and documented
- [ ] Fail-fast env validation is explicit and consistent
- [ ] Migration doc exists
- [ ] Smoke script exists and passes
- [ ] Architecture note exists
- [ ] README reflects dual-native workflow

## Exact Local Verification Commands

```bash
./braintrust --help
./braintrust list --help
./braintrust get --help
./braintrust invoke --help
./braintrust diff --help
./braintrust update --help
./braintrust test --help
./braintrust promote --help
./scripts/smoke.sh
```
