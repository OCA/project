from markupsafe import Markup

from odoo.addons.base.tests.common import BaseCommon


class TestDescriptionTemplate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = cls.env["project.task"]
        cls.description_template = cls.env["project.task.description.template"].create(
            {
                "name": "Test Template",
                "description": " - Sample Description",
            }
        )

    def test_onchange_description_template_id(self):
        record = self.model.new({"description": "<p>Existing Description</p>"})
        record.description_template_id = self.description_template
        record._onchange_description_template_id()
        self.assertEqual(
            record.description,
            Markup("<p>Existing Description</p><span>- Sample Description</span>"),
            "Onchange method failed to append description correctly.",
        )

    def test_onchange_with_empty_description(self):
        record = self.model.new({})
        record.description_template_id = self.description_template
        record._onchange_description_template_id()
        self.assertEqual(
            record.description,
            Markup("<span>- Sample Description</span>"),
            "Onchange method failed with empty initial description.",
        )
