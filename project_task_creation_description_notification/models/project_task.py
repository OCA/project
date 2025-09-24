# Copyright 2024 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class ProjectTask(models.Model):
    """Task description in notification"""

    _inherit = "project.task"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *args, body="", subtype_id=False, **kwargs):
        create_subtype = self._creation_subtype()
        if not body and subtype_id == (create_subtype and create_subtype.id):
            body = "".join(
                [
                    create_subtype.name,
                    "<br/>",
                    (_("Task Description: <br/> %s <br/>") % self.description)
                    if self.description
                    else "",
                ]
            )
        return super().message_post(*args, body=body, subtype_id=subtype_id, **kwargs)
