# Update: DSA Software SG, C.A. - Jonathan Guacaran <jonathan.guacaran@dsasoftware.com.ve>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Todo Lists',
    'version': '11.0.1.0.0',
    'category': 'Project Management',
    'sequence': 100,
    'summary': 'Personal Tasks, Contexts, Timeboxes',
    'description': """
Implement the *Getting Things Done* methodology
===============================================

This module implements a simple personal to-do list based on tasks. It adds an
editable list of tasks simplified to the minimum required fields in the project
application.

The to-do list is based on the *Getting Things Done* methodology. This
world-wide used methodology is used for personal time management improvement.

*Getting Things Done* (commonly abbreviated as *GTD*) is an action management
method created by David Allen, and described in a book of the same name.

*GTD* rests on the principle that a person needs to move tasks out of the mind
by recording them externally. That way, the mind is freed from the job of
remembering everything that needs to be done, and can concentrate on actually
performing those tasks.
    """,
    'author': "OpenERP SA,Odoo Community Association (OCA) \n Migrate By DSA Software SG, C.A. - Jonathan Guacaran",
    'license': 'AGPL-3',
    'depends': ['project'],
    'data': [
        'data/project_gtd_data.xml',
        'views/project_gtd_view.xml',
        'security/ir.model.access.csv',
        'wizard/project_gtd_empty_view.xml',
        'wizard/project_gtd_fill_view.xml',
    ],
    'demo': ['demo/project_gtd_demo.xml'],
    'test': ['test/task_timebox.yml'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
