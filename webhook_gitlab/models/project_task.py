# Copyright 2018, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    git_request_ids = fields.One2many("git.request", "task_id", string="Merge Requests")
    git_branch_ids = fields.Many2many(
        comodel_name="git.branch",
        string="Branches",
        column1="project_task_id",
        column2="git_branch_id",
    )
    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        string="Branches",
        column1="project_task_id",
        column2="git_commit_id",
    )
