from dateutil.parser import isoparse
from datetime import timezone

from odoo import _, api, fields, models


class GitCommit(models.Model):
    _name = "git.commit"
    _description = "Git Commit"
    _order = "timestamp desc,id"

    name = fields.Char(string="Title")
    description = fields.Char(string="Description")
    url = fields.Char(string="Commit URL")
    full_sha = fields.Char(string="Full SHA")
    sha = fields.Char(string="SHA", compute="_compute_sha", store=True)
    timestamp = fields.Datetime(string="Timestamp")

    git_branch_id = fields.Many2one(comodel_name="git.branch")
    task_id = fields.Many2one(comodel_name="project.task", ondelete="cascade")
    git_request_id = fields.Many2one("git.request", string="Request related to the commit")

    @api.depends("full_sha")
    def _compute_sha(self):
        
        for commit in self:
            commit.sha = commit.full_sha[:7] if commit.full_sha else ""

    def parse_timestamp(self, timestamp):
        return isoparse(timestamp).astimezone(timezone.utc).replace(tzinfo=None) if timestamp else False
