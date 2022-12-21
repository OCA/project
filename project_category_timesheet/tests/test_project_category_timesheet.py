from odoo.tests import common


class TestProjectCategoryTimesheet(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProjectCategoryTimesheet, cls).setUpClass()
        cls.cat = cls.env["project.type"].create(
            {"name": "General", "project_ok": True, "timesheet_ok": True}
        )
        cls.cat2 = cls.env["project.type"].create(
            {"name": "Discussion", "task_ok": True, "timesheet_ok": True}
        )
        cls.cat3 = cls.env["project.type"].create({"name": "No Timesheet"})
        cls.pro = cls.env["project.project"].create(
            {"name": "Pro Test", "type_id": cls.cat.id, "allow_timesheets": True}
        )
        cls.task1 = cls.env["project.task"].create(
            {"name": "Task 1 Test", "project_id": cls.pro.id, "type_id": cls.cat2.id}
        )
        cls.task2 = cls.env["project.task"].create(
            {
                "name": "Task 2 Test",
                "project_id": cls.pro.id,
            }
        )

    def test_timesheet_type_autoasign(self):
        form = common.Form(
            self.env["account.analytic.line"],
            view="project_category_timesheet.hr_timesheet_line_form",
        )
        # form.project_id = self.pro
        form.task_id = self.task1
        form.unit_amount = 1
        tsheet1 = form.save()
        form = common.Form(
            self.env["account.analytic.line"],
            view="project_category_timesheet.hr_timesheet_line_form",
        )
        # form.project_id = self.pro
        form.task_id = self.task2
        form.unit_amount = 1
        tsheet2 = form.save()

        self.assertEqual(
            tsheet1.project_type_id.id, self.cat2.id, "Type should be catch from tasks"
        )
        self.assertEqual(
            tsheet2.project_type_id.id, self.cat.id, "Type should be catch from project"
        )
