# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.tests.common import TransactionCase


class TestProjectCases(TransactionCase):

    def setUp(self):
        super(TestProjectCases, self).setUp()

        # Create new User
        # Add it to the `project user` group
        self.project_user = self.env["res.users"].create({
            "company_id": self.env.ref("base.main_company").id,
            "name": "Carlos Project User",
            "login": "cpu",
            "email": "cpu@yourcompany.com",
            "groups_id": [(6, 0, [self.ref('project.group_project_user')])]
        })

        # Refer to a task assigned to the project user
        self.task = self.env.ref('project.project_task_17')
        self.product = self.env.ref('product.consu_delivery_03')

        # Refer to a action from the user created
        self.action = self.task.sudo(self.project_user.id)
