# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.tests.common import Form

from .common import TestProjectTaskRestrictedFieldsCommon


class TestProjectTaskRestrictedFieldsEnabled(TestProjectTaskRestrictedFieldsCommon):
    """Bypass restriction enabled"""

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
            {"restricted_field_ids": restrict_fields.ids, "bypass_restriction": True}
        )
        config.execute()

    def test_edit_task(self):
        """Check user edit restricted field"""
        task_form = Form(self.task_1.with_user(self.user_2).sudo())
        field_name = self.task_1._fields.get("name").string
        msg = self._prepared_alert_message(field_name)
        with self.assertRaisesRegex(AccessError, msg):
            task_form.name = "Task 11"
            task_form.save()

    def test_edit_task_description(self):
        # Not modify description
        task_form = Form(self.task_1.with_user(self.user_2).sudo())
        task_form.description = "Test description"
        task_form.save()

        # modify description
        field_name = self.task_1._fields.get("description").string
        msg = self._prepared_alert_message(field_name)

        with self.assertRaisesRegex(AccessError, msg):
            task_form.description = "Test description edit"
            task_form.save()
