# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import timezone

from dateutil.parser import isoparse

from odoo import api, fields, models


class ProjectGitCommit(models.Model):
    _name = "project.git.commit"
    _description = "Git Commit"
    _order = "timestamp desc,id"

    name = fields.Char(string="Title")
    description = fields.Char()
    url = fields.Char(string="Commit URL")
    full_sha = fields.Char(string="Full SHA")
    sha = fields.Char(string="SHA", compute="_compute_sha", store=True)
    timestamp = fields.Datetime()

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_git_commit_task_rel",
        column1="commit_id",
        column2="task_id",
        string="Related Tasks",
    )
    git_branch_ids = fields.Many2many(
        comodel_name="project.git.branch",
        relation="project_git_branch_commit_rel",
        column1="commit_id",
        column2="branch_id",
        string="Branches",
    )
    git_pull_request_ids = fields.Many2many(
        comodel_name="project.git.pull.request",
        relation="project_git_pull_request_commit_rel",
        column1="commit_id",
        column2="pull_request_id",
        string="Pull Requests",
    )

    @api.depends("full_sha")
    def _compute_sha(self):
        for commit in self:
            commit.sha = commit.full_sha[:7] if commit.full_sha else ""

    def parse_timestamp(self, timestamp):
        return (
            isoparse(timestamp).astimezone(timezone.utc).replace(tzinfo=None)
            if timestamp
            else False
        )
