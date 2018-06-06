from odoo import api, fields, models, tools

class project_gtd_context(models.Model):
    _name = "project.gtd.context"
    _description = "Context"
    _order = "sequence, name"
    
    name = fields.Char(
        'Context', size=64, required=True, translate=True)
    sequence = fields.Integer(
        'Sequence',default=1,
        help=("Gives the sequence order when displaying "
              "a list of contexts."))


class project_gtd_timebox(models.Model):
    _name = "project.gtd.timebox"
    _order = "sequence"

    name = fields.Char(
        'Timebox', size=64, required=True, select=1, translate=1)
    sequence =  fields.Integer(
        'Sequence',
        help="Gives the sequence order when displaying "
             "a list of timebox.")


class project_task(models.Model):
    _inherit = "project.task"

    timebox_id = fields.Many2one(
        'project.gtd.timebox',
        "Timebox",
        help="Time-laps during which task has to be treated")
    context_id = fields.Many2one(
        'project.gtd.context',
        "Context",
        help="The context place where user has to treat task")

    @api.model
    def _get_context(self):
        ids = self.env['project.gtd.context'].search([])
        return ids and ids[0] or False

    @api.multi
    def _read_group_timebox_ids(
            self, domain,
            read_group_order=None, access_rights_uid=None):
        """Used to display all timeboxes on the view."""
        timebox_obj = self.env['project.gtd.timebox']
        order = timebox_obj._order
        access_rights_uid = access_rights_uid or uid
        timebox_ids = timebox_obj._search([], order=order, access_rights_uid=access_rights_uid)
        result = timebox_obj.name_get(access_rights_uid, timebox_ids)
        # Restore order of the search
        result.sort(
            lambda x, y: cmp(timebox_ids.index(x[0]), timebox_ids.index(y[0])))
        fold = dict.fromkeys(timebox_ids, False)
        return result, fold

    _defaults = {
        'context_id': _get_context
    }

    _group_by_full = {
        'timebox_id': _read_group_timebox_ids,
    }

    @api.multi
    def copy_data(self,default=None):
        context = self._context
        if context is None:
            context = {}
        if not default:
            default = {}
        if not default.get('timebox_id'):    
            default['timebox_id'] = False
        if not default.get('context_id'):    
            default['context_id'] = False
        return super(project_task, self).copy_data(default)

    @api.multi
    def next_timebox(self, *args):
        timebox_obj = self.pool.get('project.gtd.timebox')
        timebox_ids = timebox_obj.search(cr, uid, [])
        if not timebox_ids:
            return True
        for task in self.browse(cr, uid, ids):
            timebox = task.timebox_id
            if not timebox:
                self.write(cr, uid, task.id, {'timebox_id': timebox_ids[0]})
            elif timebox_ids.index(timebox) != len(timebox_ids)-1:
                index = timebox_ids.index(timebox)
                self.write(
                    cr, uid, task.id, {'timebox_id': timebox_ids[index+1]})
        return True

    @api.multi
    def prev_timebox(self, *args):
        timebox_obj = self.pool.get('project.gtd.timebox')
        timebox_ids = timebox_obj.search(cr, uid, [])
        for task in self.browse(cr, uid, ids):
            timebox = task.timebox_id
            if timebox:
                if timebox_ids.index(timebox):
                    index = timebox_ids.index(timebox)
                    self.write(
                        cr, uid, task.id,
                        {'timebox_id': timebox_ids[index - 1]})
                else:
                    self.write(cr, uid, task.id, {'timebox_id': False})
        return True

    @api.multi
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        context = self._context
        if not context:
            context = {}
        res = super(project_task, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
        search_extended = False
        timebox_obj = self.env['project.gtd.timebox']
        if (res['type'] == 'search') and context.get('gtd', False):
            #timeboxes = timebox_obj.browse(timebox_obj.search([]))
            timeboxes = timebox_obj.search([])
            search_extended = ''
            if timeboxes:
                for timebox in timeboxes:                  
                    filter_ = """
                        <filter domain="[('timebox_id', '=', {timebox_id})]"
                                string="{string}"/>\n
                        """.format(timebox_id=timebox.id, string=timebox.name)
                    search_extended += filter_
            search_extended += '<separator orientation="vertical"/>'
            res['arch'] = tools.ustr(res['arch']).replace(
                '<separator name="gtdsep"/>', search_extended)

        return res

