# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class DocumentPage(models.Model):
    _inherit = 'document.page'

    # a relation to partner_id is given by our dependency on
    # document_page_partner_id if there is no partner_id and no project_id
    # specified the term is global

    type = fields.Selection(selection_add=[('term', 'Term')])

    # stored compute field used for making the letter grouping
    # need to be stored in order to use grouping
    first_letter = fields.Char(compute='_get_first_letter', store=True)

    @api.depends('name')
    @api.multi
    def _get_first_letter(self):
        for this in self:
            # if somehow the user starts with one or more whitespaces we trim
            this.first_letter = this.name.lstrip()[:1].upper() or 'Unknown'
