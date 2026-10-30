# Copyright 2015 Incaser Informatica S.L. - Sergio Teruel
# Copyright 2015 Incaser Informatica S.L. - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import BaseCommon


class TestProjectCaseDefault(BaseCommon):
    # Use case : Prepare some data for current test case
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create({"name": "Project Test"})

    def test_project_new(self):
        self.assertEqual(len(self.project.type_ids), 7)

    def test_project_new_from_create_actions(self):
        # Projects created from the Project app get the default stages too
        for xmlid in (
            "project.open_create_project",
            "project.open_create_project_template",
        ):
            action = self.env.ref(xmlid).sudo()
            context = safe_eval(action.context)
            project = (
                self.env["project.project"]
                .sudo()
                .with_context(**context)
                .create({"name": "Project from action"})
            )
            self.assertEqual(project.type_ids, self.project.type_ids, xmlid)
