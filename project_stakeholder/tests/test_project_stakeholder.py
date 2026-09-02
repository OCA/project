# Copyright 2025 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestProjectStakeholders(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Bill Ionaire",
                "email": "bill.ionaire@example.com",
            }
        )
        cls.stakeholder_role = cls.env["project.stakeholder.role"].create(
            {
                "name": "Investor",
            }
        )
        cls.project = cls.env["project.project"].create(
            {
                "name": "Project",
            }
        )
        cls.project_stakeholder = cls.env["project.stakeholder"].create(
            {
                "role_id": cls.stakeholder_role.id,
                "partner_id": cls.partner.id,
                "project_id": cls.project.id,
                "note": "Main project investor",
            }
        )

    def test_project_has_stakeholders(self):
        self.assertIn(self.project_stakeholder, self.project.stakeholder_ids)

    def test_partner_is_stakeholder(self):
        self.assertIn(self.project_stakeholder, self.partner.stakeholder_ids)
