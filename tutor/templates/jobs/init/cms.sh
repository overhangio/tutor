dockerize -wait tcp://{{ MYSQL_HOST }}:{{ MYSQL_PORT }} -timeout 20s

echo "Loading settings $DJANGO_SETTINGS_MODULE"

./manage.py cms migrate

# Ensure a Site object exists for the CMS domain. The SITE_ID site itself is
# owned by the LMS init job (LMS and CMS share the same Site table), so here we
# only make sure Studio has its own Site to resolve from.
# https://github.com/overhangio/tutor/issues/1182
./manage.py cms shell -c "
from django.conf import settings
from django.contrib.sites.models import Site
domain = settings.CMS_BASE
name = '{{ PLATFORM_NAME }}'[:Site._meta.get_field('name').max_length]
site, created = Site.objects.get_or_create(domain=domain, defaults={'name': name})
verb = 'Created' if created else 'Found'
print(f'{verb} CMS site id={site.pk} for {domain}')
"

# Fix incorrect uploaded file path
if [ -d /openedx/data/uploads/ ]; then
  if [ -n "$(ls -A /openedx/data/uploads/)" ]; then
    echo "Migrating CMS uploaded files to shared directory"
    mv /openedx/data/uploads/* /openedx/media/
    rm -rf /openedx/data/uploads/
  fi
fi

# Schedule Studio search index population. Index creation and configuration
# are already handled by the post_migrate signal during `cms migrate` above;
# this enqueues a Celery task that cms-worker consumes to populate the index
# incrementally in the background.
./manage.py cms reindex_studio
# Create the courseware content index
./manage.py cms reindex_course --active

# Load default policies for the Open edX Authorization framework
# Check if openedx-authz package is installed if not skip loading policies and exit
if python -c "import pkg_resources; pkg_resources.require('openedx-authz')" 2>/dev/null; then
    ./manage.py cms load_policies
else
    echo "openedx-authz package is not installed, skipping loading default policies"
    exit 1
fi
