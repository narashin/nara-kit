#!/usr/bin/env python3
"""
DESIGN.md -> nara-design-studio pack (generic — no design-system specifics).

A DESIGN.md (Stitch format, see nara-design-md) already carries a full token surface: a color
role set, a typography scale, spacing, radii, and per-component style specs. That is strictly
more than the bundled neutral starter pack ships, but the studio cannot consume prose — it needs
a pack directory (tokens CSS + manifest + optionally a component bundle).

This script performs that mechanical transform. It makes no design judgments: every value it
writes traces back to a frontmatter key, and every value it had to derive (because the engine's
chrome needs a token DESIGN.md does not define) is emitted into a clearly-labelled "derived"
block and reported on stdout, never silently blended into the authored set.

Usage:
  python3 designmd_to_pack.py --design <path/to/DESIGN.md> --out <packDir> [--namespace DesignMd]

Output pack:
  tokens/tokens.css      authored tokens + a labelled derived block
  components/*.jsx       one standalone component per `components:` entry (if any)
  _ds_bundle.js          exposes those components on window.<namespace>
  _ds_manifest.json      the pack contract manifest
  _adherence.json        token allowlist for the emit-time adherence gate
"""
import argparse
import json
import os
import re
import sys

# Tokens the studio chrome depends on (starter-pack tokens.css is the authoritative list).
# Each entry: (token suffix, how to source it). "authored" entries come straight from DESIGN.md;
# anything absent is derived below and reported, so a reader can always tell the two apart.
CHROME_COLOR_TOKENS = [
    "primary", "primary-hover", "on-primary", "link",
    "canvas", "surface", "surface-elevated", "surface-soft",
    "hairline", "hairline-soft", "hairline-strong",
    "ink", "ink-soft", "charcoal", "slate", "steel", "stone",
    "positive",
]

# Chrome token <- DESIGN.md color role, used only when the chrome name is not authored directly.
# Kept explicit rather than fuzzy-matched: a wrong alias is a silently wrong palette.
COLOR_ALIASES = {
    "surface": "surface-card",
    "link": "primary",
    "ink-soft": "body-strong",
    "charcoal": "body-strong",
    "slate": "body",
    "steel": "muted",
    "stone": "muted",
    "hairline-soft": "hairline",
}

TOKEN_REF = re.compile(r"\{([a-z]+)\.([a-zA-Z0-9_-]+)\}")
HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")


# --- frontmatter -------------------------------------------------------------------------

