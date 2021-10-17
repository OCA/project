from odoo import fields, models, api


class ProjectState(models.Model):
    _inherit = "project.project"
    _name = "project.project"

    pr_state_default = fields.Selection(
        selection=lambda self: self.env['project.task']._selection_pr_state(),
        string="PR State default")
