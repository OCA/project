# -*- coding: utf-8 -*-
# (c) 2012 - 2013 Daniel Reis
# (c) 2017 Rigoberto Martínez <rigo1985@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Project Issue related Tasks',
    'summary': 'Use Tasks to support Issue resolution reports',
    'version': '0.1.0',
    'category': 'Project Management',
    'description': """\
Support for the use case where solving an Issue means a Task should be done,
such as an on site visit, and a report must be made to document the work done.
This is a common scenario in technical field services.

The Issue form already has a "Task" field, allowing to create a Task related
to an Issue.
This module adds some usability improvements:

  * "Create Task" button on the Issue form
  * Automaticaly Close the Issue when the Task is Closed
  * Automatically Cancel the Task when Issue is Cancelled
  * Make the Task also visible to all followers of the related Issue
""",
    'author': "Tecnativa, Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'license': 'AGPL-3',
    'depends': [
        'project_issue',
        ],
    'data': [
        'security/ir.model.access.csv',
        'security/project_security.xml',
        'views/project_issue_view.xml',
        'views/project_task_cause_view.xml',
        'views/project_task_view.xml',
        ],
    'installable': True,
}
