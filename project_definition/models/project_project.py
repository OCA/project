# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    term_ids = fields.Many2many('document.definition', string='Project Terms')
