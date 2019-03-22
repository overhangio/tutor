certbot certonly --standalone -n --agree-tos -m admin@{{ LMS_HOST }} -d {{ LMS_HOST }} -d {{ CMS_HOST }} -d preview.{{ LMS_HOST }}
{% if ACTIVATE_NOTES %}certbot certonly --standalone -n --agree-tos -m admin@{{ LMS_HOST }} -d notes.{{ LMS_HOST }}{% endif %}
