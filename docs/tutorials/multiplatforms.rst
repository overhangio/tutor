Running multiple Open edX platforms on a single server
======================================================

With Tutor, it is easy to run multiple Open edX instances on a single server. To do so, the following configuration parameters must be different for all platforms:

- ``TUTOR_ROOT``: so that configuration, environment, and data are not mixed up between platforms.
- ``LOCAL_PROJECT_NAME``: the various docker-compose projects cannot share the same name.
- ``CADDY_HTTP_PORT``: exposed ports cannot be shared by two different containers.
- ``LMS_HOST``, ``CMS_HOST``: the different platforms must be accessible from different domain (or subdomain) names.

In addition, a web proxy must be set up on the host, as described :ref:`in the corresponding tutorial <web_proxy>`.
