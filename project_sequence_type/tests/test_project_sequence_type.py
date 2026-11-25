# Copyright 2026 Ledo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectSequenceType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Project = cls.env["project.project"]
        cls.consulting_seq = cls.env["ir.sequence"].create(
            {
                "name": "Consulting Projects",
                "code": "project.sequence.test.consulting",
                "prefix": "CONS-",
                "padding": 4,
            }
        )
        cls.consulting = cls.env["project.type"].create(
            {"name": "Consulting", "sequence_id": cls.consulting_seq.id}
        )
        cls.internal = cls.env["project.type"].create({"name": "Internal"})

    def test_type_with_sequence_uses_it(self):
        """A project takes its code from its type's sequence."""
        project = self.Project.create(
            {"name": "Acme audit", "type_id": self.consulting.id}
        )
        self.assertEqual(project.sequence_code, "CONS-0001")
        # The type sequence keeps counting for that type.
        project2 = self.Project.create(
            {"name": "Beta audit", "type_id": self.consulting.id}
        )
        self.assertEqual(project2.sequence_code, "CONS-0002")

    def test_type_without_sequence_uses_default(self):
        """A type that defines no sequence falls back to the global one."""
        project = self.Project.create(
            {"name": "Housekeeping", "type_id": self.internal.id}
        )
        self.assertTrue(project.sequence_code)
        self.assertFalse(project.sequence_code.startswith("CONS-"))

    def test_no_type_uses_default(self):
        """A project with no type keeps the default project sequence."""
        project = self.Project.create({"name": "Misc"})
        self.assertTrue(project.sequence_code)
        self.assertFalse(project.sequence_code.startswith("CONS-"))

    def test_type_in_simplified_create_form(self):
        """The New-Project dialog exposes type_id, so the type (and its
        sequence) can be set up front instead of only after creation."""
        view = self.env.ref("project.project_project_view_form_simplified")
        arch = self.Project.get_view(view.id, "form")["arch"]
        self.assertIn('name="type_id"', arch)

    def test_explicit_sequence_code_wins(self):
        """An explicit sequence_code is never overridden by the type sequence."""
        project = self.Project.create(
            {
                "name": "Manual",
                "type_id": self.consulting.id,
                "sequence_code": "MANUAL-1",
            }
        )
        self.assertEqual(project.sequence_code, "MANUAL-1")
