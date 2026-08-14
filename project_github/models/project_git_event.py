# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ProjectGitEvent(models.Model):
    _inherit = "project.git.event"

    @api.model
    def _process_pull_request(self, event):
        """Process a GitHub Pull Request event."""
        return self._process_pull_request_event(event)

    def _extract_branch_names_from_event_github(self, event):
        """GitHub Pull Request form; push events carry the git-native ref."""
        if event.get("project_git_event_type") == "pull_request":
            pr_data = event.get("pull_request", {})
            return {
                "source_branch": pr_data.get("head", {}).get("ref", ""),
                "target_branch": pr_data.get("base", {}).get("ref", ""),
            }
        # push events carry the git-native ref
        return self._extract_branch_names_from_ref(event)

    def _extract_pr_title_from_event_github(self, event):
        return event.get("pull_request", {}).get("title", "")

    def _build_branch_url_github(self, event, branch_name):
        # Try to get from pull_request.head.repo first (PR events)
        html_url = (
            event.get("pull_request", {})
            .get("head", {})
            .get("repo", {})
            .get("html_url", "")
        )
        if not html_url:
            # Fallback to repository (push events)
            html_url = event.get("repository", {}).get("html_url", "")
        if not html_url:
            return ""
        # GitHub format: https://github.com/owner/repo/tree/branch-name
        return f"{html_url}/tree/{branch_name}"

    @api.model
    def _convert_pygithub_commit_to_dict(self, commit):
        """Convert PyGithub Commit object to dict format.

        Normalizes PyGithub commit objects to the same dict structure
        used by webhooks for uniform handling.

        :param commit: PyGithub Commit object
        :return: dict with keys: id, message, url, timestamp, author
        """
        return {
            "id": commit.sha,
            "message": commit.commit.message,
            "url": commit.html_url,
            "timestamp": commit.commit.author.date.isoformat()
            if commit.commit.author and commit.commit.author.date
            else "",
            # Extra fields for future use
            "author": {
                "name": commit.commit.author.name if commit.commit.author else "",
                "email": commit.commit.author.email if commit.commit.author else "",
            },
        }

    @api.model
    def _fetch_pr_commits_github(self, event):
        """Fetch all commits from a GitHub PR and return a list(dict)
        containing commits data.

        :param dict event: The webhook event
        :return: list of commit dicts (same format as webhook)
        """
        try:
            github = self.env["project.git.auth"]._connect_github()

            repo_full_name = event["repository"]["full_name"]  # "owner/repo"
            pr_number = event["number"]

            # Get PR and commits
            github_repo = github.get_repo(repo_full_name)
            pr = github_repo.get_pull(pr_number)

            # Convert PyGithub Commit objects to dicts (same format as webhook)
            commit_list = []
            for commit in pr.get_commits():
                commit_dict = self._convert_pygithub_commit_to_dict(commit)
                commit_list.append(commit_dict)

            return commit_list

        except Exception as e:
            # Log error but don't fail - fallback will handle it
            _logger.warning(f"Failed to fetch GitHub PR commits: {str(e)}")
            return []

    def _prepare_commit_vals_github(self, event, commit):
        # GitHub only carries the full message: derive title/description
        commit_text_lines = commit.get("message", "").split("\n", 1)
        return {
            "name": commit_text_lines[0][:60],
            "description": commit_text_lines[1] if len(commit_text_lines) > 1 else "",
        }

    @api.model
    def _prepare_pull_request_vals_github(self, event, values=None):
        """Prepare GitHub pull request values from event for ORM write/create.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values_by_arg = values or {}

        user = (
            self.env["res.users"]
            .sudo()
            .search(
                [
                    ("github_username", "=", event["pull_request"]["user"]["login"]),
                ],
                limit=1,
            )
        )
        # GitHub reports the merge with the "merged" boolean: a merged PR
        # still arrives with state "closed"
        map_state = {
            "open": "opened",
            "closed": "closed",
        }
        pr_state = (
            "merged"
            if event["pull_request"].get("merged")
            else map_state[event["pull_request"]["state"]]
        )

        default_vals = {
            "id_request": event["number"],
            "id_project": event["repository"]["id"],
            "source": "github",
            "name": event["pull_request"]["title"],
            "description": event["pull_request"].get("body", ""),
            "url": event["pull_request"]["html_url"],
            "source_branch": event["pull_request"]["head"]["ref"],
            "target_branch": event["pull_request"]["base"]["ref"],
            "state": pr_state,
            "last_commit": event["pull_request"]["head"]["sha"],
            "user_id": user.id,
        }

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    def _extract_pr_identifiers_github(self, event):
        """Return the (id_project, id_request) pair identifying the PR."""
        return event["repository"]["id"], event["number"]
