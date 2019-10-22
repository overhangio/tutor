#!/bin/sh -e
export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS

# Change file permissions of mounted volumes
echo "Setting file permissions..."
find /openedx -not -path "/openedx/edx-platform/*" -not -user openedx -exec chown openedx:openedx {} \+
echo "File permissions set."

# Run CMD as user openedx
exec chroot --userspec="$openedx:openedx" --skip-chdir / env HOME=/openedx "$@"