Links a project created from **project_template** to the template it came
from, and keeps its task stages following the template's own
**project_task_stage_order** order.

When a template project is copied, the person copying it can choose to keep
the new project linked to the template. A linked copy's task stages (order,
additions and removals) can only be changed from the template: any change
made on the template is applied to every linked copy automatically, and
linked copies cannot change their own stages. An independent copy behaves
like any other project and keeps no link to the template.

Tasks are never copied, whether the copy is linked or independent — only the
stage structure is.
