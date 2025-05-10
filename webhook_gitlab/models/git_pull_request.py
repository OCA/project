from odoo import _, fields, models


class GitPullRequest(models.Model):
    _name = "git.pull.request"
    _description = "Git Pull/Merge Request"

    name = fields.Char(string="Title")
    description = fields.Text(string="Description")
    url = fields.Char(string="PR/MR URL")
    task_id = fields.Many2one(comodel_name="project.task", string="Related Task")
    git_request_id = fields.Many2one("git.request", string="Git Request")

    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_pull_request_git_commit_rel",
        column1="git_pull_request_id",
        column2="git_commit_id",
        string="Commits",
    )

    # I leave some fields here commented: at the moment we only
    # link the PR to the task if match by task name pattern, by
    # providing an URL so you can directly open the PR on github.
    # In future we could store more information and keep the info
    # synchronized with cron jobs

    # source_branch = fields.Char(string="Source Branch")
    # target_branch = fields.Char(string="Target Branch")
    # full_sha = fields.Char(string="Commit SHA")  # final SHA after merge or from last commit

    # state = fields.Selection([
    #     ("opened", "Opened"),
    #     ("closed", "Closed"),
    #     ("merged", "Merged"),
    # ], string="Status")

    # created_at = fields.Datetime(string="Created At")
    # merged_at = fields.Datetime(string="Merged At")
    # closed_at = fields.Datetime(string="Closed At")

    # author_id = fields.Many2one("res.partner", string="Author")
    # reviewer_ids = fields.Many2many("res.partner", string="Reviewers")

    # git_commit_ids = fields.One2many("git.commit", "git_pull_request_id", string="Commits")

    # id_request = fields.Char(string="External ID")  # eg: number of MR in GitLab
    # project_id = fields.Char(string="External Project ID")
    # repository_url = fields.Char(string="Repository URL")

