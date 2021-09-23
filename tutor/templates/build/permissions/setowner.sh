#! /bin/sh
set -e
user_id="$1"
shift
for path in $@; do
  path_user_id="$(stat -c '%u' $path)"
  if [ "$path_user_id" != "$user_id" ]
  then
    echo "$path changing UID from $path_user_id to $user_id..."
    chown --recursive $user_id $path
  else
    echo "$path already owned by $user_id"
  fi
done
