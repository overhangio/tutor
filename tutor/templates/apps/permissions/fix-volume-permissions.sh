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
# chown -R processes children before the directory itself (verified: it is a
# post-order walk), so if the timeout below kills it partway through, $path's
# own group is the last thing that would have been updated. A partial failure
# therefore still reads as "not done" above on the next restart, instead of
# silently looking complete while some descendant is left unfixed.
if timeout 60 chown --recursive "$uid:$gid" "$path"; then
  echo "$path: ownership fixed"
else
  echo "$path: failed to fix ownership (error or timed out); continuing anyway" >&2
fi
