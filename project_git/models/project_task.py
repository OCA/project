# Copyright 2018, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    git_branch_ids = fields.Many2many(
        comodel_name="project.git.branch",
        relation="project_git_branch_task_rel",
        string="Branches",
        column1="task_id",
        column2="branch_id",
    )
    git_commit_ids = fields.Many2many(
        comodel_name="project.git.commit",
        relation="project_git_commit_task_rel",
        string="Commits",
        column1="task_id",
        column2="commit_id",
    )
    git_pull_request_ids = fields.Many2many(
        comodel_name="project.git.pull.request",
        relation="project_git_pull_request_task_rel",
        string="Pull Requests",
        column1="task_id",
        column2="pull_request_id",
    )
    git_branch_count = fields.Integer(compute="_compute_git_counts")
    git_commit_count = fields.Integer(compute="_compute_git_counts")
    git_pull_request_count = fields.Integer(compute="_compute_git_counts")

    @api.depends("git_branch_ids", "git_commit_ids", "git_pull_request_ids")
    def _compute_git_counts(self):
        for task in self:
            task.git_branch_count = len(task.git_branch_ids)
            task.git_commit_count = len(task.git_commit_ids)
            task.git_pull_request_count = len(task.git_pull_request_ids)

    def _action_view_git_entities(self, action_xml_id, git_entities):
        """Open the given git entities reusing the module's list actions."""
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xml_id)
        action["domain"] = [("id", "in", git_entities.ids)]
        return action

    def action_view_git_branches(self):
        return self._action_view_git_entities(
            "project_git.action_project_git_branch", self.git_branch_ids
        )

    def action_view_git_commits(self):
        return self._action_view_git_entities(
            "project_git.action_project_git_commit", self.git_commit_ids
        )

    def action_view_git_pull_requests(self):
        return self._action_view_git_entities(
            "project_git.action_project_git_pull_request", self.git_pull_request_ids
        )
