# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class GitBranch(models.Model):
    _name = "git.branch"
    _description = "Git Branch"

    name = fields.Char(string="Branch Name")
    url = fields.Char(string="Branch URL")

    task_ids = fields.Many2many(
        comodel_name="project.task",
        relation="git_branch_project_task_rel",
        column1="git_branch_id",
        column2="project_task_id",
        string="Related Tasks",
    )

    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_branch_git_commit_rel",
        column1="git_branch_id",
        column2="git_commit_id",
        string="Commits",
    )
    git_pull_request_ids = fields.One2many(
        comodel_name="git.pull.request",
        inverse_name="source_branch_id",
        string="Pull Requests",
    )
