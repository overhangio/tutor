#!/bin/sh -e

# Unset service variantm, which otherwise causes some unit tests to fail
unset SERVICE_VARIANT
# This variable should be set adequately depending on the set of unit tests to run
unset DJANGO_SETTINGS_MODULE

exec "$@"
