#!/bin/bash -e
USERID=${USERID:=0}

## Configure user with a different USERID if requested.
if [ "$USERID" -ne 0 ]
    then
        useradd --home-dir /openedx -u $USERID openedx

        # Change file permissions
        chown --no-dereference -R openedx /openedx/config

        # Run CMD as different user
        exec chroot --userspec="$USERID" --skip-chdir / env HOME=/openedx "$@"
else 
        # Run CMD as root (business as usual)
        exec "$@"
fi
