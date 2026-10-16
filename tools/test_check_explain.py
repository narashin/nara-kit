#!/usr/bin/env python3
"""Regression tests for skills/nara-explain/assets/check_explain.py (stdlib unittest).

Each case reproduces a defect confirmed in the 2026-10-16 review: a correct file
that must pass, or a broken file that must fail. Run: python3 -I tools/test_check_explain.py
"""
from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "skills" / "nara-explain" / "assets"
_spec = importlib.util.spec_from_file_location("check_explain", ASSETS / "check_explain.py")
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load check_explain.py")
ce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ce)

BASE = """<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>CSV 내보내기가 주문 리포트에 생겼다</title><style>body{color:#111}</style></head><body>
<section id="background"><h2>배경</h2><p>비교 기준 a4dd02c..5773196. 근거 <code>src/report.py:12</code>.</p></section>
<section id="intuition"><h2>직관</h2></section>
<section id="walkthrough"><h2>흐름</h2>SLOT</section>
<section id="attention"><h2>꼭 볼 곳</h2></section>
<section id="check"><h2>이해 확인</h2><details><summary>답</summary><p>x</p></details></section>
</body></html>"""


def doc(slot: str) -> str:
    return BASE.replace("SLOT", slot)


class QuotedCodePasses(unittest.TestCase):
    """F1: quoted code inside <pre>/<code> is content, not live script, CSS or a placeholder."""

    def test_base_passes(self) -> None:
        self.assertEqual(ce.check(doc("")), [])

    def test_quoted_tokens_pass(self) -> None:
        for slot in (
            "<pre><code>const r = await fetch(url) // TODO remove</code></pre>",
            "<code>@import url(https://x/y.css)</code>",
            "<pre><code>background: url(https://x/y.png)</code></pre>",
            "<pre><code>```bash\nls\n```</code></pre>",
            "<pre><code>graph TD\nA--&gt;B</code></pre>",
            "<pre><code>new WebSocket(u); new XMLHttpRequest()</code></pre>",
        ):
            with self.subTest(slot=slot):
                self.assertEqual(ce.check(doc(slot)), [])

    def test_live_and_unquoted_still_fail(self) -> None:
        for slot in (
            "<script>fetch('x')</script>",
            "<style>@import url(https://x/y.css);</style>",
            "<p>TODO fill this in</p>",
            "<p>```</p>",
        ):
            with self.subTest(slot=slot):
                self.assertNotEqual(ce.check(doc(slot)), [])


class RemoteLoadsFail(unittest.TestCase):
    """F2: every form that loads something when the file opens must fail."""

    def test_remote_forms_fail(self) -> None:
        for slot in (
            '<img src="https://e.com/x.png">',
            '<svg><image href="https://e.com/x.png"/></svg>',
            '<svg><use href="https://e.com/s.svg#a"/></svg>',
            '<object data="https://e.com/x.pdf"></object>',
            '<img srcset="https://e.com/x.png 1x">',
            '<video poster="https://e.com/p.png"></video>',
            '<div style="background:url(//e.com/x.png)"></div>',
            '<meta http-equiv="refresh" content="0;url=https://e.com">',
            "<script>fetch (u)</script>",
            "<script>navigator.sendBeacon('/x')</script>",
        ):
            with self.subTest(slot=slot):
                self.assertNotEqual(ce.check(doc(slot)), [])

    def test_inline_and_links_pass(self) -> None:
        for slot in (
            '<img alt="x" src="data:image/png;base64,iVBORw0KGgo=">',
            '<a href="https://github.com/acme-sre/web-ui/blob/abc1234/src/report.py#L12">source</a>',
            '<svg viewBox="0 0 10 10"><rect width="5" height="5"/></svg>',
        ):
            with self.subTest(slot=slot):
                self.assertEqual(ce.check(doc(slot)), [])


class UnsafeSchemesFail(unittest.TestCase):
    """F3: hrefs a browser executes as script must fail even when obfuscated."""

    def test_obfuscated_schemes_fail(self) -> None:
        for href in (" javascript:alert(1)", "java&#9;script:alert(1)", "vbscript:x", "JavaScript:x", "data:text/html,x"):
            with self.subTest(href=href):
                self.assertNotEqual(ce.check(doc(f'<a href="{href}">x</a>')), [])


class UnreadableFileExits2(unittest.TestCase):
    """F4: a file that is not UTF-8 is 'cannot read' (exit 2), not 'problems found' (exit 1)."""

    def test_non_utf8_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.html"
            bad.write_bytes(b"\xff\xfe<html>")
            self.assertEqual(ce.main(["check_explain.py", str(bad)]), 2)

    def test_missing_file_exit_2(self) -> None:
        self.assertEqual(ce.main(["check_explain.py", "/nonexistent/x.html"]), 2)


