# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.tests.common import TransactionCase

WRITE_RESTRICTED_FIELDS = [
    "name",
    "date_deadline",
    "tag_ids",
    "priority",
    "description",
]


class TestProjectTaskRestrictedFieldsCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.account_analytic_line_obj = cls.env["account.analytic.line"]
        project_project_obj = cls.env["project.project"]
        cls.project_task_obj = cls.env["project.task"]
        res_partner_obj = cls.env["res.partner"]
        res_users_obj = cls.env["res.users"].with_context(no_reset_password=True)
        project_tags_obj = cls.env["project.tags"]
        cls.config_obj = cls.env["res.config.settings"].sudo()
        cls.model_fields_obj = cls.env["ir.model.fields"].sudo()
        cls.config_parameter_obj = cls.env["ir.config_parameter"].sudo()

        project_user_group = cls.env.ref("project.group_project_user")

        cls.partner_1 = res_partner_obj.create({"name": "Test Partner #1"})
        cls.partner_2 = res_partner_obj.create({"name": "Test Partner #2"})

        cls.user_1 = res_users_obj.create(
            {
                "name": "User 1",
                "login": "user_1",
                "email": "user1@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )

        cls.user_2 = res_users_obj.create(
            {
                "name": "User 2",
                "login": "user_2",
                "email": "user2@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )

        cls.user_manager = res_users_obj.create(
            {
                "name": "User Officer",
                "login": "user_manager",
                "email": "usermanager@test.com",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            project_user_group.id,
                        ],
                    )
                ],
            }
        )
        cls.tag_test_1 = project_tags_obj.create({"name": "Test 1"})
        cls.tag_test_2 = project_tags_obj.create({"name": "Test 2"})

        cls.project_1 = project_project_obj.create(
            {
                "name": "Project #1",
                "user_id": cls.user_manager.id,
            }
        )
        cls.task_1 = cls.project_task_obj.create(
            {
                "name": "Task 1",
                "project_id": cls.project_1.id,
                "description": "Test description",
                "tag_ids": cls.tag_test_1.ids,
            }
        )

    @classmethod
    @property
    def SELF_WRITE_RESTRICTED_FIELDS(cls):
        return WRITE_RESTRICTED_FIELDS

    @classmethod
    def _prepared_alert_message(cls, field_name):
        return _("You are not allowed to modify the '%(f)s' field") % {"f": field_name}
