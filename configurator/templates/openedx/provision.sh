#!/bin/bash -e
dockerize -wait tcp://mysql:3306 -timeout 20s

while ! mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e="\r"; do
    echo "Waiting for mysql database to be ready..."
    sleep 1
done

mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'CREATE DATABASE IF NOT EXISTS {{ MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'GRANT ALL ON {{ MYSQL_DATABASE }}.* TO "{{ MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ MYSQL_PASSWORD }}";'

{% if ACTIVATE_NOTES %}
mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'CREATE DATABASE IF NOT EXISTS {{ NOTES_MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'GRANT ALL ON {{ NOTES_MYSQL_DATABASE }}.* TO "{{ NOTES_MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ NOTES_MYSQL_PASSWORD }}";'
{% endif %}

{% if ACTIVATE_XQUEUE %}
mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'CREATE DATABASE IF NOT EXISTS {{ XQUEUE_MYSQL_DATABASE }};'
mysql -u root --password="{{ MYSQL_PASSWORD }}" --host "mysql" -e 'GRANT ALL ON {{ XQUEUE_MYSQL_DATABASE }}.* TO "{{ XQUEUE_MYSQL_USERNAME }}"@"%" IDENTIFIED BY "{{ XQUEUE_MYSQL_PASSWORD }}";'
{% endif %}
