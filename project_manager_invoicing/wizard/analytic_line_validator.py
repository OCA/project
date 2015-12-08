# -*- coding: utf-8 -*-
#
#    Author: Yannick Vaucher, ported by Denis Leemann
#    Copyright 2015 Camptocamp SA
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
from openerp.osv import orm


class AnalyticLineValidator(orm.TransientModel):
    """ This wizard allows to change state for massive amount of analytic AnalyticLineValidator
    """
    _name = 'analytic.line.validator'

    # def _get_lines(self, cr, uid, ids, context=None):
    #     import pdb
    #     pdb.set_trace()
    #     return self.pool['account.analytic.line'].browse(cr, uid,
    #                        context.get('active_ids'), context=context)

    # Question besoin d'un retour? juste?
    def action_confirm(self, cr, uid, ids, context=None):
        import pdb
        pdb.set_trace()
        aa_line_ids = context.get('active_ids', [])
        return self.pool['account.analytic.line'].action_confirm(
            cr, uid, aa_line_ids, context=context)

    # Question besoin d'un retour? juste?
    def action_reset_to_draft(self, cr, uid, ids, context=None):
        import pdb
        pdb.set_trace()
        aa_line_ids = context.get('active_ids', [])
        return self.pool['account.analytic.line'].action_reset_to_draft(
            cr, uid, aa_line_ids, context=context)
