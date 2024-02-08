# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"
    _sql_constraints = [
        # Ensure compatibility with other modules that always expect a value in name
        ("name_required", "CHECK(name IS NOT NULL)", "Project name is required"),
        (
            "sequence_code_unique",
            "UNIQUE(sequence_code)",
            "Sequence code must be unique",
        ),
    ]

    sequence_code = fields.Char(
        copy=False,
        readonly=True,
    )
    name = fields.Char(
        # We actually require it with the SQL constraint, but it is disabled
        # here to let users create/write projects without name, and let this module
        # add a default name if needed
        required=False,
    )

    def _sync_analytic_account_name(self):
        """Set analytic account name equal to project's display name."""
        for rec in self:
            if not rec.analytic_account_id:
                continue
            rec.analytic_account_id.name = rec.display_name

    @api.depends("sequence_code", "name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        sequence_pattern = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "project_sequence.display_name_pattern",
                default="%(sequence_code)s - %(name)s",
            )
        )
        for project in self.filtered(
            lambda pr: pr.sequence_code and pr.sequence_code != pr.name
        ):
            project.display_name = sequence_pattern % {
                "name": project.name,
                "sequence_code": project.sequence_code,
            }
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Allow searching by sequence code by default."""
        # Do not add any domain when user just clicked on search widget
        if not (name == "" and operator == "ilike"):
            # The dangling | is needed to combine with the domain added by super()
            args = (args or []) + ["|", ("sequence_code", operator, name)]
        return super().name_search(name, args, operator, limit)

    @api.model_create_multi
    def create(self, vals_list):
        """Apply sequence code and a default name if not set."""
        # It is important to set sequence_code before calling super() because
        # other modules such as hr_timesheet expect the name to always have a value
        for vals in vals_list:
            if "sequence_code" not in vals:
                vals["sequence_code"] = self.env["ir.sequence"].next_by_code(
                    "project.sequence"
                )
            if not vals.get("name"):
                vals["name"] = vals["sequence_code"]
        res = super().create(vals_list)
        # The analytic account is created with just the project name, but
        # it is more useful to let it contain the project sequence too
        res._sync_analytic_account_name()
        return res

    def write(self, vals):
        """Sync name and analytic account name when name is changed."""
        # If name isn't changing, nothing special to do
        if "name" not in vals and "sequence_name" not in vals:
            return super().write(vals)
        # When changing name, we need to update the analytic account name too
        for one in self:
            sequence_code = vals.get("sequence_code", one.sequence_code)
            name = vals.get("name") or sequence_code
            super().write(dict(vals, name=name))
        self._sync_analytic_account_name()
        return True
