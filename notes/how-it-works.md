---
title: How It Works
type: meta
status: evergreen
tags: [meta, reference]
created: 2026-06-16
updated: 2026-11-02
---
# How It Works

> Current 30 September 2026 guidance: [autonomy-contract](autonomy-contract.md) and workspace-inventory. The historical hook setup below is not proof those hooks are running on this Windows machine. Codex reads startup instructions and writes checkpoints during an active session; unattended work requires separately verified automation.

## The honest version: nothing is automatic by default

This is the single most important thing to understand. The vault is a folder of Markdown files. Claude doesn't watch your other projects, doesn't passively absorb what you do in Claude Code elsewhere, and doesn't "learn" in the model-weights sense.

What actually happens: **you (or a hook) tell Claude to write something here, and Claude writes it.** That's the whole mechanism. No telling → nothing saved.

So building an app in some other project folder, with Claude Code, does **not** automatically land in this brain. Claude Code in that project has no idea this vault exists unless one of the two things below is set up.

## Claude does not "develop" — the wiki does

Claude (the model) is the same Claude in every conversation, everywhere. It doesn't get smarter or carry memories between sessions on its own. What grows is the **wiki** — the files in this folder. Each session, Claude reads the relevant files (`hot.md`, `index.md`, specific pages) at the *start*, and writes updates at the *end* (when told to). The "brain" getting smarter = the file content getting richer and better cross-linked, which makes future Claude sessions that read those files start from a better position. It's external memory, not internal learning.

## Two ways to make other-project work reach this vault

**1. Manual, per-session (works today, zero setup)**
At the end of a session in any project, say `/save` (or "save this to my second brain") and either:
- give the full path: `/save to ~\Documents\Second Brain`, or
- rely on a global rule (see #2) so you don't have to type the path every time

**2. Global default, set once**
Add a rule to `~/.claude/CLAUDE.md` (your user-level config, applies to every project, not this vault's CLAUDE.md) saying something like:

```markdown
## /save destination
Default /save target (when no project-local wiki exists or isn't specified): ~\Documents\Second Brain
```

Then `/save` in *any* project, with no path typed, lands here by default. Still has to be said — not automatic.

**3. Historical Claude automation (recorded 2026-06-16; not reverified here)**
Two hooks in `~/.claude/settings.json`, global, fire in every Claude Code session, any project:

- **`PostToolUse` (Bash matcher)**: detects `git commit` the instant it happens, appends `{ts, cwd, command}` to `.vault-meta/activity-queue.jsonl`. No AI call, no network, never blocks the commit. Excludes `--help` and mentions-in-strings, only matches real commit invocations.
- **`SessionStart`**: fires at the start of every new Claude Code session anywhere. If the queue file is non-empty, it injects context telling Claude to distill the queued entries into this vault and clear the queue — folded in naturally, not the focus of the session, never blocking.

So: commit in any project → captured instantly. Next time Claude Code opens anywhere → distilled into here, lazily, no waiting. See `wiki/log.md` (2026-06-16 entry) for the setup record.

## What "ingest" vs "save" vs "query" actually do

- **ingest** = you hand it a *source* (article, transcript, doc) — it extracts and structures
- **save** = you hand it a *conversation* — it extracts and structures
- **query** = you ask a question — it reads what's already structured and answers

All three read/write the same wiki, so they compound together over time.

## Cross-project reading (the other direction)

This works the same way — opt-in, not automatic. If you want some *other* project's Claude Code to be able to read from this brain (not just write to it), add to that project's own `CLAUDE.md`:

```markdown
## Wiki Knowledge Base
Path: ~\Documents\Second Brain

When you need context not already in this project:
1. Read wiki/hot.md first (recent context, ~500 words)
2. If not enough, read index
3. Raw activity captures: activity-log
3. If you need domain specifics, read wiki/<domain>/_index.md
4. Only then read individual wiki pages
```

Without this block in that project, Claude there has no path to this vault and won't think to look.

## Summary

| Question | Answer |
|---|---|
| Does building an app elsewhere auto-save here? | No |
| Does Claude "learn" and carry it everywhere? | No — files do, Claude reads them fresh each time |
| Can I make it easy to save here from any project? | Yes — global `/save` default rule, see above |
| Can I make it fully automatic? | **Historically configured for Claude; current operation is unverified.** Every `git commit`, any project, captured instantly; distilled into the vault lazily at the next Claude Code session start |
| Does this vault grow on its own? | No — it grows when you ingest, save, or query+update it |
