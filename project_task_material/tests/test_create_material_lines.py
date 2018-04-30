# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2018 - Braintec - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from .common import TestProjectCases
from odoo.exceptions import ValidationError


class ProjectTaskMaterial(TestProjectCases):

    def test_manager_add_task_material_wrong(self):
        """
        TEST CASE 1
        The project manager is adding some materials in the task
        with different wrong values

        """
        try:
            # Material with `quantity = 0.0`
            self.task.sudo(self.project_manager.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": 0.0})]})
            # Material with `negative quantity`
            self.task.sudo(self.project_manager.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": -10.0})]})
            # Material with `positive quantity`
            self.task.sudo(self.project_manager.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": 3.0})]})
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.")

    def test_manager_add_task_material_right(self):
        """
        TEST CASE 2
        The project manager is adding some materials in the task
        with different right values

        """
        # Material with `quantity = 0.0`
        self.task.sudo(self.project_manager.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 4.0})]})
        # Material with `negative quantity`
        self.task.sudo(self.project_manager.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 5.0})]})
        # Material with `positive quantity`
        self.task.sudo(self.project_manager.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 3.0})]})
        self.assertEqual(len(self.task.material_ids.ids), 3)

    def test_user_add_task_material_wrong(self):
        """
        TEST CASE 3
        The project user is adding some materials in the task
        with different wrong values

        """
        try:
            # Material with `quantity = 0.0`
            self.task.sudo(self.project_user.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": 0.0})]})
            # Material with `negative quantity`
            self.task.sudo(self.project_user.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": -10.0})]})
            # Material with `positive quantity`
            self.task.sudo(self.project_user.id).write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": 3.0})]})
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.")

    def test_user_add_task_material_right(self):
        """
        TEST CASE 4
        The project user is adding some materials in the task
        with different right values

        """
        # Material with `quantity = 0.0`
        self.task.sudo(self.project_user.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 4.0})]})
        # Material with `negative quantity`
        self.task.sudo(self.project_user.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 5.0})]})
        # Material with `positive quantity`
        self.task.sudo(self.project_user.id).write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 3.0})]})
        self.assertEqual(len(self.task.material_ids.ids), 3)
