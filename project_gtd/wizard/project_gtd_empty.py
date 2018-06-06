from odoo import api, fields, models, _
from odoo.exceptions import UserError

class project_timebox_empty(models.TransientModel):
    _name = 'project.timebox.empty'
    _description = 'Project Timebox Empty'

    name = fields.Char('Name', size=32)

    @api.model
    def view_init(self, fields_list):
        context = self._context
        if context is None:
            context = {}
        self._empty()

    @api.model
    def _empty(self):
        close = []
        up = []
        obj_tb = self.env['project.gtd.timebox']
        obj_task = self.env['project.task']

        context = self._context
        if context is None:
            context = {}
        if 'active_id' not in context:
            return {}

        ids = obj_tb.search([])
        if not len(ids):
            raise UserError(
                _('Error!'), _('No timebox child of this one!'))
        tids = obj_task.search(
            cr, uid, [('timebox_id', '=', context['active_id'])])
        for task in obj_task.browse(tids):
            if (task.stage_id and task.stage_id.fold) \
                    or (task.user_id.id != uid):
                close.append(task.id)
            else:
                up.append(task.id)
        if up:
            obj_task.write(up, {'timebox_id': ids[0]})
        if close:
            obj_task.write(close, {'timebox_id': False})
        return {}

