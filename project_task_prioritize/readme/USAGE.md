Priority Calculation
-------------------

The module calculates task priorities using a configurable formula. The default formula is:

    prioritizer_sum / (allocated_hours * (max_value - prioritizer_sum + 1))

Available variables in the formula:

* ``prioritizer_sum``: Sum of all selected prioritizer values
* ``max_value``: Sum of maximum values from all selected categories
* ``allocated_hours``: Number of hours allocated to the task
* ``rec``: The task record itself
