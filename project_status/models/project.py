from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def _read_group_status_ids(self, states, domain):
        return states.search([], limit=None)

    project_status = fields.Many2one(
        comodel_name="project.status",
        group_expand="_read_group_status_ids",
        copy=False,
        ondelete="restrict",
        index=True,
    )
