#!/usr/bin/env python3
"""nara-grooming skills usage: count how often each skill was actually reached for.

Usage: usage.py            (prints one JSON object)
Reads session transcripts and counts, per skill directory found under the skill roots:
  slash  user-typed `<command-name>/<skill></command-name>`
  tool   assistant `Skill` tool_use whose `skill` input equals the skill name exactly
  reads  `Read` of a file inside the skill directory, from a session whose cwd does NOT
         contain that file (reading your own source tree while editing it is development)

Status per skill, in order:
  used          slash + tool > 0
  viewed        no invocation, reads > 0 (recall value, not adherence)
  probation     no invocation, but the name appeared inside the window (git add/rename)
  unused        no invocation, no read, name older than the window
  unverifiable  no invocation, no read, age unknown (no git history for the name)

Only transcripts this runtime writes are read. Runs from other runtimes or schedulers are
invisible here, so an `unused` row is a candidate for a human, never a verdict.

Optional env: CLAUDE_PROJECT_DIR (default cwd; its skills/ tree supplies git ages),
              NARA_SKILLS_DIRS (colon-separated skill roots; overrides autodetect),
              NARA_TRANSCRIPTS_DIR (default ${CLAUDE_CONFIG_DIR:-~/.claude}/projects)
Requires python3 >= 3.9 and git. Stdlib only.
"""
import datetime
import json
import os
import re
import subprocess
import sys

CMD_RE = re.compile(r"<command-name>/?([A-Za-z0-9:_-]+)</command-name>")


def skill_roots(project_dir):
    env = os.environ.get("NARA_SKILLS_DIRS")
    if env:
        roots = env.split(":")
    else:
        config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
        roots = [
            os.path.join(project_dir, "skills"),
            os.path.join(config_dir, "skills"),
            os.path.expanduser("~/.codex/skills"),
            os.path.expanduser("~/.agents/skills"),
        ]
    return [r for r in roots if r and os.path.isdir(r)]


def discover_skills(roots):
    """Map skill name -> list of real directory paths holding a SKILL.md."""
    skills = {}
    for root in roots:
        for name in sorted(os.listdir(root)):
            d = os.path.join(root, name)
            if name.startswith(".") or not os.path.isfile(os.path.join(d, "SKILL.md")):
                continue
            real = os.path.realpath(d)
            paths = skills.setdefault(name, [])
            if real not in paths:
                paths.append(real)
    return skills


def git_age(project_dir, name):
    """Date the skill's current name first appeared in the project's skills/ tree, or None."""
    rel = "skills/%s/SKILL.md" % name
    if not os.path.isfile(os.path.join(project_dir, rel)):
        return None
    try:
        out = subprocess.run(
            ["git", "-C", project_dir, "log", "--diff-filter=AR", "--format=%as", "--", rel],
            capture_output=True, text=True, check=False,
        ).stdout.split()
    except OSError:
        return None
    if not out:
        return None
    try:
        return datetime.date.fromisoformat(out[-1])  # oldest is last
    except ValueError:
        return None


def parse_ts(value):
    if not isinstance(value, str):
        return None
    try:
        ts = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    # Naive stamps are read as UTC so every comparison stays aware-vs-aware.
    return ts if ts.tzinfo else ts.replace(tzinfo=datetime.timezone.utc)


def iter_records(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue  # a corrupt line never breaks the scan
                if isinstance(rec, dict):
                    yield rec
    except OSError:
        return


def content_parts(rec):
    msg = rec.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [c for c in content if isinstance(c, dict)]
    return []


def is_user_turn(rec, parts):
    if rec.get("type") != "user" or rec.get("isMeta") or rec.get("isSidechain"):
        return False
    if any(p.get("type") == "tool_result" for p in parts):
        return False
    return any(p.get("type") == "text" and p.get("text", "").strip() for p in parts)


def owner_of(file_path, skills):
    real = os.path.realpath(file_path)
    for name, dirs in skills.items():
        for d in dirs:
            if real == d or real.startswith(d + os.sep):
                return name
    return None


def inside(path, base):
    if not base:
        return False
    real, base = os.path.realpath(path), os.path.realpath(base)
    return real == base or real.startswith(base + os.sep)


def scan(transcripts_dir, skills):
    counts = {name: {"slash": 0, "tool": 0, "reads": 0} for name in skills}
    stats = {"transcripts": 0, "user_turns": 0, "start": None}
    if not os.path.isdir(transcripts_dir):
        return counts, stats
    for slug in sorted(os.listdir(transcripts_dir)):
        sdir = os.path.join(transcripts_dir, slug)
        if not os.path.isdir(sdir):
            continue
        for fname in sorted(os.listdir(sdir)):
            if not fname.endswith(".jsonl"):
                continue
            stats["transcripts"] += 1
            cwd = None
            for rec in iter_records(os.path.join(sdir, fname)):
                # cwd moves within a session; judge each record by its own, else the last seen.
                if isinstance(rec.get("cwd"), str):
                    cwd = rec["cwd"]
                ts = parse_ts(rec.get("timestamp"))
                if ts and (stats["start"] is None or ts < stats["start"]):
                    stats["start"] = ts
                parts = content_parts(rec)
                if is_user_turn(rec, parts):
                    stats["user_turns"] += 1
                    for p in parts:
                        if p.get("type") == "text":
                            for m in CMD_RE.findall(p.get("text", "")):
                                if m in counts:
                                    counts[m]["slash"] += 1
                if rec.get("type") != "assistant":
                    continue
                for p in parts:
                    if p.get("type") != "tool_use" or not isinstance(p.get("input"), dict):
                        continue
                    inp = p["input"]
                    if p.get("name") == "Skill":
                        name = inp.get("skill")
                        if isinstance(name, str) and name.lstrip("/") in counts:
                            counts[name.lstrip("/")]["tool"] += 1
                    elif p.get("name") == "Read" and isinstance(inp.get("file_path"), str):
                        fp = inp["file_path"]
                        name = owner_of(fp, skills)
                        if name and not inside(fp, cwd):
                            counts[name]["reads"] += 1
    return counts, stats


def classify(c, created, window_start):
    if c["slash"] + c["tool"] > 0:
        return "used", None
    if c["reads"] > 0:
        return "viewed", None
    if created is None:
        return "unverifiable", "age_unknown"
    if window_start is not None and created >= window_start:
        return "probation", None
    return "unused", None


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    transcripts_dir = os.environ.get("NARA_TRANSCRIPTS_DIR") or os.path.join(config_dir, "projects")
    skills = discover_skills(skill_roots(project_dir))
    counts, stats = scan(transcripts_dir, skills)
    start = stats["start"]
    window_start = start.date() if start else None
    now = datetime.datetime.now(datetime.timezone.utc)
    days = (now - start).days + 1 if start else None
    rows, totals = {}, {"used": 0, "viewed": 0, "probation": 0, "unused": 0, "unverifiable": 0}
    for name in sorted(skills):
        created = git_age(project_dir, name)
        status, reason = classify(counts[name], created, window_start)
        totals[status] += 1
        row = dict(counts[name], status=status, created=created.isoformat() if created else None)
        if reason:
            row["reason"] = reason
        rows[name] = row
    out = {
        "window": {"start": window_start.isoformat() if window_start else None, "days": days},
        "transcripts": stats["transcripts"],
        "user_turns": stats["user_turns"],
        "totals": totals,
        "skills": rows,
    }
    json.dump(out, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
