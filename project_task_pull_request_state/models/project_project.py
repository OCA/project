from odoo import fields, models


class ProjectState(models.Model):
    _inherit = "project.project"

    pr_state_default = fields.Selection(
        selection=lambda self: self.env['project.task']._selection_pr_state(),
        string="Default PR Stare",
        help="Default PR state that will be set when PR URI is added to a task in this project"
        )
