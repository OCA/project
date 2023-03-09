# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    sequence_code = fields.Char(
        readonly=True,
        copy=False,
    )
    name = fields.Char(
        required=False,
    )

    def _sync_name(self):
        """Set name if empty."""
        for rec in self - self.filtered("name"):
            rec.name = rec.sequence_code

    def name_get(self):
        """Prefix name with sequence code if they are different."""
        old_result = super().name_get()
        result = []
        for id_, name in old_result:
            project = self.browse(id_)
            if project.sequence_code != name:
                name = "{} - {}".format(project.sequence_code, name)
            result.append((id_, name))
        return result

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Allow searching by sequence code by default."""
        # Do not add any domain when user just clicked on search widget
        if not (name == "" and operator == "ilike"):
            # The dangling | is needed to combine with the domain added by super()
            args = (args or []) + ["|", ("sequence_code", operator, name)]
        return super().name_search(name, args, operator, limit)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.sequence_code = self.env["ir.sequence"].next_by_code("project.sequence")
        res._sync_name()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "name" in vals:
            self._sync_name()
        return res
