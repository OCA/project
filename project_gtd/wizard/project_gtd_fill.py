from odoo import api, fields, models, _


class project_timebox_fill(models.TransientModel):
    _name = 'project.timebox.fill.plan'
    _description = 'Project Timebox Fill'

    timebox_id = fields.Many2one(
        'project.gtd.timebox', 'Get from Timebox', required=True, default='_get_from_tb')
    timebox_to_id = fields.Many2one(
        'project.gtd.timebox', 'Set to Timebox', required=True, default='_get_to_tb')
    task_ids = fields.Many2many(
        'project.task',
        'project_task_rel', 'task_id', 'fill_id',
        'Tasks selection')

    @api.model
    def _get_from_tb(self):
        ids = self.env['project.gtd.timebox'].search([])
        return ids and ids[0] or False

    @api.model
    def _get_to_tb(self):
        contaxt = self._context
        if context is None:
            context = {}
        if 'active_id' in context:
            return context['active_id']
        return False

    @api.multi
    def process(self):
        if not ids:
            return {}
        data = self.read([])
        if not data[0]['task_ids']:
            return {}
        self.env['project.task'].write(data[0]['task_ids'],
            {'timebox_id': data[0]['timebox_to_id'][0]})
        return {'type': 'ir.actions.act_window_close'}
