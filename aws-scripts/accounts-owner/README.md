# accounts-owner

Find which AWS accounts in an AWS Organizations org a given person owns.

Ownership is not an AWS concept — it is recorded in this org as an **AWS
Organizations account tag**:

| Tag key | Notes |
|---|---|
| `<prefix>:primary-contact-owner-email` | the owner; present on nearly every account |
| `<prefix>:secondary-contact-owner-email` | rare |
| `<prefix>:description` | free-text purpose of the account |
| `<prefix>:billing-contact-email` | rare |

`<prefix>` is your organisation's tag namespace. The scripts read it from
`OWNER_TAG_PREFIX` and default to `org`. Set it once in a `.env` at the repo
root — the scripts load the nearest `.env` at or above themselves, so no
`export` and no `python-dotenv` needed:

```bash
cp .env.example .env      # then edit:
# OWNER_TAG_PREFIX=acme   ->  acme:primary-contact-owner-email
```

`.env` is git-ignored (it names your organisation); `.env.example` is the
tracked template. A real environment variable always beats the file, so a
one-off run can still override it:

```bash
OWNER_TAG_PREFIX=other python3 find_account_owner.py someone@example.edu
```

If nothing matches, the scripts warn on stderr and list the tag prefixes they
actually saw, so a wrong prefix does not masquerade as "nobody owns anything".

There is **no single API call** that filters accounts by tag value, so the
script walks every account with `ListTagsForResource` in parallel.

## Requirements

- Credentials for the **management account** (or a delegated
  administrator for Organizations). An SSO permission set with `organizations:ListAccounts`,
  `organizations:ListTagsForResource` and (for tagging) `organizations:TagResource`
  is sufficient.
- `aws` CLI on `PATH`, Python 3 (standard library only — no pip installs).

## Files

| File | What it is |
|---|---|
| `find_account_owner.py` | the lookup script |
| `apply_owner_tags.sh` | bulk-sets the owner tag from a `to_change.tsv`, with rollback |
| `ou_account_owners.py` | the reverse lookup: every owner in an OU and the accounts they own |

Data files (`accounts_tagged_cache.json`, `to_change.tsv`,
`rollback_previous_owners.json`, and any generated reports) contain live account
IDs, root emails, and staff names. They are **git-ignored** and are not part of
this repo — generate them locally with `--dump-cache`.

## Usage

```bash
python3 find_account_owner.py <email> [-o OUT] [--format txt|csv|json]
                                      [--all-tags] [--contains]
                                      [--workers N] [--cache FILE]
                                      [--dump-cache FILE]
```

| Option | Effect |
|---|---|
| `-o OUT` | write to a file instead of stdout |
| `--format` | `txt` (default, aligned table), `csv`, or `json` (raw account objects) |
| `--all-tags` | match the email against *any* tag value, not just the two owner tags |
| `--contains` | substring match instead of exact match |
| `--workers N` | parallel API calls (default 6) |
| `--cache FILE` | read from a previous dump — offline and instant, no API calls |
| `--dump-cache FILE` | on a live run, also save the full account+tag dump |

### Examples

Report one owner to the terminal (live; a few minutes for a large org):

```bash
python3 find_account_owner.py first.last@example.edu
```

Write a CSV for a ticket or spreadsheet:

```bash
python3 find_account_owner.py first.last@example.edu \
    -o owner_accounts.csv --format csv
```

Re-query without hitting the API at all, using the saved dump:

```bash
python3 find_account_owner.py first.last@example.edu \
    --cache accounts_tagged_cache.json
```

Refresh the cache while running a report:

```bash
python3 find_account_owner.py <email> --dump-cache accounts_tagged_cache.json
```

Everyone whose owner email is on a given domain (substring match):

```bash
python3 find_account_owner.py @example.edu --contains --format csv -o all_owners.csv
```

Find an account by any tag value, not just ownership:

```bash
python3 find_account_owner.py "Research Analytics" --all-tags --contains
```

## Reporting a whole OU

`ou_account_owners.py` answers the other direction: given an OU, who owns the
accounts under it, and which accounts does each of them own.

```bash
python3 ou_account_owners.py <ou-id|ou-name|root-id> [-o OUT]
                             [--format txt|json|csv] [--no-recursive]
                             [--workers N] [--cache FILE] [--dump-cache FILE]
```

| Option | Effect |
|---|---|
| `--format` | `txt` (default, one block per owner), `json`, or `csv` (one row per account) |
| `--no-recursive` | only accounts sitting directly in the OU, not in child OUs |
| `-o OUT` | write to a file instead of stdout |
| `--dump-cache FILE` | save the raw account+tag+OU dump for offline re-runs |
| `--cache FILE` | re-render from such a dump, no API calls |

The OU can be an id (`ou-xxxx-xxxxxxxx`), a root id (`r-xxxx`), or an OU **name** —
names are not unique in the tree, so if several match the script prints the
candidates with their paths and exits rather than guessing.

By default it walks the **whole subtree**: `ListAccountsForParent` only returns
direct children, so an OU with child OUs would otherwise report a fraction of
its accounts. Compare:

```bash
python3 ou_account_owners.py <OU_NAME>                # whole subtree
python3 ou_account_owners.py <OU_NAME> --no-recursive # direct children only
```

Accounts with no `<prefix>:primary-contact-owner-email` are grouped under
`(no owner tag)` rather than dropped, and the header prints
`Accounts: N (tagged + untagged)` so a complete report is distinguishable from
a lossy one. `<prefix>:secondary-contact-owner-email` is shown as a field on the
account, not as a second owner group, so the per-owner counts stay additive.

Examples:

```bash
# on screen
python3 ou_account_owners.py <OU_ID>

# JSON report for a ticket
python3 ou_account_owners.py <OU_NAME> --format json -o owners.json

# every owner in the whole org
python3 ou_account_owners.py <ROOT_ID> --format csv -o all_ou_owners.csv
```

The two caches are **not** interchangeable: `find_account_owner.py`'s dump comes
from `list-accounts` and carries no OU information, so `ou_account_owners.py`
rejects it with an explicit message.

## Caveats

- Results reflect **the tag only**. Accounts carrying no owner tag will never
  appear in any owner's report — `ou_account_owners.py` groups them under
  `(no owner tag)` so at least they are visible.
- The cache is a point-in-time snapshot. Re-run live (or with
  `--dump-cache`) when accounts have been created, retagged, or closed.
- "Owns" here means *contact tag*, not access. If you need who can actually
  log in, query IAM Identity Center account assignments instead — that is a
  different data source entirely.

## Doing it by hand

The equivalent one-liner, if you ever need it without the script — correct but
slow, since it is serial and ignores pagination past 20 accounts:

```bash
aws organizations list-accounts --query 'Accounts[].Id' --output text | tr '\t' '\n' | \
while read id; do
  aws organizations list-tags-for-resource --resource-id "$id" \
    --query "Tags[?Value=='first.last@example.edu'].Value" --output text \
    | grep -q . && echo "$id"
done
```
