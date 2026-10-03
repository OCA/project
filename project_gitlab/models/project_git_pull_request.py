# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProjectGitPullRequest(models.Model):
    _inherit = "project.git.pull.request"

    source = fields.Selection(selection_add=[("gitlab", "GitLab")])

    def _is_pr_opening_gitlab(self, event):
        return event.get("object_attributes", {}).get("action") == "open"

    def _assign_tags_to_task_gitlab(self, task):
        """Align the MR/CI state tags of a single related task."""
        self.ensure_one()
        managed_tags = task.tag_ids.filtered(
            lambda t: t.name.startswith(("MR:", "CI:")) or t.name in ("Approved", "WIP")
        )
        prefix = "project_gitlab.project_tags_"
        tags_to_add = self.env.ref(prefix + self.state)
        if self.ci_status:
            tags_to_add |= self.env.ref(prefix + self.ci_status)
        if self.approved:
            tags_to_add |= self.env.ref(prefix + "approved")
        if self.wip:
            tags_to_add |= self.env.ref(prefix + "wip")
        self._replace_task_tags(task, managed_tags, tags_to_add)

    def _post_message_gitlab(self, message, event=None):
        """Post a comment (discussion) on the GitLab merge request.

        The event, when available, is the preferred source for the GitLab
        instance base URL (project.web_url is authoritative on any GitLab
        version). Without an event the URL falls back to the record MR
        URL, assuming the modern ``/-/merge_requests/`` layout.
        """
        if self:
            self.ensure_one()
            project_id, request_id = self.id_project, self.id_request
        else:
            project_id = event["project"]["id"]
            request_id = event["object_attributes"]["iid"]
        web_url = event["project"]["web_url"] if event else self.url.split("/-/")[0]
        gitlab_client = self.env["project.git.auth"]._connect_gitlab(url=web_url)
        project = gitlab_client.projects.get(project_id)
        merge_request = project.mergerequests.get(request_id)
        merge_request.discussions.create({"body": message})
        return True
