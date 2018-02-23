# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import logging
import base64
import io
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WorkflowImportWizard(models.TransientModel):
    _name = 'project.workflow.export.wizard'

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        domain=[('state', '=', 'live')]
    )

    data = fields.Binary(
        string='File',
        readonly="1",
    )

    file_name = fields.Char(
        string='File Name',
        readonly="1",
    )

    state = fields.Selection([
        ('start', 'Start'),
        ('end', 'End'),
    ], default='start')

    @api.multi
    def button_export(self):
        self.ensure_one()

        exporter = self.get_workflow_exporter()

        stream = io.StringIO()
        exporter.wkf_write(self.workflow_id, stream, "utf-8")
        xml_string = stream.getvalue()
        stream.close()

        file_name = "%s.xml" % self.workflow_id.name

        self.write({
            'data': base64.b64encode(xml_string.encode("utf-8")),
            'file_name': file_name,
            'state': 'end'
        })

        action = self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow', 'project_workflow_export_wizard_action'
        )
        action['res_id'] = self.id
        return action

    def get_workflow_exporter(self):
        return self.env['project.workflow.xml.writer']
