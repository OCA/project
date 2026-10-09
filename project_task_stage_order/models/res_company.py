from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    task_stage_order_enabled = fields.Boolean(
        string="Per-Project Task Stage Order",
        help="Si está activado, esta empresa puede dar a cada uno de sus "
        "proyectos un orden de etapas independiente. Si está desactivado, "
        "todos los proyectos comparten el mismo orden de etapas.",
    )