def read_frontmatter(path):
    """Return the YAML frontmatter block of a markdown file as raw text."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        raise SystemExit(f"{path}: no YAML frontmatter (file must start with '---')")
    end = text.find("\n---", 3)
    if end == -1:
        raise SystemExit(f"{path}: frontmatter is not terminated by a closing '---'")
    return text[text.find("\n", 3) + 1:end]


def parse_yaml(block):
    """Parse the constrained mapping-only subset a DESIGN.md frontmatter uses.

    Uses PyYAML when importable (more permissive, handles quoting edge cases); otherwise falls
    back to an indent-stack parser. The fallback keeps this script stdlib-only so a consumer
    never has to install anything to build a pack.
    """
    try:
        import yaml  # optional; not a declared dependency
        loaded = yaml.safe_load(block)
        return loaded if isinstance(loaded, dict) else {}
    except ImportError:
        pass

    root = {}
    stack = [(-1, root)]
    for raw in block.splitlines():
        line = raw.split("#", 1)[0].rstrip() if not _in_quotes(raw, raw.find("#")) else raw.rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if ":" not in line:
            continue
        key, _, value = line.strip().partition(":")
        key, value = key.strip(), value.strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if not stack:
            stack = [(-1, root)]
        parent = stack[-1][1]
        if value == "":
            child = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(value)
    return root


def _in_quotes(line, idx):
    """True when idx sits inside a double-quoted span — keeps '#hex' from reading as a comment."""
    if idx == -1:
        return False
    return line.count('"', 0, idx) % 2 == 1


def _scalar(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


# --- token emission ----------------------------------------------------------------------

def resolve_colors(colors):
    """Return (values, derived) — the chrome color set, and notes for every non-authored token."""
    values, derived = {}, []
    for name in CHROME_COLOR_TOKENS:
        if name in colors:
            values[name] = colors[name]
            continue
        alias = COLOR_ALIASES.get(name)
        if alias and alias in colors:
            values[name] = colors[alias]
            derived.append(f"--ds-{name} <- colors.{alias}")
            continue
        if name == "primary-hover" and "primary" in colors:
            values[name] = darken(colors["primary"])
            derived.append(f"--ds-{name} <- colors.primary darkened 15%")
            continue
        if name == "on-primary":
            values[name] = "#ffffff"
            derived.append("--ds-on-primary <- fallback #ffffff (not defined in DESIGN.md)")
            continue
        derived.append(f"--ds-{name} MISSING — no DESIGN.md role maps to it")
    return values, derived


def darken(hex_color, factor=0.85):
    """Scale an #rrggbb color toward black. Deterministic, so re-running yields the same pack."""
    if not HEX.match(hex_color):
        return hex_color
    raw = hex_color.lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    if len(raw) < 6:
        return hex_color
    channels = [int(raw[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(c * factor):02x}" for c in channels)


def build_tokens_css(fm):
    """Emit tokens.css and the flat token list the manifest needs."""
    colors = fm.get("colors", {}) or {}
    typography = fm.get("typography", {}) or {}
    rounded = fm.get("rounded", {}) or {}
    spacing = fm.get("spacing", {}) or {}

    resolved, derived = resolve_colors(colors)
    tokens = []
    authored, derived_lines = [], []

    def add(name, value, kind, section):
        tokens.append({"name": name, "value": str(value), "kind": kind,
                       "definedIn": "tokens/tokens.css"})
        section.append(f"  {name}: {value};")

    for name in CHROME_COLOR_TOKENS:
        if name not in resolved:
            continue
        target = authored if name in colors else derived_lines
        add(f"--ds-{name}", resolved[name], "color", target)

    # Roles DESIGN.md defines that the chrome does not require, but a screen will want.
    for name, value in colors.items():
        token = f"--ds-{name}"
        if any(t["name"] == token for t in tokens):
            continue
        add(token, value, "color", authored)

    for name, value in spacing.items():
        add(f"--ds-space-{name}", value, "spacing", authored)

    for name, value in rounded.items():
        add(f"--ds-radius-{name}", value, "radius", authored)
    if rounded.get("md") is not None:
        add("--ds-radius-200", rounded["md"], "radius", derived_lines)
        derived.append("--ds-radius-200 <- rounded.md (chrome-required alias)")

    first_family = ""
    for name, spec in typography.items():
        if not isinstance(spec, dict):
            continue
        first_family = first_family or str(spec.get("fontFamily", ""))
        for key, suffix, kind in (("fontSize", "size", "type"), ("fontWeight", "weight", "type"),
                                  ("lineHeight", "line", "type"), ("letterSpacing", "tracking", "type")):
            if spec.get(key) is not None:
                add(f"--ds-type-{name}-{suffix}", spec[key], kind, authored)
    if first_family:
        add("--ds-font-sans", first_family, "type", authored)
    else:
        derived.append("--ds-font-sans MISSING — typography block defines no fontFamily")

    # DESIGN.md keeps elevation in prose, not frontmatter, so the chrome's one shadow is derived.
    add("--ds-shadow-popover", "0 8px 24px rgba(0, 0, 0, 0.12)", "shadow", derived_lines)
    derived.append("--ds-shadow-popover <- fallback (DESIGN.md frontmatter has no shadow tokens)")

    css = [
        "/*",
        f" * Generated from DESIGN.md by designmd_to_pack.py — do not hand-edit.",
        " * Re-run the converter after changing DESIGN.md.",
        " */",
        ":root {",
        "  /* authored — every value below traces to a DESIGN.md frontmatter key */",
        *authored,
    ]
    if derived_lines:
        css += ["", "  /* derived — the engine chrome needs these; DESIGN.md does not define them */",
                *derived_lines]
    # Left open: convert() appends the component-scoped block (if any) before closing the rule.
    return css, tokens, derived


# --- component emission ------------------------------------------------------------------

def pascal_case(name):
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[-_ ]+", name) if part)


def css_value(value, token_index):
    """Resolve a `{group.name}` DESIGN.md token reference to a var() the pack actually defines."""
    def repl(match):
        group, key = match.group(1), match.group(2)
        prefix = {"colors": "", "rounded": "radius-", "spacing": "space-"}.get(group)
        if prefix is None:
            return match.group(0)
        token = f"--ds-{prefix}{key}"
        return f"var({token})" if token in token_index else match.group(0)
    return TOKEN_REF.sub(repl, str(value))


def build_components(fm, tokens):
    """Turn each `components:` entry into a standalone JSX component.

    A component spec mixes token references (`{colors.primary}`) with literal geometry
    (`padding: 12px 24px`). Emitting that literal straight into the JSX would bake a hardcoded
    value into the pack — exactly what check_adherence.py exists to prevent — so every literal
    becomes a component-scoped token instead. The component then references only var()s, and the
    value stays retunable from one place.

    Returns (files, entries, extra_tokens).
    """
    specs = fm.get("components", {}) or {}
    token_index = {t["name"] for t in tokens}
    files, entries, extra_tokens = {}, [], []

    for raw_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        name = pascal_case(raw_name)
        style = {}
        typography_ref = spec.get("typography")
        for key, prop in (("backgroundColor", "background"), ("textColor", "color"),
                          ("rounded", "borderRadius"), ("padding", "padding"),
                          ("height", "height"), ("borderColor", "borderColor")):
            if spec.get(key) is None:
                continue
            resolved = css_value(spec[key], token_index)
            if TOKEN_REF.search(str(spec[key])) is None and str(spec[key]) != "transparent":
                # A literal — promote it to a component-scoped token rather than inlining it.
                token = f"--ds-comp-{raw_name}-{key.lower()}"
                extra_tokens.append({"name": token, "value": str(spec[key]),
                                     "kind": "component", "definedIn": "tokens/tokens.css"})
                resolved = f"var({token})"
            style[prop] = resolved
        if isinstance(typography_ref, str):
            match = TOKEN_REF.match(typography_ref)
            if match and match.group(1) == "typography":
                scale = match.group(2)
                for suffix, prop in (("size", "fontSize"), ("weight", "fontWeight"),
                                     ("line", "lineHeight"), ("tracking", "letterSpacing")):
                    token = f"--ds-type-{scale}-{suffix}"
                    if token in token_index:
                        style[prop] = f"var({token})"
        if "--ds-font-sans" in token_index:
            style["fontFamily"] = "var(--ds-font-sans)"

        tag = "input" if "input" in raw_name else "button" if "button" in raw_name else "div"
        body = "" if tag == "input" else "{children}"
        children_prop = "" if tag == "input" else "children, "
        self_closing = " />" if tag == "input" else f">{body}</{tag}>"
        style_literal = json.dumps(style, indent=4)[1:-1].strip()

        files[f"components/{name}.jsx"] = (
            f"// {name} — generated from DESIGN.md `components.{raw_name}`. Do not hand-edit.\n"
            f"function {name}({{ {children_prop}style, ...rest }}) {{\n"
            f"  const base = {{\n    {style_literal}\n  }};\n"
            f"  return <{tag} {{...rest}} style={{{{ ...base, ...style }}}}{self_closing};\n"
            f"}}\n"
        )
        files[f"components/{name}.d.ts"] = (
            f"import type {{ CSSProperties, ReactNode }} from \"react\";\n\n"
            f"export interface {name}Props {{\n"
            f"{'' if tag == 'input' else '  children?: ReactNode;' + chr(10)}"
            f"  style?: CSSProperties;\n}}\n\n"
            f"export declare function {name}(props: {name}Props): JSX.Element;\n"
        )
        entries.append({
            "name": name,
            "group": "DESIGN.md",
            "sourcePath": f"DESIGN.md#components.{raw_name}",
            "adaptedPath": f"components/{name}.jsx",
            "promptPath": "",
            "typesPath": f"components/{name}.d.ts",
            "status": "adapted",
            "note": "",
        })
    return files, entries, extra_tokens


def build_bundle(namespace, entries, files):
    """Concatenate the generated JSX into one bundle exposing window.<namespace>."""
    if not entries:
        return ("/* Generated from DESIGN.md: no `components:` block, so this pack is token-only "
                "(T1). window namespace intentionally unset. */\n")
    parts = [f"/* Generated from DESIGN.md by designmd_to_pack.py — do not hand-edit. */",
             "(function (global) {"]
    for entry in entries:
        parts.append(files[entry["adaptedPath"]].rstrip())
    names = ", ".join(entry["name"] for entry in entries)
    parts += [f"  global.{namespace} = {{ {names} }};", "})(window);", ""]
    return "\n".join(parts)


# --- main --------------------------------------------------------------------------------

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def convert(design_path, out_dir, namespace):
    fm = parse_yaml(read_frontmatter(design_path))
    name = str(fm.get("name") or "DESIGN.md pack")

    css_lines, tokens, derived = build_tokens_css(fm)
    files, entries, extra_tokens = build_components(fm, tokens)
    if extra_tokens:
        css_lines += ["", "  /* component-scoped — literal geometry from DESIGN.md `components:` */",
                      *(f"  {token['name']}: {token['value']};" for token in extra_tokens)]
        tokens += extra_tokens
    css = "\n".join(css_lines + ["}", ""])

    bundle = build_bundle(namespace, entries, files)
    tier = "T2" if entries else "T1"

    write(os.path.join(out_dir, "tokens", "tokens.css"), css)
    for rel, content in files.items():
        write(os.path.join(out_dir, rel), content)
    write(os.path.join(out_dir, "_ds_bundle.js"), bundle)
    write(os.path.join(out_dir, "_adherence.json"), json.dumps({
        "forbidRawHex": True,
        "forbidRawPx": True,
        "allowedRawPx": ["0px", "1px"],
        "allowTokens": sorted(token["name"] for token in tokens),
    }, indent=2) + "\n")
    write(os.path.join(out_dir, "_ds_manifest.json"), json.dumps({
        "namespace": namespace if entries else "",
        "source": f"design.md:{name}",
        "pack": {
            "name": name,
            "sourceRepo": os.path.abspath(design_path),
            "sourcePackages": [],
            "kitHelpersPath": "",
            "reuseRule": (f"Reuse the generated {name} components; do not recreate them from tokens."
                          if entries else
                          "Token-only pack — build new UI from the tokens, do not hardcode values."),
            "tier": tier,
        },
        "components": entries,
        "globalCssPaths": ["tokens/tokens.css"],
        "tokens": tokens,
        "cards": [],
        "adherenceConfig": "_adherence.json",
    }, indent=2) + "\n")
    return tier, tokens, entries, derived


def main():
    parser = argparse.ArgumentParser(description="Convert a DESIGN.md into a design-studio pack.")
    parser.add_argument("--design", required=True, help="path to DESIGN.md")
    parser.add_argument("--out", required=True, help="pack directory to write")
    parser.add_argument("--namespace", default="DesignMd",
                        help="window global the generated bundle exposes (default: DesignMd)")
    args = parser.parse_args()

    tier, tokens, entries, derived = convert(args.design, args.out, args.namespace)
    print(f"pack written: {args.out}")
    print(f"  tier       : {tier}")
    print(f"  tokens     : {len(tokens)}")
    print(f"  components : {len(entries)}")
    if derived:
        print(f"  derived    : {len(derived)} token(s) the engine needs that DESIGN.md does not define")
        for note in derived:
            print(f"    - {note}")
    missing = [note for note in derived if "MISSING" in note]
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
