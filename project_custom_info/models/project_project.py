# Copyright 2019 Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Project(models.Model):
    _name = "project.project"
    _inherit = [_name, "custom.info"]

    custom_info_template_id = fields.Many2one(
        context={"default_model": _name})
    custom_info_ids = fields.One2many(
        context={"default_model": _name})
