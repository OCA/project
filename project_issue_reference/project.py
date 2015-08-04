# coding: utf-8
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.model
    def _authorised_models(self):
        # TODO remove AbstractModel
        models = self.env['ir.model'].search([('osv_memory', '=', False)])
        return [(x.model, x.name) for x in models]

    reference = fields.Reference(
        selection='_authorised_models', string="Linked Object")

    @api.model
    def default_get(self, fields):
        vals = super(ProjectIssue, self).default_get(fields)
        vals['partner_id'] = (
            self.env['res.users'].browse(self.env.uid).partner_id.id)
        vals['user_id'] = False
        print '    vals', vals
        print 'ctx', self._context
        return vals
