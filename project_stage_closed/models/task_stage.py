# -*- coding: utf-8 -*-
# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    closed = fields.Boolean(
        help="Tasks in this stage are considered closed.",
        default=False,
    )
    # a small hack to avoid having two fields with the
    # same name, but show the field in the view
    # when sale_service is not installed
    closed_alias = fields.Boolean(string='Closed', related='closed')
    closed_alias_visible = fields.Boolean(
        compute='_compute_closed_alias_visible',
    )

    @api.multi
    def _compute_closed_alias_visible(self):
        ir_module = self.env['ir.module.module']
        installed = ir_module.search([('name', '=', 'sale_service'),
                                      ('state', '=', 'installed')])
        self.update({'closed_alias_visible': not bool(installed)})
