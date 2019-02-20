create_databases = """dockerize -wait tcp://mysql:3306 -timeout 20s
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
"""

migrate_lms = "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py lms migrate"
migrate_cms = "dockerize -wait tcp://mysql:3306 -timeout 20s && ./manage.py cms migrate"
migrate_forum = "bundle exec rake search:initialize && bundle exec rake search:rebuild_index"
migrate_notes = "./manage.py migrate"
migrate_xqueue = "./manage.py migrate"

oauth2 = """
./manage.py lms create_oauth2_client \
    "http://androidapp.com" "http://androidapp.com/redirect" public \
    --client_id android --client_secret {{ ANDROID_OAUTH2_SECRET }} \
    --trusted

{% if ACTIVATE_NOTES %}
./manage.py lms manage_user notes notes@{{ LMS_HOST }} --staff --superuser
./manage.py lms create_oauth2_client \
    "http://notes.openedx:8000" "http://notes.openedx:8000/complete/edx-oidc/" confidential \
    --client_name edx-notes --client_id notes --client_secret {{ NOTES_OAUTH2_SECRET }} \
    --trusted --logout_uri "http://notes.openedx:8000/logout/" --username notes
{% endif %}"""

https_certificates_create = """certbot certonly --standalone -n --agree-tos -m admin@{{ LMS_HOST }} -d {{ LMS_HOST }} -d {{ CMS_HOST }} -d preview.{{ LMS_HOST }}
{% if ACTIVATE_NOTES %}
certbot certonly --standalone -n --agree-tos -m admin@{{ LMS_HOST }} -d notes.{{ LMS_HOST }}
{% endif %}"""

create_user = """./manage.py lms --settings=tutor.production manage_user {{ OPTS }} {{ USERNAME }} {{ EMAIL }}
./manage.py lms --settings=tutor.production changepassword {{ USERNAME }}"""
import_demo_course = """git clone https://github.com/edx/edx-demo-course --branch open-release/hawthorn.2 --depth 1 ../edx-demo-course
python ./manage.py cms --settings=tutor.production import ../data ../edx-demo-course"""
index_courses = "./manage.py cms --settings=tutor.production reindex_course --all --setup"
