from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    old_start_date = fields.Date(string='Old Start Date',
                                 help="Used by the Shift Dates function. \
                                 When the Projects start date changes, the \
                                 old date is populated in this field then is \
                                 used when the 'Shift Dates' button is \
                                 pushed.")

    shift_task_dates = fields.Boolean(string="Allow date shifting",
                                      default=True,
                                      help="If checked, when you change the \
                                      start date of a project, the dates on \
                                      the Tasks will shift the number of days \
                                      you change the start date of the \
                                      Project. If the Project start dates \
                                      were originally empty, the Start/End \
                                      dates on the tasks will be set to the \
                                      Project Start/End Dates unless they \
                                      were previously set on the Tasks.")

    # SET OLD DATE VALUE WHEN CHANGED *USED FOR DATE SHIFTING
    @api.onchange('date_start')
    def on_change_dates(self):
        if self.old_start_date is not True:
            self.old_start_date = self._origin.date_start
        if self.old_start_date == self.date_start:
            self.old_start_date = False

    # SHIFT TASK AND MILESTONE DATES
    def shift_dates(self):
        # ONLY RUN IS SHIFT DATES OPTION IS TRUE
        if self.shift_task_dates and (self.old_start_date != self.date_start):
            original_start_dt = fields.Datetime.from_string(
                self.old_start_date)
            new_start_dt = fields.Datetime.from_string(self.date_start)
            difference = relativedelta(new_start_dt, original_start_dt)
            years = difference.years
            months = difference.months
            days = difference.days

            # SHIFT TASK DATES
            for record in self.task_ids:
                if (record.active) and (record.stage_id.closed is not True):
                    if record.date_start:
                        record.write({'date_start': (
                            fields.Datetime.from_string(record.date_start) +
                            relativedelta(years=+ years) +
                            relativedelta(months=+ months) +
                            relativedelta(days=+ days))})
                    if record.date_end:
                        record.write({'date_end': (
                            fields.Datetime.from_string(record.date_end) +
                            relativedelta(years=+ years) +
                            relativedelta(months=+ months) +
                            relativedelta(days=+ days))})
                    if record.date_deadline:
                        record.write({'date_deadline': (
                            fields.Datetime.from_string(record.date_deadline) +
                            relativedelta(years=+ years) +
                            relativedelta(months=+ months) +
                            relativedelta(days=+ days))})

            # SHIFT MILESTONE DATES
            # Only do this if the milestone module is installed
            module = self.env['ir.module.module'].search([(
                'name', '=', 'project_milestone')])
            if module and module.state == 'installed':
                if self.use_milestones:
                    for record2 in self.milestone_ids:
                        if record2.target_date:
                            record2.write({'target_date': (
                                fields.Datetime.from_string(
                                    record2.target_date) +
                                relativedelta(years=+ years) +
                                relativedelta(months=+ months) +
                                relativedelta(days=+ days))})

        self.old_start_date = False
