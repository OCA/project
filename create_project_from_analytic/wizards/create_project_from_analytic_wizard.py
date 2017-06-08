# -*- coding: utf-8 -*-
# (c) 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, fields, api, exceptions, _



class CreateProjectFromAnalyticWizard(models.TransientModel):
    """ Create a project from an existing analytic account."""
    _name = 'create.project.from.analytic.wizard'
    _description = __doc__

    def _prepare_project_data(self, analytic):

        return {
            'analytic_account_id': analytic.id
        }

    @api.one
    def confirm_create(self):
        res = []
        act_close = {'type': 'ir.actions.act_window_close'}
        analytic_account_ids = self._context.get('active_ids')
        if analytic_account_ids is None:
            return act_close
        analytic_model = self.env['account.analytic.account']
        project_model = self.env['project.project']
        for analytic in analytic_model.browse(analytic_account_ids):
            if project_model.search([('analytic_account_id', '=',
                                      analytic.id)]):
                raise exceptions.Warning(
                    _('Error!:: Analytic Account [%s] %s already has a '
                      'project')
                    % (analytic.code, analytic.name))
            if analytic.type != 'contract':
                raise exceptions.Warning(
                    _('Error!:: Analytic Account [%s] %s is not of type '
                      'Contract or Project')
                    % (analytic.code, analytic.name))
            project_data = self._prepare_project_data(analytic)
            project = project_model.create(project_data)
            res.append(project.id)

        return {
            'domain': "[('id','in', ["+','.join(map(str, res))+"])]",
            'name': _('Project'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'view_id': False,
            'context': False,
            'type': 'ir.actions.act_window'
        }