class TemplatePlaceholderDoesNotCite(unittest.TestCase):
    """F5: a lazily filled template (marker and TODO words removed) must not pass on its own placeholder."""

    def test_lazy_template_fails_on_citation(self) -> None:
        html = (ASSETS / "change-template.html").read_text(encoding="utf-8")
        self.assertNotEqual(ce.check(html), [], "unfilled template must fail")
        lazy = html.replace(' data-sample="true"', "")
        lazy = lazy.replace("TODO-base", "a4dd02c").replace("TODO-head", "5773196").replace("TODO-sha", "5773196")
        lazy = lazy.replace("TODO", "")
        problems = ce.check(lazy)
        self.assertTrue(any("path:line" in p for p in problems), problems)


class MermaidFails(unittest.TestCase):
    """F7: any mermaid source outside quoted code must fail."""

    def test_mermaid_variants_fail(self) -> None:
        for body in ("sequenceDiagram\nA->>B: hi", "graph TB\nA-->B", "classDiagram\nA <|-- B", "stateDiagram-v2\n[*] --> A", "erDiagram\nA ||--o{ B : has", "gantt\ntitle T"):
            with self.subTest(body=body.split()[0]):
                self.assertNotEqual(ce.check(doc(f'<pre class="mermaid">{body}</pre>')), [])
                self.assertNotEqual(ce.check(doc(f"<div>{body}</div>")), [])


class PlaceholdersFailEverywhere(unittest.TestCase):
    """Round 2 R1: template TODO slots fail in title, attributes and template code placeholders."""

    def test_leftover_slots_fail(self) -> None:
        cases = (
            BASE.replace("<title>CSV 내보내기가 주문 리포트에 생겼다</title>", "<title>TODO 무엇이 바뀌었나</title>").replace("SLOT", ""),
            doc('<ol class="flow" aria-label="TODO 흐름"><li>x</li></ol>'),
            doc('<img alt="TODO" src="data:image/png;base64,iVBORw0KGgo=">'),
            doc("<pre><code>TODO-예시: 작은 입력과 이전 결과</code></pre>"),
            doc("<code>TODO-path:TODO-line</code>"),
        )
        for html in cases:
            with self.subTest(html=html[html.find("walkthrough"):][:80]):
                self.assertTrue(any("TODO" in p for p in ce.check(html)), ce.check(html))

    def test_quoted_real_todo_passes(self) -> None:
        for code in ("// TODO remove after migration", "- // TODO-1234: remove legacy path", "+ # TODO-cleanup after migration"):
            with self.subTest(code=code):
                self.assertEqual(ce.check(doc(f"<pre><code>{code}</code></pre>")), [])


class ProseNamingDiagramsPasses(unittest.TestCase):
    """Round 2 R2: a one-line prose mention of a diagram type is not mermaid source."""

    def test_prose_keywords_pass(self) -> None:
        for slot in (
            "<p><strong>flowchart</strong> 대신 SVG로 그렸다</p>",
            "<table><tr><td>pie</td></tr></table>",
            "<p>pie chart of things</p>",
            "<p>journey of a request</p>",
            "<p>이전에는 원형 도표였는데 그것을\npie 대신 막대로 바꾼다.</p>",
            "<p>The old page drew a\nflowchart with mermaid; this one uses SVG.</p>",
            "<p>This shortens the checkout\njourney by one step.</p>",
        ):
            with self.subTest(slot=slot):
                self.assertEqual(ce.check(doc(slot)), [])


class SvgLinksAreLinks(unittest.TestCase):
    """Round 2 R3: <a xlink:href> in SVG is a link (scheme-checked), not a resource load."""

    def test_svg_link_passes(self) -> None:
        self.assertEqual(ce.check(doc('<svg><a xlink:href="https://github.com/acme-sre/web-ui"><text>n</text></a></svg>')), [])

    def test_svg_link_unsafe_scheme_fails(self) -> None:
        problems = ce.check(doc('<svg><a xlink:href="javascript:alert(1)"><text>n</text></a></svg>'))
        self.assertTrue(any("unsafe link scheme" in p for p in problems), problems)


class OutputIsStable(unittest.TestCase):
    def test_messages_are_single_line(self) -> None:
        for problem in ce.check(doc("<script>fetch('x')</script><p>TODO</p>")):
            self.assertIsNone(re.search(r"\n", problem))


if __name__ == "__main__":
    unittest.main(verbosity=1)
