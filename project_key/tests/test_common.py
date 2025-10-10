# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests.common import HttpCase, TransactionCase

from odoo.addons.base.tests.common import BaseCommon


class TestMixin:
    @staticmethod
    def _setup_records(class_or_instance):
        self = class_or_instance
        self.Project = self.env["project.project"].with_context(test_project_key=True)
        self.Task = self.env["project.task"].with_context(test_project_key=True)

        self.project_action = self.env.ref("project.open_view_project_all_config")
        self.task_action = self.env.ref("project.action_view_task")

        self.project_1 = self.Project.create({"name": "OCA"})
        self.project_2 = self.Project.create({"name": "Odoo", "key": "ODOO"})
        self.project_3 = self.Project.create({"name": "Python"})

        self.task11 = self.Task.create({"name": "1", "project_id": self.project_1.id})

        self.task12 = self.Task.create(
            {"name": "2", "parent_id": self.task11.id, "project_id": self.project_1.id}
        )

        self.task21 = self.Task.create({"name": "3", "project_id": self.project_2.id})

        self.task30 = self.Task.create({"name": "3"})

    def get_task_url(self, task):
        return f"/odoo/{task._name}/{task.id}"


class TestCommon(TransactionCase, TestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._setup_records(cls)


class HttpTestCommon(BaseCommon, HttpCase, TestMixin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls._setup_records(cls)
        cls.user_portal = cls._create_new_portal_user()
        cls.portal_partner = cls.user_portal.partner_id
