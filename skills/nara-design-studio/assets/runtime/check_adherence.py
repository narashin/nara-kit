#!/usr/bin/env python3
"""
Emit-time adherence gate for nara-design-studio output (generic — no design-system specifics).

`nara-design-studio`'s baseline rule "tokens only — no hardcoded brand values" is unenforceable as
prose: a model that writes `padding: 16px` has already violated it by the time anyone reads the
output. This script makes the rule checkable, so the pre-emit checklist has a mechanical step
instead of a self-graded one.

Two rules ship on by default and need no configuration:
  - raw hex colors  (#rgb / #rrggbb / #rrggbbaa)
  - raw px values   (beyond a small allowlist — a 1px hairline is not a spacing decision)

A pack may tighten or relax them by shipping an adherence config and pointing at it from its
manifest's `adherenceConfig` field. Config keys: forbidRawHex, forbidRawPx, allowedRawPx,
ignorePatterns (regexes whose matching lines are skipped).

Declarations inside a `:root { ... }` block are always exempt — `SKILL.md` §5 explicitly tells a
portable single-file export to inline the pack's token block, and those declarations are the
token definitions themselves, not hardcoded usage.

Usage:
  python3 check_adherence.py <file.html> [more.html ...] [--pack <packDir>] [--quiet]

Exit code: 0 = clean, 1 = violations found, 2 = bad invocation.
"""
import argparse
import json
import os
import re
import sys

HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
PX = re.compile(r"\b\d+(?:\.\d+)?px\b")
ROOT_OPEN = re.compile(r":root\s*\{")

DEFAULTS = {
    "forbidRawHex": True,
    "forbidRawPx": True,
    "allowedRawPx": ["0px", "1px"],
    "ignorePatterns": [],
}


def load_config(pack_dir):
    """Read the pack's adherence config, if it declares one. Defaults apply when it doesn't."""
    config = dict(DEFAULTS)
    if not pack_dir:
        return config, None
    manifest_path = os.path.join(pack_dir, "_ds_manifest.json")
    if not os.path.isfile(manifest_path):
        return config, None
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    rel = manifest.get("adherenceConfig")
    if not rel:
        return config, None
    config_path = os.path.join(pack_dir, rel)
    if not os.path.isfile(config_path):
        raise SystemExit(f"manifest declares adherenceConfig '{rel}' but {config_path} is missing")
    with open(config_path, encoding="utf-8") as f:
        config.update(json.load(f))
    return config, config_path


def scan(path, config):
    """Return a list of (line_no, rule, snippet) violations for one file."""
    ignore = [re.compile(pattern) for pattern in config.get("ignorePatterns", [])]
    allowed_px = set(config.get("allowedRawPx", []))
    violations = []
    depth = 0  # brace depth inside a :root block; 0 means we are outside one

    with open(path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if depth > 0:
                depth += line.count("{") - line.count("}")
                continue
            match = ROOT_OPEN.search(line)
            if match:
                # Only the tail after `:root {` could still hold non-token content; skip the line.
                depth = 1 + line.count("{", match.end()) - line.count("}", match.end())
                continue
            if any(pattern.search(line) for pattern in ignore):
                continue
            if config.get("forbidRawHex") and HEX.search(line):
                violations.append((line_no, "raw-hex", HEX.search(line).group(0)))
            if config.get("forbidRawPx"):
                for found in PX.findall(line):
                    if found not in allowed_px:
                        violations.append((line_no, "raw-px", found))
    return violations


def main():
    parser = argparse.ArgumentParser(description="Check generated studio output for hardcoded values.")
    parser.add_argument("files", nargs="+", help="generated HTML file(s) to check")
    parser.add_argument("--pack", default="", help="pack dir, to read its adherenceConfig")
    parser.add_argument("--quiet", action="store_true", help="print violations only")
    args = parser.parse_args()

    config, config_path = load_config(args.pack)
    total = 0
    for path in args.files:
        if not os.path.isfile(path):
            print(f"{path}: not a file", file=sys.stderr)
            return 2
        for line_no, rule, snippet in scan(path, config):
            total += 1
            print(f"{path}:{line_no}: {rule}: {snippet} — use a pack token via var(--ds-*)")

    if not args.quiet:
        source = config_path or "built-in defaults"
        print(f"adherence: {len(args.files)} file(s) checked against {source} — "
              f"{total} violation(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
