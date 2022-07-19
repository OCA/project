# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    milestone_ids = fields.One2many(
        "project.milestone", "project_id", string="Milestones", copy=True
    )
    use_milestones = fields.Boolean(help="Does this project use milestones?")

    milestones_required = fields.Boolean()

    @api.onchange("use_milestones")
    def _onchange_use_milestones(self):
        if not self.use_milestones and self.milestones_required:
            self.milestones_required = False
