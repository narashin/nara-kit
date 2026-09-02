#!/usr/bin/env python3
"""Poll a watchlist of GitHub repos for releases newer than the last seen one.

Deterministic layer of nara-release-watch: no LLM, no judgment. It answers only
"what shipped since I last looked", so a quiet day costs one API call per repo
and wakes no model at all.

Watchlist  (human-owned) : ~/.claude/release-watch.md      -- markdown, owner/repo per line
State      (machine-owned): ~/.claude/release-watch-state.json -- last seen tag per repo

The two files are deliberately separate. State is rewritten on every run; a
human editing their watchlist must never race that write.

Usage:
    watch.py poll [--limit N] [--dry-run]
    watch.py list
    watch.py seed [--top N]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
WATCHLIST = os.environ.get("NARA_WATCHLIST", os.path.join(HOME, ".claude/release-watch.md"))
STATE = os.environ.get(
    "NARA_WATCH_STATE", os.path.join(HOME, ".claude/release-watch-state.json")
)
REPO_RE = re.compile(r"^[A-Za-z0-9](?:[\w.-]*[A-Za-z0-9])?/[\w.-]+$")
SEMVER_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
# Anchored on a separator so a keyword only counts as its own tag component:
# an unanchored search matched aarch64 ("a-rc-h64"), source ("sou-rc-e"),
# devtools and nextgen, silently suppressing those stable releases.
PRERELEASE_RE = re.compile(
    r"(?:^|[-._+])(alpha|beta|rc|dev|canary|next|nightly|preview|snapshot)(?=[-._+\d]|$)",
    re.I,
)
GRANULARITY = ("patch", "minor", "major")


# --- io ------------------------------------------------------------------


def parse_watchlist(text: str) -> list[dict]:
    """Pull owner/repo entries out of a human-maintained markdown list.

    Tolerates headings, prose, bullets, checkboxes, inline code and trailing
    comments, so the file stays a document rather than a config format. An
    optional `@minor` / `@major` marker raises the notification threshold for
    high-cadence repos -- anthropics/claude-code alone ships hundreds of patch
    releases, which would fire the digest daily and train the reader to ignore it.
    """
    entries, seen = [], set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        line = re.sub(r"^[-*+]\s*(\[[ xX]\]\s*)?", "", line)  # bullet / checkbox
        # Trailing comment. `--` must be surrounded by whitespace: a bare split
        # truncated slugs that legitimately contain it (some/repo--name).
        line = re.split(r"\s+--\s|#", line, maxsplit=1)[0].strip()
        if not line:
            continue

        tokens = line.replace("`", "").split()
        candidate = re.sub(r"^https?://github\.com/", "", tokens[0]).rstrip("/,")

        # `owner/repo:some/dir` watches commits touching that path instead of
        # releases. Needed because a repo-level release says nothing about one
        # subdirectory -- mattpocock/skills stopped releasing on 2026-08-06 while
        # the directory we care about changed on 2026-08-15.
        candidate, _, path = candidate.partition(":")
        path = path.strip("/")
        if ".." in path.split("/"):
            continue  # never let a watchlist path climb out of the repo

        if not REPO_RE.match(candidate):
            continue
        key = f"{candidate}:{path}".lower()
        if key in seen:
            continue

        granularity = "patch"
        for token in tokens[1:]:
            marker = token.lstrip("@").lower()
            if marker in GRANULARITY:
                granularity = marker
                break

        seen.add(key)
        entry = {"repo": candidate, "granularity": granularity}
        if path:
            entry["path"] = path
        entries.append(entry)
    return entries


def load_watchlist(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return parse_watchlist(handle.read())


def is_prerelease(version: dict) -> bool:
    """Trust the API flag, but also read the tag: many repos ship alphas as
    plain releases (openai/codex tags rust-v0.153.0-alpha.5 without the flag).
    """
    return bool(version.get("prerelease")) or bool(PRERELEASE_RE.search(version["id"]))


def semver(tag: str) -> tuple[int, int, int] | None:
    match = SEMVER_RE.search(tag or "")
    return tuple(int(g) for g in match.groups()) if match else None


def clears_threshold(version_id: str, last_seen: str, granularity: str) -> bool:
    """Does this version differ from last_seen at or above `granularity`?

    Unparseable versions always pass -- suppressing something we cannot read
    would hide real releases, which is worse than an extra line in the digest.
    """
    if granularity == "patch":
        return True
    new, old = semver(version_id), semver(last_seen)
    if new is None or old is None:
        return True
    depth = 1 if granularity == "major" else 2
    return new[:depth] != old[:depth]


def load_state(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}  # a corrupt state file re-baselines; it must not block the poll


def save_state(path: str, state: dict) -> None:
    # dirname("state.json") is "", and makedirs("") raises regardless of exist_ok,
    # so a bare relative --state killed the run after every API call was spent.
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)  # atomic: never leave a half-written state behind


# --- github --------------------------------------------------------------


def gh_json(endpoint: str) -> list | dict | None:
    """Call the GitHub API via gh. Returns None on any failure (404, auth, rate).

    "Any failure" includes gh being absent or hanging. Letting those propagate
    aborted the whole poll from one bad repo, defeating the per-repo `failed[]`
    isolation in poll().
    """
    try:
        proc = subprocess.run(
            ["gh", "api", "-H", "Accept: application/vnd.github+json", endpoint],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return None  # gh missing, not executable, or timed out
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def fetch_versions(repo: str, limit: int) -> tuple[list[dict], str]:
    """Newest-first version list for a repo, plus the source used.

    Source is one of `releases`, `tags`, `none` (repo reachable but ships no
    versions -- surfaced so it is not watched silently forever), or `error`
    (auth, 404, rate limit -- must not be mistaken for "nothing shipped").
    """
    releases = gh_json(f"repos/{repo}/releases?per_page={limit}")
    if releases is None:
        # The releases call failed, so the tags call fails for the same reason --
        # it cannot change the verdict and only doubles the round trips. Returning
        # early also stops a failure from being misread as "ships no versions".
        return [], "error"

    if releases:
        return [
            {
                "id": r.get("tag_name") or str(r.get("id")),
                "name": r.get("name") or r.get("tag_name") or "",
                "url": r.get("html_url", ""),
                "published_at": r.get("published_at") or r.get("created_at") or "",
                "prerelease": bool(r.get("prerelease")),
                "body": (r.get("body") or "").strip(),
            }
            for r in releases
            if not r.get("draft")
        ], "releases"

    tags = gh_json(f"repos/{repo}/tags?per_page={limit}")
    if tags is None:
        return [], "error"  # empty releases + failed tags is a failure, not "none"

    if tags:
        return [
            {
                "id": t.get("name", ""),
                "name": t.get("name", ""),
                "url": f"https://github.com/{repo}/releases/tag/{t.get('name', '')}",
                "published_at": "",
                "prerelease": False,
                "body": "",
            }
            for t in tags
        ], "tags"

    return [], "none"  # both endpoints answered, neither carries a version


def fetch_commits(repo: str, path: str, limit: int) -> tuple[list[dict], str]:
    """Newest-first commits touching `path`, shaped like fetch_versions output.

    Same record shape so poll() and the report need no special casing: `id` is
    the SHA instead of a tag, and the watermark compares SHAs instead of tags.
    """
    quoted = urllib.parse.quote(path, safe="/")
    commits = gh_json(f"repos/{repo}/commits?path={quoted}&per_page={limit}")
    if commits is None:
        return [], "error"
    if not commits:
        # Reachable repo, no commit ever touched this path -- almost always a
        # typo in the watchlist. Reported once via the unwatchable bucket.
        return [], "none"

    out = []
    for c in commits:
        message = (c.get("commit", {}).get("message") or "").strip()
        out.append(
            {
                "id": c.get("sha", ""),
                "name": message.split("\n", 1)[0][:120],
                "url": c.get("html_url", ""),
                "published_at": c.get("commit", {}).get("author", {}).get("date", ""),
                "prerelease": False,
                "body": message,
            }
        )
    return out, "commits"


# --- poll ----------------------------------------------------------------


def poll(
    entries: list[dict] | list[str],
    state: dict,
    limit: int,
    fetch=fetch_versions,
    include_prerelease: bool = False,
    fetch_path=fetch_commits,
) -> tuple[dict, dict]:
    """Diff each entry against its last seen version. Returns (report, new_state).

    An entry with a `path` is diffed on commits touching that path instead of
    releases; everything downstream is identical because both fetchers return
    the same record shape.
    """
    # Copy the nested entries too: a shallow copy would mutate the caller's state.
    new_state = {repo: dict(entry) for repo, entry in state.items()}
    fresh, baselined, unwatchable, failed = [], [], [], []
    suppressed = 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for entry_spec in entries:
        if isinstance(entry_spec, str):  # bare slugs stay accepted
            entry_spec = {"repo": entry_spec, "granularity": "patch"}
        repo = entry_spec["repo"]
        watch_path = entry_spec.get("path")
        # Keyed by repo:path so one repo can be watched at the repo level and at
        # several paths at once without the entries colliding.
        key = state_key(entry_spec)
        granularity = entry_spec.get("granularity", "patch")

        if watch_path:
            versions, source = fetch_path(repo, watch_path, limit)
        else:
            versions, source = fetch(repo, limit)
        if source == "error":
            # Do not touch state: an auth or rate failure must not be recorded
            # as "checked", or the next run would treat it as a quiet day.
            # Always reported, every run, until the human fixes it.
            failed.append(key)
            continue

        entry = new_state.setdefault(key, {})

        if source == "none":
            # Reachable but ships no releases or tags. Report once, then stay
            # quiet -- a repo that never versions would otherwise nag daily.
            if not entry.get("unwatchable_reported"):
                unwatchable.append(key)
                entry["unwatchable_reported"] = True
            entry["last_checked"] = now
            continue

        entry.pop("unwatchable_reported", None)  # it ships versions now
        last_seen = entry.get("last_seen")
        entry.update({"last_checked": now, "source": source, "granularity": granularity})

        if not include_prerelease:
            versions = [v for v in versions if not is_prerelease(v)]
        if not versions:
            # Everything on this page was a prerelease. Leave last_seen alone so
            # the next stable release is still detected.
            continue

        if last_seen is None:
            # First sight of this repo: record the baseline and stay silent.
            # Reporting history here would flood day one and train the human to
            # ignore the digest before it ever says anything useful.
            entry["last_seen"] = versions[0]["id"]
            baselined.append({"repo": key, "baseline": versions[0]["id"]})
            continue

        unseen = []
        for version in versions:
            if version["id"] == last_seen:
                break
            unseen.append(version)

        if unseen:
            # last_seen advances past everything fetched, including versions the
            # threshold suppressed -- otherwise a patch-heavy repo re-evaluates
            # the same releases every run and never converges.
            entry["last_seen"] = unseen[0]["id"]
            entry["truncated"] = len(unseen) == limit
            for version in unseen:
                if clears_threshold(version["id"], last_seen, granularity):
                    fresh.append({"repo": key, **version})
                else:
                    suppressed += 1

    report = {
        "checked": len(entries),
        "suppressed": suppressed,
        "new": fresh,
        "baselined": baselined,
        "unwatchable": unwatchable,
        "failed": failed,
        "quiet": not fresh,
        # A broken token or a newly unwatchable repo is not a quiet day. Without
        # this the digest goes silent on total failure and the breakage is
        # invisible forever.
        "needs_attention": bool(failed or unwatchable),
    }
    return report, new_state


# --- commands ------------------------------------------------------------


def cmd_poll(args: argparse.Namespace) -> int:
    repos = load_watchlist(args.watchlist)
    if not repos:
        json.dump(
            {
                "error": "empty_watchlist",
                "watchlist": args.watchlist,
                "hint": "run 'watch.py seed' or add owner/repo lines by hand",
            },
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 1

    report, new_state = poll(
        repos,
        load_state(args.state),
        args.limit,
        include_prerelease=args.include_prerelease,
    )
    if not args.dry_run:
        save_state(args.state, new_state)
    report["state_written"] = not args.dry_run
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def state_key(entry: dict) -> str:
    """Key an entry's state by repo:path so one repo can be watched several ways."""
    return f"{entry['repo']}:{entry['path']}" if entry.get("path") else entry["repo"]


