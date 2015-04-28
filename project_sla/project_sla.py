# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Daniel Reis
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

from openerp.osv import fields, orm


class SLADefinition(orm.Model):

    """
    SLA Definition
    """
    _name = 'project.sla'
    _description = 'SLA Definition'

    _columns = {
        'name': fields.char('Title', size=64, required=True, translate=True),
        'active': fields.boolean('Active'),
        'control_model': fields.char('For documents', size=128, required=True),
        'start_field_id': fields.many2one(
            'ir.model.fields', 'Start Date', required=True,
            domain="[('model_id.model', '=', control_model),"
                   " ('ttype', 'in', ['date', 'datetime'])]",
            help="Date field used as start date for SLA check."),
        'control_field_id': fields.many2one(
            'ir.model.fields', 'Control Date', required=True,
            domain="[('model_id.model', '=', control_model),"
                   " ('ttype', 'in', ['date', 'datetime'])]",
            help="Date field used to check if the SLA was achieved."),
        'sla_line_ids': fields.one2many(
            'project.sla.line', 'sla_id', 'Definitions'),
        'analytic_ids': fields.many2many(
            'account.analytic.account', string='Contracts'),
    }

    _defaults = {
        'active': True,
    }

    def _reapply_slas(self, cr, uid, ids, recalc_closed=False, context=None):
        """
        Force SLA recalculation on all _open_ Contracts for the selected SLAs.
        To use upon SLA Definition modifications.
        """
        contract_obj = self.pool.get('account.analytic.account')
        contract_ids = contract_obj.search(cr, uid,
                                           [('sla_ids', 'in', ids),
                                            ('state', '=', 'open')],
                                           context=context)

        ctx = {} if context is None else context.copy()
        ctx.update({'sla_ids': ids})
        contract_obj._reapply_sla(cr, uid, contract_ids,
                                  recalc_closed=recalc_closed,
                                  context=ctx)
        return True

    def reapply_slas(self, cr, uid, ids, context=None):
        """ Reapply SLAs button action """
        return self._reapply_slas(cr, uid, ids, context=context)


class SLARules(orm.Model):

    """
    SLA Definition Rule Lines
    """
    _name = 'project.sla.line'
    _definition = 'SLA Definition Rule Lines'
    _order = 'sla_id,sequence'

    _columns = {
        'sla_id': fields.many2one('project.sla', 'SLA Definition'),
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Title', size=64, required=True, translate=True),
        'condition': fields.char(
            'Condition', size=256, help="Apply only if this expression is "
            "evaluated to True. The document fields can be accessed using "
            "either o, obj or object. Example: obj.priority <= '2'"),
        'limit_qty': fields.integer('Hours to Limit'),
        'warn_qty': fields.integer('Hours to Warn'),
    }

    _defaults = {
        'sequence': 10,
    }

    _sql_constraints = [
        ('check_limit_gte_warn_constr', 'CHECK (limit_qty >= warn_qty)',
         'Hours to Limit must be greater or equal to Hours to Warn'),
        ('check_limit_qty', 'CHECK (limit_qty >= 0)',
         'Hours to Limit must be greater or equal to zero'),
        ('check_warn_qty', 'CHECK (warn_qty >= 0)',
         'Hours to Warn must be greater or equal to zero'),
    ]
