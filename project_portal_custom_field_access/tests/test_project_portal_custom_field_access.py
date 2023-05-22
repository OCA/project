# Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests.common import users

from odoo.addons.project.tests.test_access_rights import TestAccessRights


class TestAccessRightsCustomFields(TestAccessRights):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # Set up a few custom fields
        cls.model_project_task = cls.env.ref("project.model_project_task")
        cls.field_custom_test = cls.env["ir.model.fields"].create(
            {
                "name": "x_test",
                "model_id": cls.model_project_task.id,
                "ttype": "char",
                "project_portal_access": True,
            }
        )

    def setUp(self):
        super().setUp()
        self.project_pigs.privacy_visibility = "portal"
        self.project_pigs.message_subscribe(partner_ids=self.portal.partner_id.ids)

    @users("Portal user")
    def test_task_custom_field_access_allowed(self):
        task = self.task.with_user(self.env.user)
        task.read(["x_test"])

    @users("Portal user")
    def test_task_custom_field_access_not_allowed(self):
        self.field_custom_test.project_portal_access = False
        task = self.task.with_user(self.env.user)
        with self.assertRaises(AccessError):
            task.read(["x_test"])

    @users("Internal user")
    def test_task_custom_field_access_internal_user_allowed(self):
        self.field_custom_test.project_portal_access = False
        task = self.task.with_user(self.env.user)
        task.read(["x_test"])
