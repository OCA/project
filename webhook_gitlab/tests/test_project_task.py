# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import WebhookGitlabCase


class TestProjectTaskGitSmartButtons(WebhookGitlabCase):
    """Git entity counters and smart buttons on the task form (Task D UI
    layer): the buttons show the linked entity counts and open the
    module's list actions filtered on the linked records."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        task_link = [(4, cls.gl_task_100.id)]
        cls.git_branch = cls.env["git.branch"].create(
            {"name": "GL-100-feature", "task_ids": task_link}
        )
        cls.git_commits = cls.env["git.commit"].create(
            [
                {
                    "name": "GL-100 first change",
                    "full_sha": "a" * 40,
                    "task_ids": task_link,
                },
                {
                    "name": "GL-100 second change",
                    "full_sha": "b" * 40,
                    "task_ids": task_link,
                },
            ]
        )
        cls.git_pull_request = cls.env["git.pull.request"].create(
            {"name": "GL-100 feature", "task_ids": task_link}
        )

    def test_git_entity_counters(self):
        self.assertEqual(self.gl_task_100.git_branch_count, 1)
        self.assertEqual(self.gl_task_100.git_commit_count, 2)
        self.assertEqual(self.gl_task_100.git_pull_request_count, 1)
        # A task without linked entities keeps zeroed counters
        self.assertEqual(self.gl_task_115.git_branch_count, 0)
        self.assertEqual(self.gl_task_115.git_commit_count, 0)
        self.assertEqual(self.gl_task_115.git_pull_request_count, 0)

    def test_smart_buttons_open_linked_entities(self):
        for action, expected_entities, expected_model in (
            (
                self.gl_task_100.action_view_git_branches(),
                self.git_branch,
                "git.branch",
            ),
            (
                self.gl_task_100.action_view_git_commits(),
                self.git_commits,
                "git.commit",
            ),
            (
                self.gl_task_100.action_view_git_pull_requests(),
                self.git_pull_request,
                "git.pull.request",
            ),
        ):
            self.assertEqual(action["res_model"], expected_model)
            self.assertEqual(action["domain"], [("id", "in", expected_entities.ids)])
