# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) 2011 Camptocamp SA (http://www.camptocamp.com) 
# All Right Reserved
#
# Author : Joël Grand-Guillaume (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
    "name" : "Project Hours Blocks Management",
    "description" : """

This module allows you to handle hours blocks, to follow for example the user support contracts. 
This means, you sell a product of type "hours block" then you input the spent hours on the hours block and 
you can track and follow how much has been used.

 """,
    "version" : "1.2",
    "author" : "Camptocamp",
    "category" : "Generic Modules/Projects & Services",
    "website": "http://www.camptocamp.com",
    "depends" : [
                 "account",
                 "hr_timesheet_invoice",
                 "analytic"
                ],
    "init_xml" : [],
    "update_xml" : [
                    "hours_block_view.xml",
                    "hours_block_menu.xml",
                    "report.xml",
                    "security/hours_block_security.xml",
                    "security/ir.model.access.csv",
                   ],
    "active": False,
    "installable": False
}
