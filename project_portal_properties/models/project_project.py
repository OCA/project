# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.web_portal_properties.fields import PortalPropertiesDefinition


class ProjectProject(models.Model):
    _inherit = "project.project"

    task_properties_definition = PortalPropertiesDefinition()
    portal_task_properties_definition = PortalPropertiesDefinition(
        compute="_compute_portal_task_properties_definition"
    )

    @api.depends("task_properties_definition")
    def _compute_portal_task_properties_definition(self):
        for project in self:
            project.portal_task_properties_definition = [
                definition
                for definition in project.task_properties_definition
                if definition.get("view_in_portal")
            ]
