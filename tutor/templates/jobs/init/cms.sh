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

# Create the index for studio and courseware content. Because we specify --init,
# this will not populate the index (potentially slow) nor replace any existing
# index (resulting in broken features until it is complete). If either of those
# are necessary, it will print instructions on what command to run to do so.
./manage.py cms reindex_studio --experimental --init
# Create the courseware content index
./manage.py cms reindex_course --active
