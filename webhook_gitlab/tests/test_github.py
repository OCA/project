# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import GITHUB_REPO_URL, NULL_SHA, WebhookGitlabCase


class TestGithubPullRequest(WebhookGitlabCase):
    # Standard set of commits returned by the mocked PR commit fetch:
    # two matching the title task (GH-100, doubled to catch singleton
    # errors in the matching logic), one referencing another task
    # (GH-115), one generic.
    MIXED_PR_COMMITS = [
        {"sha": "c" * 40, "message": "GH-100 pr commit one"},
        {"sha": "d" * 40, "message": "GH-100 pr commit two"},
        {"sha": "e" * 40, "message": "GH-115 unrelated fix"},
        {"sha": "f" * 40, "message": "generic commit"},
    ]

    def _pr_payload(self, title=None, head_ref=None):
        payload = self._load_payload("github_pull_request.json")
        if title is not None:
            payload["pull_request"]["title"] = title
        if head_ref is not None:
            payload["pull_request"]["head"]["ref"] = head_ref
        return payload

    def test_pr_pattern_match_on_title_links_pr_branch_and_commits(self):
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, pull = self._mock_github_client(commits=self.MIXED_PR_COMMITS)
        with patcher:
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertEqual(len(pull_request), 1)
        self.assertEqual(pull_request.source, "github")
        self.assertEqual(pull_request.state, "opened")
        self.assertEqual(pull_request.source_branch, "test-merge-2")
        self.assertEqual(pull_request.target_branch, "main")
        self.assertIn(pull_request.id, self.gh_task_100.git_pull_request_ids.ids)

        branch = self._get_branch("test-merge-2")
        self.assertEqual(len(branch), 1)
        self.assertEqual(branch.url, f"{GITHUB_REPO_URL}/tree/test-merge-2")
        self.assertIn(branch.id, self.gh_task_100.git_branch_ids.ids)

        # All the PR commits are linked to the task matched by the title
        self.assertEqual(
            set(self.gh_task_100.git_commit_ids.mapped("full_sha")),
            {"c" * 40, "d" * 40, "e" * 40, "f" * 40},
        )
        # The matched task is notified once on the PR with its Odoo link
        pull.create_issue_comment.assert_called_once()
        message_body = pull.create_issue_comment.call_args[0][0]
        self.assertIn("Linked to Odoo task", message_body)

    def test_pr_commit_message_matches_are_ignored(self):
        # PR/MR flow only matches on title and source branch: a fetched
        # commit referencing GH-115 must NOT link anything to that task
        # (see analysis doc, section 5.2).
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, _pull = self._mock_github_client(commits=self.MIXED_PR_COMMITS)
        with patcher:
            self._dispatch(payload, "github")

        self.assertFalse(self.gh_task_115.git_pull_request_ids)
        self.assertFalse(self.gh_task_115.git_branch_ids)
        self.assertFalse(self.gh_task_115.git_commit_ids)
        self.assertFalse(self.gh_task_no_pattern.git_pull_request_ids)

    def test_pr_pattern_match_on_source_branch(self):
        payload = self._pr_payload(head_ref="GH-115-docs")
        patcher, _pull = self._mock_github_client(
            commits=[{"sha": "c" * 40, "message": "generic commit"}]
        )
        with patcher:
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertIn(pull_request.id, self.gh_task_115.git_pull_request_ids.ids)
        branch = self._get_branch("GH-115-docs")
        self.assertIn(branch.id, self.gh_task_115.git_branch_ids.ids)
        self.assertEqual(self.gh_task_115.git_commit_ids.mapped("full_sha"), ["c" * 40])
        self.assertFalse(self.gh_task_100.git_pull_request_ids)

    def test_pr_legacy_task_id_in_title_links_pr_and_posts_message(self):
        payload = self._pr_payload(
            title=f"update readme task#{self.gh_task_no_pattern.id}"
        )
        patcher, pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertEqual(len(pull_request), 1)
        self.assertEqual(pull_request.task_ids, self.gh_task_no_pattern)
        pull.create_issue_comment.assert_called_once()
        message_body = pull.create_issue_comment.call_args[0][0]
        self.assertIn("Linked to Odoo task", message_body)

    def test_pr_commit_fetch_failure_falls_back_to_head_sha(self):
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, pull = self._mock_github_client()
        pull.get_commits.side_effect = Exception("API not available")
        with patcher:
            self._dispatch(payload, "github")

        head_sha = payload["pull_request"]["head"]["sha"]
        self.assertEqual(
            self.gh_task_100.git_commit_ids.mapped("full_sha"), [head_sha]
        )

    def test_pr_without_match_creates_nothing_but_warns_once(self):
        # Known repository but no pattern nor task#ID anywhere: the PR is
        # not tracked and the "no task reference" warning is posted on
        # opening only, never again on later update events (anti-spam).
        payload = self._pr_payload(title="Generic title")
        patcher, pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")
            payload["action"] = "synchronize"
            self._dispatch(payload, "github")

        self.assertFalse(self._get_pull_request(payload["pull_request"]["html_url"]))
        self.assertFalse(self._get_branch("test-merge-2"))
        pull.create_issue_comment.assert_called_once()
        message_body = pull.create_issue_comment.call_args[0][0]
        self.assertIn("WARNING", str(message_body))

    def test_pr_legacy_task_id_not_found_warns_once(self):
        # Explicit task#<id> reference to a non-existent task: the broken
        # reference is warned about on opening only, and nothing is created.
        missing_id = self.env["project.task"].search([], order="id desc", limit=1).id + 1000
        payload = self._pr_payload(title=f"update readme task#{missing_id}")
        patcher, pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")
            payload["action"] = "synchronize"
            self._dispatch(payload, "github")

        self.assertFalse(self._get_pull_request(payload["pull_request"]["html_url"]))
        pull.create_issue_comment.assert_called_once()
        message_body = pull.create_issue_comment.call_args[0][0]
        self.assertIn("cannot be found", str(message_body))

    def test_pr_commit_message_is_split_in_title_and_description(self):
        long_title = "GH-100 " + "x" * 80
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, _pull = self._mock_github_client(
            commits=[{"sha": "c" * 40, "message": f"{long_title}\nrest of message"}]
        )
        with patcher:
            self._dispatch(payload, "github")

        commit = self._get_commit("c" * 40)
        self.assertEqual(commit.name, long_title[:60])
        self.assertEqual(commit.description, "rest of message")


