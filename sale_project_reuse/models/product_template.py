# Copyright 2026 glueckkanja AG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    reuse_project = fields.Boolean(
        help="Sales orders containing this product reuse the project configured "
        "on the customer.",
    )
    reuse_project_visible = fields.Boolean(
        compute="_compute_reuse_project_visible",
        export_string_translation=False,
    )

    @api.depends("service_tracking", "project_template_id")
    def _compute_reuse_project_visible(self):
        for product in self:
            product.reuse_project_visible = product.service_tracking in [
                "task_in_project",
                "project_only",
                "copy_tasks_in_project",
            ]

    @api.onchange("service_tracking")
    def _onchange_service_tracking_reuse_project(self):
        """Clear the flag when it does not apply, like core does for projects."""
        if not self.reuse_project_visible:
            self.reuse_project = False
