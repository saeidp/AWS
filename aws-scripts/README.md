# aws-scripts

Small operational scripts for managing an AWS Organizations estate: tag
compliance reporting, account-owner lookup, and Service Catalog inventory.

Python 3 with the standard library plus the `aws` CLI — no SDK dependency.

## Layout

| Path | What it does |
|---|---|
| `accounts-owner/` | Find and bulk-update the account-owner tag across the org. See its [README](accounts-owner/README.md). |
| `account_reports/generate_report_per_account.py` | Per-account tag-compliance reports (CSV/HTML) from AWS Resource Groups Tagging. |
| `Utilities/list_provisioned_products.py` | List Service Catalog provisioned products. |

## Requirements

- `aws` CLI on `PATH`, authenticated against the target account
- Python 3.12 (see `.python-version`); `uv sync` if you want the locked env

## Generated output is not committed

Every script writes reports containing live account IDs, resource ARNs, root
account emails, and staff names. Those paths are covered by `.gitignore` and
must stay out of version control. Account IDs in documentation are masked as
`<MGMT_ACCOUNT_ID>`.
