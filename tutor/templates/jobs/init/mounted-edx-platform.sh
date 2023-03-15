# When a new local copy of edx-platform is bind-mounted, certain build
# artifacts from the openedx image's edx-platform directory are lost.
# We regenerate them here.

if [ -f /openedx/edx-platform/bindmount-canary ] ; then
	# If this file exists, then edx-platform has not been bind-mounted,
	# so no build artifacts need to be regenerated.
	echo "Using edx-platform from image (not bind-mount)."
	echo "No extra setup is required."
	exit
fi

echo "Performing additional setup for bind-mounted edx-platform."
set -x # Echo out executed lines

# Regenerate Open_edX.egg-info
pip install -e .

# Regenerate node_modules
npm clean-install

# Regenerate static assets.
openedx-assets build --env=dev

set -x
echo "Done setting up bind-mounted edx-platform."
