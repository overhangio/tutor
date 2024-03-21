# The initialization job contains various re-install operations needed to be done
# on mounted directories (edx-platform, /mnt/*xblock, /mnt/<edx-ora, search, enterprise>)
# 1. /mnt/*
# Whenever xblocks or other installable packages are mounted, during the image build, they are copied over to container
# and installed. This results in egg_info generation for the mounted directories. However, the egg_info is not carried
# over to host. When the containers are launched, the host directories without egg_info are mounted on runtime
# and disappear from pip list.
#
# 2. edx-platform
# When a new local copy of edx-platform is bind-mounted, certain build
# artifacts from the openedx image's edx-platform directory are lost.
# We regenerate them here.


for mounted_dir in /mnt/*; do
    if [ -f $mounted_dir/setup.py ] && ! ls $mounted_dir/*.egg-info >/dev/null 2>&1 ; then
        echo "Unable to locate egg-info in $mounted_dir"
        pip install -e $mounted_dir
    fi
done

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

# Pull latest translations via atlas
rm -rf conf/locale conf/plugins-locale
./manage.py lms pull_plugin_translations --verbose --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }}
./manage.py lms pull_xblock_translations --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }}
rm -rf conf/locale
atlas pull --repository='{{ ATLAS_REPOSITORY }}' --revision='{{ ATLAS_REVISION }}' {{ ATLAS_OPTIONS }} \
	translations/edx-platform/conf/locale:conf/locale \
	translations/studio-frontend/src/i18n/messages:conf/plugins-locale/studio-frontend
./manage.py lms compile_xblock_translations
./manage.py cms compile_xblock_translations
./manage.py lms compile_plugin_translations
./manage.py lms compilemessages -v1
./manage.py lms compilejsi18n
./manage.py cms compilejsi18n

# Regenerate static assets.
openedx-assets build --env=dev

set -x
echo "Done setting up bind-mounted edx-platform."
