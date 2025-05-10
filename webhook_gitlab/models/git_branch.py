from odoo import _, fields, models


class GitBranch(models.Model):
    _name = "git.branch"
    _description = "Git Branch"

    name = fields.Char(string="Branch Name")
    url = fields.Char(string="Branch URL")

    task_id = fields.Many2one(comodel_name="project.task", ondelete="cascade")
    git_request_id = fields.Many2one("git.request", string="Request related to the branch")

    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_branch_git_commit_rel",
        column1="git_branch_id",
        column2="git_commit_id",
        string="Commits",
    )
