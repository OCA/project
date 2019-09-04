from odoo import models, fields, api, SUPERUSER_ID


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def _read_group_status_ids(self, statuses, domain, order):
        statuse_ids = statuses._search(
            [], order=order, access_rights_uid=SUPERUSER_ID)
        return statuses.browse(statuse_ids)

    project_status = fields.Many2one(
        'project.status', string="Project Status",
        group_expand='_read_group_status_ids', copy=False,
        ondelete='restrict', index=True)
