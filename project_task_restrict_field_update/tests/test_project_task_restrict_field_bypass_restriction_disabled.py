# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import Form

from .common import TestProjectTaskRestrictedFieldsCommon


class TestProjectTaskRestrictedFieldsDisabled(TestProjectTaskRestrictedFieldsCommon):
    """Bypass restriction disabled"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        restrict_fields = cls.model_fields_obj.search(
            [
                ("model", "=", "project.task"),
                ("name", "in", cls.SELF_WRITE_RESTRICTED_FIELDS),
            ]
        )

        config = cls.config_obj.create(
            {"restricted_field_ids": restrict_fields.ids, "bypass_restriction": False}
        )
        config.execute()

    def test_get_restricted_fields_settings(self):
        """Test setting the default restricted fields in General Settings."""

        restricted_field_ids = self.config_parameter_obj.get_param(
            "project_task_restrict_field_update.restricted_field_ids"
        )
        restrict_fields = list(map(int, restricted_field_ids.split(",")))
        actual = set(self.model_fields_obj.browse(restrict_fields).mapped("name"))
        expected = set(self.SELF_WRITE_RESTRICTED_FIELDS)
        self.assertEqual(actual, expected, msg="Must be equal RESTRICTED FIELDS")

    def test_get_restricted_fields(self):
        """Test setting the default restricted fields in General Settings."""

        restricted_field_ids = self.config_parameter_obj.get_param(
            "project_task_restrict_field_update.restricted_field_ids"
        )
        restrict_fields = list(map(int, restricted_field_ids.split(",")))
        actual = set(self.model_fields_obj.browse(restrict_fields).mapped("name"))
        expected = set(self.task_1._get_write_restricted_fields())
        self.assertEqual(actual, expected, msg="Must be equal RESTRICTED FIELDS")

    def test_html_content_modified(self):
        """
        Check if the _is_html_content_modified method correctly compares two HTML contents.
        """
        test_txt_1 = "<p>Test</p>"
        test_txt_2 = "<p>Test</p>"
        test_txt_3 = "<p>Test2</p>"
        self.assertTrue(
            self.project_task_obj._is_html_content_modified(test_txt_2, test_txt_3),
            msg="Must be equal True",
        )
        self.assertFalse(
            self.project_task_obj._is_html_content_modified(test_txt_1, test_txt_2),
            msg="Must be equal False",
        )

    def test_get_html_content(self):
        """
        Check if the _get_html_content method correctly converts HTML content to plain text.
        """
        test_txt_1 = "<p>Test</p>"
        result = self.project_task_obj._get_html_content(test_txt_1)
        expected = "Test"
        self.assertEqual(result, expected, msg=f"Must be equal {expected}")

    def test_edit_task(self):
        """Check user edit restricted field"""
        task_form = Form(self.task_1.with_user(self.user_2))
        field_name = self.task_1._fields.get("name").string
        msg = self._prepared_alert_message(field_name)
        with self.assertRaisesRegex(AccessError, msg):
            task_form.name = "Task 11"
            task_form.save()

    def test_edit_task_description(self):
        # Not modify description
        task_form = Form(self.task_1.with_user(self.user_2))
        task_form.description = "Test description"
        task_form.save()

        # modify description
        field_name = self.task_1._fields.get("description").string
        msg = self._prepared_alert_message(field_name)

        with self.assertRaisesRegex(AccessError, msg):
            task_form.description = "Test description edit"
            task_form.save()
