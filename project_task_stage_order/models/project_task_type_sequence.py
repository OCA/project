from odoo import fields, models


class ProjectTaskTypeSequence(models.Model):
    _name = "project.task.type.sequence"
    _description = "Task Stage order per Project"
    _order = "sequence"

    project_id = fields.Many2one("project.project", required=True, ondelete="cascade")
    stage_id = fields.Many2one("project.task.type", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        related="project_id.company_id",
        store=True,
        index=True,
    )
