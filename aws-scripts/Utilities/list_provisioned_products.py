#!/usr/bin/env python3
"""List Service Catalog provisioned product names, optionally filtered by substring.

Uses the default AWS CLI profile/region. Paginates through all results
since search-provisioned-products caps at 100 per page.

Usage:
    ./list_provisioned_products.py            # list all names
    ./list_provisioned_products.py -- --       # names containing '--'
    ./list_provisioned_products.py smaat       # names containing 'smaat'
"""
import argparse
import json
import subprocess


def fetch_all_names():
    names = []
    token = None
    while True:
        cmd = ["aws", "servicecatalog", "search-provisioned-products", "--output", "json"]
        if token:
            cmd += ["--page-token", token]
        out = json.loads(subprocess.check_output(cmd))
        names.extend(p["Name"] for p in out.get("ProvisionedProducts", []))
        token = out.get("NextPageToken")
        if not token:
            break
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filter", nargs="?", help="only show names containing this substring")
    args = parser.parse_args()

    names = fetch_all_names()
    if args.filter:
        names = [n for n in names if args.filter in n]

    print(f"TOTAL: {len(names)}")
    for n in names:
        print(n)


if __name__ == "__main__":
    main()