class TestGithubPush(WebhookGitlabCase):
    def _push_payload(self, ref="refs/heads/main", commits=None, before=None):
        payload = self._load_payload("github_push.json")
        payload["ref"] = ref
        if commits is not None:
            payload["commits"] = commits
            if commits:
                payload["after"] = commits[-1]["id"]
                payload["head_commit"] = commits[-1]
        if before is not None:
            payload["before"] = before
        return payload

    @staticmethod
    def _commit(sha, message):
        return {
            "id": sha,
            "message": message,
            "timestamp": "2026-08-24T02:45:14+02:00",
            "url": f"{GITHUB_REPO_URL}/commit/{sha}",
            "author": {
                "name": "Demo User",
                "email": "demo@example.com",
                "username": "demo-user",
            },
        }

    def test_push_branch_name_match_links_branch_and_all_commits(self):
        commits = [
            self._commit("a" * 40, "generic commit one"),
            self._commit("b" * 40, "generic commit two"),
            self._commit("c" * 40, "generic commit three"),
        ]
        payload = self._push_payload(ref="refs/heads/GH-100-readme", commits=commits)
        self._dispatch(payload, "github")

        branch = self._get_branch("GH-100-readme")
        self.assertEqual(len(branch), 1)
        self.assertEqual(branch.url, f"{GITHUB_REPO_URL}/tree/GH-100-readme")
        self.assertIn(branch.id, self.gh_task_100.git_branch_ids.ids)
        self.assertEqual(
            set(self.gh_task_100.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40, "c" * 40},
        )
        self.assertFalse(self.gh_task_115.git_commit_ids)
        self.assertFalse(self.gh_task_no_pattern.git_commit_ids)

    def test_push_mixed_commit_messages_link_branch_and_all_commits(self):
        # Mirror of the GitLab mixed push scenario.
        # NOTE: current (pre granular-matching) behavior: a single matching
        # commit message links the branch AND every pushed commit to the task.
        commits = [
            self._commit("a" * 40, "GH-115 fix the docs"),
            self._commit("b" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "github")

        branch = self._get_branch("develop")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gh_task_115.git_branch_ids.ids)
        self.assertEqual(
            set(self.gh_task_115.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40},
        )
        self.assertFalse(self.gh_task_100.git_commit_ids)

    def test_push_commits_matching_different_tasks(self):
        # Push on a non-matching branch: two commits reference GH-100
        # (doubled to catch singleton errors in the matching logic), one
        # references GH-115, one references nothing.
        # Current behavior: every matching task gets the branch and ALL
        # pushed commits (see the GitLab mirror test).
        commits = [
            self._commit("a" * 40, "GH-100 part one"),
            self._commit("b" * 40, "GH-100 part two"),
            self._commit("c" * 40, "GH-115 side fix"),
            self._commit("d" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "github")

        all_shas = {"a" * 40, "b" * 40, "c" * 40, "d" * 40}
        for task in (self.gh_task_100, self.gh_task_115):
            self.assertEqual(set(task.git_commit_ids.mapped("full_sha")), all_shas)
            self.assertIn(
                self._get_branch("develop").id, task.git_branch_ids.ids
            )
        self.assertFalse(self.gh_task_no_pattern.git_commit_ids)

    def test_branch_creation_mixed_commits_links_branch_and_commits(self):
        # Branch creation carrying 4 commits: branch name matches GH-100,
        # two commits reference GH-100 (doubled to catch singleton errors),
        # one references GH-115, one references nothing.
        # Current behavior: branch + ALL commits linked to every matching task.
        commits = [
            self._commit("a" * 40, "GH-100 part one"),
            self._commit("b" * 40, "GH-100 part two"),
            self._commit("c" * 40, "GH-115 side fix"),
            self._commit("d" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(
            ref="refs/heads/GH-100-feature", commits=commits, before=NULL_SHA
        )
        self._dispatch(payload, "github")

        branch = self._get_branch("GH-100-feature")
        self.assertEqual(len(branch), 1)
        all_shas = {"a" * 40, "b" * 40, "c" * 40, "d" * 40}
        for task in (self.gh_task_100, self.gh_task_115):
            self.assertIn(branch.id, task.git_branch_ids.ids)
            self.assertEqual(set(task.git_commit_ids.mapped("full_sha")), all_shas)
        self.assertFalse(self.gh_task_no_pattern.git_commit_ids)

    def test_push_without_match_creates_nothing(self):
        commits = [
            self._commit("a" * 40, "generic commit one"),
            self._commit("b" * 40, "generic commit two"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "github")

        self.assertFalse(self._get_branch("develop"))
        self.assertFalse(self._get_commit("a" * 40))
        self.assertFalse(self._get_commit("b" * 40))
