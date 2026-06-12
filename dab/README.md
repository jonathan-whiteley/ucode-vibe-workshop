# Starter DAB for Module 6

This is the skeleton attendees clone in Module 6 to package their workshop assets as a Databricks Asset Bundle.

The bundle includes:

- A `resources.apps` entry referencing the attendee's AppKit app
- Bundle variables for `genie_space_id` and `dashboard_id`
- A daily multi-task job (refresh derived tables → score sentiment via FMAPI → redeploy app)
- Two targets: `dev` and `prod`

## Customizing

Search for `<INITIALS>` and `<TODO>` in `databricks.yml` and the job task files; replace with your values during Module 6.

## Deploy

```bash
databricks bundle deploy --target dev
databricks bundle run occ-daily-refresh --target dev
```

(See the Lab Companion Guide Module 6 for the full walkthrough.)
