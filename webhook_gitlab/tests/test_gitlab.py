# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .common import GITLAB_REPO_URL, NULL_SHA, WebhookGitlabCase


class TestGitlabPush(WebhookGitlabCase):
    def _push_payload(self, ref="refs/heads/main", commits=None, before=None, after=None):
        payload = self._load_payload("gitlab_push.json")
        payload["ref"] = ref
        if commits is not None:
            payload["commits"] = commits
            payload["total_commits_count"] = len(commits)
            if commits:
                payload["after"] = commits[-1]["id"]
                payload["checkout_sha"] = commits[-1]["id"]
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
            "title": message.split("\n", 1)[0],
            "timestamp": "2026-05-18T00:17:37+02:00",
            "url": f"{GITLAB_REPO_URL}/-/commit/{sha}",
            "author": {"name": "Demo User", "email": "demo@example.com"},
        }

    def test_push_branch_name_match_links_branch_only(self):
        # Entities link by their own reference only: the branch name
        # matches GL-100 but the commit messages mention no task, so only
        # the branch is linked and the commits are not tracked.
        commits = [
            self._commit("a" * 40, "generic commit one"),
            self._commit("b" * 40, "generic commit two"),
            self._commit("c" * 40, "generic commit three"),
        ]
        payload = self._push_payload(ref="refs/heads/GL-100-feature", commits=commits)
        self._dispatch(payload, "gitlab")

        branch = self._get_branch("GL-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertEqual(branch.url, f"{GITLAB_REPO_URL}/-/tree/GL-100-feature")
        self.assertIn(branch.id, self.gl_task_100.git_branch_ids.ids)
        self.assertFalse(self.gl_task_100.git_commit_ids)
        for sha in ("a" * 40, "b" * 40, "c" * 40):
            self.assertFalse(self._get_commit(sha))
        # Tasks not referenced by the branch name are untouched
        self.assertFalse(self.gl_task_115.git_branch_ids)
        self.assertFalse(self.gl_task_no_pattern.git_branch_ids)

    def test_push_mixed_commit_messages_link_only_matching_commit(self):
        # Mixed push on a generic branch: one commit matches GL-115, the
        # other two do not match anything. Granular matching: only the
        # matching commit is linked to the task; the generic branch and
        # the unrelated commits are not tracked at all.
        commits = [
            self._commit("a" * 40, "GL-115 fix the bug"),
            self._commit("b" * 40, "unrelated commit"),
            self._commit("c" * 40, "another unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_branch("develop"))
        self.assertFalse(self.gl_task_115.git_branch_ids)
        self.assertEqual(self.gl_task_115.git_commit_ids.mapped("full_sha"), ["a" * 40])
        self.assertFalse(self._get_commit("b" * 40))
        self.assertFalse(self._get_commit("c" * 40))
        # Tasks never referenced stay untouched
        self.assertFalse(self.gl_task_100.git_commit_ids)
        self.assertFalse(self.gl_task_no_pattern.git_commit_ids)

    def test_push_commits_matching_different_tasks(self):
        # Push on a non-matching branch: two commits reference GL-100
        # (doubled to catch singleton errors in the matching logic), one
        # references GL-115, one references nothing. Granular matching:
        # each task is linked only to its own commit(s), without branch.
        commits = [
            self._commit("a" * 40, "GL-100 part one"),
            self._commit("b" * 40, "GL-100 part two"),
            self._commit("c" * 40, "GL-115 side fix"),
            self._commit("d" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_branch("develop"))
        self.assertEqual(
            set(self.gl_task_100.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40},
        )
        self.assertFalse(self.gl_task_100.git_branch_ids)
        self.assertEqual(self.gl_task_115.git_commit_ids.mapped("full_sha"), ["c" * 40])
        self.assertFalse(self.gl_task_115.git_branch_ids)
        self.assertFalse(self._get_commit("d" * 40))
        self.assertFalse(self.gl_task_no_pattern.git_commit_ids)

    def test_push_without_match_creates_nothing(self):
        commits = [
            self._commit("a" * 40, "generic commit one"),
            self._commit("b" * 40, "generic commit two"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_branch("develop"))
        self.assertFalse(self._get_commit("a" * 40))
        self.assertFalse(self._get_commit("b" * 40))

    def test_push_unrelated_repository_creates_nothing(self):
        payload = self._push_payload(ref="refs/heads/GL-100-feature")
        payload["project"]["git_http_url"] = "https://gitlab.example.com/other/repo.git"
        self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_branch("GL-100-feature"))

    def test_push_commit_mentioning_two_tasks_links_both(self):
        # Every pattern occurrence in a text is matched, so a commit
        # message mentioning two tasks links the commit to both.
        commits = [self._commit("a" * 40, "GL-100 GL-115 combined fix")]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        self.assertEqual(self.gl_task_100.git_commit_ids.mapped("full_sha"), ["a" * 40])
        self.assertEqual(self.gl_task_115.git_commit_ids.mapped("full_sha"), ["a" * 40])

    def test_push_is_idempotent(self):
        commits = [
            self._commit("a" * 40, "GL-100 commit one"),
            self._commit("b" * 40, "GL-100 commit two"),
        ]
        payload = self._push_payload(ref="refs/heads/GL-100-feature", commits=commits)
        self._dispatch(payload, "gitlab")
        self._dispatch(payload, "gitlab")

        branch = self._get_branch("GL-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertEqual(len(self._get_commit("a" * 40)), 1)
        self.assertEqual(len(self._get_commit("b" * 40)), 1)
        self.assertEqual(len(self.gl_task_100.git_commit_ids), 2)
        self.assertEqual(len(self.gl_task_100.git_branch_ids), 1)
        # Entity correlations are established once, without duplicates
        self.assertEqual(
            set(branch.git_commit_ids.mapped("full_sha")), {"a" * 40, "b" * 40}
        )
        self.assertEqual(self._get_commit("a" * 40).git_branch_ids, branch)

    def test_branch_creation_with_branch_name_match(self):
        payload = self._push_payload(
            ref="refs/heads/GL-100-feature", commits=[], before=NULL_SHA
        )
        payload["after"] = "a" * 40
        self._dispatch(payload, "gitlab")

        branch = self._get_branch("GL-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gl_task_100.git_branch_ids.ids)
        self.assertFalse(self.gl_task_100.git_commit_ids)

    def test_branch_creation_mixed_commits_links_branch_and_commits(self):
        # Branch creation carrying 4 commits: branch name matches GL-100,
        # two commits reference GL-100 (doubled to catch singleton errors),
        # one references GL-115, one references nothing. Each entity links
        # by its own reference: GL-100 gets the branch and its own commits,
        # GL-115 gets its commit only, the unrelated commit is not tracked.
        commits = [
            self._commit("a" * 40, "GL-100 part one"),
            self._commit("b" * 40, "GL-100 part two"),
            self._commit("c" * 40, "GL-115 side fix"),
            self._commit("d" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(
            ref="refs/heads/GL-100-feature", commits=commits, before=NULL_SHA
        )
        self._dispatch(payload, "gitlab")

        branch = self._get_branch("GL-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gl_task_100.git_branch_ids.ids)
        self.assertEqual(
            set(self.gl_task_100.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40},
        )
        self.assertFalse(self.gl_task_115.git_branch_ids)
        self.assertEqual(self.gl_task_115.git_commit_ids.mapped("full_sha"), ["c" * 40])
        self.assertFalse(self._get_commit("d" * 40))
        self.assertFalse(self.gl_task_no_pattern.git_commit_ids)
        # The tracked commits are correlated to their branch record
        self.assertEqual(
            set(branch.git_commit_ids.mapped("full_sha")),
            {"a" * 40, "b" * 40, "c" * 40},
        )

    def test_branch_creation_without_match_creates_nothing(self):
        payload = self._push_payload(ref="refs/heads/develop", commits=[], before=NULL_SHA)
        payload["after"] = "a" * 40
        self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_branch("develop"))

    def test_branch_deletion_keeps_branch_record(self):
        creation = self._push_payload(
            ref="refs/heads/GL-100-feature", commits=[], before=NULL_SHA
        )
        creation["after"] = "a" * 40
        self._dispatch(creation, "gitlab")
        self.assertEqual(len(self._get_branch("GL-100-feature")), 1)

        deletion = self._push_payload(
            ref="refs/heads/GL-100-feature", commits=[], before="a" * 40, after=NULL_SHA
        )
        self._dispatch(deletion, "gitlab")

        # Current behavior: the branch record is kept on deletion
        branch = self._get_branch("GL-100-feature")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gl_task_100.git_branch_ids.ids)

    def test_push_invalid_key_formats_do_not_match(self):
        # The default extraction follows the key format: two or more
        # UPPERCASE letters, a hyphen, digits. A lowercase key, a
        # single-letter key and a technical token like "utf-8" extract no
        # pattern - even when a task name contains the same token.
        self.env["project.task"].create(
            {
                "name": "GL-130 utf-8 export support",
                "project_id": self.gitlab_project.id,
            }
        )
        commits = [
            self._commit("a" * 40, "convert export to utf-8"),
            self._commit("b" * 40, "T-34 single letter key"),
            self._commit("c" * 40, "gl-100 lowercase key"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        for sha in ("a" * 40, "b" * 40, "c" * 40):
            self.assertFalse(self._get_commit(sha))
        self.assertFalse(self.gl_task_100.git_commit_ids)

    def test_push_commit_task_id_reference_links_commit(self):
        # An explicit taskid#/tid# reference resolves by database id: it
        # links a task with no pattern in its name, following the same
        # granular rules (only the referencing commit, no branch)
        commits = [
            self._commit("a" * 40, f"tid#{self.gl_task_no_pattern.id} quick fix"),
            self._commit("b" * 40, "unrelated commit"),
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        self._dispatch(payload, "gitlab")

        self.assertEqual(
            self.gl_task_no_pattern.git_commit_ids.mapped("full_sha"), ["a" * 40]
        )
        self.assertFalse(self.gl_task_no_pattern.git_branch_ids)
        self.assertFalse(self._get_commit("b" * 40))

    def test_push_task_id_reference_ignores_repository_mapping(self):
        # The id reference is global: it links tasks of projects not
        # related to the repository, and keeps working even when the
        # repository is not mapped to any Odoo project at all.
        commits = [
            self._commit("a" * 40, f"taskid#{self.gh_task_no_pattern.id} cross fix")
        ]
        payload = self._push_payload(ref="refs/heads/develop", commits=commits)
        payload["project"]["git_http_url"] = "https://gitlab.example.com/other/repo.git"
        self._dispatch(payload, "gitlab")

        self.assertEqual(
            self.gh_task_no_pattern.git_commit_ids.mapped("full_sha"), ["a" * 40]
        )

    def test_branch_creation_task_id_reference_links_branch(self):
        payload = self._push_payload(
            ref=f"refs/heads/tid#{self.gl_task_no_pattern.id}-fix",
            commits=[],
            before=NULL_SHA,
        )
        payload["after"] = "a" * 40
        self._dispatch(payload, "gitlab")

        branch = self._get_branch(f"tid#{self.gl_task_no_pattern.id}-fix")
        self.assertEqual(len(branch), 1)
        self.assertIn(branch.id, self.gl_task_no_pattern.git_branch_ids.ids)


class TestGitlabMergeRequest(WebhookGitlabCase):
    # Standard set of commits returned by the mocked MR commit fetch:
    # two matching the title task (GL-100, doubled to catch singleton
    # errors in the matching logic), one referencing another task
    # (GL-115), one generic.
    MIXED_MR_COMMITS = [
        {"sha": "c" * 40, "message": "GL-100 mr commit one"},
        {"sha": "d" * 40, "message": "GL-100 mr commit two"},
        {"sha": "e" * 40, "message": "GL-115 unrelated fix"},
        {"sha": "f" * 40, "message": "generic commit"},
    ]

    def _mr_payload(self, title=None, source_branch=None):
        payload = self._load_payload("gitlab_merge_request.json")
        if title is not None:
            payload["object_attributes"]["title"] = title
        if source_branch is not None:
            payload["object_attributes"]["source_branch"] = source_branch
        return payload

    def test_mr_pattern_match_on_title_links_pr_branch_and_commits(self):
        payload = self._mr_payload(title="GL-100 add new file")
        patcher, merge_request = self._mock_gitlab_client(commits=self.MIXED_MR_COMMITS)
        with patcher:
            self._dispatch(payload, "gitlab")

        pull_request = self._get_pull_request(payload["object_attributes"]["url"])
        self.assertEqual(len(pull_request), 1)
        self.assertEqual(pull_request.source, "gitlab")
        self.assertEqual(pull_request.state, "opened")
        self.assertEqual(pull_request.source_branch, "merge-req-branch")
        self.assertEqual(pull_request.target_branch, "main")
        self.assertIn(pull_request.id, self.gl_task_100.git_pull_request_ids.ids)

        branch = self._get_branch("merge-req-branch")
        self.assertEqual(len(branch), 1)
        self.assertEqual(branch.url, f"{GITLAB_REPO_URL}/-/tree/merge-req-branch")
        self.assertIn(branch.id, self.gl_task_100.git_branch_ids.ids)

        # Commits link by their own message only: the title-matched task
        # gets just the commits that mention it
        self.assertEqual(
            set(self.gl_task_100.git_commit_ids.mapped("full_sha")),
            {"c" * 40, "d" * 40},
        )
        self.assertFalse(self._get_commit("f" * 40))
        # The tracked entities are correlated with each other: the MR with
        # its source branch record and every tracked commit with both
        self.assertEqual(pull_request.source_branch_id, branch)
        tracked_shas = {"c" * 40, "d" * 40, "e" * 40}
        self.assertEqual(
            set(pull_request.git_commit_ids.mapped("full_sha")), tracked_shas
        )
        self.assertEqual(
            set(branch.git_commit_ids.mapped("full_sha")), tracked_shas
        )
        # Each matched task (GL-100 by title, GL-115 by commit message) is
        # notified once on the MR with its Odoo link
        self.assertEqual(merge_request.discussions.create.call_count, 2)
        for call in merge_request.discussions.create.call_args_list:
            self.assertIn("Linked to Odoo task", call[0][0]["body"])

    def test_mr_commit_message_match_links_mr_branch_and_commit(self):
        # A fetched commit referencing GL-115 links the MR and that commit
        # to the task, plus the source branch (a PR is linked when one of
        # its commits mentions the task, and the source branch follows the
        # linked PR). The other MR commits stay unrelated to GL-115.
        payload = self._mr_payload(title="GL-100 add new file")
        patcher, _merge_request = self._mock_gitlab_client(commits=self.MIXED_MR_COMMITS)
        with patcher:
            self._dispatch(payload, "gitlab")

        pull_request = self._get_pull_request(payload["object_attributes"]["url"])
        self.assertIn(pull_request.id, self.gl_task_115.git_pull_request_ids.ids)
        branch = self._get_branch("merge-req-branch")
        self.assertIn(branch.id, self.gl_task_115.git_branch_ids.ids)
        self.assertEqual(self.gl_task_115.git_commit_ids.mapped("full_sha"), ["e" * 40])
        self.assertFalse(self.gl_task_no_pattern.git_pull_request_ids)
        # The commit-matched commit is correlated to the MR and the branch
        git_commit = self._get_commit("e" * 40)
        self.assertEqual(git_commit.git_pull_request_ids, pull_request)
        self.assertEqual(git_commit.git_branch_ids, branch)

    def test_mr_pattern_match_on_source_branch(self):
        payload = self._mr_payload(source_branch="GL-115-fix")
        patcher, _merge_request = self._mock_gitlab_client(
            commits=[{"sha": "c" * 40, "message": "generic commit"}]
        )
        with patcher:
            self._dispatch(payload, "gitlab")

        pull_request = self._get_pull_request(payload["object_attributes"]["url"])
        self.assertIn(pull_request.id, self.gl_task_115.git_pull_request_ids.ids)
        branch = self._get_branch("GL-115-fix")
        self.assertIn(branch.id, self.gl_task_115.git_branch_ids.ids)
        # The MR commit does not mention any task: it is not tracked
        self.assertFalse(self.gl_task_115.git_commit_ids)
        self.assertFalse(self._get_commit("c" * 40))
        # The other tasks are untouched
        self.assertFalse(self.gl_task_100.git_pull_request_ids)

    def test_mr_task_id_reference_in_title_links_pr_and_posts_message(self):
        payload = self._mr_payload(title=f"Add new file taskid#{self.gl_task_no_pattern.id}")
        patcher, merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")

        pull_request = self._get_pull_request(payload["object_attributes"]["url"])
        self.assertEqual(len(pull_request), 1)
        self.assertEqual(pull_request.task_ids, self.gl_task_no_pattern)
        self.assertIn(
            pull_request.id, self.gl_task_no_pattern.git_pull_request_ids.ids
        )
        merge_request.discussions.create.assert_called_once()
        message_body = merge_request.discussions.create.call_args[0][0]["body"]
        self.assertIn("Linked to Odoo task", message_body)

    def test_mr_commit_fetch_failure_falls_back_to_last_commit(self):
        # When the commit fetch fails, the head commit carried by the
        # payload is the only message-matching source left: here it
        # mentions GL-115, so it gets linked to that task.
        payload = self._mr_payload(title="GL-100 add new file")
        payload["object_attributes"]["last_commit"]["message"] = "GL-115 hotfix"
        patcher, merge_request = self._mock_gitlab_client()
        merge_request.commits.side_effect = Exception("API not available")
        with patcher:
            self._dispatch(payload, "gitlab")

        last_commit_sha = payload["object_attributes"]["last_commit"]["id"]
        self.assertEqual(
            self.gl_task_115.git_commit_ids.mapped("full_sha"), [last_commit_sha]
        )
        self.assertFalse(self.gl_task_100.git_commit_ids)

    def test_mr_processed_twice_does_not_duplicate_records(self):
        payload = self._mr_payload(title="GL-100 add new file")
        patcher, merge_request = self._mock_gitlab_client(commits=self.MIXED_MR_COMMITS)
        with patcher:
            self._dispatch(payload, "gitlab")
            self._dispatch(payload, "gitlab")

        pull_request = self._get_pull_request(payload["object_attributes"]["url"])
        self.assertEqual(len(pull_request), 1)
        self.assertEqual(len(self._get_branch("merge-req-branch")), 1)
        for sha in ("c" * 40, "d" * 40, "e" * 40):
            self.assertEqual(len(self._get_commit(sha)), 1)
        self.assertFalse(self._get_commit("f" * 40))
        self.assertEqual(len(self.gl_task_100.git_commit_ids), 2)
        # Entity correlations are not duplicated either
        self.assertEqual(len(pull_request.git_commit_ids), 3)
        self.assertEqual(pull_request.source_branch_id, self._get_branch("merge-req-branch"))
        # The task link message is posted only once per matched task
        # (GL-100 by title, GL-115 by commit message - anti-spam tracking)
        self.assertEqual(merge_request.discussions.create.call_count, 2)

    def test_mr_state_tags_are_assigned_to_task(self):
        payload = self._mr_payload(title="GL-100 add new file")
        patcher, _merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")

        tag_names = self.gl_task_100.tag_ids.mapped("name")
        self.assertIn("MR: Opened", tag_names)

    def test_post_message_without_event_connects_via_record_url(self):
        # Without an event the GitLab connection URL falls back to the
        # record MR URL (modern /-/merge_requests/ layout); the event,
        # when present, stays the preferred source.
        pull_request = self.env["git.pull.request"].create(
            {
                "name": "GL-100 fallback",
                "source": "gitlab",
                "url": f"{GITLAB_REPO_URL}/-/merge_requests/7",
                "id_request": 7,
                "id_project": 1001,
                "state": "opened",
            }
        )
        patcher, merge_request = self._mock_gitlab_client()
        with patcher as connect_gitlab:
            pull_request._post_message("fallback message")

        self.assertEqual(connect_gitlab.call_args.kwargs.get("url"), GITLAB_REPO_URL)
        merge_request.discussions.create.assert_called_once_with(
            {"body": "fallback message"}
        )

    def test_mr_unrelated_repository_skips_pattern_matching(self):
        payload = self._mr_payload(title="GL-100 add new file")
        payload["project"]["git_http_url"] = "https://gitlab.example.com/other/repo.git"
        patcher, merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_pull_request(payload["object_attributes"]["url"]))
        self.assertFalse(self.gl_task_100.git_pull_request_ids)
        # No negative-result message is posted on the MR
        merge_request.discussions.create.assert_not_called()

    def test_mr_without_match_creates_nothing_but_warns_once(self):
        # Known repository but no reference anywhere: the MR is
        # not tracked and the "no task reference" warning is posted on
        # opening only, never again on later update events (anti-spam).
        payload = self._mr_payload(title="Generic title")
        patcher, merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")
            payload["object_attributes"]["action"] = "update"
            self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_pull_request(payload["object_attributes"]["url"]))
        self.assertFalse(self._get_branch("merge-req-branch"))
        merge_request.discussions.create.assert_called_once()
        message_body = merge_request.discussions.create.call_args[0][0]["body"]
        self.assertIn("WARNING", str(message_body))

    def test_mr_old_reference_formats_are_not_supported(self):
        # "task#<id>"/"t#<id>" belonged to the old title-only reference
        # format: they are no longer recognized (single unified format:
        # taskid#/tid#), so the MR is not tracked and the missing
        # reference warning is posted.
        payload = self._mr_payload(
            title=f"Add new file task#{self.gl_task_no_pattern.id}"
        )
        patcher, merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_pull_request(payload["object_attributes"]["url"]))
        self.assertFalse(self.gl_task_no_pattern.git_pull_request_ids)
        message_body = merge_request.discussions.create.call_args[0][0]["body"]
        self.assertIn("WARNING", str(message_body))

    def test_mr_task_id_reference_not_found_warns_once(self):
        # Explicit taskid#<id> reference to a non-existent task: the broken
        # reference is warned about on opening only, and nothing is created.
        missing_id = self.env["project.task"].search([], order="id desc", limit=1).id + 1000
        payload = self._mr_payload(title=f"Add new file taskid#{missing_id}")
        patcher, merge_request = self._mock_gitlab_client()
        with patcher:
            self._dispatch(payload, "gitlab")
            payload["object_attributes"]["action"] = "update"
            self._dispatch(payload, "gitlab")

        self.assertFalse(self._get_pull_request(payload["object_attributes"]["url"]))
        merge_request.discussions.create.assert_called_once()
        message_body = merge_request.discussions.create.call_args[0][0]["body"]
        self.assertIn("cannot be found", str(message_body))


class TestGitlabPipeline(WebhookGitlabCase):
    def test_pipeline_updates_pull_request_ci_status(self):
        pull_request = self.env["git.pull.request"].create(
            {
                "name": "GL-100 add new file",
                "url": f"{GITLAB_REPO_URL}/-/merge_requests/1",
                "id_request": 1,
                "id_project": 1001,
                "source": "gitlab",
                "source_branch": "merge-req-branch",
                "target_branch": "main",
                "state": "opened",
                "last_commit": "feedfacefeedfacefeedfacefeedfacefeedface",
                "task_ids": [(4, self.gl_task_100.id)],
            }
        )
        self.assertEqual(pull_request.ci_status, "pending")

        payload = self._load_payload("gitlab_pipeline.json")
        self._dispatch(payload, "gitlab")

        self.assertEqual(pull_request.ci_status, "success")

    def test_pipeline_without_matching_pull_request_does_nothing(self):
        pull_request = self.env["git.pull.request"].create(
            {
                "name": "GL-100 add new file",
                "url": f"{GITLAB_REPO_URL}/-/merge_requests/1",
                "id_request": 1,
                "id_project": 1001,
                "source": "gitlab",
                "source_branch": "merge-req-branch",
                "state": "opened",
                "last_commit": "feedfacefeedfacefeedfacefeedfacefeedface",
                "task_ids": [(4, self.gl_task_100.id)],
            }
        )
        payload = self._load_payload("gitlab_pipeline.json")
        payload["object_attributes"]["ref"] = "unknown-branch"
        self._dispatch(payload, "gitlab")

        self.assertEqual(pull_request.ci_status, "pending")
