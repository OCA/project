# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, fields, api


class StageChangeConfirmationWizard(models.TransientModel):
    _name = 'wkf.project.task.confirmation'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assignee',
        required=True,
        default=lambda s: s.env.user.id,
    )

    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='New Stage',
        readonly=True,
    )

    message = fields.Html(
        string='Action Message',
        required=True,
    )

    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
        required=True,
        ondelete="cascade",
    )

    @api.multi
    def apply(self):
        self.ensure_one()

        values = self.prepare_values()
        self.task_id.write(values)

        if self.message:
            return self.message_post(body=self.message, message_type='comment')

        return {'type': 'ir.actions.act_window_close'}

    def prepare_values(self):
        return {
            'user_id': self.user_id.id,
            'stage_id': self.stage_id.id,
        }
