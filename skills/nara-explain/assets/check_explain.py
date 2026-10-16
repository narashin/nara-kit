#!/usr/bin/env python3
"""Static checks for a nara-explain change HTML file (stdlib only).

Checks the saved file only. It does not open a browser, so it says nothing about
how the page renders; that needs nara-browser-verify.

Usage: check_explain.py <file.html>
Exit 0 = clean, 1 = problems found, 2 = cannot read the file.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser

REQUIRED_SECTIONS = ("background", "intuition", "walkthrough", "attention", "check")
GENERIC_TITLES = {"설명", "explanation", "report", "change", "변경", "pr", "diff"}
SHA = r"[0-9a-f]{7,40}"


class Doc(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.loads: list[str] = []
        self.title = ""
        self._in_title = False
        self.details = 0
        self.details_without_summary = 0
        self._details_open: list[bool] = []
        self._expect_summary = False
        self.sample = False
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        if self._expect_summary and tag != "summary":
            self.details_without_summary += 1
        self._expect_summary = False
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag in ("script", "img", "iframe", "audio", "video", "source", "embed", "object") and a.get("src"):
            self.loads.append(f"<{tag} src={a['src']}>")
        if tag == "link" and a.get("href"):
            self.loads.append(f"<link href={a['href']}>")
        if tag == "html" and a.get("data-sample") == "true":
            self.sample = True
        if tag == "title":
            self._in_title = True
        if tag == "details":
            self.details += 1
            self._expect_summary = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._expect_summary and data.strip():
            self.details_without_summary += 1
            self._expect_summary = False
        if self._in_title:
            self.title += data
        self.text.append(data)


def check(html: str) -> list[str]:
    doc = Doc()
    doc.feed(html)
    problems: list[str] = []
    body = " ".join(doc.text)

    if doc.sample:
        problems.append("template sample marker (data-sample=\"true\") was not removed")
    visible = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    if "TODO" in visible:
        problems.append(f"{visible.count('TODO')} TODO placeholder(s) left outside comments")

    title = doc.title.strip()
    if not title or title.lower() in GENERIC_TITLES:
        problems.append(f"<title> is empty or generic: {title!r}")

    dup = sorted({i for i in doc.ids if doc.ids.count(i) > 1})
    if dup:
        problems.append(f"duplicate ids: {', '.join(dup)}")
    ids = set(doc.ids)
    for href in doc.hrefs:
        if href.startswith("#") and len(href) > 1 and href[1:] not in ids:
            problems.append(f"fragment link {href} has no target")
        if href.lower().startswith(("javascript:", "data:")):
            problems.append(f"unsafe link scheme: {href[:30]}")
    for missing in (s for s in REQUIRED_SECTIONS if s not in ids):
        problems.append(f"required section id missing: {missing}")

    if doc.loads:
        problems.append(f"external resource loads: {', '.join(doc.loads[:3])}")
    if re.search(r"@import|url\(\s*['\"]?https?:", html):
        problems.append("CSS loads a remote resource (@import or url(http...))")
    if re.search(r"\bfetch\(|XMLHttpRequest|new\s+WebSocket", html):
        problems.append("script makes a network request")

    if doc.details == 0:
        problems.append("no <details>: the understanding-check answer must be collapsed")
    if doc.details_without_summary:
        problems.append(f"{doc.details_without_summary} <details> without a first-child <summary>")

    if not re.search(rf"{SHA}\s*\.\.\s*{SHA}", body):
        problems.append("no pinned base..head SHA pair in the text")
    if not re.search(r"[\w./-]+\.\w+:\d+", body):
        problems.append("no path:line citation in the text")
    if re.search(r"```|^\s*graph (TD|LR)|^\s*flowchart ", html, re.M):
        problems.append("markdown fence or mermaid source in HTML (draw inline SVG instead)")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            html = handle.read()
    except OSError as error:
        print(f"cannot read {argv[1]}: {error}", file=sys.stderr)
        return 2
    problems = check(html)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        return 1
    print("ok: static checks passed (render not checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
