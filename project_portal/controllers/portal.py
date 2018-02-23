# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from collections import OrderedDict

from odoo import http, _
from odoo.http import request
from odoo.osv.expression import OR

from odoo.addons.portal.controllers.portal\
    import get_records_pager, pager as portal_pager

from odoo.addons.project.controllers.portal \
    import CustomerPortal


class CustomerPortal(CustomerPortal):

    # ========================
    #   Portal My Projects
    # ========================
    @http.route([
        '/my/projects',
        '/my/projects/page/<int:page>'
    ], type='http', auth="user", website=True)
    def portal_my_projects(self, page=1, date_begin=None, date_end=None,
                           sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        values.update(self.portal_my_projects_prepare_values(
            page, date_begin, date_end, sortby, **kw)
        )
        return self.portal_my_projects_render(values)

    def portal_my_projects_render(self, values):
        return request.render("project.portal_my_projects", values)

    def portal_my_projects_prepare_values(self, page=1, date_begin=None,
                                          date_end=None, sortby=None, **kw):
        Project = request.env['project.project']
        domain = [('privacy_visibility', '=', 'portal')]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project.project', domain)
        if date_begin and date_end:
            domain += [
                ('create_date', '>', date_begin),
                ('create_date', '<=', date_end)
            ]
        # projects count
        project_count = Project.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/projects",
            url_args={
                'date_begin': date_begin,
                'date_end': date_end,
                'sortby': sortby
            },
            total=project_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        projects = Project.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_projects_history'] = projects.ids[:100]

        return {
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'page_name': 'project',
            'archive_groups': archive_groups,
            'default_url': '/my/projects',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        }

    # ========================
    #   Portal My Project
    # ========================
    @http.route([
        '/my/project/<int:project_id>'
    ], type='http', auth="user", website=True)
    def portal_my_project(self, project_id=None, **kw):
        values = self.portal_my_project_prepare_values(project_id, **kw)
        return self.portal_my_project_render(values)

    def portal_my_project_prepare_values(self, project_id=None, **kw):
        project = request.env['project.project'].browse(project_id)
        vals = {'project': project}
        history = request.session.get('my_projects_history', [])
        vals.update(get_records_pager(history, project))
        return vals

    def portal_my_project_render(self, values):
        return request.render("project.portal_my_project", values)

    # ========================
    #   Portal My Tasks
    # ========================
    @http.route([
        '/my/tasks',
        '/my/tasks/page/<int:page>'
    ], type='http', auth="user", website=True)
    def portal_my_tasks(self, page=1, date_begin=None, date_end=None,
                        sortby=None, filterby=None, search=None,
                        search_in='content', **kw):

        values = self._prepare_portal_layout_values()

        values.update(self.portal_my_tasks_prepare_values(
            page, date_begin, date_end, sortby, filterby,
            search, search_in, **kw)
        )

        return self.portal_my_tasks_render(values)

    def portal_my_tasks_prepare_searchbar(self):
        return {
            'sorting': {
                'date': {
                    'label': _('Newest'),
                    'order': 'create_date desc'
                },
                'name': {
                    'label': _('Title'),
                    'order': 'name'
                },
                'stage': {
                    'label': _('Stage'),
                    'order': 'stage_id'
                },
                'update': {
                    'label': _('Last Stage Update'),
                    'order': 'date_last_stage_update desc'
                },
            },

            'filters': {
                'all': {'label': _('All'), 'domain': []},
            },

            'inputs': {
                'content': {
                    'input': 'content',
                    'label':
                        _('Search <span class="nolabel"> (in Content)</span>')
                },
                'message': {
                    'input': 'message',
                    'label': _('Search in Messages')
                },
                'customer': {
                    'input': 'customer',
                    'label': _('Search in Customer')
                },
                'stage': {
                    'input': 'stage',
                    'label': _('Search in Stages')
                },
                'all': {
                    'input': 'all',
                    'label': _('Search in All')
                },
            }
        }

    def portal_my_tasks_prepare_task_search_domain(self, search_in, search):
        search_domain = []
        if search and search_in:
            if search_in in ('content', 'all'):
                search_domain = OR([
                    search_domain, [
                        '|',
                        ('name', 'ilike', search),
                        ('description', 'ilike', search)
                    ]
                ])

            if search_in in ('customer', 'all'):
                search_domain = OR([
                    search_domain, [('partner_id', 'ilike', search)]
                ])
            if search_in in ('message', 'all'):
                search_domain = OR([
                    search_domain, [('message_ids.body', 'ilike', search)]
                ])
            if search_in in ('stage', 'all'):
                search_domain = OR([
                    search_domain, [('stage_id', 'ilike', search)]
                ])
        return search_domain

    def portal_my_tasks_prepare_task_search(self, projects, searchbar,
                                            date_begin=None, date_end=None,
                                            sortby=None,
                                            filterby=None, search=None,
                                            search_in='content', **kw):

        # This is a good place to add mandatory criteria

        domain = [('project_id.privacy_visibility', '=', 'portal')]

        for proj in projects:
            searchbar['filters'].update({
                str(proj.id): {
                    'label': proj.name,
                    'domain': [('project_id', '=', proj.id)]
                }
            })

        domain += searchbar['filters'][filterby]['domain']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('project.task', domain)
        if date_begin and date_end:
            domain += [
                ('create_date', '>', date_begin),
                ('create_date', '<=', date_end)
            ]

        # search
        search_domain = self.portal_my_tasks_prepare_task_search_domain(
            search_in, search
        )
        domain += search_domain

        return {
            'domain': domain,
            'archive_groups': archive_groups,
        }

    def portal_my_tasks_prepare_values(self, page=1, date_begin=None,
                                       date_end=None, sortby=None,
                                       filterby=None,
                                       search=None, search_in='content', **kw):

        # default sort by value
        if not sortby:
            sortby = 'date'

        # default filter by value
        if not filterby:
            filterby = 'all'

        searchbar = self.portal_my_tasks_prepare_searchbar()
        projects = request.env['project.project'].search([
            ('privacy_visibility', '=', 'portal')
        ])

        search = self.portal_my_tasks_prepare_task_search(
            projects, searchbar, date_begin, date_end, sortby, filterby,
            search, search_in, **kw
        )

        # task count
        task_count = request.env['project.task'].search_count(search['domain'])

        # pager
        pager = portal_pager(
            url="/my/tasks",
            url_args={
                'date_begin': date_begin,
                'date_end': date_end,
                'sortby': sortby,
                'filterby': filterby
            },
            total=task_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        sort_order = searchbar['sorting'][sortby]['order']
        tasks = request.env['project.task'].search(
            search['domain'],
            order=sort_order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        request.session['my_tasks_history'] = tasks.ids[:100]

        return {
            'date': date_begin,
            'date_end': date_end,
            'projects': projects,
            'tasks': tasks,
            'page_name': 'task',
            'archive_groups': search['archive_groups'],
            'default_url': '/my/tasks',
            'pager': pager,
            'searchbar_sortings': searchbar['sorting'],
            'searchbar_inputs': searchbar['inputs'],
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(
                sorted(searchbar['filters'].items())
            ),
            'filterby': filterby,
        }

    def portal_my_tasks_render(self, values):
        return request.render("project.portal_my_tasks", values)

    # ========================
    #   Portal My Tasks
    # ========================
    @http.route([
        '/my/task/<int:task_id>'
    ], type='http', auth="user", website=True)
    def portal_my_task(self, task_id=None, **kw):
        values = self.portal_my_task_prepare_values(task_id, **kw)
        return self.portal_my_task_render(values)

    def portal_my_task_prepare_values(self, task_id=None, **kw):
        task = request.env['project.task'].browse(task_id)
        vals = {
            'task': task,
            'user': request.env.user
        }
        history = request.session.get('my_tasks_history', [])
        vals.update(get_records_pager(history, task))
        return vals

    def portal_my_task_render(self, values):
        return request.render("project.portal_my_task", values)
