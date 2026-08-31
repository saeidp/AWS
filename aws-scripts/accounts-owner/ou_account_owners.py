#!/usr/bin/env python3
"""
Report every account owner in an AWS Organizations OU, and which accounts each
of them owns.

Ownership is recorded as an account tag (see find_account_owner.py):

    <prefix>:primary-contact-owner-email
    <prefix>:secondary-contact-owner-email   (rare, shown as a field, not a group)

The tag prefix is site-specific: set OWNER_TAG_PREFIX to your organisation's tag
namespace (default "org"), in the environment or in a .env at the repo root.

Given an OU (by id, or by name if it is unique in the tree) this walks the OU
subtree, reads the tags of every account it finds, and groups the accounts by
owner email.

Must be run with credentials in the management account or a delegated
administrator for Organizations. Needs organizations:ListRoots,
ListOrganizationalUnitsForParent, ListAccountsForParent, DescribeOrganizationalUnit
and ListTagsForResource.

Usage:
    python3 ou_account_owners.py <ou-id|ou-name|root-id> [-o OUTFILE]
            [--format txt|json|csv] [--no-recursive] [--workers N]
            [--dump-cache FILE] [--cache FILE]

Examples:
    python3 ou_account_owners.py ou-abcd-12345678
    python3 ou_account_owners.py Workloads --format json -o workloads_owners.json
    python3 ou_account_owners.py r-abcd --dump-cache ou_accounts_cache.json
"""
import argparse
import concurrent.futures as cf
import csv
import datetime
import io
import json
import sys

from find_account_owner import (aws, warn_if_prefix_unused, PRIMARY_TAG_KEY,
                                SECONDARY_TAG_KEY, DESCRIPTION_TAG_KEY)

PRIMARY_KEY, SECONDARY_KEY = PRIMARY_TAG_KEY, SECONDARY_TAG_KEY
NO_OWNER = "(no owner tag)"


def paginate(args, key):
    """Yield every item of a paginated Organizations list-* call."""
    token = None
    while True:
        page = aws(args + (["--next-token", token] if token else []))
        yield from page[key]
        token = page.get("NextToken")
        if not token:
            return


def list_roots():
    return list(paginate(["organizations", "list-roots"], "Roots"))


def child_ous(parent_id):
    return list(paginate(["organizations", "list-organizational-units-for-parent",
                          "--parent-id", parent_id], "OrganizationalUnits"))


def child_accounts(parent_id):
    return list(paginate(["organizations", "list-accounts-for-parent",
                          "--parent-id", parent_id], "Accounts"))


def resolve_ou(name_or_id):
    """Return (id, name, path) for an OU/root id, or search the tree by name."""
    if name_or_id.startswith("r-"):
        for r in list_roots():
            if r["Id"] == name_or_id:
                return r["Id"], r["Name"], r["Name"]
        sys.exit(f"no root with id {name_or_id}")

    if name_or_id.startswith("ou-"):
        try:
            ou = aws(["organizations", "describe-organizational-unit",
                      "--organizational-unit-id", name_or_id])["OrganizationalUnit"]
        except RuntimeError as e:
            sys.exit(f"cannot describe {name_or_id}: {e}")
        return ou["Id"], ou["Name"], find_path(ou["Id"], ou["Name"])

    # Not an id: walk the whole tree looking for OUs with this name. Names are
    # not unique across the tree, so refuse to guess when several match.
    matches = []
    for root in list_roots():
        walk_names(root["Id"], root["Name"], name_or_id.lower(), matches)
    if not matches:
        sys.exit(f"no OU (or root) named {name_or_id!r}; pass an ou-... id instead")
    if len(matches) > 1:
        print(f"{name_or_id!r} matches {len(matches)} OUs - re-run with the id:",
              file=sys.stderr)
        for oid, _, path in matches:
            print(f"  {oid}  {path}", file=sys.stderr)
        sys.exit(2)
    return matches[0]


def walk_names(parent_id, parent_path, wanted, out):
    for ou in child_ous(parent_id):
        path = f"{parent_path}/{ou['Name']}"
        if ou["Name"].lower() == wanted:
            out.append((ou["Id"], ou["Name"], path))
        walk_names(ou["Id"], path, wanted, out)


def find_path(ou_id, ou_name):
    """Human-readable path for an OU, walking *up* to the root (O(depth) calls)."""
    parts, current = [ou_name], ou_id
    while True:
        parents = aws(["organizations", "list-parents",
                       "--child-id", current])["Parents"]
        if not parents:
            break
        parent = parents[0]
        if parent["Type"] == "ROOT":
            name = next((r["Name"] for r in list_roots()
                         if r["Id"] == parent["Id"]), parent["Id"])
            parts.append(name)
            break
        parts.append(aws(["organizations", "describe-organizational-unit",
                          "--organizational-unit-id", parent["Id"]]
                         )["OrganizationalUnit"]["Name"])
        current = parent["Id"]
    return "/".join(reversed(parts))


def collect_accounts(ou_id, ou_path, recursive):
    """Accounts in the OU (and, by default, every OU beneath it)."""
    found, queue = [], [(ou_id, ou_path)]
    while queue:
        pid, path = queue.pop(0)
        for a in child_accounts(pid):
            found.append({**a, "OuId": pid, "OuPath": path})
        if recursive:
            queue += [(ou["Id"], f"{path}/{ou['Name']}") for ou in child_ous(pid)]
    return found


def add_tags(account):
    tags = aws(["organizations", "list-tags-for-resource",
                "--resource-id", account["Id"]])["Tags"]
    return {**account, "Tags": {t["Key"]: t["Value"] for t in tags}}


