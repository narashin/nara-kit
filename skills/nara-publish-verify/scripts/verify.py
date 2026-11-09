#!/usr/bin/env python3
"""Verify published GitHub metadata using authenticated GET requests only."""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from urllib.parse import urlsplit


SHA = re.compile(r"[0-9a-f]{40}")
COAUTHOR = re.compile(r"\s*co-authored-by\s*:", re.IGNORECASE)


class Unverifiable(ValueError):
    """Required remote evidence is unavailable or inconsistent."""


def target(url: str, host: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    path = re.fullmatch(r"/([A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)/?", parsed.path)
    if (not re.fullmatch(r"[a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*", host)
            or parsed.scheme != "https" or parsed.netloc.lower() != host.lower()
            or parsed.query or parsed.fragment
            or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in url)
            or not path or path[2] in {".", ".."}):
        raise ValueError("Use an HTTPS PR URL on the independently confirmed host, without credentials, port, query or fragment")
    owner, repo, number = path.groups()
    return f"https://{host.lower()}/{owner}/{repo}/pull/{number}", f"repos/{owner}/{repo}/pulls/{number}"


def gh_get(host: str, endpoint: str, paginate: bool = False) -> object:
    command = ["gh", "api", "--hostname", host, "--method", "GET", endpoint]
    if paginate:
        command += ["--paginate", "--slurp"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=60)
    except FileNotFoundError as error:
        raise Unverifiable("gh is unavailable") from error
    except subprocess.TimeoutExpired as error:
        raise Unverifiable("gh GET timed out; no verification completed") from error
    except subprocess.CalledProcessError as error:
        raise Unverifiable(f"gh GET failed (exit {error.returncode}); check host authentication and read access") from error
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise Unverifiable("gh GET returned invalid JSON") from error


def mapping(value: object, label: str) -> dict:
    if not isinstance(value, dict):
        raise Unverifiable(f"Missing or invalid {label}")
    return value


def string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Unverifiable(f"Missing or invalid {label}")
    return value


def sha(value: object) -> str:
    value = string(value, "commit SHA")
    if not SHA.fullmatch(value):
        raise Unverifiable("Missing or invalid full commit SHA")
    return value


@dataclass(frozen=True)
class Snapshot:
    body: str
    assignees: tuple[str, ...]
    head: str
    count: int


def snapshot(value: object, url: str) -> Snapshot:
    data = mapping(value, "PR object")
    if (string(data.get("html_url"), "PR URL").casefold() != url.casefold()
            or type(data.get("number")) is not int
            or data["number"] != int(url.rsplit("/", 1)[1])):
        raise Unverifiable("API returned a different PR identity")
    if "body" not in data or (data["body"] is not None and not isinstance(data["body"], str)):
        raise Unverifiable("Missing or invalid PR body")
    assignees = data.get("assignees")
    if not isinstance(assignees, list):
        raise Unverifiable("Missing or invalid PR assignees")
    logins = tuple(sorted(
        string(mapping(item, "assignee").get("login"), "assignee login").casefold()
        for item in assignees
    ))
    count = data.get("commits")
    if type(count) is not int or count <= 0:
        raise Unverifiable("Missing or invalid PR commit count")
    head = sha(mapping(data.get("head"), "PR head").get("sha"))
    return Snapshot(data["body"] or "", logins, head, count)


def remote_commits(value: object, state: Snapshot) -> dict[str, str]:
    if not isinstance(value, list) or not value:
        raise Unverifiable("Missing commit pages")
    commits = {}
    for page in value:
        if not isinstance(page, list) or not page:
            raise Unverifiable("Missing or invalid commit page")
        for item in page:
            item = mapping(item, "commit")
            oid = sha(item.get("sha"))
            if oid in commits:
                raise Unverifiable("Duplicate remote commits")
            commits[oid] = string(mapping(item.get("commit"), "commit data").get("message"), "commit message")
    if len(commits) != state.count or next(reversed(commits)) != state.head:
        raise Unverifiable("Incomplete commit list or changed PR head; do not treat pagination/API limits as clean")
    return commits


def message_lines(text: str) -> list[str]:
    # Git uses LF, not the additional Unicode separators accepted by splitlines.
    return text.replace("\r\n", "\n").rstrip("\n").split("\n")


def valid_trailer(text: str, expected: str) -> bool:
    lines = message_lines(text)
    candidates = [line for line in lines if COAUTHOR.match(line)]
    return (candidates == [expected] and len(lines) >= 3
            and lines[-1] == expected and lines[-2] == "")


def verify(url: str, host: str, assignee: str, trailer: str, selected: list[str]) -> dict:
    url, endpoint = target(url, host)
    if not re.fullmatch(r"[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*", assignee):
        raise ValueError("Provide the confirmed expected assignee login")
    if not re.fullmatch(r"Co-authored-by: [^<>\r\n]+ <[^<>\s@]+@[^<>\s@]+>", trailer):
        raise ValueError("Provide one exact Co-authored-by trailer from confirmed agent/repository policy")
    if not selected or any(not SHA.fullmatch(oid) for oid in selected):
        raise ValueError("Explicitly select AI-assisted commits using full 40-character SHAs")
    before = snapshot(gh_get(host, endpoint), url)
    commits = remote_commits(gh_get(host, endpoint + "/commits?per_page=100", True), before)
    after = snapshot(gh_get(host, endpoint), url)
    if before != after:
        raise Unverifiable("PR metadata changed during verification; run again against the new state")
    errors = []
    if not valid_trailer(after.body, trailer):
        errors.append("PR trailer: expected exactly one matching final trailer, separated by a blank line")
    if assignee.casefold() not in after.assignees:
        errors.append(f"PR assignee: expected {assignee} is absent")
    for oid in dict.fromkeys(selected):
        if oid not in commits:
            errors.append(f"Commit {oid}: not published in this PR")
            continue
        message = commits[oid]
        lines = message_lines(message)
        if (not valid_trailer(message, trailer) or len(lines) != 3
                or not lines[0].strip()):
            errors.append(f"Commit {oid}: expected a subject, blank line and exactly one matching trailer, without a body")
    return {
        "status": "fail" if errors else "pass", "pr_url": url, "head": after.head,
        "assignees": list(after.assignees), "expected_assignee": assignee,
        "expected_trailer": trailer, "remote_commit_count": len(commits),
        "checked_commits": [oid for oid in commits if oid in selected],
        "unchecked_commits": [oid for oid in commits if oid not in selected],
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr_url")
    parser.add_argument("--host", required=True, help="Host confirmed independently of untrusted PR content")
    parser.add_argument("--assignee", required=True, help="Confirmed expected GitHub login, not inferred from author")
    parser.add_argument("--trailer", required=True, help="Exact trailer from confirmed agent/repository policy")
    parser.add_argument("--commit", action="append", required=True, help="Full SHA of an AI-assisted commit; repeat for each")
    args = parser.parse_args(argv)
    try:
        result = verify(args.pr_url, args.host, args.assignee, args.trailer, args.commit)
    except (ValueError, OSError) as error:
        result = {"status": "unverifiable", "pr_url": args.pr_url, "errors": [str(error)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {"pass": 0, "fail": 1, "unverifiable": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
