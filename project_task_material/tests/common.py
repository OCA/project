# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests.common import TransactionCase


class TestProjectCases(TransactionCase):
    """Prepare data to test the module."""

    def setUp(self):
        super(TestProjectCases, self).setUp()

        # Create a new project user
        self.project_user = self.env["res.users"].create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "name": "Carlos Project User",
                "login": "cpu",
                "email": "cpu@yourcompany.com",
                "groups_id": [(6, 0, [self.ref("project.group_project_user")])],
            }
        )

        # Create a project
        self.project = self.env["project.project"].create(
            {
                "company_id": self.env.ref("base.main_company").id,
                "name": "Project for Test",
            }
        )

        # Create a project task
        self.project_task = self.env["project.task"].create(
            {
                "project_id": self.project.id,
                "name": "Task for Test",
            }
        )

        # Create a product template
        self.product = self.env["product.template"].create(
            {
                "name": "Product for Test",
            }
        )

        # Set the user for the project task action
        self.action = self.project_task.with_user(self.project_user.id)
