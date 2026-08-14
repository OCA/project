# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import time

from odoo import api, models

_logger = logging.getLogger(__name__)


class ProjectGitEvent(models.Model):
    _inherit = "project.git.event"

    @api.model
    def _process_merge_request(self, event):
        """Process a GitLab Merge Request event."""
        return self._process_pull_request_event(event)

    @api.model
    def _process_pipeline(self, event):
        """Process pipeline status and update project.git.pull.request.
        The title must contain the type of registry and the ID preceded by a #
        sign.

        Ex. [IMP] project_git: new module task #1234
        """
        git_pull_request = (
            self.env["project.git.pull.request"]
            .sudo()
            .search(
                [
                    ("source_branch", "=", event["object_attributes"]["ref"]),
                    ("last_commit", "=", event["object_attributes"]["sha"]),
                ]
            )
        )

        if git_pull_request:
            git_pull_request.sudo().write(
                {
                    "ci_status": event["object_attributes"]["status"],
                }
            )
        return True

    def _extract_branch_names_from_event_gitlab(self, event):
        if event.get("project_git_event_type") == "merge_request":
            obj_attrs = event.get("object_attributes", {})
            return {
                "source_branch": obj_attrs.get("source_branch", ""),
                "target_branch": obj_attrs.get("target_branch", ""),
            }
        # push events carry the git-native ref
        return self._extract_branch_names_from_ref(event)

    def _extract_pr_title_from_event_gitlab(self, event):
        return event.get("object_attributes", {}).get("title", "")

    def _extract_pr_fallback_commits_gitlab(self, event):
        # A MR without commits yet carries last_commit: null
        last_commit = event.get("object_attributes", {}).get("last_commit")
        return [last_commit] if last_commit else []

    def _build_branch_url_gitlab(self, event, branch_name):
        web_url = event.get("project", {}).get("web_url", "")
        if not web_url:
            return ""
        # GitLab format: https://gitlab.com/owner/repo/-/tree/branch-name
        return f"{web_url}/-/tree/{branch_name}"

    @api.model
    def _convert_gitlab_commit_to_dict(self, commit, project=None):
        """Convert python-gitlab ProjectCommit object to dict format.

        Normalizes python-gitlab commit objects to the same dict structure
        used by webhooks for uniform handling.

        If any field is missing and project is provided, fetches full commit
        via API. In the latter case the commit is fetched with a small delay
        to stay within GitLab's rate limits (10 req/sec limit). This should
        avoid event handling failure when, ad example, a PR has 10+ commits.

        :param commit: python-gitlab ProjectCommit object
        :param project: python-gitlab Project object (optional, for full
            get() if needed)
        :return: dict with keys
        """

        # Use getattr for each field to detect missing data in case of lazy loading
        commit_id = getattr(commit, "id", None)
        message = getattr(commit, "message", None)
        title = getattr(commit, "title", None)
        url = getattr(commit, "web_url", None)
        timestamp = getattr(commit, "created_at", None)
        author_name = getattr(commit, "author_name", None)
        author_email = getattr(commit, "author_email", None)
        # If any field is missing and project available, fetch full commit
        if (
            any(
                field is None
                for field in [
                    commit_id,
                    message,
                    title,
                    url,
                    timestamp,
                    author_name,
                    author_email,
                ]
            )
            and project
        ):
            _logger.info(
                "Lazy-loaded commit missing fields, fetching full commit: %s",
                commit_id or "unknown",
            )
            commit = project.commits.get(commit.id)

            # Re-extract all fields from full commit
            commit_id = getattr(commit, "id", None)
            message = getattr(commit, "message", None)
            title = getattr(commit, "title", None)
            url = getattr(commit, "web_url", None)
            timestamp = getattr(commit, "created_at", None)
            author_name = getattr(commit, "author_name", None)
            author_email = getattr(commit, "author_email", None)

            # Throttle to respect rate gitlab limits (10 req/sec limit)
            time.sleep(0.3)

        return {
            "id": commit_id or "",
            "message": message or "",
            "title": title or "",
            "url": url or "",
            "timestamp": timestamp or "",
            # Extra fields for future use
            "author": {
                "name": author_name or "",
                "email": author_email or "",
            },
        }

    @api.model
    def _fetch_pr_commits_gitlab(self, event):
        """Fetch all commits from a GitLab MR and return a list(dict)
        containing commits data.

        :param dict event: The webhook event
        :return: list of commit dicts (same format as webhook)
        """
        commit_list = []
        try:
            gl = self.env["project.git.auth"]._connect_gitlab(
                url=event["project"]["web_url"]
            )

            project_id = event["project"]["id"]
            mr_iid = event["object_attributes"]["iid"]

            # Get MR and commits
            project = gl.projects.get(project_id)
            mr = project.mergerequests.get(mr_iid)

            # Convert commits into webooh event commit format
            for commit in mr.commits():
                commit_dict = self._convert_gitlab_commit_to_dict(
                    commit, project=project
                )
                commit_list.append(commit_dict)

        except Exception as e:
            # Log error but don't fail - fallback will handle it
            _logger.warning(f"Failed to fetch GitLab MR commits: {str(e)}")
        return commit_list

    def _prepare_commit_vals_gitlab(self, event, commit):
        # GitLab carries the commit title as its own field
        return {
            "name": commit.get("title", ""),
            "description": commit.get("message", ""),
        }

    @api.model
    def _prepare_pull_request_vals_gitlab(self, event, values=None):
        """Prepare GitLab merge request values from event for ORM write/create.

        :param dict event: The webhook event
        :param dict values: Optional dict with values to override/merge (e.g. "task_id")
        :return: dict of pull request values ready for create/write
        """
        values_by_arg = values or {}

        approved = False
        if event["object_attributes"]["action"] == "approved":
            approved = True
        # A MR without commits yet carries last_commit: null
        last_commit = event["object_attributes"].get("last_commit") or {}
        user = (
            self.env["res.users"]
            .sudo()
            .search([("gitlab_username", "=", event["user"]["username"])])
        )

        default_vals = {
            "id_request": event["object_attributes"]["iid"],
            "id_project": event["project"]["id"],
            "source": "gitlab",
            "name": event["object_attributes"]["title"],
            "description": event["object_attributes"].get("description", ""),
            "url": event["object_attributes"]["url"],
            "source_branch": event["object_attributes"]["source_branch"],
            "target_branch": event["object_attributes"]["target_branch"],
            "wip": event["object_attributes"]["work_in_progress"],
            "state": event["object_attributes"]["state"],
            "approved": approved,
            "last_commit": last_commit.get("id", ""),
            "user_id": user.id,
        }

        # Merge with values_by_arg (task_id, etc.)
        return {**default_vals, **values_by_arg}

    def _extract_pr_identifiers_gitlab(self, event):
        """Return the (id_project, id_request) pair identifying the MR."""
        return event["project"]["id"], event["object_attributes"]["iid"]
