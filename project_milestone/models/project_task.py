# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    milestone_id = fields.Many2one(
        "project.milestone",
        string="Milestone",
        group_expand="_read_group_milestone_ids",
        domain="[('project_id', '=', project_id)]",
    )
    use_milestones = fields.Boolean(
        related="project_id.use_milestones", help="Does this project use milestones?"
    )
    milestones_required = fields.Boolean(
        related="project_id.milestones_required",
    )

    @api.model
    def _read_group_milestone_ids(self, milestone_ids, domain, order):
        if "default_project_id" in self.env.context:
            milestone_ids = self.env["project.milestone"].search(
                [("project_id", "=", self.env.context["default_project_id"])]
            )
        return milestone_ids

    @api.model
    def create(self, vals):
        if self.env.context.get("default_parent_id", False):
            parent_task = self.browse(self.env.context.get("default_parent_id"))

            if parent_task.milestone_id:
                vals.update(
                    {
                        "milestone_id": parent_task.milestone_id.id,
                    }
                )
        res = super(ProjectTask, self).create(vals)

        return res

    @api.onchange("parent_id")
    def _onchange_parent_id_milestone(self):
        if self.parent_id and self.parent_id.milestone_id:
            self.milestone_id = self.parent_id.milestone_id.id
        else:
            self.milestone_id = False