def cmd_list(args: argparse.Namespace) -> int:
    repos = load_watchlist(args.watchlist)
    state = load_state(args.state)
    rows = []
    for e in repos:
        st = state.get(state_key(e), {})
        rows.append(
            {
                "repo": e["repo"],
                "path": e.get("path"),
                "mode": "commits" if e.get("path") else "releases",
                "granularity": e["granularity"],
                "last_seen": st.get("last_seen"),
                "last_checked": st.get("last_checked"),
                "source": st.get("source"),
                "unwatchable": st.get("unwatchable_reported", False),
            }
        )
    json.dump(
        {
            "watchlist": args.watchlist,
            "count": len(repos),
            "repos": rows,
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    """Propose a starting watchlist from the user's starred repos.

    Prints candidates only. Stars are noisy -- people star for many reasons --
    so the human prunes this into the watchlist rather than adopting it whole.
    """
    starred = gh_json(f"user/starred?per_page={args.top}")
    if not isinstance(starred, list):
        json.dump(
            {"error": "gh_failed", "hint": "gh auth login --hostname github.com"},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
        return 1
    json.dump(
        {
            "candidates": [
                {
                    "repo": s.get("full_name", ""),
                    "description": (s.get("description") or "")[:160],
                    "stars": s.get("stargazers_count", 0),
                    "pushed_at": s.get("pushed_at", ""),
                }
                for s in starred
            ]
        },
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    # Path flags live on both the root and every subcommand, so they work either
    # before or after the verb. Root-only placement is a usability trap.
    # SUPPRESS, not a real default: with `parents=`, a subparser default
    # OVERWRITES what the root already parsed, so `--state X list` silently fell
    # back to the real state file instead of X. apply_defaults() fills the gap
    # once, after both parser levels have had their say.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--watchlist", default=argparse.SUPPRESS)
    common.add_argument("--state", default=argparse.SUPPRESS)

    parser = argparse.ArgumentParser(description=__doc__, parents=[common])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_poll = sub.add_parser(
        "poll", parents=[common], help="report versions newer than last seen"
    )
    p_poll.add_argument("--limit", type=int, default=5, help="versions fetched per repo")
    p_poll.add_argument("--dry-run", action="store_true", help="do not write state")
    p_poll.add_argument(
        "--include-prerelease",
        action="store_true",
        help="report alpha/beta/rc versions too (off by default)",
    )
    p_poll.set_defaults(func=cmd_poll)

    p_list = sub.add_parser(
        "list", parents=[common], help="show the watchlist and its state"
    )
    p_list.set_defaults(func=cmd_list)

    p_seed = sub.add_parser(
        "seed", parents=[common], help="propose candidates from starred repos"
    )
    p_seed.add_argument("--top", type=int, default=50)
    p_seed.set_defaults(func=cmd_seed)
    return parser


def apply_defaults(parsed: argparse.Namespace) -> argparse.Namespace:
    """Fill options the user left off either side of the subcommand."""
    if not hasattr(parsed, "watchlist"):
        parsed.watchlist = WATCHLIST
    if not hasattr(parsed, "state"):
        parsed.state = STATE
    return parsed


if __name__ == "__main__":
    parsed = apply_defaults(build_parser().parse_args())
    sys.exit(parsed.func(parsed))
