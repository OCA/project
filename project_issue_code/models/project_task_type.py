# -*- coding: utf-8 -*-
# © 2016 Alejandro Tapia (alejandro.tapia@openpyme.mx)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import orm, fields


class project_task_type(orm.Model):
    _inherit = 'project.task.type'

    _columns = {
        'set_issue_code': fields.boolean(
            'Set code', help='Set the code for issues flow into this stage',
        )
    }
