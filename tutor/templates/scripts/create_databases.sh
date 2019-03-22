dockerize -wait tcp://{{ MYSQL_HOST }}:{{ MYSQL_PORT }} -timeout 20s
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'CREATE DATABASE IF NOT EXISTS {{ OPENEDX_MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'GRANT ALL ON {{ OPENEDX_MYSQL_DATABASE }}.* TO "{{ OPENEDX_MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ OPENEDX_MYSQL_PASSWORD }}";'

{% if ACTIVATE_NOTES %}
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'CREATE DATABASE IF NOT EXISTS {{ NOTES_MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'GRANT ALL ON {{ NOTES_MYSQL_DATABASE }}.* TO "{{ NOTES_MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ NOTES_MYSQL_PASSWORD }}";'
{% endif %}

{% if ACTIVATE_XQUEUE %}
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'CREATE DATABASE IF NOT EXISTS {{ XQUEUE_MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_ROOT_PASSWORD }}" --host "{{ MYSQL_HOST }}" -e 'GRANT ALL ON {{ XQUEUE_MYSQL_DATABASE }}.* TO "{{ XQUEUE_MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ XQUEUE_MYSQL_PASSWORD }}";'
{% endif %}
