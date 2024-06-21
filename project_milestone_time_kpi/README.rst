Project Milestone time KPI
==========================

.. contents:: Table of Contents

Context
-------
The module has just enriched the milestones tab on the project, in order to offer 3 new fields:

* Total Estimated Hours.
* Total Hours Spent.
* Total Remaining Work.

This option is advantageous because it allows you to compare the total hours spent on the project with the estimated hours of each milestone in order to be able to weight an overrun on a batch phase, and to see the time remaining on the batch by also having visual status of milestones.

These fields are added to the list view of projects, in order to facilitate monitoring.


Overview
--------
The module inherits two modules that have been added to allow to define an estimated time on the milestone
`(project_milestone_estimated_hours)`, and to calculate the times spent on a milestone `(project_milestone_spent_hours)`

The module add 4 new fields to project:

* **Total Estimated Hours**: Field calculated by taking into account the total of the 'Estimated hours' fields of each milestone associated with the project.
* **Total Spent Hours**: Field calculated by taking into account the total of the 'Hours spent' fields of each milestone associated with the project.
* **Remaining Estimated Hours**: Calculated field based on the following calculation: Total Estimated Hours - Total Hours Spent.
* **Total Remaining Work**: Field calculated based on the total of the ‘Remaining hours’ fields of the tasks associated with a project.

**Total Estimated Hours**, **Total Spent Hours** and **Total Remaining Work** are visible under the milestone tab
in form view and visible in tree view after milestones column.

Usage
-----
As a user, from a project whose **Use milestones** box is checked, go to the tab of a project.

1. Add 2 milestones:

* Analysis (estimated 10h).

    .. image:: project_milestone_time_kpi/static/description/milestone_1.png
        :width: 100%
        :align: center
        :height: 600px
        :alt: Milestone_1

* Realization (estimated 20h).

    .. image:: project_milestone_time_kpi/static/description/milestone_2.png
        :width: 100%
        :align: center
        :height: 600px
        :alt: Milestone_2

2. From the project tasks, assigned to the respective milestones, add timelines.

    .. image:: project_milestone_time_kpi/static/description/milestone_spent_hours.png
        :width: 100%
        :align: center
        :height: 600px
        :alt: Milestone_spent_hours

You can see that the estimated times of the milestones, and the times spent are well up in the list of milestones.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)
