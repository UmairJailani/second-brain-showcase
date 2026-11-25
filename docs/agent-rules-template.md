# Agent rules template

A cleaned-up version of the rulebook my AI agents (Claude Code and Codex) load at the start of every session. Put it in `AGENTS.md` (Codex and most agents) and point `CLAUDE.md` at the same text, so every agent follows one set of rules.

Replace the `<...>` parts with your own.

```markdown
# Working with <your name>

Use <path to vault> as the durable knowledge base.
Before substantial work, read wiki/hot.md, wiki/meta/preferences.md and the
relevant goal/project note. Current profile: wiki/meta/profile.md.
Do not assume old machine paths or historical plans are current.

- Keep communication short and plain. Give progress updates and clearly state
  finished or waiting.
- Complete authorized work without routine permission questions. Make ordinary
  implementation decisions independently. When the outcome needs my choice,
  offer two meaningful alternatives, not a yes/no question in disguise.
- Respect real system access controls. Never claim a preference disables
  enforcement, or that work continues unattended without a verified runner.
- Read local project instructions and the actual code first. Preserve unique
  work and unrelated changes.
- Fetch before judging remote sync. Verify backups against the live remote,
  not the local exit code.
- Learning: hints first, let me attempt the exercise; no finished solutions
  unless I ask.
- Record meaningful decisions and evidence in the current monthly diary,
  and keep wiki/hot.md short.
```

## Why each rule exists

| Rule | The failure it prevents |
|---|---|
| Read `hot.md` and the profile first | Sessions starting from zero, or from facts that changed months ago |
| "Do not assume old paths or plans are current" | Agents acting on a plan that was replaced, or a folder that moved |
| Two meaningful alternatives, not yes/no | Constant "should I proceed?" interruptions that add nothing |
| No claims about unattended work | An agent saying "I'll keep working overnight" with nothing actually running |
| Verify backups against the remote | A backup reported as done that never reached GitHub (this happened) |
| Hints first when learning | Finishing exercises *for* me, so I learn nothing |
| Diary + short `hot.md` | The next session not knowing what the last one did |
