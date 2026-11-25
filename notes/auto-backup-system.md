---
type: project
status: active
tags: [project, infra, backup]
created: 2026-08-11
updated: 2026-11-20
title: Auto Backup System
---
# Auto-Backup System

A background safety net that periodically commits and pushes uncommitted work across every git-tracked project, second-brain, and Claude's own native memory — so a crashed/interrupted session can never again lose more than ~10 minutes of work, and a "backed up" claim is never taken on faith.

## Why this exists

2026-08-11: Umair's PC (running Claude Code on a "new build" for Yaad) started overheating and crashing. Claude had told him work was backed up along the way and he trusted it. When the laptop caught up on the project later, neither the `yaad` GitHub repo nor the `second-brain` vault showed any trace of that PC session's final work or the real-world milestone (Play Store production rollout) it involved. Checked GitHub directly (not just local clones) for both repos — no hidden branches, no unmerged PRs, nothing. Conclusion: a push was confirmed that either never actually happened or never actually reached the remote — the confirmation itself was the failure point, not a sync gap between devices.

## Scope

Three things get swept on the same schedule, same mechanism:

1. **Code repos** — every git repo found under `~/Projects/*` (auto-discovered, not a maintained list — new projects get picked up automatically)
2. **Second brain** — `~/Projects/second-brain`, same mechanism as #1. This layers on top of, not replaces, Obsidian's own git plugin (which only runs while Obsidian is open) — it covers edits made directly by Claude Code with Obsidian closed.
3. **Claude's native memory** — `~/.claude/projects/*/memory/` isn't a git repo and shouldn't become one directly (the rest of `.claude/` holds transcripts/config that shouldn't be swept into git). Instead, a sync step mirrors just the `memory/` subfolders into `~/Projects/second-brain/claude-memory/<hostname>/<project-slug>/` before the normal sweep runs — so it rides along as part of second-brain's own backup, no separate repo needed.

## Mechanism

Periodic only (not reactive/instant) — a systemd (Linux's standard background-service manager) `--user` timer (a scheduled job tied to the logged-in user, not the whole system) firing every 10 minutes. Rejected a file-watcher/reactive layer as unnecessary complexity: the failure being fixed is "a session got cut off," not sub-minute data loss, and one moving part is easier to keep healthy than two.

### Memory-mirror sync step (runs first, only affects second-brain)

For each `~/.claude/projects/*/memory/` directory:
```
rsync -a --delete <source>/memory/ ~/Projects/second-brain/claude-memory/$(hostname)/<project-slug>/
```
`rsync` is a standard file-copying tool that only copies what's changed, rather than the whole folder every time. `--delete` so removed/renamed memory files don't linger forever in the backup. `<project-slug>` is the raw encoded folder name Claude Code already uses (e.g. `-home-umairj`) — no decoding needed, just needs to be unique and stable. Keyed by hostname (the machine's own network name) so the laptop and PC's memory dumps sit side by side without colliding.

### Per-repo backup step (runs for every repo under `~/Projects/*`, including second-brain after the sync step above)

For each repo:
1. `flock` (a lock file that stops two copies of the same job running at once) on a per-repo lockfile — skip this cycle if a previous run is still in flight (safety against a slow push overlapping the next tick)
2. `git pull --rebase --autostash -q` — pulls in anything pushed from another machine first; `--autostash` so any local uncommitted changes survive the rebase (git's way of replaying your own changes on top of newly-pulled ones instead of merging them side by side). If this fails (real conflict), log an ERROR and stop for this repo this cycle — never auto-resolve a conflict.
3. If `git status --porcelain` shows anything: `git add -A` then `git commit -m "auto-backup: <ISO timestamp> [<hostname>]"`
4. `git push -q`
5. **Verify, don't trust the exit code**: `git fetch -q` then compare local `HEAD` (the commit this machine thinks is current) against `@{u}` (the upstream ref — what GitHub actually has). Only a match counts as a confirmed backup. This is the exact step that was missing on 2026-08-11 — a push can report success and still not be what actually landed.
6. Log the outcome (repo, timestamp, success/fail/skip-no-changes) to `~/.local/state/auto-backup/backup.log`. Also visible via `journalctl --user -u auto-backup.service` (the command that shows a systemd service's own log history) since it runs as a systemd service.
7. On any failure (conflict, rejected push, or verify mismatch): `notify-send` (Linux's command for popping up a desktop notification) a desktop alert. Silent on success/no-op, so this doesn't nag every 10 minutes when everything's fine.

### Systemd units

- `~/.config/systemd/user/auto-backup.service` — `Type=oneshot` (tells systemd this job runs once to completion and exits, rather than staying running), runs the script
- `~/.config/systemd/user/auto-backup.timer` — `OnUnitActiveSec=10min` (run again 10 minutes after the last run finished), `OnBootSec=2min` (also run 2 minutes after startup), `Persistent=true` (normally means "catch up on a missed run after the machine was asleep/off") — note: `Persistent=true` only actually affects `OnCalendar=` (wall-clock) timers per `systemd.timer(5)` (the systemd manual page for timers), not the monotonic `OnBootSec=`/`OnUnitActiveSec=` used here, so it doesn't guarantee sleep/shutdown catch-up the way it sounds like it would. In practice this still runs ~10min after the next activation and 2min after a cold boot, which is close enough for this use case.
- Enabled via `systemctl --user enable --now auto-backup.timer`

## What this does NOT fix

This protects files that already exist on disk. It does not create a record of something that happened purely in a web UI with nothing ever written down (e.g. clicking "roll out" in Play Console) — that still needs one line typed somewhere, by Umair or Claude, before there's anything for this system to back up. Once it's typed, though, it can't get lost to a crash again.

## Rollout

Built and enabled on the laptop (`the Linux laptop`) first. **Needs replicating on the PC once it's back — but as a real Windows build, not a copy.** The PC is coming back on Windows after a reinstall, not Linux, so the systemd/bash/pkexec implementation here cannot be copy-pasted; see `scripts/auto-backup/README.md`'s Windows section for the architectural mapping (Windows Task Scheduler in place of systemd, PowerShell in place of the bash shell scripting, no `pkexec` — Linux's tool for running one command as admin — needed on Windows, which has its own UAC prompt) — deliberately left unbuilt/untested until that machine actually exists, per the standing rule to scan a device before replicating anything onto it (preferences #13).

**Implemented and enabled on `the Linux laptop` (this laptop), 2026-08-11.** Verified end-to-end: real dry run against `yaad` and `second-brain` showed clean `[OK]` entries for both, `claude-memory/<hostname>/` populated in second-brain. Still needs the same setup run on the PC once it's fixed — see `scripts/auto-backup/README.md` for the exact steps.

## Related

preferences (backup-related standing rules), yaad-app (the project whose loss triggered this), device-sync (laptop/PC parity tracking — add this system to that manifest once it exists on both machines)
