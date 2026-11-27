dockerize -wait tcp://{{ MYSQL_HOST }}:{{ MYSQL_PORT }} -timeout 20s

{%- if MONGODB_HOST.startswith("mongodb+srv://") %}
echo "MongoDB is using SRV records, so we cannot wait for it to be ready"
{%- elif ',' in MONGODB_HOST %}
echo "Waiting for MongoDB (replica set, checking all members)"
{%- for host in MONGODB_HOST.split(',') %}
dockerize -wait tcp://{{ host.strip() }}:{{ MONGODB_PORT }} -timeout 20s
{%- endfor %}
{%- else %}
dockerize -wait tcp://{{ MONGODB_HOST }}:{{ MONGODB_PORT }} -timeout 20s
{%- endif %}

echo "Loading settings $DJANGO_SETTINGS_MODULE"

./manage.py lms migrate

# Fix incorrect uploaded file path
if [ -d /openedx/data/uploads/ ]; then
  if [ -n "$(ls -A /openedx/data/uploads/)" ]; then
    echo "Migrating LMS uploaded files to shared directory"
    mv /openedx/data/uploads/* /openedx/media/
    rm -rf /openedx/data/uploads/
  fi
fi

# Run all remaining steps in a single Django process: each `./manage.py` call boots
# Django from scratch, which takes several seconds.
cat <<'TUTOR_LMS_INIT_EOF' > /tmp/tutor_lms_init.py
from django.core.management import call_command

# Create meilisearch indexes
import search.meilisearch
search.meilisearch.create_indexes()

# Create waffle switches to enable some features, if they have not been explicitly defined before
# Completion tracking: add green ticks to every completed unit
from waffle import get_waffle_switch_model
if not get_waffle_switch_model().objects.filter(name="completion.enable_completion_tracking").exists():
    call_command("waffle_switch", "completion.enable_completion_tracking", "on", "--create")

# Load default policies for the Open edX Authorization framework
import importlib.metadata
try:
    importlib.metadata.distribution("openedx-authz")
    openedx_authz_installed = True
except importlib.metadata.PackageNotFoundError:
    openedx_authz_installed = False
if openedx_authz_installed:
    call_command("load_policies")

# Service users, OAuth2 applications and waffle flags declared by Tutor and plugins
{{ openedx_lms_init_script() }}

if not openedx_authz_installed:
    print("openedx-authz package is not installed, skipping loading default policies")
    raise SystemExit(1)
TUTOR_LMS_INIT_EOF
PYTHONUNBUFFERED=1 ./manage.py lms shell -c "$(cat /tmp/tutor_lms_init.py)"
