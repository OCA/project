# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PortalProperties(fields.Properties):
    properties = None
    store = False

    def _compute(self, records):
        """
        Overriding the compute in order to pass the related properties
        """
        for record in records:
            record[self.name] = self._add_default_values(
                record.env,
                {
                    self.name: record.sudo()[self.properties or self.name],
                    self.definition_record: record[self.definition_record],
                },
            )


class ProjectTask(models.Model):
    _inherit = "project.task"

    portal_task_properties = PortalProperties(
        properties="task_properties",
        definition="project_id.portal_task_properties_definition",
    )

    @property
    def SELF_READABLE_FIELDS(self):
        result = super().SELF_READABLE_FIELDS
        result.add("portal_task_properties")
        return result
