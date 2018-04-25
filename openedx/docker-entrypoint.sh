#!/bin/bash -e
export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS
USERID=${USERID:=1000}

## Configure user with a different USERID if requested.
if [ "$USERID" -ne 1000 ]
    then
        echo "creating new user 'openedx' with UID $USERID"
        useradd -m openedx -u $USERID
        chown --no-dereference -R openedx /openedx

        # Run CMD as different user
        exec chroot --userspec="$USERID" --skip-chdir / "$@"
else 
        # Run CMD as root (business as usual)
        exec "$@"
fi
