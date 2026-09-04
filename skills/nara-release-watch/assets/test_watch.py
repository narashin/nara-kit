"""Tests for the nara-release-watch poller.

Run: python3 -m pytest skills/nara-release-watch/assets/test_watch.py -q
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import watch  # noqa: E402

SCRIPT = Path(__file__).parent / "watch.py"


def rel(tag: str, prerelease: bool = False) -> dict:
    return {
        "id": tag,
        "name": tag,
        "url": f"https://example.test/{tag}",
        "published_at": "2026-09-01T00:00:00Z",
        "prerelease": prerelease,
        "body": "",
    }


def faker(table: dict):
    """table: repo -> (versions, source)"""

    def _fetch(repo, limit):
        return table.get(repo, ([], "error"))

    return _fetch


# --- watchlist parsing ---------------------------------------------------


def slugs(text: str) -> list[str]:
    return [e["repo"] for e in watch.parse_watchlist(text)]


def test_parses_markdown_prose_and_bullets():
    text = """
# 내 watchlist

> 취향대로 솎아낸 목록

## AI 도구
- anthropics/claude-code @minor
- [x] openai/codex   # 체크박스 + 주석
* `narashin/nara-kit`
+ https://github.com/obra/superpowers/
문장 안에 있는 건 잡지 않는다: 이 repo 좋다

