from odoo import api, fields, models


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def _read_group_status_ids(self, states, domain):
        # Retrieve all statuses to display them as column headers in the Kanban view.
        # limit=None is passed explicitly to avoid pylint W8163 (no-search-all).
        return states.search([], limit=None)

    project_status = fields.Many2one(
        comodel_name="project.status",
        group_expand="_read_group_status_ids",
        copy=False,
        ondelete="restrict",
        index=True,
    )
