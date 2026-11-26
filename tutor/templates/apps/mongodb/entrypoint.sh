#!/bin/bash
# Start MongoDB with authentication enabled, after making sure that the Tutor user
# exists with the current password. This works both on empty data directories and
# on data created by earlier versions of Tutor, which ran MongoDB without
# authentication.
set -euo pipefail

# Extra arguments are passed to mongod. A leading "mongod" is dropped, such that
# overrides like `command: mongod --wiredTigerCacheSizeGB 1` keep working. The
# storage engine is not set here: WiredTiger is the default.
if [ "${1:-}" = "mongod" ]; then
    shift
fi

if ! command -v mongosh > /dev/null; then
    echo "tutor: MongoDB images older than 6.0 do not support authentication in Tutor."
    echo "tutor: Disable it with: tutor config save --set MONGODB_PASSWORD="
    exit 1
fi

# mongosh writes logs to $HOME, which is the data volume in the mongo image
export HOME=/tmp

# 1. Start a temporary server with authentication disabled. It listens on the
#    loopback interface only, on a separate port, so that it cannot be reached
#    from other containers.
SETUP_PORT=27018
if ! mongod --bind_ip 127.0.0.1 --port "$SETUP_PORT" \
    --fork --logpath /tmp/mongod-setup.log "$@"; then
    cat /tmp/mongod-setup.log 2> /dev/null || true
    exit 1
fi

# 2. Create the user, or reset its password. Credentials are read from the
#    environment, such that they do not show up in the process list. Roles are only
#    set on creation, such that administrators can change them.
mongosh --quiet --port "$SETUP_PORT" admin --eval '
  const user = process.env.MONGODB_USERNAME;
  const pwd = process.env.MONGODB_PASSWORD;
  if (db.getUser(user) === null) {
    db.createUser({ user, pwd, roles: [{ role: "root", db: "admin" }] });
    print("tutor: created MongoDB user " + user);
  } else {
    db.updateUser(user, { pwd });
    print("tutor: updated MongoDB user " + user);
  }
'

# 3. Stop the temporary server and replace this script with the actual server, such
#    that mongod runs as PID 1 and receives signals directly.
mongod --dbpath /data/db --shutdown > /dev/null
exec mongod --auth --bind_ip_all "$@"