## 중복
- Anthropics/Claude-Code
"""
    assert slugs(text) == [
        "anthropics/claude-code",
        "openai/codex",
        "narashin/nara-kit",
        "obra/superpowers",
    ]


def test_granularity_marker_is_parsed_and_defaults_to_patch():
    entries = watch.parse_watchlist(
        "- a/b @minor\n- c/d @major\n- e/f\n- g/h @nonsense\n"
    )
    assert [(e["repo"], e["granularity"]) for e in entries] == [
        ("a/b", "minor"),
        ("c/d", "major"),
        ("e/f", "patch"),
        ("g/h", "patch"),  # unknown marker falls back, never silently drops the repo
    ]


def test_prose_line_does_not_become_a_repo():
    assert slugs("이건 그냥 설명이고 슬래시가/있어도 아님 뒤에 말이 더 붙는다") == []


def test_bare_slug_without_bullet_is_accepted():
    assert slugs("anthropics/claude-code\n") == ["anthropics/claude-code"]


# --- noise control -------------------------------------------------------


def test_prereleases_are_skipped_by_default_even_without_the_api_flag():
    # openai/codex tags rust-v0.153.0-alpha.5 as a normal release.
    report, state = watch.poll(
        [{"repo": "a/b", "granularity": "patch"}],
        {"a/b": {"last_seen": "v1.0.0"}},
        5,
        fetch=faker({"a/b": ([rel("rust-v0.153.0-alpha.5"), rel("v1.0.0")], "releases")}),
    )
    assert report["new"] == []
    assert state["a/b"]["last_seen"] == "v1.0.0"  # stable baseline preserved


def test_include_prerelease_opts_back_in():
    report, _ = watch.poll(
        [{"repo": "a/b", "granularity": "patch"}],
        {"a/b": {"last_seen": "v1.0.0"}},
        5,
        fetch=faker({"a/b": ([rel("v1.1.0-rc.1"), rel("v1.0.0")], "releases")}),
        include_prerelease=True,
    )
    assert [r["id"] for r in report["new"]] == ["v1.1.0-rc.1"]


def test_all_prerelease_page_leaves_last_seen_intact():
    report, state = watch.poll(
        [{"repo": "a/b", "granularity": "patch"}],
        {"a/b": {"last_seen": "v1.0.0"}},
        5,
        fetch=faker({"a/b": ([rel("v2.0.0-beta.1")], "releases")}),
    )
    assert report["quiet"] is True
    assert state["a/b"]["last_seen"] == "v1.0.0"


def test_minor_threshold_suppresses_patch_bumps_but_advances_state():
    # anthropics/claude-code ships hundreds of patches; they must not fire daily.
    report, state = watch.poll(
        [{"repo": "a/b", "granularity": "minor"}],
        {"a/b": {"last_seen": "v2.1.255"}},
        5,
        fetch=faker({"a/b": ([rel("v2.1.258"), rel("v2.1.256")], "releases")}),
    )
    assert report["new"] == []
    assert report["suppressed"] == 2
    # State advances so the same patches are never re-evaluated.
    assert state["a/b"]["last_seen"] == "v2.1.258"


def test_minor_threshold_still_reports_a_minor_bump():
    report, _ = watch.poll(
        [{"repo": "a/b", "granularity": "minor"}],
        {"a/b": {"last_seen": "v2.1.255"}},
        5,
        fetch=faker({"a/b": ([rel("v2.2.0"), rel("v2.1.256")], "releases")}),
    )
    assert [r["id"] for r in report["new"]] == ["v2.2.0"]
    assert report["suppressed"] == 1


def test_major_threshold_suppresses_minor_bumps():
    report, _ = watch.poll(
        [{"repo": "a/b", "granularity": "major"}],
        {"a/b": {"last_seen": "v2.1.0"}},
        5,
        fetch=faker({"a/b": ([rel("v3.0.0"), rel("v2.9.0")], "releases")}),
    )
    assert [r["id"] for r in report["new"]] == ["v3.0.0"]


def test_unparseable_version_is_never_suppressed():
    # Suppressing what we cannot read would hide real releases.
    report, _ = watch.poll(
        [{"repo": "a/b", "granularity": "minor"}],
        {"a/b": {"last_seen": "release-2026-08"}},
        5,
        fetch=faker({"a/b": ([rel("release-2026-09")], "releases")}),
    )
    assert [r["id"] for r in report["new"]] == ["release-2026-09"]


# --- first-run baseline --------------------------------------------------


def test_first_run_baselines_silently():
    # Day one must not dump release history, or the digest is noise before it
    # has ever said anything useful.
    report, state = watch.poll(
        ["a/b"], {}, 5, fetch=faker({"a/b": ([rel("v2"), rel("v1")], "releases")})
    )
    assert report["new"] == []
    assert report["quiet"] is True
    assert report["baselined"] == [{"repo": "a/b", "baseline": "v2"}]
    assert state["a/b"]["last_seen"] == "v2"


def test_second_run_reports_only_versions_after_last_seen():
    state = {"a/b": {"last_seen": "v1"}}
    report, new_state = watch.poll(
        ["a/b"],
        state,
        5,
        fetch=faker({"a/b": ([rel("v3"), rel("v2"), rel("v1")], "releases")}),
    )
    assert [r["id"] for r in report["new"]] == ["v3", "v2"]
    assert report["quiet"] is False
    assert new_state["a/b"]["last_seen"] == "v3"


def test_no_change_is_a_quiet_day():
    report, _ = watch.poll(
        ["a/b"],
        {"a/b": {"last_seen": "v3"}},
        5,
        fetch=faker({"a/b": ([rel("v3"), rel("v2")], "releases")}),
    )
    assert report["new"] == []
    assert report["quiet"] is True


def test_truncation_is_flagged_when_page_is_full():
    # Every fetched version is unseen, so older ones may exist beyond the page.
    report, new_state = watch.poll(
        ["a/b"],
        {"a/b": {"last_seen": "v0"}},
        2,
        fetch=faker({"a/b": ([rel("v9"), rel("v8")], "releases")}),
    )
    assert len(report["new"]) == 2
    assert new_state["a/b"]["truncated"] is True


# --- failure vs emptiness ------------------------------------------------


def test_gh_error_demands_attention_and_leaves_state_untouched():
    state = {"a/b": {"last_seen": "v1", "last_checked": "old"}}
    report, new_state = watch.poll(["a/b"], state, 5, fetch=faker({}))
    assert report["failed"] == ["a/b"]
    assert report["unwatchable"] == []
    # A total failure day must not read as quiet, or broken auth stays invisible.
    assert report["needs_attention"] is True
    # last_checked must NOT advance, or the next run reads this as "nothing shipped"
    assert new_state["a/b"] == {"last_seen": "v1", "last_checked": "old"}


def test_repo_without_releases_or_tags_is_reported_unwatchable():
    report, state = watch.poll(["a/b"], {}, 5, fetch=faker({"a/b": ([], "none")}))
    assert report["unwatchable"] == ["a/b"]
    assert report["failed"] == []
    assert report["needs_attention"] is True
    assert state["a/b"]["unwatchable_reported"] is True


def test_unwatchable_repo_is_reported_once_then_stays_quiet():
    _, state = watch.poll(["a/b"], {}, 5, fetch=faker({"a/b": ([], "none")}))
    report, _ = watch.poll(["a/b"], state, 5, fetch=faker({"a/b": ([], "none")}))
    assert report["unwatchable"] == []
    assert report["needs_attention"] is False


def test_repo_that_starts_versioning_clears_the_unwatchable_flag():
    _, state = watch.poll(["a/b"], {}, 5, fetch=faker({"a/b": ([], "none")}))
    _, new_state = watch.poll(
        ["a/b"], state, 5, fetch=faker({"a/b": ([rel("v1")], "releases")})
    )
    assert "unwatchable_reported" not in new_state["a/b"]
    assert new_state["a/b"]["last_seen"] == "v1"


def test_quiet_day_needs_no_attention():
    report, _ = watch.poll(
        ["a/b"],
        {"a/b": {"last_seen": "v1"}},
        5,
        fetch=faker({"a/b": ([rel("v1")], "releases")}),
    )
    assert report["quiet"] is True
    assert report["needs_attention"] is False


def test_tag_fallback_records_its_source():
    _, state = watch.poll(
        ["a/b"], {}, 5, fetch=faker({"a/b": ([rel("1.2.0")], "tags")})
    )
    assert state["a/b"]["source"] == "tags"


# --- state io ------------------------------------------------------------


def test_corrupt_state_file_rebaselines_instead_of_raising(tmp_path):
    path = tmp_path / "state.json"
    path.write_text("{ this is not json", encoding="utf-8")
    assert watch.load_state(str(path)) == {}


def test_save_state_is_atomic_and_leaves_no_temp(tmp_path):
    path = tmp_path / "sub" / "state.json"
    watch.save_state(str(path), {"a/b": {"last_seen": "v1"}})
    assert json.loads(path.read_text())["a/b"]["last_seen"] == "v1"
    assert not (tmp_path / "sub" / "state.json.tmp").exists()


def test_missing_watchlist_yields_no_repos(tmp_path):
    assert watch.load_watchlist(str(tmp_path / "nope.md")) == []


# --- regressions found by review 2026-09-02 ------------------------------


@pytest.mark.parametrize(
    "tag",
    ["v1.0.0-aarch64", "v1.0.0-source", "v1.0.0-devtools", "v1.0.0-nextgen",
     "v3.0.0", "v1.0.0-linux-arm64"],
)
def test_stable_tags_are_not_mistaken_for_prereleases(tag):
    # The keyword search was unanchored, so aarch64 matched "rc", source matched
    # "rc", devtools matched "dev" -- silently suppressing stable releases.
    assert watch.is_prerelease({"id": tag, "prerelease": False}) is False


@pytest.mark.parametrize(
    "tag",
    ["rust-v0.153.0-alpha.5", "v1.1.0-rc.1", "v2.0.0-beta.1", "v1.0.0-dev",
     "v1.0.0.nightly", "v9-canary+2"],
)
def test_real_prerelease_tags_are_still_caught(tag):
    # Flag deliberately False: this pins the tag-string branch on its own.
    assert watch.is_prerelease({"id": tag, "prerelease": False}) is True


def test_api_prerelease_flag_alone_is_enough():
    # Deleting the flag branch of is_prerelease used to pass the whole suite,
    # because no test ever set it -- a clean semver tag flagged as prerelease.
    report, state = watch.poll(
        [{"repo": "a/b", "granularity": "patch"}],
        {"a/b": {"last_seen": "v1.0.0"}},
        5,
        fetch=faker({"a/b": ([rel("v2.0.0", prerelease=True), rel("v1.0.0")], "releases")}),
    )
    assert report["new"] == []
    assert state["a/b"]["last_seen"] == "v1.0.0"


def test_watchlist_keeps_a_slug_containing_a_double_dash():
    entries = watch.parse_watchlist("- some/repo--name\n- a/b -- trailing note\n")
    assert [e["repo"] for e in entries] == ["some/repo--name", "a/b"]


# --- fetch_versions source classification (was entirely untested) --------


def gh_stub(responses: dict, calls: list):
    def _gh(endpoint):
        calls.append(endpoint)
        for key, value in responses.items():
            if key in endpoint:
                return value
        return None
    return _gh


@pytest.mark.parametrize(
    "releases,tags,expected",
    [
        ([{"tag_name": "v1"}], None, "releases"),
        ([], [{"name": "v1"}], "tags"),
        (None, None, "error"),
        ([], None, "error"),      # empty releases + failed tags is a FAILURE
        (None, [], "error"),
        ([], [], "none"),         # both answered, neither has a version
    ],
)
def test_fetch_versions_classifies_the_source(monkeypatch, releases, tags, expected):
    calls = []
    monkeypatch.setattr(
        watch, "gh_json", gh_stub({"releases": releases, "tags": tags}, calls)
    )
    _, source = watch.fetch_versions("a/b", 5)
    assert source == expected


def test_failed_releases_call_skips_the_tags_call(monkeypatch):
    # The tags call fails for the same reason and cannot change the verdict, so
    # issuing it only doubled the round trips on every failing repo.
    calls = []
    monkeypatch.setattr(watch, "gh_json", gh_stub({"releases": None}, calls))
    _, source = watch.fetch_versions("a/b", 5)
    assert source == "error"
    assert not any("tags" in c for c in calls)


def test_gh_missing_or_hanging_returns_none_instead_of_raising(monkeypatch):
    # Letting these propagate aborted the entire poll from one bad repo.
    for exc in (FileNotFoundError("gh"), subprocess.TimeoutExpired("gh", 30)):
        def boom(*a, **k):
            raise exc
        monkeypatch.setattr(watch.subprocess, "run", boom)
        assert watch.gh_json("repos/a/b/releases") is None


def test_one_failing_repo_does_not_abort_the_rest(monkeypatch):
    def flaky(repo, limit):
        if repo == "b/b":
            return [], "error"
        return [rel("v1")], "releases"
    report, _ = watch.poll(
        [{"repo": r, "granularity": "patch"} for r in ("a/a", "b/b", "c/c")],
        {}, 5, fetch=flaky,
    )
    assert report["failed"] == ["b/b"]
    assert [b["repo"] for b in report["baselined"]] == ["a/a", "c/c"]


def test_save_state_accepts_a_bare_relative_filename(tmp_path, monkeypatch):
    # dirname("state.json") is "", and makedirs("") raises regardless of
    # exist_ok -- killing the run after every API call was already spent.
    monkeypatch.chdir(tmp_path)
    watch.save_state("state.json", {"a/b": {"last_seen": "v1"}})
    assert json.loads((tmp_path / "state.json").read_text())["a/b"]["last_seen"] == "v1"


def test_flags_work_on_either_side_of_the_subcommand(tmp_path):
    (tmp_path / "wl.md").write_text("- some/repo\n", encoding="utf-8")
    (tmp_path / "st.json").write_text(
        json.dumps({"some/repo": {"last_seen": "vSENTINEL"}}), encoding="utf-8"
    )
    paths = ["--watchlist", str(tmp_path / "wl.md"), "--state", str(tmp_path / "st.json")]
    seen = []
    for argv in ([*paths, "list"], ["list", *paths]):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *argv], capture_output=True, text=True, check=True
        )
        seen.append(json.loads(proc.stdout)["repos"][0]["last_seen"])
    # A subparser default used to clobber the root value, so the flag before the
    # verb was ignored and the real home-directory state file was read instead.
    assert seen == ["vSENTINEL", "vSENTINEL"]


# --- path mode (owner/repo:dir) -----------------------------------------


def test_path_entry_is_parsed_and_repo_entry_is_unaffected():
    entries = watch.parse_watchlist(
        "- anthropics/claude-code @minor\n"
        "- mattpocock/skills:skills/productivity/grill-me\n"
        "- mattpocock/skills:/skills/productivity/grilling/\n"
    )
    assert entries == [
        {"repo": "anthropics/claude-code", "granularity": "minor"},
        {"repo": "mattpocock/skills", "granularity": "patch",
         "path": "skills/productivity/grill-me"},
        {"repo": "mattpocock/skills", "granularity": "patch",
         "path": "skills/productivity/grilling"},
    ]


def test_path_traversal_entry_is_dropped():
    assert watch.parse_watchlist("- evil/repo:../../etc\n- evil/repo:a/../b\n") == []


def test_same_repo_at_two_paths_does_not_collide():
    entries = watch.parse_watchlist("- a/b:one\n- a/b:two\n- a/b\n")
    assert [watch.state_key(e) for e in entries] == ["a/b:one", "a/b:two", "a/b"]


def test_path_entry_uses_the_commit_fetcher_and_its_own_state():
    calls = []

    def fake_commits(repo, path, limit):
        calls.append((repo, path))
        return [rel("sha_new"), rel("sha_old")], "commits"

    def fake_versions(repo, limit):
        raise AssertionError("path entries must not hit the releases fetcher")

    report, state = watch.poll(
        [{"repo": "a/b", "granularity": "patch", "path": "skills/x"}],
        {"a/b:skills/x": {"last_seen": "sha_old"}},
        5,
        fetch=fake_versions,
        fetch_path=fake_commits,
    )
    assert calls == [("a/b", "skills/x")]
    assert [r["id"] for r in report["new"]] == ["sha_new"]
    assert [r["repo"] for r in report["new"]] == ["a/b:skills/x"]
    assert state["a/b:skills/x"]["last_seen"] == "sha_new"
    assert "a/b" not in state  # repo-level state untouched


def test_repo_level_and_path_level_states_are_independent():
    report, state = watch.poll(
        [
            {"repo": "a/b", "granularity": "patch"},
            {"repo": "a/b", "granularity": "patch", "path": "dir"},
        ],
        {},
        5,
        fetch=faker({"a/b": ([rel("v1")], "releases")}),
        fetch_path=lambda r, p, l: ([rel("sha1")], "commits"),
    )
    assert sorted(state) == ["a/b", "a/b:dir"]
    assert state["a/b"]["last_seen"] == "v1"
    assert state["a/b:dir"]["last_seen"] == "sha1"
    assert {b["repo"] for b in report["baselined"]} == {"a/b", "a/b:dir"}


def test_path_with_no_commits_is_reported_unwatchable_once(monkeypatch):
    # An empty commit list for a path almost always means a typo in the watchlist.
    monkeypatch.setattr(watch, "gh_json", lambda endpoint: [])
    assert watch.fetch_commits("a/b", "nope/dir", 5) == ([], "none")


def test_commit_fetch_failure_is_an_error_not_emptiness(monkeypatch):
    monkeypatch.setattr(watch, "gh_json", lambda endpoint: None)
    assert watch.fetch_commits("a/b", "dir", 5) == ([], "error")


def test_commit_records_match_the_version_record_shape(monkeypatch):
    monkeypatch.setattr(
        watch,
        "gh_json",
        lambda endpoint: [
            {
                "sha": "abc123",
                "html_url": "https://example.test/c/abc123",
                "commit": {
                    "message": "feat: add thing\n\nlonger body",
                    "author": {"date": "2026-08-15T00:00:00Z"},
                },
            }
        ],
    )
    versions, source = watch.fetch_commits("a/b", "dir", 5)
    assert source == "commits"
    assert set(versions[0]) == {"id", "name", "url", "published_at", "prerelease", "body"}
    assert versions[0]["id"] == "abc123"
    assert versions[0]["name"] == "feat: add thing"  # subject only
    assert versions[0]["body"] == "feat: add thing\n\nlonger body"
    assert versions[0]["prerelease"] is False


def test_path_is_url_quoted_in_the_endpoint(monkeypatch):
    seen = []
    monkeypatch.setattr(watch, "gh_json", lambda e: seen.append(e) or [])
    watch.fetch_commits("a/b", "skills/pro ductivity/grill-me", 5)
    assert "path=skills/pro%20ductivity/grill-me" in seen[0]


# --- stage contract ------------------------------------------------------


def test_poll_report_declares_the_watch_stage_forbids_judgment():
    # The contract must ride in the data: the skill ships a distillation rubric,
    # so a watch note drifts into judging when only prose forbids it.
    report, _ = watch.poll(["a/b"], {}, 5, fetch=faker({"a/b": ([rel("v1")], "releases")}))
    assert report["stage"] == "watch"
    assert report["judgment"] == "forbidden"


def test_digest_report_declares_the_opposite_stage(tmp_path, capsys):
    queue = tmp_path / "queue.json"
    queue.write_text(json.dumps([{"repo": "a/b", "id": "v2"}]), encoding="utf-8")
    watch.cmd_digest(argparse.Namespace(queue=str(queue), drain=False))
    report = json.loads(capsys.readouterr().out)
    assert (report["stage"], report["judgment"]) == ("digest", "required")


# --- highlights filter (watch-stage note, digest queue) -------------------

ORCA_BODY = """Thank you so much for using Orca! ❤️

