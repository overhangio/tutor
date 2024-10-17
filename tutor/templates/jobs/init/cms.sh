dockerize -wait tcp://{{ MYSQL_HOST }}:{{ MYSQL_PORT }} -timeout 20s

echo "Loading settings $DJANGO_SETTINGS_MODULE"

./manage.py cms migrate

# Fix incorrect uploaded file path
if [ -d /openedx/data/uploads/ ]; then
  if [ -n "$(ls -A /openedx/data/uploads/)" ]; then
    echo "Migrating CMS uploaded files to shared directory"
    mv /openedx/data/uploads/* /openedx/media/
    rm -rf /openedx/data/uploads/
  fi
fi

# Create waffle switches to enable some features, if they have not been explicitly defined before
# Copy-paste of units in Studio (highly requested new feature, but defaults to off in Quince)
(./manage.py cms waffle_flag --list | grep contentstore.enable_copy_paste_units) || ./manage.py lms waffle_flag --create contentstore.enable_copy_paste_units --everyone

# Re-index studio and courseware content
# Note that this might be slow for large courses until this issue is resolved:
# https://github.com/openedx/modular-learning/issues/235
# But this is a necessary step to make sure the indexes are created and properly
# configured.
./manage.py cms reindex_studio --experimental
./manage.py cms reindex_course --active
