# Daniel Reis, 2014
# GNU Affero General Public License <http://www.gnu.org/licenses/>

from odoo import models, fields


_TASK_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled')]


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'
    state = fields.Selection(_TASK_STATE, 'State')
