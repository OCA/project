# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    time_type_id = fields.Many2one(
        compute="_compute_time_type_id",
        store=True,
        readonly=False,
        copy=True,
    )

    @api.depends("employee_id", "project_id", "task_id")
    def _compute_time_type_id(self):
        """Search the default time_type in 'project.time.type.rule'"""
        employee_id = self._context.get("default_employee_id")
        if employee_id:
            def_employee = self.env["hr.employee"].browse(employee_id)
        else:
            def_employee = self.env["hr.employee"].search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
        for line in self.filtered(lambda line: not line.time_type_id):
            # order from rules or order='task_id desc, project_id desc, user_id desc'
            rule = self.rule_guess(line, def_employee)
            line.time_type_id = rule.time_type_id if rule else False

    def rule_guess(self, line, def_employee):
        dom = []
        if line.project_id:
            dom.append(("project_id", "=", line.project_id.id))
            if line.task_id:
                # project.task.type
                dom.append(("project_type_id", "=", line.task_id.stage_id.id))

        employee = line.employee_id or def_employee
        if employee:
            department = employee.department_id
            dom.append(("employee_id", "=", employee.id))
            if department:
                dom.append(("department_id", "=", department.id))

        ors = len(dom) - 1 if len(dom) > 0 else 0
        dom = ["|" for x in range(ors)] + dom

        all_rules = self.env["project.time.type.rule"].search(dom)
        rule = None
        weight = 0
        for r in all_rules:
            w = 0
            if r.project_type_id and line.task_id and line.task_id.stage_id:
                if r.project_type_id == line.task_id.stage_id:
                    w += 1
                else:
                    continue
            if r.project_id:
                if r.project_id == line.project_id:
                    w += 2
                else:
                    continue
            if r.employee_id:
                if r.employee_id == employee:
                    w += 8
                else:
                    continue
            elif r.department_id:
                if r.department_id == department:
                    w += 4
                else:
                    continue

            if w > weight:
                weight = w
                rule = r
        return rule

    @api.onchange("time_type_id")
    def _onchange_project_type_id(self):
        if self.time_type_id and (not self.name or self.name == "/"):
            self.name = (
                "{}: ".format(self.time_type_id.code)
                if self.time_type_id.code
                else self.time_type_id.name
            )
