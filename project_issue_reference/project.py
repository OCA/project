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

from openerp import models, fields, api, SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.model
    def _authorised_models(self):
        """ similar in new api to
            openerp.addons.base.res.res_request import referencable_models

            Inherit this method to add more models depending of your
            modules dependencies
        """
        models = self.env['res.request.link'].search([])
        return [(x.object, x.name) for x in models]

    reference = fields.Reference(
        selection='_authorised_models', string="Issue Origin")

    @api.model
    def default_get(self, fields):
        vals = super(ProjectIssue, self).default_get(fields)
        vals['partner_id'] = (
            self.env['res.users'].browse(self.env.uid).partner_id.id)
        vals['user_id'] = False
        if 'from_model' in self._context and 'from_id' in self._context:
            vals['reference'] = '%s,%s' % (self._context['from_model'],
                                           self._context['from_id'])
        return vals


class IrActionActWindows(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None, context=None,
             load='_classic_read'):
        if context is None:
            context = {}

        def update_context(action):
            action['context'] = safe_eval(action.get('context', '{}'))
            action['context'].update({
                'from_model': context.get('active_model'),
                'from_id': context.get('active_id'),
            })

        res = super(IrActionActWindows, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)
        if isinstance(ids, list):
            action_id = ids[0]
        else:
            action_id = ids
        _, issue_action = self.pool['ir.model.data'].get_object_reference(
            cr, SUPERUSER_ID, 'project_issue_reference',
            'project_issue_from_anywhere')
        if action_id == issue_action:
            if isinstance(res, list):
                for elem in res:
                    update_context(elem)
            else:
                update_context(res)
        return res
