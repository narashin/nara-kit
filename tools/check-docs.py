#!/usr/bin/env python3
"""Check mechanically decidable catalog contracts for nara-kit (stdlib only).

Checks:
  1. frontmatter    every skills/<dir>/SKILL.md opens with `---`, `name` equals the
                    directory name, and `description` is present.
  2. catalog parity every skill directory appears exactly once as a catalog row in
                    skills/README.md, and no row names a directory that does not exist.
  3. counts         every skill count written in README.md, skills/README.md and
                    CLAUDE.md equals the directory count (the `grep -c '^nara-'`
                    verify line is count minus one because `naranizer` has no prefix).
  4. scope          a skill whose frontmatter has `metadata.nara.scope: multica` must
                    sit under the Multica catalog category, and every row under that
                    category must carry the tag. Keeps the README category and the
                    frontmatter tag from drifting apart.
  5. sibling links  every `](../nara-<other>/...)` link inside skills/ resolves.
  6. skill README   every skill directory ships a README.md.
  7. user-only      `disable-model-invocation: true` (Claude Code) and
                    agents/openai.yaml `policy.allow_implicit_invocation: false` (Codex)
                    appear together or not at all. Codex ignores the SKILL.md flag, so a
                    skill with only one of them is user-only on one host and not the other.
  8. contract       every SKILL.md links the shared output contract
                    (skills/nara-now/references/output-contract.md) before its first `##`
                    section. Only skills/<name>/ ships, so this pointer is the only way an
                    installed skill sees the contract.
  9. changelog      a released `## [x.y.z]` section of CHANGELOG.md holds no more entries
                    (`- ` and `### ` lines) than it did at tag `vx.y.z`. A rebase over a
                    release lands `[Unreleased]` lines in the just-released section without
                    a conflict; redaction edits keep the count and pass. Untagged versions
                    and a checkout without git are skipped and named in the summary.

Exit 1 with one line per error, exit 0 with a one-line summary. Prose still needs review.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
CATALOG = SKILLS / "README.md"
COUNT_FILES = [ROOT / "README.md", CATALOG, ROOT / "CLAUDE.md"]
MULTICA_HEADING = "multica"
SCOPE_KEY = ("metadata", "nara", "scope")

CODEX_POLICY = re.compile(r"^\s+allow_implicit_invocation:\s*false\s*$", re.MULTILINE)
TRUE_VALUES = {"true", "yes", "on", "1"}

CONTRACT = SKILLS / "nara-now" / "references" / "output-contract.md"

ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|")
HEADING = re.compile(r"^(#{2,3})\s+(.*)$")
SIBLING_LINK = re.compile(r"\]\(((?:\.\./)+nara-[^)]+)\)")  # ../ from SKILL.md, ../../ from references/
COUNT_PATTERNS = [
    re.compile(r"\*\*(\d+) skills\*\*"),
    re.compile(r"\*\*(\d+)개 스킬\*\*"),
    re.compile(r"(\d+)개 스킬 카탈로그"),
    re.compile(r"(\d+) opinionated workflow skills"),
]
VERIFY_LINE = re.compile(r"grep -c '\^nara-'`?\s*(?:→|->)\s*(\d+)")
CHANGELOG = ROOT / "CHANGELOG.md"
VERSION_HEADING = re.compile(r"^## \[(\d+\.\d+\.\d+)\][^\n]*$", re.MULTILINE)
ENTRY_LINE = re.compile(r"^(?:- |### )", re.MULTILINE)


def frontmatter(path: Path) -> tuple[dict, str]:
    """Return a minimal nested dict of the YAML frontmatter plus the body.

    Only what this checker needs is parsed: top-level `key: value` lines and
    indentation-nested maps. Block scalars (`>-`, `|`) are recorded as present
    with an empty value. Malformed input raises ValueError.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("file does not open with `---`")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("frontmatter is not closed with `---`")
    block = text[4:end]
    body = text[end + 4:]
    data: dict = {}
    stack: list[tuple[int, dict]] = [(-1, data)]
    skip_deeper_than: int | None = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        if skip_deeper_than is not None:
            if indent > skip_deeper_than:
                continue
            skip_deeper_than = None
        if line.lstrip().startswith("- "):
            continue
        key, sep, value = line.strip().partition(":")
        if not sep:
            raise ValueError(f"unparseable frontmatter line: {line!r}")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        value = value.strip()
        if value in (">-", ">", "|", "|-"):
            parent[key] = ""
            skip_deeper_than = indent
        elif value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value.strip("'\"")
    return data, body


def nested(data: dict, *keys: str):
    node = data
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").is_file())


def catalog_rows(text: str) -> dict[str, list[tuple[int, str]]]:
    """Map skill name -> [(line number, category heading)] for rows under `## Catalog`."""
    rows: dict[str, list[tuple[int, str]]] = {}
    inside = False
    category = ""
    for number, line in enumerate(text.splitlines(), 1):
        heading = HEADING.match(line)
        if heading:
            level, title = heading.groups()
            if level == "##":
                inside = title.lower().startswith("catalog")
                category = ""
            elif inside:
                category = title
            continue
        if not inside:
            continue
        row = ROW.match(line)
        if row:
            rows.setdefault(row.group(1), []).append((number, category))
    return rows


def changelog_sections(text: str) -> dict[str, str]:
    """Map each released version to its section text, up to the next version heading."""
    marks = list(VERSION_HEADING.finditer(text))
    sections: dict[str, str] = {}
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        sections[mark.group(1)] = text[mark.start():end]
    return sections


