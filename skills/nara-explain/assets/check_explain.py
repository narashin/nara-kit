#!/usr/bin/env python3
"""Static checks for a nara-explain change HTML file (stdlib only).

Checks the saved file only. It does not open a browser, so it says nothing about
how the page renders; that needs nara-browser-verify.

Text is split by context before any check runs. Live `<script>` text and
`<style>`/`style=""` CSS are checked for network and remote loads; reader-visible
text outside `<pre>`/`<code>` is checked for placeholders, fences and mermaid.
Quoted code inside `<pre>`/`<code>` is content and only counts toward citations;
there, only the template's own `TODO-` sentinel counts as a leftover placeholder.
`TODO` in the title or any attribute value always counts.

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
# Attributes whose value the browser fetches when the page opens.
LOAD_ATTRS = ("src", "srcset", "poster", "data", "background", "xlink:href")
UNSAFE_SCHEMES = ("javascript:", "vbscript:", "data:")
NETWORK = re.compile(
    r"\b(?:fetch|sendBeacon|EventSource|importScripts)\s*\(|XMLHttpRequest|new\s+WebSocket|new\s+Image\s*\(|\bimport\s*\("
)
REMOTE_CSS = re.compile(r"@import|url\(\s*['\"]?\s*(?:[a-z][a-z0-9+.-]*:)?//", re.I)
MERMAID = re.compile(
    r"^\s*(?:graph\s+(?:TD|TB|BT|LR|RL)\b|flowchart\b|sequenceDiagram|classDiagram|stateDiagram|erDiagram|gantt\b|journey\b|pie\b)",
    re.M,
)
TEMPLATE_SENTINEL = re.compile(r"TODO-(?:예시|path|line|sha|base|head)")
CITATION = re.compile(r"(?<![\w./-])(?!path/to/)[\w./-]+\.\w+:\d+")
CONTROL = "".join(chr(c) for c in range(0x21))
# Elements that start a new block of reader-visible text; inline elements (em, code, a) do not.
BLOCK_TAGS = frozenset((
    "html", "body", "section", "article", "header", "footer", "main", "nav", "aside", "div",
    "p", "li", "ol", "ul", "dl", "dt", "dd", "td", "th", "tr", "table", "caption", "blockquote",
    "figure", "figcaption", "details", "summary", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "br", "hr",
))


def normalize_url(value: str) -> str:
    """Mirror the browser's URL preprocessing before comparing schemes."""
    return re.sub(r"[\t\n\r]", "", value.strip(CONTROL)).lower()


