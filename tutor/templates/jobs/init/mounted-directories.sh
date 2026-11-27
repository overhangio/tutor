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
# Each step below is skipped when its inputs did not change since the last successful
# run, so that relaunching a dev environment is fast. To force all steps to run again,
# delete the edx-platform "node_modules" directory. Note that modification times do not
# detect deleted files, nor files that were moved or copied with their original times.

pip_stamp=node_modules/.tutor-pip-stamp
npm_fingerprint=node_modules/.tutor-npm-fingerprint
assets_stamp=node_modules/.tutor-build-dev-stamp
# Outside of node_modules, which is deleted by "npm clean-install"
run_start=$(mktemp)

# Regenerate the package metadata
if [ ! -e "$pip_stamp" ] || ! ls -d *.egg-info >/dev/null 2>&1 \
    || [ -n "$(find pyproject.toml setup.py setup.cfg -newer "$pip_stamp" 2>/dev/null)" ]; then
    (set -x; pip install -e .)
else
    echo "Package metadata is up-to-date, skipping 'pip install -e .'"
fi

# Regenerate node_modules
npm_fingerprint_value="$(node --version) $(cat package.json package-lock.json .npmrc scripts/copy-node-modules.sh 2>/dev/null | sha256sum | cut -d ' ' -f 1)"
# node_modules/.package-lock.json is rewritten by any npm install, such as one run on the host
if [ "$(cat "$npm_fingerprint" 2>/dev/null)" != "$npm_fingerprint_value" ] \
    || [ ! -e node_modules/.bin/webpack ] \
    || [ -z "$(ls -A common/static/common/js/vendor 2>/dev/null)" ] \
    || [ -n "$(find node_modules/.package-lock.json -newer "$npm_fingerprint" 2>/dev/null)" ]; then
    (set -x; npm clean-install)
    echo "$npm_fingerprint_value" > "$npm_fingerprint"
else
    echo "node_modules is up-to-date, skipping 'npm clean-install'"
fi

# Regenerate static assets
# Theme files are re-rendered by "tutor config save" on every launch, so we compare
# their content instead of their modification time. Theme css is compiled next to the
# themes, which may be shared with other edx-platform clones, so we also compare the
# compiled css when it persists across launches, i.e. when the theme directory is mounted.
theme_dirs=$(echo "${COMPREHENSIVE_THEME_DIRS:-/openedx/themes}" | tr ':' ' ')
themes_sources=$(find $theme_dirs -type f \( -name '*.scss' -o -name '*.sass' \) -exec sha256sum {} + 2>/dev/null | sort | sha256sum | cut -d ' ' -f 1)
# These environment variables are compiled into the webpack bundles
build_env=$(printf '%s\n' "$JS_ENV_EXTRA_CONFIG" "$CAPTIONS_CONTENT_TO_REPLACE" "$CAPTIONS_CONTENT_REPLACEMENT" | sha256sum | cut -d ' ' -f 1)
themes_outputs() {
    for theme_dir in $theme_dirs; do
        case "$theme_dir" in
            /openedx/edx-platform/*) ;;
            *) grep -qs " $theme_dir " /proc/self/mountinfo || { echo "$theme_dir not mounted"; continue; } ;;
        esac
        echo "$theme_dir"
        find "$theme_dir" -type f -name '*.css' -exec sha256sum {} + 2>/dev/null
    done | sort | sha256sum | cut -d ' ' -f 1
}
if [ "$(cat "$assets_stamp" 2>/dev/null)" != "$themes_sources $build_env $(themes_outputs)" ] \
    || [ -z "$(ls -A common/static/bundles 2>/dev/null)" ] \
    || [ -z "$(ls -A lms/static/css 2>/dev/null)" ] \
    || [ -z "$(ls -A cms/static/css 2>/dev/null)" ] \
    || [ -n "$(find package.json .babelrc webpack*.js webpack-config scripts/compile_sass.py lms cms common openedx xmodule \
        \( -path common/static/bundles -o -path common/static/common/js/vendor -o -path common/static/common/css/vendor \) -prune -o \
        -newer "$assets_stamp" \
        \( -name '*.js' -o -name '*.jsx' -o -name '*.ts' -o -name '*.tsx' -o -name '*.scss' -o -name '*.sass' \
            -o -name '*.underscore' -o -name '*.svg' -o -name package.json -o -name .babelrc -o -name compile_sass.py \) \
        -print -quit 2>/dev/null)" ]; then
    # Date the stamp from before the build, so that files edited during the build are picked up next time.
    touch "$assets_stamp.tmp"
    # Remove the previous stamp, so that an interrupted build is not skipped next time.
    rm -f "$assets_stamp"
    (set -x; npm run build-dev)
    echo "$themes_sources $build_env $(themes_outputs)" > "$assets_stamp"
    touch -r "$assets_stamp.tmp" "$assets_stamp"
    rm "$assets_stamp.tmp"
else
    echo "Static assets are up-to-date, skipping 'npm run build-dev'"
fi

# The pip stamp is written last, because "npm clean-install" deletes node_modules. It is
# dated from the start of this job, so that files edited during the job are picked up next time.
touch -r "$run_start" "$pip_stamp"
rm -f "$run_start"

echo "Done setting up bind-mounted edx-platform."
