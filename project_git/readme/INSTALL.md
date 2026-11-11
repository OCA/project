This module requires no git platform Python library, but it does
nothing by itself: install one bridge module per platform you want to
connect (`project_github` for GitHub, `project_gitlab` for GitLab).
Each bridge installs the Python library of its platform.

Webhook processing relies on the `queue_job` module, from the
[OCA/queue](https://github.com/OCA/queue) repository: the events are
processed asynchronously by its jobrunner, which must be active — add
`queue_job` to the `server_wide_modules` of your instance (see the
`queue_job` documentation). On hostings where the standard jobrunner
cannot run (e.g. Odoo.sh), also install `queue_job_cron_jobrunner`
(same repository) to process the jobs from a cron instead.
