# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# Copyright 2018 Dreambits Technologies Pvt. Ltd. (<http://dreambits.in>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectCategory(models.Model):
    """Data Model for Project Category."""

    _name = 'project.category'
    _inherit = 'project.tags'

    description = fields.Char()
