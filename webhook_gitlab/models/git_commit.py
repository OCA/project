# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="git_commit_project_task_rel",
        column1="git_commit_id",
        column2="project_task_id",
        string="Related Tasks",
    )
    git_branch_ids = fields.Many2many(
        comodel_name="git.branch",
        relation="git_branch_git_commit_rel",
        column1="git_commit_id",
        column2="git_branch_id",
        string="Branches",
    )
    git_pull_request_ids = fields.Many2many(
        comodel_name="git.pull.request",
        relation="git_pull_request_git_commit_rel",
        column1="git_commit_id",
        column2="git_pull_request_id",
        string="Pull Requests",
    )

    @api.depends("full_sha")
    def _compute_sha(self):
        
        for commit in self:
            commit.sha = commit.full_sha[:7] if commit.full_sha else ""

    def parse_timestamp(self, timestamp):
        return isoparse(timestamp).astimezone(timezone.utc).replace(tzinfo=None) if timestamp else False
