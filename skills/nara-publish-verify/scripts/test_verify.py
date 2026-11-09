import copy
import io
import json
import subprocess
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import verify


URL = "https://git.example.com/acme/api-server/pull/42"
HOST = "git.example.com"
TRAILER = "Co-authored-by: Test Agent <agent@example.com>"
SHA = "a" * 40
OTHER = "b" * 40


def pr():
    return {
        "html_url": URL,
        "number": 42,
        "body": "Summary\n\n" + TRAILER,
        "assignees": [{"login": "owner"}],
        "head": {"sha": SHA},
        "commits": 1,
    }


def commit(sha=SHA, message="fix: validate permissions\n\n" + TRAILER):
    return {"sha": sha, "commit": {"message": message}}


class VerifyTests(unittest.TestCase):
    def run_check(self, details=None, pages=None, after=None, shas=None):
        details = pr() if details is None else details
        pages = [[commit()]] if pages is None else pages
        after = copy.deepcopy(details) if after is None else after
        responses = [details, pages, after]
        with patch("verify.subprocess.run") as run:
            run.side_effect = [
                subprocess.CompletedProcess([], 0, json.dumps(value), "")
                for value in responses
            ]
            result = verify.verify(URL, HOST, "owner", TRAILER, shas or [SHA])
        return result, run.call_args_list

    def test_published_remote_state_passes_with_get_only(self):
        result, calls = self.run_check()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["checked_commits"], [SHA])
        commands = [call.args[0] for call in calls]
        self.assertEqual(commands[0], [
            "gh", "api", "--hostname", HOST, "--method", "GET",
            "repos/acme/api-server/pulls/42",
        ])
        self.assertEqual(commands[1], commands[0][:-1] + [
            "repos/acme/api-server/pulls/42/commits?per_page=100",
            "--paginate", "--slurp",
        ])
        self.assertEqual(commands[2], commands[0])
        self.assertTrue(all(call.kwargs.get("shell", False) is False for call in calls))
        self.assertTrue(all(call.kwargs["timeout"] == 60 for call in calls))

    def test_missing_wrong_duplicate_and_nonterminal_pr_trailers_fail(self):
        for body in ["Summary", "Summary\n\nCo-authored-by: Other <other@example.com>",
                     TRAILER + "\n\n" + TRAILER, "Summary\n\n" + TRAILER + "\nMore",
                     "Summary\n" + TRAILER, None]:
            with self.subTest(body=body):
                details = pr()
                details["body"] = body
                result, _ = self.run_check(details=details)
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any("PR trailer" in error for error in result["errors"]))

    def test_missing_or_other_assignee_fails_but_extra_assignees_are_allowed(self):
        for logins, status in [([], "fail"), (["someone"], "fail"),
                               (["OWNER", "someone"], "pass")]:
            with self.subTest(logins=logins):
                details = pr()
                details["assignees"] = [{"login": login} for login in logins]
                result, _ = self.run_check(details=details)
                self.assertEqual(result["status"], status)

    def test_enterprise_managed_logins_and_personal_repositories(self):
        url = URL.replace("/acme/", "/owner_acme/")
        details = pr()
        details["html_url"] = url
        details["assignees"] = [{"login": "owner_acme"}]
        with patch("verify.gh_get", side_effect=[details, [[commit()]], details]):
            result = verify.verify(url, HOST, "owner_acme", TRAILER, [SHA])
        self.assertEqual(result["status"], "pass")

    def test_selected_commit_trailer_and_no_body_policy(self):
        for message in ["fix: missing", "fix: wrong\n\nCo-authored-by: Other <x@example.com>",
                        "fix: duplicate\n\n" + TRAILER + "\n" + TRAILER,
                        "fix: body\n\nDescription\n\n" + TRAILER,
                        "fix: spacing\n" + TRAILER, "\n\n" + TRAILER,
                        "fix: wrong\n\n co-authored-by: Test Agent <agent@example.com>"]:
            with self.subTest(message=message):
                result, _ = self.run_check(pages=[[commit(message=message)]])
                self.assertEqual(result["status"], "fail")
                self.assertTrue(any(SHA in error for error in result["errors"]))

    def test_unpublished_selected_commit_fails(self):
        result, _ = self.run_check(shas=[OTHER])
        self.assertEqual(result["status"], "fail")
        self.assertIn(OTHER, " ".join(result["errors"]))

    def test_only_git_line_delimiters_can_separate_trailers(self):
        for separator, status in [("\n", "pass"), ("\r\n", "pass"),
                                  ("\r", "fail"), (chr(0x2028), "fail"),
                                  (chr(0x2029), "fail"), (chr(0x85), "fail")]:
            with self.subTest(separator=repr(separator)):
                details = pr()
                details["body"] = separator.join(["Summary", "", TRAILER])
                message = separator.join(["fix: permissions", "", TRAILER])
                result, _ = self.run_check(details=details, pages=[[commit(message=message)]])
                self.assertEqual(result["status"], status)
                if status == "fail":
                    self.assertEqual(len(result["errors"]), 2)

    def test_human_commits_are_not_silently_subject_to_ai_policy(self):
        details = pr()
        details["commits"] = 2
        result, _ = self.run_check(details=details, pages=[
            [commit(OTHER, "Human commit\n\nBody")], [commit()],
        ])
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["unchecked_commits"], [OTHER])
        self.assertEqual(result["remote_commit_count"], 2)

    def test_pagination_gaps_duplicates_and_head_mismatch_are_unknown(self):
        for pages in [[], [[]], [[commit(), commit()]], [[commit(OTHER)]]]:
            with self.subTest(pages=pages), self.assertRaises(verify.Unverifiable):
                self.run_check(pages=pages)

    def test_schema_errors_are_unknown_not_clean(self):
        for key in ["body", "assignees", "head", "commits", "html_url", "number"]:
            with self.subTest(missing=key), self.assertRaises(verify.Unverifiable):
                details = pr()
                del details[key]
                self.run_check(details=details)
        for key, value in [("assignees", None), ("assignees", [{}]),
                           ("commits", True), ("body", {}), ("head", {"sha": "short"}),
                           ("html_url", URL.replace("api-server", "other"))]:
            with self.subTest(key=key, value=value), self.assertRaises(verify.Unverifiable):
                details = pr()
                details[key] = value
                self.run_check(details=details)
        for pages in [[{}], [[{}]], [[{"sha": SHA, "commit": {}}]],
                      [[commit(message=None)]]]:
            with self.subTest(pages=pages), self.assertRaises(verify.Unverifiable):
                self.run_check(pages=pages)

    def test_concurrent_head_body_and_assignment_changes_are_unknown(self):
        for key, value in [("head", {"sha": OTHER}), ("body", "Changed"),
                           ("assignees", []), ("commits", 2)]:
            with self.subTest(key=key), self.assertRaises(verify.Unverifiable):
                after = pr()
                after[key] = value
                self.run_check(after=after)

    def test_bad_urls_or_unconfirmed_policy_never_call_gh(self):
        bad_urls = [URL.replace("https:", "http:"), URL + "?x=1", URL + "#discussion",
                    URL.replace(HOST, "other.example.com"),
                    URL.replace(HOST, "user@" + HOST),
                    URL.replace(HOST, HOST + ":443"), URL.replace("acme", ".."),
                    URL.replace("api-server", "{repo}"), URL + "/files", URL + "\n",
                    chr(0) + URL, URL + chr(127)]
        with patch("verify.subprocess.run") as run:
            for url in bad_urls:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    verify.verify(url, HOST, "owner", TRAILER, [SHA])
            for assignee, trailer, shas in [("", TRAILER, [SHA]), ("owner", "", [SHA]),
                                             ("owner", TRAILER, []),
                                             ("owner", TRAILER, ["abc123"])]:
                with self.subTest(assignee=assignee, trailer=trailer, shas=shas):
                    with self.assertRaises(ValueError):
                        verify.verify(URL, HOST, assignee, trailer, shas)
            run.assert_not_called()

    def test_cli_api_errors_produce_unknown_and_nonzero_without_leaking_stderr(self):
        args = [URL, "--host", HOST, "--assignee", "owner", "--trailer", TRAILER,
                "--commit", SHA]
        for failure in [FileNotFoundError(), subprocess.TimeoutExpired("gh", 60),
                        subprocess.CalledProcessError(1, "gh", stderr="SECRET"),
                        subprocess.CompletedProcess([], 0, "not json", "")]:
            with self.subTest(failure=failure), patch("verify.subprocess.run") as run:
                if isinstance(failure, subprocess.CompletedProcess):
                    run.return_value = failure
                else:
                    run.side_effect = failure
                output = io.StringIO()
                with redirect_stdout(output):
                    code = verify.main(args)
                report = json.loads(output.getvalue())
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "unverifiable")
                self.assertNotIn("SECRET", output.getvalue())


if __name__ == "__main__":
    unittest.main()