def collect(ou_id, ou_path, recursive, workers):
    accounts = collect_accounts(ou_id, ou_path, recursive)
    print(f"fetching tags for {len(accounts)} accounts in {ou_path}...",
          file=sys.stderr)
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(add_tags, accounts))


def group_by_owner(accounts):
    """[(display_email, [accounts])], most accounts first. Untagged go last."""
    groups = {}
    for a in accounts:
        raw = a["Tags"].get(PRIMARY_KEY, "").strip()
        key = raw.lower() or NO_OWNER
        display, items = groups.setdefault(key, (raw or NO_OWNER, []))
        items.append(a)
    ordered = sorted(
        (g for k, g in groups.items() if k != NO_OWNER),
        key=lambda g: (-len(g[1]), g[0].lower()),
    )
    if NO_OWNER in groups:
        ordered.append(groups[NO_OWNER])
    for _, items in ordered:
        items.sort(key=lambda a: a["Name"].lower())
    return ordered


def render_txt(groups, ou, source, recursive):
    total = sum(len(items) for _, items in groups)
    untagged = sum(len(i) for e, i in groups if e == NO_OWNER)
    out = [
        f"Account owners in OU {ou['name']} ({ou['id']})",
        f"OU path: {ou['path']}   Scope: {'subtree' if recursive else 'direct children only'}",
        f"Source: AWS Organizations account tags ({source})",
        f"Generated: {datetime.date.today().isoformat()}",
        f"Owners: {len(groups) - (1 if untagged else 0)}   "
        f"Accounts: {total} ({total - untagged} tagged + {untagged} untagged)",
        "",
    ]
    for email, items in groups:
        out.append(f"{email}  -  {len(items)} account{'s' if len(items) != 1 else ''}")
        out.append("  %-14s %-38s %-10s %s" % ("ACCOUNT ID", "ACCOUNT NAME",
                                               "STATUS", "OU PATH"))
        out.append("  " + "-" * 118)
        for a in items:
            out.append("  %-14s %-38s %-10s %s"
                       % (a["Id"], a["Name"], a["Status"], a["OuPath"]))
            second = a["Tags"].get(SECONDARY_KEY)
            if second:
                out.append(f"  {'':14} secondary owner: {second}")
        out.append("")
    return "\n".join(out) + "\n"


def render_json(groups, ou, source, recursive):
    total = sum(len(items) for _, items in groups)
    doc = {
        "ou": ou,
        "scope": "subtree" if recursive else "direct",
        "source": source,
        "generated": datetime.date.today().isoformat(),
        "total_accounts": total,
        "owners": [
            {
                "email": email,
                "account_count": len(items),
                "accounts": [
                    {
                        "id": a["Id"],
                        "name": a["Name"],
                        "status": a["Status"],
                        "root_email": a["Email"],
                        "ou_id": a["OuId"],
                        "ou_path": a["OuPath"],
                        "description": a["Tags"].get(DESCRIPTION_TAG_KEY, ""),
                        "secondary_owner": a["Tags"].get(SECONDARY_KEY, ""),
                    }
                    for a in items
                ],
            }
            for email, items in groups
        ],
    }
    return json.dumps(doc, indent=2) + "\n"


def render_csv(groups):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["OwnerEmail", "AccountId", "AccountName", "Status", "RootEmail",
                "OuId", "OuPath", "Description", "SecondaryOwnerEmail"])
    for email, items in groups:
        for a in items:
            t = a["Tags"]
            w.writerow([email, a["Id"], a["Name"], a["Status"], a["Email"],
                        a["OuId"], a["OuPath"], t.get(DESCRIPTION_TAG_KEY, ""),
                        t.get(SECONDARY_KEY, "")])
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ou", help="OU id (ou-...), root id (r-...), or unique OU name")
    ap.add_argument("-o", "--out")
    ap.add_argument("--format", choices=["txt", "json", "csv"], default="txt")
    ap.add_argument("--no-recursive", action="store_true",
                    help="only accounts directly in the OU, not in child OUs")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--dump-cache", help="also save the raw account+tag dump here")
    ap.add_argument("--cache", help="read a previous --dump-cache file instead of "
                                    "calling the API")
    args = ap.parse_args()
    recursive = not args.no_recursive

    if args.cache:
        dump = json.load(open(args.cache))
        if not isinstance(dump, dict) or "accounts" not in dump or "ou" not in dump:
            sys.exit(f"{args.cache} is not an ou_account_owners dump (needs 'ou' and "
                     f"'accounts'); caches from find_account_owner.py have no OU data")
        ou, accounts = dump["ou"], dump["accounts"]
        if args.no_recursive and dump.get("scope") == "subtree":
            # the dump holds the whole subtree; narrow it to the OU itself
            accounts = [a for a in accounts if a["OuId"] == ou["id"]]
        else:
            recursive = dump.get("scope", "subtree") == "subtree"
        source = f"cache {args.cache}"
    else:
        ou_id, ou_name, ou_path = resolve_ou(args.ou)
        ou = {"id": ou_id, "name": ou_name, "path": ou_path}
        accounts = collect(ou_id, ou_path, recursive, args.workers)
        ident = aws(["sts", "get-caller-identity"])
        source = f"live, via management account {ident['Account']}"
        if args.dump_cache:
            json.dump({"ou": ou, "scope": "subtree" if recursive else "direct",
                       "accounts": accounts}, open(args.dump_cache, "w"), indent=1)

    warn_if_prefix_unused(accounts)
    groups = group_by_owner(accounts)

    if args.format == "txt":
        text = render_txt(groups, ou, source, recursive)
    elif args.format == "json":
        text = render_json(groups, ou, source, recursive)
    else:
        text = render_csv(groups)

    if args.out:
        open(args.out, "w").write(text)
        print(f"wrote {len(groups)} owners / {len(accounts)} accounts to {args.out}",
              file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
