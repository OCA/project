# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from .common import GITHUB_REPO_URL, GITLAB_REPO_URL, WebhookGitlabCase


class TestTaskMatching(WebhookGitlabCase):
    """Platform-agnostic tests for the task matching logic and its
    configuration (no webhook payload involved)."""

    def test_task_id_reference_to_missing_task_is_ignored(self):
        # Outside PR/MR titles (which warn on the platform), a broken
        # explicit reference is silently skipped
        missing_id = (
            self.env["project.task"].search([], order="id desc", limit=1).id + 1000
        )
        matching_tasks = self.git_event._find_matching_tasks(
            projects=self.gitlab_project, pattern_text=f"tid#{missing_id} quick fix"
        )
        self.assertFalse(matching_tasks)

    def test_repository_matching_by_dev_project_url(self):
        # git_dev_project_url is an alternative mapping surface,
        # equivalent to git_project_url for repository matching
        dev_project = self.env["project.project"].create(
            {
                "name": "Dev Mirror Repo",
                "git_dev_project_url": "https://gitlab.example.com/acme/demo-dev-repo",
            }
        )
        repository_projects = self.git_event._get_related_projects_by_url(
            event={
                "repository_url": "https://gitlab.example.com/acme/demo-dev-repo.git"
            }
        )
        self.assertEqual(repository_projects, dev_project)

    def test_repository_matching_handles_git_suffix_variants(self):
        # gitlab_project is stored with the ".git" suffix, github_project
        # without: each must match the event URL spelled the other way
        repository_projects = self.git_event._get_related_projects_by_url(
            event={"repository_url": GITLAB_REPO_URL}
        )
        self.assertEqual(repository_projects, self.gitlab_project)
        repository_projects = self.git_event._get_related_projects_by_url(
            event={"repository_url": f"{GITHUB_REPO_URL}.git"}
        )
        self.assertEqual(repository_projects, self.github_project)

    def test_task_name_search_is_case_insensitive(self):
        # The extracted key is searched in the task names ignoring case,
        # as a task naming tolerance (the extraction stays strict)
        lowercase_task = self.env["project.task"].create(
            {
                "name": "gl-140 lowercase named task",
                "project_id": self.gitlab_project.id,
            }
        )
        matching_tasks = self.git_event._find_matching_tasks(
            projects=self.gitlab_project, pattern_text="GL-140 fix the export"
        )
        self.assertEqual(matching_tasks, lowercase_task)

    def test_closed_tasks_are_matched(self):
        # A key referencing a done/canceled task still links the git
        # activity: pushing further commits on a task already marked
        # as done is a common human pipeline slip
        done_task = self.env["project.task"].create(
            {
                "name": "GL-155 already done task",
                "project_id": self.gitlab_project.id,
                "state": "1_done",
            }
        )
        matching_tasks = self.git_event._find_matching_tasks(
            projects=self.gitlab_project, pattern_text="GL-155 hotfix after close"
        )
        self.assertEqual(matching_tasks, done_task)
