from .common import *

SECRET_KEY = '{{ NOTES_SECRET_KEY }}'
ALLOWED_HOSTS = ['localhost', 'notes', 'notes.openedx', 'notes.localhost', 'notes.{{ LMS_HOST }}']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '{{ MYSQL_HOST }}',
        'PORT': {{ MYSQL_PORT }},
        'NAME': '{{ NOTES_MYSQL_DATABASE }}',
        'USER': '{{ NOTES_MYSQL_USERNAME }}',
        'PASSWORD': '{{ NOTES_MYSQL_PASSWORD }}',
    }
}

CLIENT_ID = 'notes'
CLIENT_SECRET = '{{ NOTES_OAUTH2_SECRET }}'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'notesserver.highlight.ElasticsearchSearchEngine',
        'URL': 'http://{{ ELASTICSEARCH_HOST }}:{{ ELASTICSEARCH_PORT }}/',
        'INDEX_NAME': 'notes',
    },
}

LOGGING['handlers']['local'] = LOGGING['handlers']['console'].copy()