def check_changelog(errors: list[str]) -> tuple[int, list[str]]:
    """Compare entry counts of released sections with the tagged CHANGELOG. Returns (checked, skipped)."""
    if not CHANGELOG.is_file():
        return 0, []
    current = changelog_sections(CHANGELOG.read_text(encoding="utf-8"))
    checked, skipped = 0, []
    for version, body in current.items():
        try:
            tagged = subprocess.run(
                ["git", "-C", str(ROOT), "show", f"v{version}:CHANGELOG.md"],
                capture_output=True, text=True, check=False,
            )
        except FileNotFoundError:
            return checked, ["git not found"]
        if tagged.returncode != 0:
            skipped.append(version)
            continue
        before = changelog_sections(tagged.stdout).get(version)
        if before is None:
            skipped.append(version)
            continue
        checked += 1
        had, has = len(ENTRY_LINE.findall(before)), len(ENTRY_LINE.findall(body))
        if has > had:
            errors.append(f"CHANGELOG.md: released section [{version}] has {has} entries, tag v{version} had {had}. "
                          f"New lines belong under [Unreleased] (a rebase over a release puts them here silently)")
    return checked, skipped


def main() -> int:
    errors: list[str] = []
    dirs = skill_dirs()
    names = [d.name for d in dirs]
    scopes: dict[str, str | None] = {}
    user_only: list[str] = []

    for d in dirs:
        rel = d.relative_to(ROOT).as_posix()
        try:
            data, body = frontmatter(d / "SKILL.md")
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{rel}/SKILL.md: {exc}")
            continue
        if data.get("name") != d.name:
            errors.append(f"{rel}/SKILL.md: frontmatter name {data.get('name')!r} != directory name")
        if "description" not in data:
            errors.append(f"{rel}/SKILL.md: missing description")
        scope = nested(data, *SCOPE_KEY)
        scopes[d.name] = scope if isinstance(scope, str) else None
        if not (d / "README.md").is_file():
            errors.append(f"{rel}: missing README.md (thin human guide)")
        flag = data.get("disable-model-invocation")
        claude_user_only = isinstance(flag, str) and flag.lower() in TRUE_VALUES
        codex_yaml = d / "agents" / "openai.yaml"
        codex_user_only = codex_yaml.is_file() and bool(CODEX_POLICY.search(codex_yaml.read_text(encoding="utf-8")))
        if claude_user_only != codex_user_only:
            has, lacks = (("disable-model-invocation: true", "agents/openai.yaml allow_implicit_invocation: false")
                          if claude_user_only else
                          ("agents/openai.yaml allow_implicit_invocation: false", "disable-model-invocation: true"))
            errors.append(f"{rel}: has {has} but lacks {lacks}")
        if claude_user_only:
            user_only.append(d.name)
        head = body.split("\n## ", 1)[0]
        expected = "references/output-contract.md" if d.name == "nara-now" else "../nara-now/references/output-contract.md"
        if f"]({expected})" not in head:
            errors.append(f"{rel}/SKILL.md: no output-contract pointer ]({expected}) before the first ## section")

    catalog_text = CATALOG.read_text(encoding="utf-8")
    rows = catalog_rows(catalog_text)
    for name in names:
        hits = rows.get(name, [])
        if not hits:
            errors.append(f"skills/README.md: `{name}` has no catalog row")
        elif len(hits) > 1:
            lines = ", ".join(str(n) for n, _ in hits)
            errors.append(f"skills/README.md: `{name}` listed {len(hits)} times (lines {lines})")
    for name, hits in rows.items():
        if name not in names:
            errors.append(f"skills/README.md:{hits[0][0]}: catalog row `{name}` has no skills/{name}/ directory")

    for name in names:
        hits = rows.get(name)
        if not hits:
            continue
        line, category = hits[0]
        in_multica = MULTICA_HEADING in category.lower()
        tagged = scopes.get(name) == "multica"
        if tagged and not in_multica:
            errors.append(f"skills/README.md:{line}: `{name}` is tagged metadata.nara.scope=multica but sits under '{category}'")
        if in_multica and not tagged:
            errors.append(f"skills/{name}/SKILL.md: listed under '{category}' but lacks metadata.nara.scope: multica")

    if not CONTRACT.is_file():
        errors.append(f"{CONTRACT.relative_to(ROOT).as_posix()}: shared output contract is missing")

    total = len(names)
    for path in COUNT_FILES:
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern in COUNT_PATTERNS:
                for match in pattern.finditer(line):
                    if int(match.group(1)) != total:
                        errors.append(f"{rel}:{number}: says {match.group(1)} skills, directory count is {total}")
            verify = VERIFY_LINE.search(line)
            if verify and int(verify.group(1)) != total - 1:
                errors.append(f"{rel}:{number}: verify line expects {verify.group(1)} nara- dirs, actual is {total - 1} (+ naranizer)")

    link_count = 0
    for md in SKILLS.rglob("*.md"):
        for match in SIBLING_LINK.finditer(md.read_text(encoding="utf-8")):
            link_count += 1
            target = (md.parent / match.group(1)).resolve()
            if not target.exists():
                errors.append(f"{md.relative_to(ROOT).as_posix()}: sibling link {match.group(1)} does not resolve")

    released, untagged = check_changelog(errors)

    if errors:
        print("\n".join(errors))
        return 1
    multica = sum(1 for s in scopes.values() if s == "multica")
    print(f"Pass: {total} skills, catalog parity ok, counts ok, {multica} multica-scoped, "
          f"{len(user_only)} user-only (Claude+Codex agree), {link_count} sibling links resolve, "
          f"{released} released changelog sections match their tags"
          + (f" (unchecked: {', '.join(untagged)})" if untagged else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
