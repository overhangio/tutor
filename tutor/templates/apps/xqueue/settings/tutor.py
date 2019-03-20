from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '{{ MYSQL_HOST }}',
        'PORT': {{ MYSQL_PORT }},
        'NAME': '{{ XQUEUE_MYSQL_DATABASE }}',
        'USER': '{{ XQUEUE_MYSQL_USERNAME }}',
        'PASSWORD': '{{ XQUEUE_MYSQL_PASSWORD }}',
    }
}

LOGGING = get_logger_config(
    log_dir="/openedx/data/",
    logging_env="tutor",
    dev_env=True,
)

SECRET_KEY = '{{ XQUEUE_SECRET_KEY }}'

XQUEUE_USERS = {
    '{{ XQUEUE_AUTH_USERNAME }}': '{{ XQUEUE_AUTH_PASSWORD}}'
}
