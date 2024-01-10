from bs4 import BeautifulSoup

from odoo import _, fields, models
from odoo.exceptions import AccessError


class ProjectTask(models.Model):
    _inherit = "project.task"

    can_write_restricted = fields.Boolean(
        compute="_compute_can_write_restricted",
        help="This field is used for conditional display of other fields on views",
    )

    def _compute_can_write_restricted(self):
        """Computes 'can_write_restricted' field values"""
        self.can_write_restricted = self._can_write_restricted()

    def _can_write_restricted(self):
        """Checks if user can update manager only fields

        Returns:
            Boolean: True if the user can write, otherwise False
        """

        # Check if user is a member of the 'Project/Manager' group or is a superuser
        can_write_restricted = (
            self.env.user.has_group("project.group_project_manager")
            or self.env.user._is_superuser()
        )

        # Check if user is modifying tasks they did create themselves or
        # if bypass restriction is enabled
        tasks_created_by_user = self.filtered(lambda t: t.create_uid.id == self.env.uid)
        bypass_restriction = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("project_task_restrict_field_update.bypass_restriction", False)
        )
        can_write_restricted = (
            bool(tasks_created_by_user) or bool(bypass_restriction)
            if not can_write_restricted and tasks_created_by_user
            else can_write_restricted
        )

        return can_write_restricted

    def _get_write_restricted_fields(self):
        """Returns a list of write restricted fields
        Returns:
            List of str: list of fields
        """
        ICPSudo = self.env["ir.config_parameter"].sudo()
        model_fields_obj = self.env["ir.model.fields"].sudo()
        restricted_field_ids = ICPSudo.get_param(
            "project_task_restrict_field_update.restricted_field_ids"
        )

        restrict_fields = (
            list(map(int, restricted_field_ids.split(",")))
            if restricted_field_ids
            else []
        )
        return (
            model_fields_obj.browse(restrict_fields).mapped("name")
            if restrict_fields
            else []
        )

    def _filter_html_fields(self, vals):
        """
        Filters the HTML fields that have been modified with actual content changes.

        Args:
            vals (dict): The dictionary of field names and values.

        Returns:
            dict: The filtered dictionary of field names and values.
        """
        filtered_vals = {}
        for field_name, field_value in vals.items():
            field = self._fields.get(field_name)
            if field and field.type == "html":
                current_value = self[field_name]
                if self._is_html_content_modified(current_value, field_value):
                    filtered_vals[field_name] = field_value
            else:
                filtered_vals[field_name] = field_value
        return filtered_vals

    def _is_html_content_modified(self, current_value, new_value):
        """
        Checks if the HTML content has been modified.

        Args:
            current_value (str): The current HTML value.
            new_value (str): The new HTML value.

        Returns:
            bool: True if the content has been modified, otherwise False.
        """
        current_content = self._get_html_content(current_value)
        new_content = self._get_html_content(new_value)
        return current_content != new_content

    def _get_html_content(self, html_value):
        """Extract the actual content from the HTML field

        Args:
            html_value (str): The current HTML value.
        Returns:
            str: Text
        """
        return BeautifulSoup(html_value, "html.parser").get_text() if html_value else ""

    def write(self, vals):
        if not self._can_write_restricted():
            # Check if any of the manager only fields is updated
            restricted_fields = self._get_write_restricted_fields()
            vals = self._filter_html_fields(vals)
            for updated_field in vals.keys():
                if updated_field in restricted_fields:
                    # Get the field caption for the access error message
                    field_name = self._fields.get(updated_field).string
                    raise AccessError(
                        _("You are not allowed to modify the '%(f)s' field")
                        % {"f": field_name}
                    )
        return super().write(vals)
