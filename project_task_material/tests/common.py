# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# Copyright 2026 Mario Castillo López <@mcastillol14>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests.common import TransactionCase


class TestProjectCases(TransactionCase):
    """Prepare data to test the module."""

    def setUp(self):
        """Create the user, project and task used across the tests."""
        super().setUp()

        self.project_user = self.env["res.users"].create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "name": "Carlos Project User",
                "login": "cpu",
                "email": "cpu@yourcompany.com",
                "group_ids": [(6, 0, [self.ref("project.group_project_user")])],
            }
        )

        self.project = self.env["project.project"].create({"name": "Project Test"})

        self.task = self.env["project.task"].create(
            {"project_id": self.project.id, "name": "Task Test"}
        )
        # product.consu_delivery_03 is demo data, not loaded by default since 19.0
        self.product = self.env["product.product"].create(
            {"name": "Test Material Product", "type": "consu"}
        )

        self.action = self.task.with_user(self.project_user.id)
