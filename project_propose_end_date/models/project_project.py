# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, orm


class Project(orm.Model):
    _inherit = "project.project"

    def onchange_date_start(self, cr, uid, ids, date_start, context=None):
        if context is None:
            context = {}
        res = {
            'value': {}
        }

        for project in self.browse(cr, uid, ids, context=context):
            if not project.date:
                res['value']['date'] = date_start
        return res
