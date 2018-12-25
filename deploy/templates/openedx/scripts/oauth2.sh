#!/bin/bash -e

{% if ACTIVATE_NOTES %}
./manage.py lms manage_user notes notes@{{ LMS_HOST }} --staff --superuser
./manage.py lms create_oauth2_client \
    "http://notes.openedx:8000" \
    "http://notes.openedx:8000/complete/edx-oidc/" \
    confidential \
    --client_name edx-notes --client_id notes --client_secret {{ NOTES_OAUTH2_SECRET }} \
    --trusted --logout_uri "http://notes.openedx:8000/logout/" --username notes
{% endif %}
