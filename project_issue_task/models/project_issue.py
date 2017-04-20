# -*- coding: utf-8 -*-
# Copyright 2015 - 2013 Daniel Reis
# Copyright 2016 - Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import _, api, models
from openerp.exceptions import UserError


class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    @api.multi
    def action_create_task(self):
        """Create a task related to the issue(s), and open it(them)."""
        list_view = self.env.ref('project.view_task_tree2')
        form_view = self.env.ref('project.view_task_form2')
        tasks_ids = []
        for rec in self:
            if rec.task_id:
                raise UserError(_("A Task is already assigned to the Issue!"))
            task_data = {
                'project_id': rec.project_id.id,
                'partner_id': rec.partner_id.id,
                'name': _('Report for %s') % rec.name,
                'tag_ids': [(6, 0, rec.tag_ids.ids)],
            }
            task_model = self.env['project.task']
            task = task_model.create(task_data)
            rec.write({'task_id': task.id})
            tasks_ids.append(task.id)
        res = {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
        }
        if len(tasks_ids) > 1:  # pragma: no cover
            res['domain'] = "[('id','in',%s)]" % tasks_ids
            res['views'] = [(list_view.id, 'tree')]
        elif len(tasks_ids) == 1:
            res['views'] = [(form_view.id, 'form')]
            res['res_id'] = tasks_ids[0]
        return res
