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
        string="Commits",
        column1="project_task_id",
        column2="git_commit_id",
    )
    git_pull_request_ids = fields.Many2many(
        comodel_name="git.pull.request",
        string="Pull Requests",
        column1="project_task_id",
        column2="git_pull_request_id",
    )

    def _prepare_commit_vals(self, commit, event_source="gitlab"):
        """Prepare commit vals in the context of a project.task"""
        vals = {}
        timestamp = self.env["git.commit"].parse_timestamp(commit.get("timestamp", ""))
        if event_source == "gitlab":
            vals.update({
                "name": commit.get("title", ""),
                "description": commit.get("message", ""),
                "url": commit.get("url", ""),
                "full_sha": commit.get("id", ""),
                "task_id": self.id,
                "timestamp": timestamp,
            })
        elif event_source == "github":
            commit_text_lines = commit.get("message", "").split("\n", 1)
            commit_title = commit_text_lines[0][:60]
            commit_description = commit_text_lines[1] if len(commit_text_lines) > 1 else ""
            vals.update({
                "name": commit_title,
                "description": commit_description,
                "url": commit.get("url", ""),
                "full_sha": commit.get("id", ""),
                "task_id": self.id,
                "timestamp": timestamp,
            })
        return vals

    def _prepare_branch_vals(self, branch_name, branch_url=""):
        """Prepare branch vals in the context of a project.task"""
        return {
            "name": branch_name,
            "url": branch_url,
            "task_id": self.id,
        }

    def _prepare_pull_request_vals(self, pr_data, event_source="gitlab"):
        """Prepare pull request vals in the context of a project.task"""
        vals = {
            "task_id": self.id,
        }
        
        if event_source == "gitlab":
            vals.update({
                "name": pr_data.get("title", ""),
                "description": pr_data.get("description", ""),
                "url": pr_data.get("url", ""),
            })
        elif event_source == "github":
            vals.update({
                "name": pr_data.get("title", ""),
                "description": pr_data.get("body", ""),
                "url": pr_data.get("html_url", ""),
            })
        
        return vals
