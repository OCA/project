# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2016 MATMOZ d.o.o.. - Matjaž Mozetič
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _


class Project(models.Model):
    _inherit = "project.project"

    @api.multi
    def action_openTasksTreeView(self):

        context = self.env.context.copy()
        context['view_buttons'] = True
        view = {
            'name': _('Details'),
            'view_type': 'form',
            'view_mode': 'tree,form,kanban,gantt',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
            'context': context
        }
        return view
