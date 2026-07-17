# Copyright 2026 Patryk Pyczko (Nagarro)<patryk.pyczko@nagarro.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        index=True,
    )
    is_postsale = fields.Boolean(
        string="Is a Post-sale Lead",
        default=False,
        help="Technical field to identify leads generated automatically "
        "by the post-sale automation.",
    )
    postsale_cycle_date = fields.Date(
        string="Post-sale Cycle Date",
        help="The logical date of the post-sale cycle this lead belongs to. "
        "Used to prevent duplicates.",
    )
