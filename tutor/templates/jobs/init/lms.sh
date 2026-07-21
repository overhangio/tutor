dockerize -wait tcp://{{ MYSQL_HOST }}:{{ MYSQL_PORT }} -timeout 20s

{%- if MONGODB_HOST.startswith("mongodb+srv://") %}
echo "MongoDB is using SRV records, so we cannot wait for it to be ready"
{%- else %}
dockerize -wait tcp://{{ MONGODB_HOST }}:{{ MONGODB_PORT }} -timeout 20s
{%- endif %}

echo "Loading settings $DJANGO_SETTINGS_MODULE"

./manage.py lms migrate

# Point the SITE_ID site at the LMS domain instead of the default "example.com"
# site that Django auto-creates during the first migration. Otherwise, code paths
# that run outside of an HTTP request (e.g. bulk emails sent from Celery workers)
# fall back to SITE_ID and send links/branding for "example.com".
# https://github.com/overhangio/tutor/issues/1182
./manage.py lms shell -c "
from django.conf import settings
from django.contrib.sites.models import Site
site_id = settings.SITE_ID
domain = settings.LMS_BASE
name = '{{ PLATFORM_NAME }}'[:Site._meta.get_field('name').max_length]
current = Site.objects.filter(pk=site_id).first()
existing = Site.objects.filter(domain=domain).first()
current_domain = current.domain if current else None
if existing and existing.pk == site_id:
    print(f'SITE_ID {site_id} already points at {domain}')
elif existing:
    # Two sites exist: the SITE_ID site and a separate site for the LMS domain.
    # Both may have data attached (SiteConfiguration, themes, ...), so we cannot
    # safely guess which to keep. Leave the database untouched and let the
    # operator decide.
    print('WARNING: cannot automatically fix SITE_ID: two candidate sites exist.')
    print(f'WARNING:   - SITE_ID={site_id} currently points at site id={current.pk if current else None} ({current_domain!r})')
    print(f'WARNING:   - the LMS domain {domain!r} is site id={existing.pk}')
    print('WARNING: the database was left unchanged. Request-less features (e.g. bulk')
    print(f'WARNING: email) will keep using {current_domain!r}.')
    print('WARNING: to fix, review both sites, delete the one you do not need, and set')
    print('WARNING: SITE_ID (via a plugin) to the id of the site you keep.')
elif current is None:
    Site.objects.create(pk=site_id, domain=domain, name=name)
    print(f'Created site id={site_id} for {domain}')
elif current.domain == 'example.com':
    current.domain = domain
    current.name = name
    current.save()
    print(f'Renamed default site id={site_id} from example.com to {domain}')
else:
    print(f'SITE_ID {site_id} points at {current.domain} - leaving unchanged')
"

# Create meilisearch indexes
./manage.py lms shell -c "import search.meilisearch; search.meilisearch.create_indexes()"

# Create oauth2 apps for CMS SSO
# https://github.com/openedx/edx-platform/blob/master/docs/guides/studio_oauth.rst
./manage.py lms manage_user cms cms@openedx --unusable-password
./manage.py lms create_dot_application \
  --grant-type authorization-code \
  --redirect-uris "{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ CMS_HOST }}/complete/edx-oauth2/" \
  --client-id {{ CMS_OAUTH2_KEY_SSO }} \
  --client-secret {{ CMS_OAUTH2_SECRET }} \
  --scopes user_id \
  --skip-authorization \
  --update cms-sso cms
./manage.py lms create_dot_application \
  --grant-type authorization-code \
  --redirect-uris "http://{{ CMS_HOST }}:8001/complete/edx-oauth2/" \
  --client-id {{ CMS_OAUTH2_KEY_SSO_DEV }} \
  --client-secret {{ CMS_OAUTH2_SECRET }} \
  --scopes user_id \
  --skip-authorization \
  --update cms-sso-dev cms


# Fix incorrect uploaded file path
if [ -d /openedx/data/uploads/ ]; then
  if [ -n "$(ls -A /openedx/data/uploads/)" ]; then
    echo "Migrating LMS uploaded files to shared directory"
    mv /openedx/data/uploads/* /openedx/media/
    rm -rf /openedx/data/uploads/
  fi
fi

# Create waffle switches to enable some features, if they have not been explicitly defined before
# Completion tracking: add green ticks to every completed unit
(./manage.py lms waffle_switch --list | grep completion.enable_completion_tracking) || ./manage.py lms waffle_switch --create completion.enable_completion_tracking on

# Load default policies for the Open edX Authorization framework
# Check if openedx-authz package is installed if not skip loading policies and exit
if python -c "import pkg_resources; pkg_resources.require('openedx-authz')" 2>/dev/null; then
    ./manage.py lms load_policies
else
    echo "openedx-authz package is not installed, skipping loading default policies"
    exit 1
fi
