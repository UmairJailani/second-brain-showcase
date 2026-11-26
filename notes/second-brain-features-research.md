---
title: What other AI second brains have (and what I added)
type: resource
status: active
tags: [resource, second-brain, research, voice, automation]
created: 2026-11-26
updated: 2026-11-26
---
# What other AI second brains have (and what I added)

Compared my vault with well-known public setups in November 2026: Daniel Miessler's Personal AI Infrastructure (PAI), Karpathy-style LLM wikis, Tiago Forte's Building a Second Brain, Nate B. Jones's capture-to-AI pipeline, and several published Obsidian + Claude + voice setups.

## The comparison

| Feature | Who has it | Me before | Now |
|---|---|---|---|
| Shared rules every AI reads first | Karpathy pattern (`CLAUDE.md` / `AGENTS.md`), PAI | ✅ | ✅ |
| "Current state" page + decision diary | Most LLM-wiki setups | ✅ `hot.md` + monthly diary | ✅ |
| Verified backups | Rare | ✅ checks GitHub, not the exit code | ✅ |
| Public view with a privacy filter | Quartz/digital gardens (opt-in flag) | ❌ | ✅ hourly opt-in sync |
| **Voice capture** (speak a thought, it lands in the inbox) | Telegram + Whisper pipelines, AutoADHD, voice journaling | ❌ | ✅ offline, Windows built-in |
| **Spoken brief** (the assistant talks back) | PAI's digital assistant has a voice | ❌ | ✅ reads hot.md aloud |
| **Inbox for raw captures** | Karpathy `raw/`, Forte's "Capture" step | ⚠️ `.raw/` existed, unused | ✅ `.raw/inbox/` + processing rule |
| **Weekly review** | Forte, Nate B. Jones "daily nudges", evening reviews | ❌ | ✅ auto-written every Sunday |
| **Purpose page (TELOS)** | PAI: mission, goals, challenges, strategies | ⚠️ spread across profile/goals | ✅ one draft page, my words marked ✍️ |
| Search over the whole vault | qmd, Smart Connections, MCP servers | ✅ `retrieve.py` (BM25 + rerank) | ✅ |
| Capture from the phone | Telegram bots, Slack, voice-memo apps | ❌ | ❌ needs an account and token, see below |
| Better transcription (Urdu, noisy audio) | whisper.cpp, SuperWhisper, Deepgram | ❌ | ❌ needs an install, see below |
| Spaced repetition for learning | Obsidian SR plugins, Anki | ⚠️ Anki used separately | ❌ |
| Passive capture (screen/meeting memory) | Screenpipe + MCP | ❌ | ❌ deliberately not: privacy cost too high |

## What I added (November 2026)
- **Voice capture:** `scripts/voice/capture.ps1` listens to the microphone (Windows' offline speech recognition), stops when I say "stop note" or pause, and saves `.raw/inbox/voice-<time>.md`. It can also transcribe a WAV file. Clear English only; for Urdu, Windows voice typing (Win+H) works in any text box.
- **Spoken brief:** `scripts/voice/brief.ps1` reads the date, inbox count and latest items from `hot.md` aloud.
- **Inbox rule:** agents process `.raw/inbox/` at the start of a session: file each capture into the right note, then archive it.
- **Weekly review:** `scripts/review/weekly_review.py` writes `wiki/reviews/weekly-YYYY-Www.md` every Sunday at 21:00: commits, new notes, diary decisions, inbox count, what's waiting on me, plus reflection prompts. It never overwrites a review I've written in.
- **TELOS page:** telos collects mission, goals, challenges, strategies and principles in one place. Lines from confirmed facts are marked ✅; lines only I can write are ✍️ and agents may not invent them.

## Worth adding later (needs a decision or an install)
1. **Phone capture via a Telegram bot.** Voice or text message → transcribed → inbox. Needs a bot token and something always running (PC on, or a small cloud function).
2. **Whisper transcription.** Much better accuracy, handles Urdu. Needs `whisper.cpp` or `faster-whisper` plus a model download (about 150 MB–1.5 GB).
3. **Spaced repetition** for Python and Japanese inside the vault, so learning notes turn into review cards.
4. **MCP access from the Claude desktop and phone apps**, so the vault can be queried outside Claude Code.

## Sources
- [Daniel Miessler: Building a Personal AI Infrastructure](https://danielmiessler.com/blog/personal-ai-infrastructure) and [PAI 5.0](https://danielmiessler.com/blog/announcing-pai-5-life-operating-system)
- [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), [NicholasSpisak/second-brain](https://github.com/NicholasSpisak/second-brain)
- [Forte Labs: How my second brain evolved with AI](https://optin.fortelabs.co/posts/how-my-second-brain-evolved-with-ai-and-yours-can-too)
- [Nate B. Jones on building a second brain](https://shows.acast.com/ai-news-strategy-daily-with-nate-b-jones/episodes/69ab3b84f6d1583bb8e58b3b)
- Voice pipelines: [AutoADHD](https://github.com/uetzel/AutoADHD), [Voice-activated second brain](https://carlonicolini.github.io/sections/tech/tech,/productivity/2026/04/11/voice-activated-second-brain.html), [Obsidian + Claude night shift](https://dev.to/sabahattink/how-i-automated-my-obsidian-vault-with-claude-it-now-works-the-night-shift-3gjl)
- Publishing with a filter: [sspaeti/second-brain-public](https://github.com/sspaeti/second-brain-public), [narze/garden-astro](https://github.com/narze/garden-astro), [Quartz private pages](https://quartz.jzhao.xyz/features/private-pages)
