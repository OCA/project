# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo.exceptions import ValidationError
from odoo.tests import common


class ProjectTaskMaterial(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(ProjectTaskMaterial, cls).setUpClass()

        cls.task = cls.env.ref('project.project_task_data_0')
        cls.product = cls.env.ref('product.consu_delivery_03_product_template')

    def test_create_task_material(self):
        """ Testing creation of task material """
        with self.assertRaises(ValidationError), self.cr.savepoint():
            # Adding a line with quantity equal to 0
            self.task.write({'material_ids': [
                (0, 0, {'product_id': self.product.id, 'quantity': 0.0})]})
        # Line is not created
        self.assertEqual(len(self.task.material_ids.ids), 0)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            # Adding a line with quantity less than 0
            self.task.write({'material_ids': [
                (0, 0, {'product_id': self.product.id, 'quantity': -10.0})]})
        # Line is not created
        self.assertEqual(len(self.task.material_ids.ids), 0)
        # Adding a line with quantity greater than 0
        self.task.write({'material_ids': [
            (0, 0, {'product_id': self.product.id, 'quantity': 3.0})]})
        self.assertEqual(len(self.task.material_ids.ids), 1)
