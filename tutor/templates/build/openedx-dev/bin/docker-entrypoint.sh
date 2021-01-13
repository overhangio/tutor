#!/bin/sh -e
export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS

if id -u openedx > /dev/null 2>&1; then
    # Change owners of mounted volumes
    echo "Setting file permissions for user openedx..."
    find /openedx \
        -not -path "/openedx/edx-platform/*" \
        -not -user openedx \
        -writable \
        -exec chown openedx:openedx {} \+
    echo "File permissions set."

    # Run CMD as user openedx
    exec chroot --userspec="openedx:openedx" --skip-chdir / env HOME=/openedx "$@"
else
    echo "Running openedx-dev as root user"
    exec "$@"
fi
