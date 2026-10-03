Connect your GitLab repositories, step by step:

1. **Configure the base module first**: webhook endpoint, shared
   authorization token and project mapping are documented in
   `project_git`.

2. **Set one `project_gitlab.token.<instance-url>/` system parameter
   per GitLab instance** to a GitLab access token. Create the token on
   GitLab from your avatar menu, **Edit profile > Access tokens**; in
   Odoo, with the developer mode activated, set the parameter from
   **Settings > Technical > Parameters > System Parameters**. The key
   is the instance root URL **with a trailing slash**, e.g.
   `project_gitlab.token.https://gitlab.com/`. This token lets Odoo
   call the GitLab API: fetch the MR commits, post messages on the MR,
   deploy the webhook, retry CI jobs.

   A missing token — or the demo default shipped by the module — makes
   the API calls fail with an explicit error: replace it with a real
   token.

   When the MR commits cannot be fetched via API (e.g. missing token),
   the head commit carried by the MR payload is used as fallback.

3. **Deploy the webhook** with the **Create Webhooks** button on the
   project form (**Project > Configuration > Projects**, open the
   project; to configure it by hand instead, use the project page on
   GitLab, **Settings > Webhooks**). The webhook is subscribed to push,
   merge request and pipeline events; GitLab sends the authorization
   token verbatim in the `X-Gitlab-Token` header and the module
   verifies it.

4. **Optionally, map GitLab users to Odoo users**: go to **Settings >
   Users & Companies > Users**, open the user and fill the **Gitlab
   Username** field with their GitLab username. The author of each
   merge request is matched against this field and shown on the MR
   record as **Created by User** (left empty when no user matches).
