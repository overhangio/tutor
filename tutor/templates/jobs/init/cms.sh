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

# Run all remaining steps in a single Django process: each `./manage.py` call boots
# Django from scratch, which takes several seconds.
cat <<'TUTOR_CMS_INIT_EOF' > /tmp/tutor_cms_init.py
from django.core.management import call_command

# Schedule Studio search index population. Index creation and configuration
# are already handled by the post_migrate signal during `cms migrate` above;
# this enqueues a Celery task that cms-worker consumes to populate the index
# incrementally in the background.
call_command("reindex_studio")

# Create the courseware content index
call_command("reindex_course", "--active")

# Load default policies for the Open edX Authorization framework
import importlib.metadata
try:
    importlib.metadata.distribution("openedx-authz")
except importlib.metadata.PackageNotFoundError:
    print("openedx-authz package is not installed, skipping loading default policies")
    raise SystemExit(1)
call_command("load_policies")
TUTOR_CMS_INIT_EOF
./manage.py cms shell -c "$(cat /tmp/tutor_cms_init.py)"
