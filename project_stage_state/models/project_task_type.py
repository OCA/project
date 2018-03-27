# Daniel Reis, 2014
# GNU Affero General Public License <http://www.gnu.org/licenses/>

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'
    state = fields.Selection(
        related='stage_id.state', store=True, readonly=True)
