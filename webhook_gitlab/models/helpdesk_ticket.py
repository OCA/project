# Copyright 2018, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    git_request_ids = fields.One2many(
        "git.request", "ticket_id", string="Merge Requests"
    )
