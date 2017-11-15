# -*- coding: utf-8 -*-
##############################################################################
#
#
#
##############################################################################

{
    'name': 'Project Scrum',
   'summary': 'Use Scrum Method  to manager your project',
    'version': '8.0.1.1.0',
    'category': 'Project Management',
    'description': """
Using Scrum to plan the work in a team.
=========================================================================================================

More information:
    """,
    'author': "Tenovar:Mohamed Habib Challouf,Odoo Community Association (OCA)",
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
   
   
     'qweb': ['static/src/xml/project_scrum.xml'],
    'demo': ['project_scrum_demo.xml'],
    'installable': True,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
