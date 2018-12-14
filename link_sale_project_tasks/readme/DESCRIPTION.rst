This module provides a new invoicing policy on a product to transform your sale order in projects and tasks (and to update those in case sale order is updated).

A new product template invoicing policy section in order to set how each product should behave when transformed from sale order to project/task :
This new invoicing policy available only for service products (called "Create a project and link tasks"). This would allow you to create a project / task when the corresponding product is defined in a confirmed sale order, but is not tracking the hours spent on the task for invoicing (as opposed to existing "Create task and track hours" option).

The planned hours on each task are calculated based on the order line amount / configurable daily price * configurable hours per day.

This module also allows to define per product default stage or project to which the tasks will be assigned.

This module depends upon *sale_timesheet* and *project* modules.
