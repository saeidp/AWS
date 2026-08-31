#!/usr/bin/env python3
"""
List the AWS accounts in the organisation owned by a given person.

Ownership is recorded as an AWS Organizations *account tag*:

    <prefix>:primary-contact-owner-email
    <prefix>:secondary-contact-owner-email   (rare)

The tag prefix is site-specific. Set OWNER_TAG_PREFIX to match your
organisation's tag namespace (default "org"), either in the environment or in a
.env file at the repo root:

    export OWNER_TAG_PREFIX=acme      # -> acme:primary-contact-owner-email

There is no single API that filters accounts by tag, so this walks every
account with ListTagsForResource, in parallel (a few hundred accounts takes
minutes serially, far less threaded).

Must be run with credentials in the management account or a delegated
administrator for Organizations.

Usage:
    python3 find_account_owner.py <email> [-o OUTFILE] [--format txt|csv|json]
                                          [--all-tags] [--workers N]

    <email>       owner email to search for (case-insensitive, substring match
                  with --contains, exact match by default)
    -o OUTFILE    write the report here (default: stdout)
    --format      output format (default txt)
    --all-tags    match the email against *any* account tag value, not just
                  the two owner-contact tags
    --contains    substring match instead of exact match
    --dump-cache  also write the full account+tag dump here, so a later run
                  can use --cache and skip the API calls entirely
    --cache FILE  read accounts from a previous --dump-cache file (offline)

Examples:
    python3 find_account_owner.py first.last@example.edu
    python3 find_account_owner.py other.person@example.edu -o owner.txt
    python3 find_account_owner.py @example.edu --contains --format csv
"""
import argparse
import concurrent.futures as cf
import csv
import datetime
import json
import os
import pathlib
import subprocess
import sys
import time

def load_dotenv():
    """Read KEY=VALUE from the nearest .env at or above this script.

    Only fills in names that are not already set, so a real environment
    variable always wins over the file. No dependency on python-dotenv.
    """
    here = pathlib.Path(__file__).resolve().parent
    for d in [here, *here.parents]:
        env = d / ".env"
        if not env.is_file():
            continue
        for line in env.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        return env
    return None


DOTENV = load_dotenv()

# Tag namespace is site-specific; override with OWNER_TAG_PREFIX (or .env).
TAG_PREFIX = os.environ.get("OWNER_TAG_PREFIX", "org")
PRIMARY_TAG_KEY = f"{TAG_PREFIX}:primary-contact-owner-email"
SECONDARY_TAG_KEY = f"{TAG_PREFIX}:secondary-contact-owner-email"
DESCRIPTION_TAG_KEY = f"{TAG_PREFIX}:description"
OWNER_TAG_KEYS = (PRIMARY_TAG_KEY, SECONDARY_TAG_KEY)


def warn_if_prefix_unused(accounts):
    """A wrong OWNER_TAG_PREFIX looks exactly like 'nobody owns anything'."""
    if accounts and not any(k in a["Tags"] for a in accounts for k in OWNER_TAG_KEYS):
        seen = sorted({k.split(":")[0] for a in accounts for k in a["Tags"] if ":" in k})
        where = f"loaded {DOTENV}" if DOTENV else "no .env found"
        print(f"warning: no account carries {PRIMARY_TAG_KEY!r} ({where}). "
              f"Tag prefixes actually in use: {', '.join(seen) or 'none'}. "
              f"Set OWNER_TAG_PREFIX to the right one.", file=sys.stderr)


def aws(args, retries=4):
    """Run an aws CLI command, returning parsed JSON. Retries on throttling."""
    last = ""
    for attempt in range(retries):
        p = subprocess.run(
            ["aws"] + args + ["--output", "json"], capture_output=True, text=True
        )
        if p.returncode == 0:
            return json.loads(p.stdout)
        last = p.stderr.strip()
        time.sleep(0.5 * 2 ** attempt)
    raise RuntimeError(f"aws {' '.join(args)} failed: {last[:300]}")


def list_accounts():
    accounts, token = [], None
    while True:
        args = ["organizations", "list-accounts"]
        if token:
            args += ["--next-token", token]
        page = aws(args)
        accounts += page["Accounts"]
        token = page.get("NextToken")
        if not token:
            return accounts


def account_tags(account):
    tags = aws(["organizations", "list-tags-for-resource",
                "--resource-id", account["Id"]])["Tags"]
    return {**account, "Tags": {t["Key"]: t["Value"] for t in tags}}


def collect(workers):
    accounts = list_accounts()
    print(f"fetching tags for {len(accounts)} accounts...", file=sys.stderr)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(account_tags, accounts))


def matches(account, email, all_tags, contains):
    keys = account["Tags"].keys() if all_tags else OWNER_TAG_KEYS
    for k in keys:
        v = account["Tags"].get(k, "").lower()
        if (email in v) if contains else (v == email):
            return True
    return False


def render_txt(hits, email, source):
    today = datetime.date.today().isoformat()
    out = [
        f"AWS accounts owned by {email}",
        f"Source: AWS Organizations account tags ({source})",
        f"Generated: {today}   Total: {len(hits)} accounts",
        "",
        "%-14s %-38s %-10s %s" % ("ACCOUNT ID", "ACCOUNT NAME", "STATUS", "ROOT EMAIL"),
        "-" * 120,
    ]
    for a in hits:
        out.append("%-14s %-38s %-10s %s"
                   % (a["Id"], a["Name"], a["Status"], a["Email"]))
    out += ["", "Descriptions:"]
    for a in hits:
        out.append("  %s (%s): %s"
                   % (a["Id"], a["Name"], a["Tags"].get(DESCRIPTION_TAG_KEY, "")))
    return "\n".join(out) + "\n"


def render_csv(hits):
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["AccountId", "Name", "Status", "Email", "JoinedTimestamp",
                "OwnerEmail", "SecondaryOwnerEmail", "Description"])
    for a in hits:
        t = a["Tags"]
        w.writerow([a["Id"], a["Name"], a["Status"], a["Email"],
                    a.get("JoinedTimestamp", ""),
                    t.get(PRIMARY_TAG_KEY, ""),
                    t.get(SECONDARY_TAG_KEY, ""),
                    t.get(DESCRIPTION_TAG_KEY, "")])
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("email")
    ap.add_argument("-o", "--out")
    ap.add_argument("--format", choices=["txt", "csv", "json"], default="txt")
    ap.add_argument("--all-tags", action="store_true")
    ap.add_argument("--contains", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dump-cache")
    ap.add_argument("--cache")
    args = ap.parse_args()

    if args.cache:
        accounts = json.load(open(args.cache))
        source = f"cache {args.cache}"
    else:
        accounts = collect(args.workers)
        ident = aws(["sts", "get-caller-identity"])
        source = f"live, via management account {ident['Account']}"
        if args.dump_cache:
            json.dump(accounts, open(args.dump_cache, "w"), indent=1)

    if not args.all_tags:   # --all-tags does not depend on the prefix
        warn_if_prefix_unused(accounts)

    email = args.email.lower()
    hits = [a for a in accounts if matches(a, email, args.all_tags, args.contains)]
    hits.sort(key=lambda a: a["Name"].lower())

    if args.format == "txt":
        text = render_txt(hits, args.email, source)
    elif args.format == "csv":
        text = render_csv(hits)
    else:
        text = json.dumps(hits, indent=2) + "\n"

    if args.out:
        open(args.out, "w").write(text)
        print(f"wrote {len(hits)} accounts to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
