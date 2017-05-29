# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.multi
    @api.depends('model_reference')
    def _get_origin(self):
        for rec in self:
            if rec.model_reference and rec.model_reference._rec_name:
                rec.task_origin = rec.model_reference.display_name or False
            else:
                rec.task_origin = False

    @api.model
    def _authorised_models(self):
        """ Inherit this method to add more models depending of your
            modules dependencies
        """
        models = self.env['ir.model'].search([])
        return [(x.model, x.name) for x in models]

    action_id = fields.Many2one(
        'ir.actions.act_window', string="Action",
        help="Action called to go to the original window.")
    model_reference = fields.Reference(
        selection='_authorised_models')
    task_origin = fields.Char(compute='_get_origin')

    @api.model
    def default_get(self, fields):
        vals = super(ProjectTask, self).default_get(fields)
        if 'from_model' in self.env.context and 'from_id' in self.env.context:
            vals['model_reference'] = '%s,%s' % (
                self.env.context['from_model'],
                self.env.context['from_id'])
        if 'from_action' in self.env.context:
            vals['action_id'] = self.env.context['from_action']
        return vals

    def goto_document(self):
        self.ensure_one()
        if self.model_reference:
            action = {
                'name': 'Task to original document',
                'res_model': self.model_reference._name,
                'res_id': self.model_reference.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                'view_mode': 'form',
            }
            if self.action_id:
                action['id'] = self.action_id.id
                action['action_id'] = self.action_id.id
                view = [x.view_id for x in self.action_id.view_ids
                        if x.view_mode == 'form']
                if view:
                    view_ref = self.env['ir.model.data'].search(
                        [('res_id', '=', view[0].id),
                         ('model', '=', 'ir.ui.view')])
                    if view_ref:
                        action['context'] = {'form_view_ref': '%s.%s' % (
                            view_ref.module, view_ref.name)}
            return action
        raise UserError(_(
            "Field 'Task Origin' is not set.\n"
            "Impossible to go to the original document."))


class IrActionActWindows(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, fields=None, load='_classic_read'):

        def update_context(action):
            action['context'] = safe_eval(action.get('context', '{}'))
            action['context'].update({
                'from_model': self.env.context.get('active_model'),
                'from_id': self.env.context.get('active_id'),
            })
            if 'params' in self.env.context and 'action':
                action['context'].update({
                    'from_action': self.env.context['params'].get('action')})
            if 'params' in self.env.context and 'action':
                action['context'].update({
                    'from_action': self.env.context['params'].get('action')})

        res = super(IrActionActWindows, self).read(fields=fields, load=load)
        if not self.env.context.get('install_mode'):
            task_action_id = self.env.ref(
                'project_model_to_task.task_from_elsewhere')
            if self == task_action_id:
                if isinstance(res, list):
                    for elem in res:
                        update_context(elem)
                else:
                    update_context(res)
        return res