## Notable changes
* Faster, smoother everyday use through renderer performance improvements.

## UI / workspaces
* Add parent worktree selection when creating workspace by @a in https://github.com/x/y/pull/1
* fix(terminal): mount one surface per workspace id by @b in https://github.com/x/y/pull/2
* Revert "fix(native-chat): preserve large results" by @c in https://github.com/x/y/pull/3
* chore: bump deps by @d in https://github.com/x/y/pull/4
* feat(browser-preview): reland remote HTML document previews by @e in https://github.com/x/y/pull/5

## New Contributors
* @someone made their first contribution in https://github.com/x/y/pull/6

**Full Changelog**: https://github.com/x/y/compare/v1...v2
"""


def test_highlights_keep_features_and_drop_conventional_noise():
    got = watch.extract_highlights(ORCA_BODY)
    assert got == [
        "Add parent worktree selection when creating workspace",
        "feat(browser-preview): reland remote HTML document previews",
    ]


def test_highlights_drop_the_notable_changes_marketing_section():
    # Those bullets carry no information the PR titles below do not carry better.
    assert not any("everyday use" in h for h in watch.extract_highlights(ORCA_BODY))


def test_highlights_strip_the_author_suffix_but_keep_plain_titles():
    got = watch.extract_highlights("* Improve cmd j ranking with recency by @z in https://github.com/x/y/pull/9\n")
    assert got == ["Improve cmd j ranking with recency"]


def test_prose_body_yields_no_highlights():
    # Hand-written notes have no bullets; the caller falls back to name + link.
    assert watch.extract_highlights("We rewrote the planner.\nIt is faster now.") == []


def test_highlights_are_capped():
    body = "\n".join(f"* Add feature number {i}" for i in range(50))
    assert len(watch.extract_highlights(body, cap=30)) == 30


def test_fixup_style_words_are_not_mistaken_for_noise_prefixes():
    # \b must sit on a real boundary: "Fixture loader" is not a fix() commit.
    assert watch.extract_highlights("* Fixture loader for the palette\n") == [
        "Fixture loader for the palette"
    ]


# --- digest queue ----------------------------------------------------------


def queue_item(repo="a/b", vid="v2", highlights=None):
    return {
        "repo": repo,
        "id": vid,
        "name": vid,
        "url": f"https://example.test/{vid}",
        "published_at": "2026-09-01T00:00:00Z",
        "prerelease": False,
        "body": "* Add thing by @x in https://example.test/pr/1",
        "highlights": highlights if highlights is not None else ["Add thing"],
    }


def test_enqueue_appends_and_dedupes_on_repo_and_id(tmp_path):
    path = str(tmp_path / "queue.json")
    assert watch.enqueue(path, [queue_item()]) == 1
    # A rewound state re-polling the same release must not double the backlog.
    assert watch.enqueue(path, [queue_item(), queue_item(vid="v3")]) == 1
    items = watch.load_queue(path)
    assert [(i["repo"], i["id"]) for i in items] == [("a/b", "v2"), ("a/b", "v3")]
    assert items[0]["highlights"] == ["Add thing"]
    assert "queued_at" in items[0]


def test_enqueue_truncates_the_body_excerpt(tmp_path):
    path = str(tmp_path / "queue.json")
    item = queue_item()
    item["body"] = "x" * 5000
    watch.enqueue(path, [item])
    assert len(watch.load_queue(path)[0]["body_excerpt"]) == 1500


def test_corrupt_queue_file_loses_backlog_but_does_not_raise(tmp_path):
    path = tmp_path / "queue.json"
    path.write_text("{ not json", encoding="utf-8")
    assert watch.load_queue(str(path)) == []


def test_fresh_poll_items_carry_highlights():
    version = rel("v2")
    version["body"] = "* Add thing by @x in https://example.test/pr/1\n* fix: nope\n"
    report, _ = watch.poll(
        ["a/b"],
        {"a/b": {"last_seen": "v1"}},
        5,
        fetch=faker({"a/b": ([version, rel("v1")], "releases")}),
    )
    assert report["new"][0]["highlights"] == ["Add thing"]


def test_digest_cli_reads_then_drains_only_when_asked(tmp_path):
    queue = tmp_path / "queue.json"
    queue.write_text(json.dumps([{"repo": "a/b", "id": "v2"}]), encoding="utf-8")
    flags = ["--queue", str(queue)]

    read_only = json.loads(
        subprocess.run(
            [sys.executable, str(SCRIPT), "digest", *flags],
            capture_output=True, text=True, check=True,
        ).stdout
    )
    assert read_only["count"] == 1 and read_only["drained"] is False
    assert json.loads(queue.read_text()) != []  # a plain read must not drain

    drained = json.loads(
        subprocess.run(
            [sys.executable, str(SCRIPT), "digest", "--drain", *flags],
            capture_output=True, text=True, check=True,
        ).stdout
    )
    assert drained["count"] == 1 and drained["drained"] is True
    assert json.loads(queue.read_text()) == []


def cmd_poll_args(tmp_path, dry_run: bool) -> argparse.Namespace:
    wl = tmp_path / "wl.md"
    wl.write_text("- a/b\n", encoding="utf-8")
    st = tmp_path / "st.json"
    st.write_text(json.dumps({"a/b": {"last_seen": "v1"}}), encoding="utf-8")
    return argparse.Namespace(
        watchlist=str(wl),
        state=str(st),
        queue=str(tmp_path / "queue.json"),
        limit=5,
        dry_run=dry_run,
        include_prerelease=False,
    )


def test_dry_run_poll_does_not_enqueue(tmp_path, monkeypatch, capsys):
    # Queue and state must advance together: a dry run burns neither.
    # poll()'s `fetch=fetch_versions` default binds at def time, so patching the
    # fetcher name does nothing here; gh_json is resolved at call time instead.
    monkeypatch.setattr(
        watch,
        "gh_json",
        lambda endpoint: [{"tag_name": "v2"}, {"tag_name": "v1"}]
        if "releases" in endpoint
        else [],
    )
    args = cmd_poll_args(tmp_path, dry_run=True)
    assert watch.cmd_poll(args) == 0
    report = json.loads(capsys.readouterr().out)
    assert [r["id"] for r in report["new"]] == ["v2"]
    assert report["queued"] == 0
    assert not (tmp_path / "queue.json").exists()


def test_real_poll_enqueues_the_fresh_items(tmp_path, monkeypatch, capsys):
    # poll()'s `fetch=fetch_versions` default binds at def time, so patching the
    # fetcher name does nothing here; gh_json is resolved at call time instead.
    monkeypatch.setattr(
        watch,
        "gh_json",
        lambda endpoint: [{"tag_name": "v2"}, {"tag_name": "v1"}]
        if "releases" in endpoint
        else [],
    )
    args = cmd_poll_args(tmp_path, dry_run=False)
    assert watch.cmd_poll(args) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["queued"] == 1
    assert [(i["repo"], i["id"]) for i in watch.load_queue(args.queue)] == [("a/b", "v2")]


def test_a_hex_sha_can_never_look_like_a_prerelease():
    # The prerelease keywords all contain a non-hex letter (r, v, t, y, s, w, p),
    # so the filter is inert on commit SHAs and needs no special casing.
    for sha in ("deadbeefcafe1234", "0123456789abcdef", "aabbccddeeff0011"):
        assert watch.is_prerelease({"id": sha, "prerelease": False}) is False
