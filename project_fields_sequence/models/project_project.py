# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import api, models

PROJECT_FIELDS_SEQUENCE_CODE_BASE = "project.field."


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        is_model = self.env["ir.sequence"].sudo()
        fields_with_seq = {
            seq.code[len(PROJECT_FIELDS_SEQUENCE_CODE_BASE) :]
            for seq in is_model.search(
                [
                    ("code", "=like", PROJECT_FIELDS_SEQUENCE_CODE_BASE + "%"),
                ]
            )
        }
        for fname in fields_list:
            if fname in fields_with_seq:
                res[fname] = is_model.next_by_code(
                    f"{PROJECT_FIELDS_SEQUENCE_CODE_BASE}{fname}"
                )
        return res
