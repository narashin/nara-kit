# test_check_adherence.py — the emit-time gate must catch hardcoded values without flagging
# the token declarations a portable single-file export legitimately inlines.
import json, os, sys, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_adherence as gate  # noqa: E402


def _write(tmp, name, content):
    path = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def test_clean_token_driven_output_passes():
    tmp = tempfile.mkdtemp()
    try:
        path = _write(tmp, "screen.html",
                      '<div style="color: var(--ds-ink); padding: var(--ds-space-md)">ok</div>\n')
        assert gate.scan(path, dict(gate.DEFAULTS)) == []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_catches_raw_hex_and_raw_px():
    tmp = tempfile.mkdtemp()
    try:
        path = _write(tmp, "screen.html",
                      '<div style="color: #18181b">a</div>\n'
                      '<div style="padding: 16px">b</div>\n')
        found = gate.scan(path, dict(gate.DEFAULTS))
        assert [(line, rule) for line, rule, _ in found] == [(1, "raw-hex"), (2, "raw-px")]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_hairline_px_is_allowed_but_spacing_px_is_not():
    tmp = tempfile.mkdtemp()
    try:
        path = _write(tmp, "screen.html",
                      '<div style="border: 1px solid var(--ds-hairline); margin: 24px">x</div>\n')
        found = gate.scan(path, dict(gate.DEFAULTS))
        assert [snippet for _line, _rule, snippet in found] == ["24px"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_inlined_root_token_block_is_exempt():
    tmp = tempfile.mkdtemp()
    try:
        path = _write(tmp, "screen.html",
                      "<style>\n:root {\n  --ds-ink: #18181b;\n  --ds-space-md: 16px;\n}\n</style>\n"
                      '<div style="color: #ff0000">leak</div>\n')
        found = gate.scan(path, dict(gate.DEFAULTS))
        # Only the usage outside :root is a violation; the token declarations are not.
        assert [(line, snippet) for line, _rule, snippet in found] == [(7, "#ff0000")]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_pack_config_overrides_defaults():
    tmp = tempfile.mkdtemp()
    try:
        pack = os.path.join(tmp, "pack")
        _write(pack, "_ds_manifest.json", json.dumps({"adherenceConfig": "_adherence.json"}))
        _write(pack, "_adherence.json", json.dumps({
            "forbidRawHex": False,
            "allowedRawPx": ["0px", "1px", "16px"],
            "ignorePatterns": ["data-studio-label"],
        }))
        config, config_path = gate.load_config(pack)
        assert config_path.endswith("_adherence.json")
        path = _write(tmp, "screen.html",
                      '<div style="color: #18181b; padding: 16px">hex+px allowed here</div>\n'
                      '<div data-studio-label="Row: 32px tall">ignored line</div>\n'
                      '<div style="gap: 40px">caught</div>\n')
        found = gate.scan(path, config)
        assert [(line, snippet) for line, _rule, snippet in found] == [(3, "40px")]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_missing_declared_config_is_an_error_not_a_silent_pass():
    tmp = tempfile.mkdtemp()
    try:
        pack = os.path.join(tmp, "pack")
        _write(pack, "_ds_manifest.json", json.dumps({"adherenceConfig": "_adherence.json"}))
        try:
            gate.load_config(pack)
            raise AssertionError("expected SystemExit for a declared-but-missing config")
        except SystemExit:
            pass
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_generated_pack_config_is_consumable():
    # The converter's output must satisfy this gate's loader — the two ship as a pair.
    sys.path.insert(0, HERE)
    import designmd_to_pack as conv
    tmp = tempfile.mkdtemp()
    try:
        design = _write(tmp, "DESIGN.md",
                        '---\nname: T\ncolors:\n  primary: "#2563eb"\n  ink: "#18181b"\n---\n')
        pack = os.path.join(tmp, "pack")
        conv.convert(design, pack, "T")
        config, config_path = gate.load_config(pack)
        assert config_path and config["forbidRawHex"] is True
        assert "--ds-primary" in config["allowTokens"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
