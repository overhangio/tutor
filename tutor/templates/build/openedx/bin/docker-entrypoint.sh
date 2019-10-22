#!/bin/sh -e
export DJANGO_SETTINGS_MODULE=$SERVICE_VARIANT.envs.$SETTINGS
exec "$@"