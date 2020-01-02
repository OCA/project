# -*- coding: utf-8 -*-
# Copyright 2019 Kmee Informática LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project Wsjf',
    'summary': """
        This module implements the Weighted Shortest Job First prioritization model.

        Weighted Shortest Job First (WSJF) is a prioritization model used to sequence jobs (eg., Features, Capabilities, and Epics) to produce maximum economic benefit. WSJF is estimated as the Cost of Delay (CoD) divided by job size.

        Calculating the Cost of Delay

        Four primary elements contribute to the Cost of Delay:
         - User-business value – Do our users prefer this over that? What is the revenue impact on our business? Is there a potential penalty or other adverse consequences if we delay?
         - Time criticality – How does the user/business value decay over time? Is there a fixed deadline? Will they wait for us or move to another solution? Are there Milestones on the critical path impacted by this?
         - Risk reduction-opportunity enablement value – What else does this do for our business? Does it reduce the risk of this or a future delivery? Is there value in the information we will receive? Will this feature open up new business opportunities?
         - Internal pressure – It is the pressure given internally, given a trade agreement, a defaulting customer, need for cash increase (work harder on a project that gives you more revenue)

        Duration
        
        Next, we need to understand the job duration. That can be pretty difficult to determine, especially early on when we might not know who is going to do the work or the capacity allocation for the teams. Fortunately, we have a ready proxy: job size. In systems with fixed resources, job size is a good proxy for the duration. (If I’m the only one mowing my lawn, and the front yard is three times bigger than the backyard, it’s going to take three times longer.) Also, we know how to estimate item size in Story points already. Taking job size, we have a reasonably straightforward calculation for comparing jobs via WSJF: WSJF = Cost of Delay / Job size.
    """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Kmee Informática LTDA,Odoo Community Association (OCA)',
    'website': 'www.kmee.com.br',
    'depends': [
        'project',
    ],
    'data': [
        'views/project_project.xml',
        'views/project_task.xml',
    ],
    'demo': [
    ],
}
