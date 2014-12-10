# Project Assignment #
**Automatically reassign task to specified partner depending on stage**

## Functions ##
- For each stage, the partner can be specified in stage, then in project and finally task itself
- We use partner instead of user for more flexibility
- Use base inherit config

## Created Views ##
- * INHERIT project.project.form.assignpartner (form)
- * INHERIT project.project.tree.assignpartner (tree)
- * INHERIT project.task.form.assignpartner (form)
- * INHERIT project.task.search.assignpartner (search)
- * INHERIT project.task.tree.assignpartner (tree)
- * INHERIT project.task.type.form.assignpartner (form)
- project.assigned.partner.config.form (form)
- project.assigned.partner.config.tree (tree)

## Dependencies ##
- base_recursive_model	vc
- project

## Created Menus ##
- This module does not create menu.

## Defined Reports ##
- This module does not create report.