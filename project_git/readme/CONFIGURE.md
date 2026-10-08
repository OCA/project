## Configuration at a glance

The complete setup, end to end — each step is detailed in the sections
below or in the platform bridge documentation:

1. **Install the platform bridge** of your platform (`project_github`,
   `project_gitlab`, or both): this base module alone processes no
   event.
2. **Set the shared webhook secret** in the
   `project_git.authorization_token` system parameter: incoming
   webhook requests are authorized against it.
3. **Set the platform API token** system parameter of the bridge
   (`project_github.token` / `project_gitlab.token.<instance-url>/`):
   it lets Odoo call the platform API.
4. **Map the repository** on the Odoo project: paste the repository
   home page URL (e.g. `https://github.com/myorg/myrepo`) in the
   **Git Project URL** field of the project form.
5. **Deploy the webhook** with the **Create Webhooks** button on the
   same form (the endpoint URL is built from `web.base.url`), or
   configure it by hand on the repository pointing to
   `https://<your-odoo-host>/project_git/webhook/`.
6. Done: reference your tasks from git — an issue key like `ABC-123`
   or an explicit `taskid#<id>` in branch names, commit messages and
   PR/MR titles — and the git activity shows up on the tasks.

## Webhook endpoint

Configure your repositories to send webhooks (push, merge/pull request,
pipeline events) to:

    https://<your-odoo-host>/project_git/webhook/

In the webhook settings of the repository, set a secret token: incoming
requests are authorized against it (each platform bridge implements the
verification method of its platform, e.g. a token header or a payload
signature; the exact repository pages are documented in the bridges).

The webhook can also be deployed automatically: once the project is
mapped (see below) and the system parameters are set, the **Create
Webhooks** button on the Odoo project form (**Project > Configuration >
Projects**, open the project) creates the webhook on the repository
through the platform bridge. Deploying again replaces the webhook, so
the button can be reused after changing the Odoo base URL or the token.

## System parameters

With the developer mode activated, go to **Settings > Technical >
Parameters > System Parameters** and set:

- `project_git.authorization_token`: the secret token set on the
  webhooks. Incoming requests are rejected when this parameter is
  missing or still set to the demo default.

The API tokens used by Odoo to call the platforms are configured on the
bridge modules (see their documentation).

## Project mapping

Go to **Project > Configuration > Projects**, open the project and set
the repository home page URL (e.g. `https://gitlab.com/mygroup/myrepo`)
in the **Git Project URL** field of the **Settings** tab; a trailing
`.git` is tolerated.

A second repository (e.g. a separate development repo) can be mapped
in the **Git Dev Project URL** field: it behaves the same for matching,
and the **Create Webhooks** button deploys the webhook on both.

Pattern-based matching only searches the tasks of the mapped projects:
without a mapped project, pattern keys match nothing. Explicit
`taskid#`/`tid#` references resolve globally and need no mapping.
