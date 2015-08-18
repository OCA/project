# -*- encoding: utf-8 -*-
######################################################################################################
#
# Copyright (C) B.H.C. sprl - All Rights Reserved, http://www.bhc.be
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied,
# including but not limited to the implied warranties
# of merchantability and/or fitness for a particular purpose
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

{
    "name" : "Shared Calendar",
    "version" : "1.0",
    "author" : "BHC",
    "website" : "http://www.bhc.be/en/application/capacity-planning",
    "category" : "Generic Modules/Others",
    "depends" : ["base","project"],
    "description" : """The shared calendar module allows you to synchronize different objects in one calendar such as tasks, phone calls, meetings, vacation... 
    Of course, you may also add custom objects in relation with your business.
    You will also be able to manage in one place all your employees calendar so it will be easy to check in one view all your staff agenda.
    The added value of this module is that you may modify elements in the shared calendar with a direct impact on the individual’s calendar by clicking on the element but also via the drag and drop option.""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["security/planning_management_security.xml","security/ir.model.access.csv","shared_calendar.xml"],
    'images': ['images/Calendar.png','images/Confguration.png','images/Edition.png'],
    "active": False,
    "installable": True,
}
