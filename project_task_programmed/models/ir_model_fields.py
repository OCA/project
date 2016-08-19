# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    @api.multi
    def name_get(self):
        result = []
        for field in self:
            result.append((field.id, '%s (%s)' % (
                field.field_description,
                field.model
            )))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []

        domain = [
            '|', '|',
            ('name', operator, name),
            ('field_description', operator, name),
            ('model', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
