## Skills
A skill is a set of local instructions stored in a `SKILL.md` file.

### Available skills
- braintrust: Runtime-agnostic Braintrust prompt management for Claude and Codex. Use for prompt listing, retrieval, invoke/testing, diff/update, and promotion. (file: skills/braintrust/SKILL.md)

### How to use skills
- Trigger rule: If the task involves Braintrust prompt operations (or mentions `/braintrust` / `./braintrust`), use the `braintrust` skill.
- Runtime mapping:
  - Codex/shell: `./braintrust <command> [options]`
  - Claude plugin: `/braintrust <command> [options]`
- Both adapters call the same implementation: `skills/braintrust/bt_cli.py`.
