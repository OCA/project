# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    git_branch_ids = fields.Many2many(
        comodel_name="git.branch",
        relation="git_branch_project_task_rel",
        string="Branches",
        column1="project_task_id",
        column2="git_branch_id",
    )
    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_commit_project_task_rel",
        string="Commits",
        column1="project_task_id",
        column2="git_commit_id",
    )
    git_pull_request_ids = fields.Many2many(
        comodel_name="git.pull.request",
        relation="git_pull_request_project_task_rel",
        string="Pull Requests",
        column1="project_task_id",
        column2="git_pull_request_id",
    )
