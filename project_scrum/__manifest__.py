# -*- coding: utf-8 -*-


{
    'name': 'Project Scrum',
   'summary': 'Use Scrum Method  to manager your project',
    'version': '10',
    'category': 'Project Management',
    'description': """
Using Scrum to plan the work in a team.
=========================================================================================================

More information:
    """,
    'author': "Mohamed Habib Challouf,Samir Guesmi,Odoo Community Association (OCA)",
    'website': 'http://www.tenovar.com',
    'depends': [ 'base_setup',
                 'project',
                 'mail',
                 'hr_timesheet',
                 'web_kanban',
                 'web_planner',
                 'web_tour', ],
    'data': ['project_scrum_view.xml', 'sequences_projects.xml',
        'wizard/project_scrum_test_task_view.xml',
        'security/ir.model.access.csv',
        'security/project_security.xml',
       ],
     'external_dependencies': {
        'python' : ['bs4',],
    },
   
     'qweb': ['static/src/xml/project_scrum.xml'],
    'demo': ['project_scrum_demo.xml'],
    'installable': True,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
