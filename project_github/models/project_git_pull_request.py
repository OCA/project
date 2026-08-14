# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProjectGitPullRequest(models.Model):
    _inherit = "project.git.pull.request"

    source = fields.Selection(selection_add=[("github", "GitHub")])

    def _is_pr_opening_github(self, event):
        return event.get("action") == "opened"

    def _post_message_github(self, message, event=None):
        """Post a comment on the GitHub pull request"""
        if self:
            self.ensure_one()
            repository_id, request_id = self.id_project, self.id_request
        else:
            repository_id = event["repository"]["id"]
            request_id = event["number"]
        github = self.env["project.git.auth"]._connect_github()
        repo = github.get_repo(repository_id)
        pull = repo.get_pull(request_id)
        pull.create_issue_comment(message)
        return True
