# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
from freezegun import freeze_time

from odoo.tests.common import Form, SavepointCase, new_test_user, tagged, users


@tagged("-at_install", "post_install")
@freeze_time("2023-01-01 12:00:00")
class TestProjectSequence(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(cls.env, "manager", "project.group_project_manager")
        cls.pjr_seq = cls.env.ref("project_sequence.seq_project_sequence")
        cls.pjr_seq.date_range_ids.unlink()
        cls.pjr_seq._get_current_sequence().number_next = 11

    @users("manager")
    def test_sequence_after_creation(self):
        """Sequence is applied only after project creation."""
        prj_f = Form(self.env["project.project"])
        self.assertFalse(prj_f.name)
        self.assertFalse(prj_f.sequence_code)
        proj = prj_f.save()
        self.assertTrue(proj.sequence_code)
        self.assertEqual(proj.name, proj.sequence_code)
        self.assertEqual(proj.sequence_code, "23-00011")
        self.assertEqual(proj.display_name, "23-00011")

    @users("manager")
    def test_sequence_copied_to_name_if_emptied(self):
        """Sequence is copied to project name if user removes it."""
        proj = self.env["project.project"].create({"name": "whatever"})
        self.assertEqual(proj.name, "whatever")
        self.assertEqual(proj.sequence_code, "23-00012")
        self.assertEqual(proj.display_name, "23-00012 - whatever")
        with Form(proj) as prj_f:
            prj_f.name = False
        self.assertEqual(proj.name, "23-00012")
        self.assertEqual(proj.sequence_code, "23-00012")
        self.assertEqual(proj.display_name, "23-00012")
