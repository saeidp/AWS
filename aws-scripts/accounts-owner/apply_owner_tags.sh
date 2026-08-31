#!/usr/bin/env bash
# Set <prefix>:primary-contact-owner-email on the accounts listed in to_change.tsv.
#
# The tag prefix is site-specific: set OWNER_TAG_PREFIX (default "org").
#
#   ./apply_owner_tags.sh                 # DRY RUN - prints what it would do
#   ./apply_owner_tags.sh --apply         # actually writes the tags
#   ./apply_owner_tags.sh --apply --rollback   # restore previous owners instead
#
# Requires management-account credentials with organizations:TagResource.
# Previous values are in rollback_previous_owners.json.
set -uo pipefail
cd "$(dirname "$0")"

NEW_OWNER="${NEW_OWNER:?set NEW_OWNER to the target owner email, e.g. NEW_OWNER=first.last@example.edu}"
KEY="${OWNER_TAG_PREFIX:-org}:primary-contact-owner-email"
APPLY=0; ROLLBACK=0
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --rollback) ROLLBACK=1 ;;
    *) echo "unknown arg: $a" >&2; exit 2 ;;
  esac
done

if [ "$ROLLBACK" = 1 ]; then
  MAP=$(python3 -c "import json;[print(r['Id'],r['Name'],r['PreviousOwner'] or '__DELETE__') for r in json.load(open('rollback_previous_owners.json'))]")
else
  MAP=$(awk -F'\t' -v o="$NEW_OWNER" '{print $1, $2, o}' to_change.tsv)
fi

n=0; failed=0
while read -r id name owner; do
  [ -z "${id:-}" ] && continue
  n=$((n+1))
  if [ "$APPLY" = 0 ]; then
    echo "DRY RUN  $id  $name  ->  $owner"
    continue
  fi
  if [ "$owner" = "__DELETE__" ]; then
    aws organizations untag-resource --resource-id "$id" --tag-keys "$KEY" >/dev/null 2>&1
  else
    aws organizations tag-resource --resource-id "$id" \
        --tags "Key=$KEY,Value=$owner" >/dev/null 2>&1
  fi
  if [ $? -eq 0 ]; then
    echo "OK       $id  $name  ->  $owner"
  else
    echo "FAILED   $id  $name" >&2; failed=$((failed+1))
  fi
done <<< "$MAP"

echo
echo "$n accounts processed, $failed failed$([ "$APPLY" = 0 ] && echo ' (dry run - nothing changed)')"
