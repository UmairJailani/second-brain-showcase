---
title: Public showcase pipeline
type: project
status: active
tags: [project, github, privacy, automation]
created: 2026-11-26
updated: 2026-11-26
---
# Public showcase pipeline

The vault is private. A public repo, `UmairJailani/second-brain-showcase`, shows how it works and publishes selected notes. It updates itself every hour.

## How it works
1. **Opt-in.** A note goes public only if its frontmatter has `publish: true`.
2. **Hourly job.** Task Scheduler runs `scripts/showcase/publish.ps1` at 20 past each hour and at logon. It clones the vault's *committed* content into a temporary folder, so unsaved edits never get published.
3. **Privacy filter.** `scripts/showcase/sync.py` rewrites home paths and machine names, skips any note containing an email, phone number, ID number, IP address, key or token, money amount or a term from `showcase/private-terms.txt`, turns links to private notes into plain text, and keeps only safe frontmatter fields.
4. **Final scan.** The built output is scanned again; any hit stops the run and nothing is pushed.
5. **Verify.** After pushing, the job compares the local commit with GitHub's. Log: `%LOCALAPPDATA%\second-brain-showcase\sync.log`.

Hand-written pages (README, docs) live in `showcase/static/`. Stats and the latest-notes list are generated on each run.

## Decisions and reasoning
- **Opt-in, not opt-out.** Listing everything private is impossible; listing what is public is easy. A forgotten flag means a note stays private, never the reverse.
- **Skip whole notes instead of blacking out words.** Partial redaction still reveals that something was there.
- **Local job instead of a GitHub Action.** An Action would need a new deploy key stored as a secret. Creating that key was blocked, so the job runs on the PC with the existing GitHub login. Trade-off: the showcase only updates while the PC is on.
- **Build from commits, not the working folder.** Notes being edited mid-session are often unfinished and unchecked.
- **Fail closed.** If the filter is unsure, the run stops. A stale showcase is harmless; a leak is not.

## First run (2026-11-26)
Three notes published. The storage-move note was skipped by the filter because it names a private recovery folder, which shows the per-note block working.

## To publish another note
Add `publish: true` to its frontmatter and commit. The next hourly run picks it up. Check `sync.log` for `SKIPPED` lines if it doesn't appear.

## Related
The profile README on GitHub has a "Recently" section that a GitHub Action in the profile repo refreshes every 6 hours from the showcase's notes list and recently updated public repos.
