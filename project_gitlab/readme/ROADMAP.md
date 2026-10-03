- The **Update Odoo.sh** button retries the latest successful GitLab
  CI job named `odoo_sh_deploy` — the job name is hardcoded, reflecting
  the original author's deployment workflow, where a CI job pushes the
  code to an Odoo.sh instance. The job name could be made configurable
  (e.g. a field on the project, defaulting to `odoo_sh_deploy`),
  turning the button into a generic "retry the deploy CI job" action
  for any deployment pipeline.
