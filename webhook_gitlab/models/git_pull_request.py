# Copyright 2020, Jarsa
# Copyright 2026 Francesco Ballerini
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class GitPullRequest(models.Model):
    _name = "git.pull.request"
    _description = "Git Pull/Merge Request"

    name = fields.Char(string="Title")
    description = fields.Text(string="Description")
    url = fields.Char(string="PR/MR URL")

    id_request = fields.Integer(
        string="Request ID",
        help="Technical field used to track the merge request id"
    )
    id_project = fields.Integer(
        string="Project ID",
        help="Technical field used to track the project id in Gitlab",
    )
    source = fields.Selection(
        [("gitlab", "GitLab"), ("github", "GitHub")],
        string="Source Platform"
    )

    source_branch = fields.Char(string="Source Branch")
    target_branch = fields.Char(string="Target Branch")

    state = fields.Selection(
        [
            ("opened", "Opened"),
            ("merged", "Merged"),
            ("closed", "Closed"),
            ("locked", "Locked"),
        ]
    )
    ci_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("running", "Running"),
            ("success", "Success"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
            ("canceled", "Canceled"),
            ("unknown", "Unknown"),
        ],
        default="pending",
        string="CI Status",
    )

    wip = fields.Boolean(string="WIP")
    approved = fields.Boolean()

    last_commit = fields.Char()
    user_id = fields.Many2one("res.users", string="Created by User")
    task_id = fields.Many2one(
        comodel_name="project.task",
        string="Related Task",
        ondelete="cascade"
    )

    git_commit_ids = fields.Many2many(
        comodel_name="git.commit",
        relation="git_pull_request_git_commit_rel",
        column1="git_pull_request_id",
        column2="git_commit_id",
        string="Commits",
    )

    def open_merge_request(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": self.url,
        }

    @api.model_create_multi
    def create(self, vals_list):
        rec = super().create(vals_list)
        rec.assign_tags()
        return rec

    def write(self, vals):
        res = super().write(vals)
        self.assign_tags()
        return res

    def assign_tags(self):
        for rec in self:
            if not rec.task_id or not rec.state:
                continue
            tags = []
            record = rec.task_id
            tag_model = record.tag_ids._name
            current_tags = self.env[tag_model]
            current_tags |= record.tag_ids.filtered(lambda t: t.name.startswith("MR:") or t.name.startswith("CI:"))
            for tag in current_tags:
                tags.append((3, tag.id, 0))
            # Create prefix to have a base to get the external ID.
            # Possible values of prefix:
            # 'webhook_gitlab.project_tags_'
            prefix = "webhook_gitlab." + tag_model.replace(".", "_") + "_"
            # Get CI status tag.
            if rec.ci_status:
                tags.append((4, self.env.ref(prefix + rec.ci_status).id, 0))
            # Get MR state tag.
            tags.append((4, self.env.ref(prefix + rec.state).id, 0))
            if rec.approved:
                tags.append((4, self.env.ref(prefix + "approved").id, 0))
            else:
                tags.append((3, self.env.ref(prefix + "approved").id, 0))
            if rec.wip:
                tags.append((4, self.env.ref(prefix + "wip").id, 0))
            else:
                tags.append((3, self.env.ref(prefix + "wip").id, 0))
            record.write(
                {
                    "tag_ids": tags,
                }
            )
