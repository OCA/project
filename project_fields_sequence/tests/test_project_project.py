# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import Form, TransactionCase

from ..models.project_project import PROJECT_FIELDS_SEQUENCE_CODE_BASE


class TestProjectProject(TransactionCase):
    def setUp(self):
        super().setUp()
        is_model = self.env["ir.sequence"]
        self.pf_s_name = is_model.create(
            {
                "name": "Project Fields: Name",
                "code": f"{PROJECT_FIELDS_SEQUENCE_CODE_BASE}name",
                "implementation": "standard",
                "prefix": "PFN/",
                "padding": 3,
                "number_increment": 1,
            }
        )
        self.pf_s_label_tasks = is_model.create(
            {
                "name": "Project Fields: Label Tasks",
                "code": f"{PROJECT_FIELDS_SEQUENCE_CODE_BASE}label_tasks",
                "implementation": "standard",
                "prefix": "PFLT-",
                "padding": 3,
                "number_increment": 1,
            }
        )

    def test_project_default_field_values(self):
        """Test that new created project has the correct default field values."""
        with Form(self.env["project.project"]) as pp_form:
            self.assertIn(self.pf_s_name.prefix, pp_form.name)
            self.assertIn(self.pf_s_label_tasks.prefix, pp_form.label_tasks)
