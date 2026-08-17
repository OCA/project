# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProjectGitBranch(models.Model):
    _name = "project.git.branch"
    _description = "Git Branch"

    name = fields.Char(string="Branch Name")
    url = fields.Char(string="Branch URL")

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="project_git_branch_task_rel",
        column1="branch_id",
        column2="task_id",
        string="Related Tasks",
    )

    git_commit_ids = fields.Many2many(
        comodel_name="project.git.commit",
        relation="project_git_branch_commit_rel",
        column1="branch_id",
        column2="commit_id",
        string="Commits",
    )
    git_pull_request_ids = fields.One2many(
        comodel_name="project.git.pull.request",
        inverse_name="source_branch_id",
        string="Pull Requests",
    )

    _sql_constraints = [
        (
            "url_unique",
            "unique(url)",
            "A branch with the same URL is already tracked.",
        )
    ]