def is_inline(value: str) -> bool:
    v = normalize_url(value)
    return not v or v.startswith(("data:", "#"))


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
        self.mermaid_class = False
        self.attr_values: list[str] = []
        self.code: list[str] = []      # text inside <pre>/<code>
        self.text: list[str] = []      # all reader-visible text, quoted code included
        self.prose: list[str] = []     # reader-visible text outside <pre>/<code>
        self.blocks: list[str] = []    # prose joined per block element, inline elements merged
        self._block: list[str] = []
        self.script: list[str] = []
        self.css: list[str] = []
        self._raw: str | None = None   # "script" | "style" while inside one
        self._code_depth = 0

    def _close_expected_summary(self) -> None:
        if self._expect_summary:
            self.details_without_summary += 1
            self._expect_summary = False

    def _flush_block(self) -> None:
        if self._block:
            self.blocks.append("".join(self._block))
            self._block = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in BLOCK_TAGS:
            self._flush_block()
        a = {k: (v or "") for k, v in attrs}
        self.attr_values.extend(v for k, v in a.items() if k not in ("href", "src", "srcset", "xlink:href"))
        if tag != "summary":
            self._close_expected_summary()
        self._expect_summary = False
        if "id" in a:
            self.ids.append(a["id"])
        if "mermaid" in a.get("class", "").split():
            self.mermaid_class = True
        if a.get("style"):
            self.css.append(a["style"])
        if tag == "a":
            # A link is navigation, not a load: HTML href and SVG xlink:href both go to the scheme checks.
            self.hrefs.extend(a[k] for k in ("href", "xlink:href") if k in a)
        else:
            if tag in ("link", "image", "use", "feimage") and a.get("href") and not is_inline(a["href"]):
                self.loads.append(f"<{tag} href={a['href'][:60]}>")
            for attr in LOAD_ATTRS:
                if a.get(attr) and not is_inline(a[attr]):
                    self.loads.append(f"<{tag} {attr}={a[attr][:60]}>")
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            self.loads.append("<meta http-equiv=refresh>")
        if tag == "html" and a.get("data-sample") == "true":
            self.sample = True
        if tag == "title":
            self._in_title = True
        if tag in ("script", "style"):
            self._raw = tag
        if tag in ("pre", "code"):
            self._code_depth += 1
        if tag == "details":
            self.details += 1
            self._expect_summary = True

    def handle_endtag(self, tag: str) -> None:
        if tag in BLOCK_TAGS:
            self._flush_block()
        if tag == "title":
            self._in_title = False
        if tag in ("script", "style"):
            self._raw = None
        if tag in ("pre", "code") and self._code_depth:
            self._code_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._raw == "script":
            self.script.append(data)
            return
        if self._raw == "style":
            self.css.append(data)
            return
        if data.strip():
            self._close_expected_summary()
        if self._in_title:
            self.title += data
            return
        self.text.append(data)
        if self._code_depth:
            self.code.append(data)
        else:
            self.prose.append(data)
            self._block.append(data)

    def close(self) -> None:
        super().close()
        self._flush_block()
        self._close_expected_summary()


def check(html: str) -> list[str]:
    doc = Doc()
    doc.feed(html)
    doc.close()
    problems: list[str] = []
    text = " ".join(doc.text)
    prose = "\n".join(doc.prose)  # newline keeps ^-anchored mermaid checks working per text node

    if doc.sample:
        problems.append("template sample marker (data-sample=\"true\") was not removed")
    attrs = " ".join(doc.attr_values)
    code = " ".join(doc.code)
    todo = prose.count("TODO") + doc.title.count("TODO") + attrs.count("TODO") + len(TEMPLATE_SENTINEL.findall(code))
    if todo:
        problems.append(f"{todo} TODO placeholder(s) left (text, title, attributes, or TODO- in quoted code)")

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
        if normalize_url(href).startswith(UNSAFE_SCHEMES):
            problems.append(f"unsafe link scheme: {href.strip()[:30]!r}")
    for missing in (s for s in REQUIRED_SECTIONS if s not in ids):
        problems.append(f"required section id missing: {missing}")

    if doc.loads:
        problems.append(f"external resource loads: {', '.join(doc.loads[:3])}")
    if REMOTE_CSS.search(" ".join(doc.css)):
        problems.append("CSS loads a remote resource (@import or url(//...))")
    if NETWORK.search(" ".join(doc.script)):
        problems.append("script makes a network request")

    if doc.details == 0:
        problems.append("no <details>: the understanding-check answer must be collapsed")
    if doc.details_without_summary:
        problems.append(f"{doc.details_without_summary} <details> without a first-child <summary>")

    if not re.search(rf"{SHA}\s*\.\.\s*{SHA}", text):
        problems.append("no pinned base..head SHA pair in the text")
    if not CITATION.search(text):
        problems.append("no path:line citation in the text (template placeholders do not count)")
    # Mermaid source is multi-line and opens its block; a one-line mention of "flowchart" or "pie"
    # in prose is not, nor is a wrapped prose line. Inline elements are merged into their block,
    # so <p>... <em>x</em>\npie ...</p> is judged by the paragraph's first line.
    multiline_mermaid = any("\n" in b.strip() and MERMAID.match(b.strip()) for b in doc.blocks)
    if "```" in prose or doc.mermaid_class or multiline_mermaid:
        problems.append("markdown fence or mermaid source outside quoted code (draw inline SVG instead)")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            html = handle.read()
    except (OSError, UnicodeDecodeError) as error:
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
