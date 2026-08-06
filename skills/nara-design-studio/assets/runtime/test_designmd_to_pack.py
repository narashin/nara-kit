# test_designmd_to_pack.py — exercises the DESIGN.md -> pack transform, including the
# stdlib-only YAML fallback (a consumer may not have PyYAML installed).
import json, os, sys, tempfile, shutil, importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designmd_to_pack as conv  # noqa: E402

DESIGN_MD = """---
version: alpha
name: Acme
description: Test spec
colors:
  primary: "#2563eb"
  ink: "#18181b"
  body: "#3f3f46"
  body-strong: "#27272a"
  muted: "#71717a"
  hairline: "#e4e4e7"
  hairline-strong: "#d4d4d8"
  canvas: "#ffffff"
  surface-card: "#fafafa"
  surface-elevated: "#f4f4f5"
  surface-soft: "#f6f6f7"
  on-primary: "#ffffff"
  positive: "#16a34a"
  negative: "#dc2626"
typography:
  body-md:
    fontFamily: "Inter, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: 0
  button:
    fontFamily: "Inter, sans-serif"
    fontSize: 14px
    fontWeight: 700
    lineHeight: 1
    letterSpacing: 0
rounded:
  sm: 4px
  md: 8px
spacing:
  md: 16px
  lg: 24px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.button}"
    rounded: "{rounded.md}"
    padding: 12px 24px
    height: 40px
---

# Body is ignored by the converter.
"""


def _convert():
    tmp = tempfile.mkdtemp()
    design = os.path.join(tmp, "DESIGN.md")
    with open(design, "w", encoding="utf-8") as f:
        f.write(DESIGN_MD)
    out = os.path.join(tmp, "pack")
    result = conv.convert(design, out, "Acme")
    return tmp, out, result


def test_emits_a_t2_pack_with_manifest_and_bundle():
    tmp, out, (tier, tokens, entries, _derived) = _convert()
    try:
        assert tier == "T2"  # a `components:` block means real mountable components
        manifest = json.load(open(os.path.join(out, "_ds_manifest.json"), encoding="utf-8"))
        assert manifest["namespace"] == "Acme"
        assert manifest["pack"]["tier"] == "T2"
        assert manifest["globalCssPaths"] == ["tokens/tokens.css"]
        assert manifest["adherenceConfig"] == "_adherence.json"
        assert [e["name"] for e in manifest["components"]] == ["ButtonPrimary"]
        bundle = open(os.path.join(out, "_ds_bundle.js"), encoding="utf-8").read()
        assert "global.Acme = { ButtonPrimary };" in bundle
        assert os.path.isfile(os.path.join(out, "components", "ButtonPrimary.d.ts"))
        assert len(tokens) > 20 and entries
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_tokens_css_separates_authored_from_derived():
    tmp, out, (_tier, _tokens, _entries, derived) = _convert()
    try:
        css = open(os.path.join(out, "tokens", "tokens.css"), encoding="utf-8").read()
        # Authored values land verbatim; chrome tokens DESIGN.md lacks are derived and reported.
        assert "--ds-primary: #2563eb;" in css
        assert "--ds-surface: #fafafa;" in css          # aliased from colors.surface-card
        assert "--ds-primary-hover: #1f54c7;" in css    # darkened primary, deterministic
        assert "derived" in css
        assert any("surface-card" in note for note in derived)
        assert not any("MISSING" in note for note in derived)
        # Roles beyond the chrome set survive so screens can use them.
        assert "--ds-negative: #dc2626;" in css
        assert "--ds-space-lg: 24px;" in css
        assert "--ds-type-button-weight: 700;" in css
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_component_resolves_token_refs_to_var():
    tmp, out, _result = _convert()
    try:
        jsx = open(os.path.join(out, "components", "ButtonPrimary.jsx"), encoding="utf-8").read()
        assert "var(--ds-primary)" in jsx          # {colors.primary}
        assert "var(--ds-radius-md)" in jsx        # {rounded.md}
        assert "var(--ds-type-button-size)" in jsx  # {typography.button} expanded
        assert "{children}" in jsx
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_generated_components_contain_no_hardcoded_values():
    # DESIGN.md specs mix token refs with literal geometry ("padding: 12px 24px"). Inlining that
    # literal would bake into the pack exactly what the adherence gate forbids in output.
    sys.path.insert(0, HERE)
    import check_adherence as gate
    tmp, out, _result = _convert()
    try:
        jsx_path = os.path.join(out, "components", "ButtonPrimary.jsx")
        assert gate.scan(jsx_path, dict(gate.DEFAULTS)) == []
        assert "var(--ds-comp-button-primary-padding)" in open(jsx_path, encoding="utf-8").read()
        css = open(os.path.join(out, "tokens", "tokens.css"), encoding="utf-8").read()
        assert "--ds-comp-button-primary-padding: 12px 24px;" in css
        assert "--ds-comp-button-primary-height: 40px;" in css
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_token_only_design_md_lands_at_t1():
    tmp = tempfile.mkdtemp()
    try:
        design = os.path.join(tmp, "DESIGN.md")
        with open(design, "w", encoding="utf-8") as f:
            f.write(DESIGN_MD.split("components:")[0] + "---\n")
        out = os.path.join(tmp, "pack")
        tier, _tokens, entries, _derived = conv.convert(design, out, "Acme")
        assert tier == "T1" and entries == []
        manifest = json.load(open(os.path.join(out, "_ds_manifest.json"), encoding="utf-8"))
        assert manifest["namespace"] == ""  # nothing to mount; render guard skips mounting
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_stdlib_fallback_parser_matches_pyyaml():
    tmp = tempfile.mkdtemp()
    try:
        design = os.path.join(tmp, "DESIGN.md")
        with open(design, "w", encoding="utf-8") as f:
            f.write(DESIGN_MD)
        raw = conv.read_frontmatter(design)
        with_yaml = conv.parse_yaml(raw)

        # Force the ImportError branch so the stdlib parser is exercised on the same input.
        saved = sys.modules.get("yaml")
        sys.modules["yaml"] = None  # `import yaml` raises ImportError when the entry is None
        try:
            importlib.reload(conv)
            fallback = conv.parse_yaml(raw)
        finally:
            if saved is None:
                sys.modules.pop("yaml", None)
            else:
                sys.modules["yaml"] = saved
            importlib.reload(conv)

        assert fallback["colors"]["primary"] == with_yaml["colors"]["primary"] == "#2563eb"
        assert fallback["typography"]["button"]["fontWeight"] in (700, "700")
        assert fallback["components"]["button-primary"]["rounded"] == "{rounded.md}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
