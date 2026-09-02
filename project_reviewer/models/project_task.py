# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    reviewer_ids = fields.Many2many(
        comodel_name="res.users", string="Reviewers", tracking=True
    )
