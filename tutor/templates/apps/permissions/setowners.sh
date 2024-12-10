#! /bin/sh
setowner $OPENEDX_USER_ID /mounts/lms /mounts/cms /mounts/openedx
{% if RUN_MEILISEARCH %}setowner 1000 /mounts/meilisearch{% endif %}
{% if RUN_MONGODB %}setowner 999 /mounts/mongodb{% endif %}
{% if RUN_MYSQL %}setowner 999 /mounts/mysql{% endif %}
{% if RUN_REDIS %}setowner 1000 /mounts/redis{% endif %}

{{ patch("local-docker-compose-permissions-command") }}
