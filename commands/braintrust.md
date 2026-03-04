---
name: braintrust
description: Claude adapter for the shared Braintrust CLI
skill: braintrust
---

# /braintrust

Claude-native adapter for the shared CLI engine at `skills/braintrust/bt_cli.py`.

Run:

```bash
/braintrust <command> [options]
```

Canonical cross-runtime commands:

- `list`
- `get --slug X`
- `invoke --slug X --input '{...}'`
- `diff --slug X --system "..."`
- `update --slug X --system "..."`
- `test --slug X --input '{...}' [--system "..."] [--force]`
- `promote --from X --to Y [--force]`

For full details, see `skills/braintrust/SKILL.md`.
