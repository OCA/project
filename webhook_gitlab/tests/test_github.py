# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

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

        # Commits link by their own message only: the title-matched task
        # gets just the commits that mention it
        self.assertEqual(
            set(self.gh_task_100.git_commit_ids.mapped("full_sha")),
            {"c" * 40, "d" * 40},
        )
        self.assertFalse(self._get_commit("f" * 40))
        # The tracked entities are correlated with each other: the PR with
        # its source branch record and every tracked commit with both
        self.assertEqual(pull_request.source_branch_id, branch)
        tracked_shas = {"c" * 40, "d" * 40, "e" * 40}
        self.assertEqual(
            set(pull_request.git_commit_ids.mapped("full_sha")), tracked_shas
        )
        self.assertEqual(set(branch.git_commit_ids.mapped("full_sha")), tracked_shas)
        # Each matched task (GH-100 by title, GH-115 by commit message) is
        # notified once on the PR with its Odoo link
        self.assertEqual(pull.create_issue_comment.call_count, 2)
        for call in pull.create_issue_comment.call_args_list:
            self.assertIn("Linked to Odoo task", call[0][0])

    def test_pr_commit_message_match_links_pr_branch_and_commit(self):
        # A fetched commit referencing GH-115 links the PR and that commit
        # to the task, plus the source branch (a PR is linked when one of
        # its commits mentions the task, and the source branch follows the
        # linked PR). The other PR commits stay unrelated to GH-115.
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, _pull = self._mock_github_client(commits=self.MIXED_PR_COMMITS)
        with patcher:
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertIn(pull_request.id, self.gh_task_115.git_pull_request_ids.ids)
        branch = self._get_branch("test-merge-2")
        self.assertIn(branch.id, self.gh_task_115.git_branch_ids.ids)
        self.assertEqual(self.gh_task_115.git_commit_ids.mapped("full_sha"), ["e" * 40])
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
        # The PR commit does not mention any task: it is not tracked
        self.assertFalse(self.gh_task_115.git_commit_ids)
        self.assertFalse(self._get_commit("c" * 40))
        self.assertFalse(self.gh_task_100.git_pull_request_ids)

    def test_pr_task_id_reference_in_title_links_pr_and_posts_message(self):
        payload = self._pr_payload(
            title=f"update readme tid#{self.gh_task_no_pattern.id}"
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
        # When the commit fetch fails, the synthetic head commit built
        # from the payload embeds the PR title in its message, so it
        # matches (and links to) the same task as the title.
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, pull = self._mock_github_client()
        pull.get_commits.side_effect = Exception("API not available")
        with patcher:
            self._dispatch(payload, "github")

        head_sha = payload["pull_request"]["head"]["sha"]
        self.assertEqual(self.gh_task_100.git_commit_ids.mapped("full_sha"), [head_sha])

    def test_pr_without_match_creates_nothing_but_warns_once(self):
        # Known repository but no reference anywhere: the PR is
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

    def test_pr_task_id_reference_not_found_warns_once(self):
        # Explicit taskid#<id> reference to a non-existent task: the broken
        # reference is warned about on opening only, and nothing is created.
        missing_id = (
            self.env["project.task"].search([], order="id desc", limit=1).id + 1000
        )
        payload = self._pr_payload(title=f"update readme taskid#{missing_id}")
        patcher, pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")
            payload["action"] = "synchronize"
            self._dispatch(payload, "github")

        self.assertFalse(self._get_pull_request(payload["pull_request"]["html_url"]))
        pull.create_issue_comment.assert_called_once()
        message_body = pull.create_issue_comment.call_args[0][0]
        self.assertIn("cannot be found", str(message_body))

    def test_pr_closed_event_updates_state_and_tags(self):
        payload = self._pr_payload(title="GH-100 update readme")
        patcher, _pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")
            self.assertIn("MR: Opened", self.gh_task_100.tag_ids.mapped("name"))
            payload["action"] = "closed"
            payload["pull_request"]["state"] = "closed"
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertEqual(pull_request.state, "closed")
        # The state tag is replaced, not accumulated
        tag_names = self.gh_task_100.tag_ids.mapped("name")
        self.assertIn("MR: Closed", tag_names)
        self.assertNotIn("MR: Opened", tag_names)

    def test_pr_user_mapping_by_github_username(self):
        github_user = self.env["res.users"].create(
            {
                "name": "GitHub Webhook User",
                "login": "github-webhook-user@example.com",
                "github_username": "gh-webhook-demo-user",
            }
        )
        payload = self._pr_payload(title="GH-100 update readme")
        payload["pull_request"]["user"]["login"] = "gh-webhook-demo-user"
        patcher, _pull = self._mock_github_client()
        with patcher:
            self._dispatch(payload, "github")

        pull_request = self._get_pull_request(payload["pull_request"]["html_url"])
        self.assertEqual(pull_request.user_id, github_user)

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
    def _push_payload(
        self, ref="refs/heads/main", commits=None, before=None, after=None
    ):
        payload = self._load_payload("github_push.json")
        payload["ref"] = ref
        if commits is not None:
            payload["commits"] = commits
            if commits:
                payload["after"] = commits[-1]["id"]
                payload["head_commit"] = commits[-1]
        if before is not None:
            payload["before"] = before
        if after is not None:
            payload["after"] = after
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

    def test_tag_push_is_skipped(self):
        # GitHub delivers tag pushes as regular push events: even when
        # the tag name and the commit messages reference tasks, nothing
        # must be tracked (the parser remaps them onto the handlerless
        # tag_push type, the one GitLab tag pushes carry natively)
        commits = [self._commit("d" * 40, "GH-100 commit carried by the tag")]
        payload = self._push_payload(ref="refs/tags/GH-100-rc1", commits=commits)
        event = self._dispatch(payload, "github")

        self.assertEqual(event["project_git_event_type"], "tag_push")
        self.assertFalse(self._get_branch("refs/tags/GH-100-rc1"))
        self.assertFalse(self._get_commit("d" * 40))

    def test_push_branch_name_match_links_branch_only(self):
        # Entities link by their own reference only: the branch name
        # matches GH-100 but the commit messages mention no task, so only
        # the branch is linked and the commits are not tracked.
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
        self.assertFalse(self.gh_task_100.git_commit_ids)
        for sha in ("a" * 40, "b" * 40, "c" * 40):
            self.assertFalse(self._get_commit(sha))
        self.assertFalse(self.gh_task_115.git_branch_ids)
        self.assertFalse(self.gh_task_no_pattern.git_branch_ids)

    def test_push_mixed_commit_messages_link_only_matching_commit(self):
        # Mirror of the GitLab mixed push scenario. Granular matching:
        # only the matching commit is linked to the task; the generic
        # branch and the unrelated commit are not tracked at all.
        commits = [
            self._commit("a" * 40, "GH-115 fix the docs"),
            self._commit("b" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "github")

        self.assertFalse(self._get_branch("develop"))
        self.assertFalse(self.gh_task_115.git_branch_ids)
        self.assertEqual(self.gh_task_115.git_commit_ids.mapped("full_sha"), ["a" * 40])
        self.assertFalse(self._get_commit("b" * 40))
        self.assertFalse(self.gh_task_100.git_commit_ids)

    def test_push_commits_matching_different_tasks(self):
        # Push on a non-matching branch: two commits reference GH-100
        # (doubled to catch singleton errors in the matching logic), one
        # references GH-115, one references nothing. Granular matching:
        # each task is linked only to its own commit(s), without branch
        # (see the GitLab mirror test).
        commits = [
            self._commit("a" * 40, "GH-100 part one"),
            self._commit("b" * 40, "GH-100 part two"),
            self._commit("c" * 40, "GH-115 side fix"),
            self._commit("d" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "github")

        self.assertFalse(self._get_branch("develop"))
        self.assertEqual(
            set(self.gh_task_100.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40},
        )
        self.assertFalse(self.gh_task_100.git_branch_ids)
        self.assertEqual(self.gh_task_115.git_commit_ids.mapped("full_sha"), ["c" * 40])
        self.assertFalse(self.gh_task_115.git_branch_ids)
        self.assertFalse(self._get_commit("d" * 40))
        self.assertFalse(self.gh_task_no_pattern.git_commit_ids)

    def test_branch_creation_mixed_commits_links_branch_and_commits(self):
        # Branch creation carrying 4 commits: branch name matches GH-100,
        # two commits reference GH-100 (doubled to catch singleton errors),
        # one references GH-115, one references nothing. Each entity links
        # by its own reference: GH-100 gets the branch and its own commits,
        # GH-115 gets its commit only, the unrelated commit is not tracked.
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
        self.assertIn(branch.id, self.gh_task_100.git_branch_ids.ids)
        self.assertEqual(
            set(self.gh_task_100.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40},
        )
        self.assertFalse(self.gh_task_115.git_branch_ids)
        self.assertEqual(self.gh_task_115.git_commit_ids.mapped("full_sha"), ["c" * 40])
        self.assertFalse(self._get_commit("d" * 40))
        self.assertFalse(self.gh_task_no_pattern.git_commit_ids)
        # The tracked commits are correlated to their branch record
        self.assertEqual(
            set(branch.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40, "c" * 40},
        )

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

    def test_push_unrelated_repository_creates_nothing(self):
        commits = [self._commit("a" * 40, "GH-100 part one")]
        payload = self._push_payload(ref="refs/heads/GH-100-readme", commits=commits)
        payload["repository"]["html_url"] = "https://github.example.com/other/repo"
        self._dispatch(payload, "github")

        self.assertFalse(self._get_branch("GH-100-readme"))
        self.assertFalse(self._get_commit("a" * 40))

    def test_branch_deletion_keeps_branch_record(self):
        creation = self._push_payload(
            ref="refs/heads/GH-100-feature",
            commits=[],
            before=NULL_SHA,
            after="a" * 40,
        )
        self._dispatch(creation, "github")
        self.assertEqual(len(self._get_branch("GH-100-feature")), 1)

        deletion = self._push_payload(
            ref="refs/heads/GH-100-feature", commits=[], before="a" * 40, after=NULL_SHA
        )
        self._dispatch(deletion, "github")

        # Current behavior: the branch record is kept on deletion
        branch = self._get_branch("GH-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gh_task_100.git_branch_ids.ids)
