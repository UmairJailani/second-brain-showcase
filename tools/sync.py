#!/usr/bin/env python3
"""Build the public Second Brain showcase from this private vault.

Privacy model (fail closed):
  1. Opt-in only. A note is published only if its frontmatter says `publish: true`.
  2. Redaction. Home-folder paths, machine names and similar details are rewritten.
  3. Per-note block. A note that still contains anything on the block list
     (emails, phone numbers, ID numbers, keys/tokens, money amounts, private terms)
     is skipped entirely, and the reason is logged.
  4. Link stripping. [[links]] to notes that are not published become plain text,
     so private note titles never leak through links.
  5. Final scan. The whole output folder is scanned again; any hit aborts the run
     with a non-zero exit code, so nothing is pushed.

Run hourly on the PC by publish.ps1 (Task Scheduler), which builds from committed
content only and verifies the push on GitHub.

Usage: python scripts/showcase/sync.py <output-dir>
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

VAULT = Path(__file__).resolve().parents[2]
SHOWCASE = VAULT / "showcase"
WIKI = VAULT / "wiki"
CONFIG = yaml.safe_load((SHOWCASE / "config.yml").read_text(encoding="utf-8"))

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
LINK_RE = re.compile(r"\[\[([^\]|#]+)(#[^\]|]*)?(?:\|([^\]]+))?\]\]")

# --- redaction: rewritten, note still published ---------------------------------
REDACT = [
    (re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s`'\")]+", re.I), "~"),
    (re.compile(r"/home/[^/\s`'\")]+"), "~"),
    (re.compile(r"[A-Za-z]:[\\/]+umair\b", re.I), "D:/data"),
]
for pattern, replacement in (CONFIG.get("replace") or {}).items():
    REDACT.append((re.compile(re.escape(pattern), re.I), replacement))

# --- block list: any hit means the note is NOT published -------------------------
BLOCK = {
    "email address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "phone number": re.compile(r"(?:\+92|\b0)3\d{2}[-\s]?\d{7}\b|\+\d{1,3}[\s-]?\d{3}[\s-]?\d{3,4}[\s-]?\d{3,4}"),
    "ID number": re.compile(r"\b\d{5}-\d{7}-\d\b"),
    "IP address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "API key or token": re.compile(
        r"(?:sk-[A-Za-z0-9_-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|AIza[0-9A-Za-z_-]{30,}"
        r"|xox[abpr]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
        r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|(?:password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S{6,})",
        re.I,
    ),
    "money amount": re.compile(r"\b(?:Rs\.?|PKR|USD|\$)\s?\d[\d,]*", re.I),
}
TERMS_FILE = SHOWCASE / "private-terms.txt"
PRIVATE_TERMS = [
    t.strip() for t in TERMS_FILE.read_text(encoding="utf-8").splitlines()
    if t.strip() and not t.startswith("#")
] if TERMS_FILE.exists() else []
if PRIVATE_TERMS:
    BLOCK["private term"] = re.compile("|".join(re.escape(t) for t in PRIVATE_TERMS), re.I)

KEEP_FM = ["title", "type", "status", "tags", "created", "updated"]


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return (fm if isinstance(fm, dict) else {}), text[m.end():]


def block_hits(text: str) -> list[str]:
    return [name for name, rx in BLOCK.items() if rx.search(text)]


def redact(text: str) -> str:
    for rx, rep in REDACT:
        text = rx.sub(rep, text)
    return text


def slug(path: Path) -> str:
    return path.stem


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(VAULT), *args], capture_output=True, text=True).stdout


def collect_notes() -> tuple[list[dict], list[str]]:
    published, skipped = [], []
    for path in sorted(WIKI.rglob("*.md")):
        fm, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if fm.get("publish") is not True:
            continue
        rel = path.relative_to(WIKI).as_posix()
        body = redact(body)
        title = str(fm.get("title") or path.stem.replace("-", " ").title())
        hits = block_hits(body + "\n" + title)
        if hits:
            skipped.append(f"{rel}: {', '.join(hits)}")
            continue
        published.append({"path": path, "rel": rel, "slug": slug(path), "fm": fm, "body": body, "title": title})
    return published, skipped


def rewrite_links(body: str, targets: dict[str, str]) -> str:
    def repl(m: re.Match) -> str:
        target = m.group(1).strip().split("/")[-1]
        label = (m.group(3) or m.group(1).split("/")[-1]).strip()
        if target in targets:
            return f"[{label}]({targets[target]}.md)"
        return label  # private note: keep only the readable text, no link
    return LINK_RE.sub(repl, body)


def note_date(n: dict) -> str:
    return str(n["fm"].get("updated") or n["fm"].get("created") or "")


def build(out: Path) -> None:
    if out.exists():
        for child in out.iterdir():
            if child.name == ".git":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)

    # 1. static, hand-written pages
    shutil.copytree(SHOWCASE / "static", out, dirs_exist_ok=True)
    tools = out / "tools"
    tools.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__), tools / "sync.py")
    shutil.copy2(Path(__file__).with_name("publish.ps1"), tools / "publish.ps1")

    # 2. opted-in notes
    notes, skipped = collect_notes()
    targets = {n["slug"]: n["slug"] for n in notes}
    notes_dir = out / "notes"
    notes_dir.mkdir(exist_ok=True)
    for n in notes:
        fm = {k: n["fm"][k] for k in KEEP_FM if k in n["fm"]}
        fm["title"] = n["title"]
        body = rewrite_links(n["body"], targets)
        header = "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=None) + "---\n"
        (notes_dir / f"{n['slug']}.md").write_text(header + body.lstrip("\n"), encoding="utf-8")

    notes.sort(key=note_date, reverse=True)
    index = ["# Notes", "", "Notes published from the private vault. Each one opted in with `publish: true` and passed the privacy filter.", "",
             "| Note | Type | Updated |", "|---|---|---|"]
    index += [f"| [{n['title']}]({n['slug']}.md) | {n['fm'].get('type', '')} | {note_date(n)} |" for n in notes]
    (notes_dir / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")

    # 3. generated stats (counts only, no private titles)
    all_notes = list(WIKI.rglob("*.md"))
    by_folder = Counter(p.relative_to(WIKI).parts[0] if len(p.relative_to(WIKI).parts) > 1 else "(root)" for p in all_notes)
    months = Counter(line[:7] for line in git("log", "--format=%ad", "--date=short").split())
    first = git("log", "--reverse", "--format=%ad", "--date=short").split()[:1]
    total_commits = sum(months.values())
    stats = [
        f"- **{len(all_notes)} notes** in the private vault, **{len(notes)} published** here",
        f"- **{total_commits} commits** since {first[0] if first else 'the start'}",
        "- Notes per area: " + ", ".join(f"{k} {v}" for k, v in sorted(by_folder.items(), key=lambda kv: -kv[1])),
    ]
    activity = ["| Month | Commits |", "|---|---|"] + [f"| {m} | {'▇' * max(1, round(c / 10))} {c} |" for m, c in sorted(months.items())]
    latest = [f"- [{n['title']}](notes/{n['slug']}.md) · {note_date(n)}" for n in notes[:8]] or ["- (none yet)"]

    readme = out / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace("{{STATS}}", "\n".join(stats))
    text = text.replace("{{ACTIVITY}}", "\n".join(activity))
    text = text.replace("{{LATEST}}", "\n".join(latest))
    text = text.replace("{{SYNCED}}", dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    readme.write_text(text, encoding="utf-8")

    # 4. final scan of everything that would be published (tools/ holds the filter's own patterns)
    leaks = []
    for f in out.rglob("*"):
        if not f.is_file() or ".git" in f.parts or "tools" in f.relative_to(out).parts:
            continue
        if f.suffix.lower() not in {".md", ".yml", ".yaml", ".txt", ".json", ".html", ".svg"}:
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        for name, rx in BLOCK.items():
            for m in rx.finditer(content):
                if name == "email address" and m.group(0).endswith("noreply.github.com"):
                    continue
                leaks.append(f"{f.relative_to(out).as_posix()}: {name}")
    for s in skipped:
        print(f"SKIPPED (privacy filter) {s}")
    print(f"Published {len(notes)} notes to {out}")
    if leaks:
        print("ABORT: final privacy scan found:", *sorted(set(leaks)), sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    build(Path(sys.argv[1]).resolve())
