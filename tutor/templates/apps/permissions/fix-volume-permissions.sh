#! /bin/sh
set -e
uid="$1"
gid="$2"
path="$3"

current_gid="$(stat -c '%g' "$path")"
if [ "$current_gid" = "$gid" ]; then
  echo "$path: group already $gid, nothing to do"
  exit 0
fi

echo "$path: group is $current_gid, expected $gid; fixing ownership"
if timeout 60 chown --recursive "$uid:$gid" "$path"; then
  echo "$path: ownership fixed"
else
  echo "$path: failed to fix ownership (error or timed out); continuing anyway" >&2
fi
