from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{{ XQUEUE_MYSQL_DATABASE }}',
        'USER': '{{ XQUEUE_MYSQL_USERNAME }}',
        'PASSWORD': '{{ XQUEUE_MYSQL_PASSWORD }}',
        'HOST': 'mysql',
        'PORT': '3306',
    }
}

LOGGING = get_logger_config(
    log_dir="/openedx/data/",
    logging_env="tutor",
    dev_env=True,
)

RABBIT_HOST = 'rabbitmq'
RABBIT_PORT = 5672
SECRET_KEY = '{{ XQUEUE_SECRET_KEY }}'

XQUEUE_USERS = {
    '{{ XQUEUE_AUTH_USERNAME }}': '{{ XQUEUE_AUTH_PASSWORD}}'
}
