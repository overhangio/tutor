.. _configuration_customisation:

Configuration and customisation
===============================

Tutor offers plenty of possibilities for platform customisation out of the box. There are two main ways in which the base Open edX installation can be customised:

a. Modifying the Tutor :ref:`configuration parameters <configuration>`.
b. Modifying the :ref:`Open edX docker image <customise>` that runs the Open edX platform.

This section does not cover :ref:`plugin development <plugins>`. For simple changes, such as modifying the ``*.env.yml`` files or the edx-platform settings, *you should not fork edx-platform or tutor*! Instead, you should create a simple :ref:`plugin for Tutor <plugins_yaml>`.

.. _configuration:

Configuration
-------------

With Tutor, all Open edX deployment parameters are stored in a single ``config.yml`` file. This is the file that is generated when you run ``tutor local launch`` or ``tutor config save``. To view the content of this file, run::

    cat "$(tutor config printroot)/config.yml"

By default, this file contains only the required configuration parameters for running the platform. Optional configuration parameters may also be specified to modify the default behaviour. To do so, you can edit the ``config.yml`` file manually::

    vim "$(tutor config printroot)/config.yml"

Alternatively, you can set each parameter from the command line::

    tutor config save --set PARAM1=VALUE1 --set PARAM2=VALUE2

Or from the system environment::

    export TUTOR_PARAM1=VALUE1

Once the base configuration is created or updated, the environment is automatically re-generated. The environment is the set of all files required to manage an Open edX platform: Dockerfile, ``lms.env.yml``, settings files, etc. You can view the environment files in the ``env`` folder::

    ls "$(tutor config printroot)/env"

With an up-to-date environment, Tutor is ready to launch an Open edX platform and perform usual operations. Below, we document some of the configuration parameters.

Individual service activation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``RUN_ELASTICSEARCH`` (default: ``true``)
- ``RUN_MONGODB`` (default: ``true``)
- ``RUN_MYSQL`` (default: ``true``)
- ``RUN_REDIS`` (default: ``true``)
- ``RUN_SMTP`` (default: ``true``)
- ``ENABLE_HTTPS`` (default: ``false``)

Every single Open edX service may be (de)activated at will by these configuration parameters. This is useful if you want, for instance, to distribute the various Open edX services on different servers.

Docker
~~~~~~

.. _docker_images:

Custom images
*************

- ``DOCKER_IMAGE_OPENEDX`` (default: ``"{{ DOCKER_REGISTRY }}overhangio/openedx:{{ TUTOR_VERSION }}"``)

This configuration parameter defines the name of the Docker image to run for the lms and cms containers. By default, the Docker image tag matches the Tutor version it was built with.

- ``DOCKER_IMAGE_OPENEDX_DEV`` (default: ``"openedx-dev:{{ TUTOR_VERSION }}"``)

This configuration parameter defines the name of the Docker image to run the development version of the lms and cms containers.  By default, the Docker image tag matches the Tutor version it was built with.

.. https://hub.docker.com/r/devture/exim-relay/tags

- ``DOCKER_IMAGE_CADDY`` (default: ``"docker.io/caddy:2.6.2"``)

This configuration parameter defines which Caddy Docker image to use.

- ``DOCKER_IMAGE_ELASTICSEARCH`` (default: ``"docker.io/elasticsearch:7.17.9"``)

This configuration parameter defines which Elasticsearch Docker image to use.

- ``DOCKER_IMAGE_MONGODB`` (default: ``"docker.io/mongo:7.0.7"``)

This configuration parameter defines which MongoDB Docker image to use.

.. https://hub.docker.com/_/mysql/tags?page=1&name=8.0

- ``DOCKER_IMAGE_MYSQL`` (default: ``"docker.io/mysql:8.4.0"``)

This configuration parameter defines which MySQL Docker image to use.

.. https://hub.docker.com/_/redis/tags

- ``DOCKER_IMAGE_REDIS`` (default: ``"docker.io/redis:7.2.4"``)

This configuration parameter defines which Redis Docker image to use.

.. https://hub.docker.com/r/devture/exim-relay/tags

- ``DOCKER_IMAGE_SMTP`` (default: ``"docker.io/devture/exim-relay:4.96-r1-0``)

This configuration parameter defines which Simple Mail Transfer Protocol (SMTP) Docker image to use.

- ``DOCKER_IMAGE_PERMISSIONS`` (default: ``"{{ DOCKER_REGISTRY }}overhangio/openedx-permissions:{{ TUTOR_VERSION }}"``)

This configuration parameter defines the Docker image to be used for setting file permissions. The default image sets all containers to be run as unprivileged users.

Custom registry
***************

- ``DOCKER_REGISTRY`` (default: ``"docker.io/"``)

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

.. _openedx_configuration:

Compose
*******

- ``DEV_PROJECT_NAME`` (default: ``"{{ TUTOR_APP }}_dev"``)

This configuration parameter sets the Development version of the Docker Compose project name.

- ``LOCAL_PROJECT_NAME`` (default: ``"{{ TUTOR_APP }}_local"``)

This configuration parameter sets the Local version of the Docker Compose project name.

Open edX customisation
~~~~~~~~~~~~~~~~~~~~~~

- ``EDX_PLATFORM_REPOSITORY`` (default: ``"https://github.com/openedx/edx-platform.git"``)

This defines the git repository from which you install Open edX platform code. If you run an Open edX fork with custom patches, set this to your own git repository. You may also override this configuration parameter at build time, by providing a ``--build-arg`` option.

- ``OPENEDX_COMMON_VERSION`` (default: ``"release/sumac"``, or ``master`` in :ref:`nightly <nightly>`)

This defines the default version that will be pulled from all Open edX git repositories.

- ``EDX_PLATFORM_VERSION`` (default: the value of ``OPENEDX_COMMON_VERSION``)

This defines the version that will be pulled from just the Open edX platform git repositories. You may also override this configuration parameter at build time, by providing a ``--build-arg`` option.

- ``OPENEDX_CMS_UWSGI_WORKERS`` (default: ``2``)
- ``OPENEDX_LMS_UWSGI_WORKERS`` (default: ``2``)

By default, there are 2 `uwsgi worker processes <https://uwsgi-docs.readthedocs.io/en/latest/Options.html#processes>`__ to serve requests for the LMS and the CMS. However, each worker requires upwards of 500 Mb of RAM. You should reduce this value to 1 if your computer/server does not have enough memory.

- ``OPENEDX_CELERY_REDIS_DB`` (default: ``0``)
- ``OPENEDX_CACHE_REDIS_DB`` (default: ``1``)

These two configuration parameters define which Redis database to use for Open edX cache and celery task.

.. _openedx_extra_pip_requirements:

- ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` (default: ``[]``)

Define extra pip packages that are going to be installed for edx-platform.

- ``NPM_REGISTRY`` (default: ``"https://registry.npmjs.org/"``)

This defines the registry from which you'll be pulling NPM packages when building Docker images. Like ``EDX_PLATFORM_REPOSITORY``, this can be overridden at build time with a ``--build-arg`` option.

- ``OPENEDX_AWS_ACCESS_KEY`` (default: ``""``)

This configuration parameter sets the Django setting ``AWS_ACCESS_KEY_ID`` in edx-platform's LMS, CMS, envs, and production.py for use by the library django-storages with Amazon S3.

- ``OPENEDX_AWS_SECRET_ACCESS_KEY`` (default: ``""``)

This configuration parameter sets the Django setting ``AWS_SECRET_ACCESS_KEY`` in edx-platform's LMS, CMS, envs, and production.py for use by the library django-storages with Amazon S3.

- ``OPENEDX_MYSQL_DATABASE`` (default: ``"openedx"``)

This configuration parameter sets the name of the MySQL Database to be used by the Open edX Instance.

- ``OPENEDX_MYSQL_USERNAME`` (default: ``"openedx"``)

This configuration parameter sets the username associated with the MySQL Database.

CMS OAUTH2 SSO
~~~~~~~~~~~~~~

- ``CMS_OAUTH2_KEY_SSO`` (default: ``"cms-sso"``)

This defines the Studio's (CMS) OAUTH 2.0 Login (Key or Client ID) for SSO in the production environment.

- ``CMS_OAUTH2_KEY_SSO_DEV`` (default: ``"cms-sso-dev"``)

This defines the Studio's (CMS) OAUTH 2.0 Login (Key or Client ID) for SSO in the development environment.

For more information, see `Enabling OAuth for Studio login <https://github.com/openedx/edx-platform/blob/master/docs/guides/studio_oauth.rst>`__.

JWTs
~~~~

- ``JWT_COMMON_AUDIENCE`` (default: ``"openedx"``)
- ``JWT_COMMON_ISSUER`` (default: ``"{% if ENABLE_HTTPS %}https{% else %}http{% endif %}://{{ LMS_HOST }}/oauth2"``)
- ``JWT_COMMON_SECRET_KEY`` (default: ``"{{ OPENEDX_SECRET_KEY }}"``)

These configuration parameters are rendered into the ``JWT_AUTH`` dictionary with keys ``JWT_AUDIENCE``, ``JWT_ISSUER``, and ``JWT_SECRET_KEY``, respectively. These parameters may be changed in order to create a custom user login for testing purposes.

Vendor services
~~~~~~~~~~~~~~~

Caddy
*****

- ``CADDY_HTTP_PORT`` (default: ``80``)
- ``ENABLE_WEB_PROXY`` (default: ``true``)

`Caddy <https://caddyserver.com>`__ is a web server used in Tutor both as a web proxy and for the generation of SSL/TLS certificates at runtime. Port indicated by ``CADDY_HTTP_PORT`` is exposed on the host, in addition to port 443. If ``ENABLE_WEB_PROXY`` is set to ``false`` then we assume that SSL termination does not occur in the Caddy container and only ``CADDY_HTTP_PORT`` is exposed on the host.

MySQL
*****

- ``RUN_MYSQL`` (default: ``true``)
- ``MYSQL_HOST`` (default: ``"mysql"``)
- ``MYSQL_PORT`` (default: ``3306``)
- ``MYSQL_ROOT_USERNAME`` (default: ``"root"``)
- ``MYSQL_ROOT_PASSWORD`` (default: randomly generated) Note that you are responsible for creating the root user if you are using a managed database.

By default, a running Open edX platform deployed with Tutor includes all necessary 3rd-party services, such as MySQL, MongoDb, etc. But it's also possible to store data on a separate database, such as `Amazon RDS <https://aws.amazon.com/rds/>`_. For instance, to store data on an external MySQL database set the following configuration::

    RUN_MYSQL: false
    MYSQL_HOST: yourhost
    MYSQL_ROOT_USERNAME: <root user name>
    MYSQL_ROOT_PASSWORD: <root user password>

.. note::
    When configuring an external MySQL database, please make sure it is using version 8.4.

Elasticsearch
*************

- ``ELASTICSEARCH_SCHEME`` (default: ``"http"``)
- ``ELASTICSEARCH_HOST`` (default: ``"elasticsearch"``)
- ``ELASTICSEARCH_PORT`` (default: ``9200``)
- ``ELASTICSEARCH_HEAP_SIZE`` (default: ``"1g"``)

MongoDB
*******

- ``RUN_MONGODB`` (default: ``true``)
- ``MONGODB_DATABASE`` (default: ``"openedx"``)
- ``MONGODB_HOST`` (default: ``"mongodb"``)
- ``MONGODB_PASSWORD`` (default: ``""``)
- ``MONGODB_PORT`` (default: ``27017``)
- ``MONGODB_USERNAME`` (default: ``""``)
- ``MONGODB_USE_SSL`` (default: ``false``)
- ``MONGODB_REPLICA_SET`` (default: ``""``)
- ``MONGODB_AUTH_MECHANISM`` (default: ``""``)
- ``MONGODB_AUTH_SOURCE`` (default: ``"admin"``)

Note that most of these settings will have to be modified to connect to a MongoDB cluster that runs separately of Tutor, such as `Atlas <https://www.mongodb.com/atlas>`__. In particular, the authentication source, mechanism and the SSL connection parameters should not be specified as part of the `host URI <https://www.mongodb.com/docs/manual/reference/connection-string/>`__ but as separate Tutor settings. Supported values for ``MONGODB_AUTH_MECHANISM`` are the same as for pymongo (see the `pymongo documentation <https://pymongo.readthedocs.io/en/stable/examples/authentication.html>`__).

Redis
*****

- ``RUN_REDIS`` (default: ``true``)
- ``REDIS_HOST`` (default: ``"redis"``)
- ``REDIS_PORT`` (default: ``6379``)
- ``REDIS_USERNAME`` (default: ``""``)
- ``REDIS_PASSWORD`` (default: ``""``)

Note that Redis has replaced Rabbitmq as the Celery message broker since Tutor v11.0.0.

SMTP
****

- ``RUN_SMTP`` (default: ``true``)
- ``SMTP_HOST`` (default: ``"smtp"``)
- ``SMTP_PORT`` (default: ``8025``)
- ``SMTP_USERNAME`` (default: ``""``)
- ``SMTP_PASSWORD`` (default: ``""``)
- ``SMTP_USE_TLS`` (default: ``false``)
- ``SMTP_USE_SSL`` (default: ``false``)

Note that the SMTP server shipped with Tutor by default does not implement TLS. With external servers, only one of SSL or TLS should be enabled, at most.

SSL/TLS certificates for HTTPS access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``ENABLE_HTTPS`` (default: ``false``)

When ``ENABLE_HTTPS`` is ``true``, the whole Open edX platform will be reconfigured to work with "https" URIs. Calls to "http" URIs will be redirected to "https". By default, SSL/TLS certificates will automatically be generated by Tutor (thanks to `Caddy <https://caddyserver.com/>`__) from the `Let's Encrypt <https://letsencrypt.org/>`_ certificate authority.

The following DNS records must exist and point to your server::

    LMS_HOST (e.g: myopenedx.com)
    PREVIEW_LMS_HOST (e.g: preview.myopenedx.com)
    CMS_HOST (e.g: studio.myopenedx.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

If you would like to perform SSL/TLS termination with your own custom certificates, you will have to keep ``ENABLE_HTTPS=true`` and turn off the Caddy load balancing with ``ENABLE_WEB_PROXY=false``. See the corresponding :ref:`tutorial <web_proxy>` for more information.

.. _customise:

.. _custom_openedx_docker_image:

Kubernetes
~~~~~~~~~~

- ``K8S_NAMESPACE`` (default: ``"openedx"``)

This configuration parameter sets the Kubernetes Namespace.

Miscellaneous Project Settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``CONTACT_EMAIL`` (default: ``"contact@{{ LMS_HOST }}"``)

This configuration parameter sets the Contact Email.

- ``PLATFORM_NAME`` (default: ``"My Open edX"``)

This configuration parameter sets the Platform Name.

Custom Open edX docker image
----------------------------

There are different ways you can customise your Open edX platform. For instance, optional features can be activated during configuration. But if you want to add unique features to your Open edX platform, you are going to have to modify and re-build the ``openedx`` docker image. This is the image that contains the ``edx-platform`` repository: it is in charge of running the web application for the Open edX "core". Both the LMS and the CMS run from the ``openedx`` docker image.

On a vanilla platform deployed by Tutor, the image that is run is downloaded from the `overhangio/openedx repository on Docker Hub <https://hub.docker.com/r/overhangio/openedx/>`_. This is also the image that is downloaded whenever we run ``tutor images pull openedx``. But you can decide to build the image locally instead of downloading it. To do so, build and tag the ``openedx`` image::

    tutor images build openedx

The following sections describe how to modify various aspects of the docker image. Every time, you will have to re-build your own image with this command. Re-building should take ~20 minutes on a server with good bandwidth. After building a custom image, you should stop the old running containers::

    tutor local stop

The custom image will be used the next time you run ``tutor local launch`` or ``tutor local start``. Do not attempt to run ``tutor local restart``! Restarting will not pick up the new image and will continue to use the old image.

"openedx" Docker image build arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When building the "openedx" Docker image, it is possible to specify a few `arguments <https://docs.docker.com/engine/reference/builder/#arg>`__:

- ``EDX_PLATFORM_REPOSITORY`` (default: ``"{{ EDX_PLATFORM_REPOSITORY }}"``)
- ``EDX_PLATFORM_VERSION`` (default: ``"{{ EDX_PLATFORM_VERSION }}"``, which if unset defaults to ``{{ OPENEDX_COMMON_VERSION }}``)
- ``NPM_REGISTRY`` (default: ``"{{ NPM_REGISTRY }}"``)

These arguments can be specified from the command line, `very much like Docker <https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg>`__. For instance::

    tutor images build -a EDX_PLATFORM_VERSION=customsha1 openedx

Adding custom themes
~~~~~~~~~~~~~~~~~~~~

See :ref:`the corresponding tutorial <theming>`.

.. _custom_extra_xblocks:

Installing extra xblocks and requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Would you like to include custom xblocks, or extra requirements to your Open edX platform? Additional requirements can be added to the ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` parameter in the :ref:`config file <configuration>`. For instance, to include the `polling xblock from Opencraft <https://github.com/open-craft/xblock-poll/>`_::

    tutor config save --append OPENEDX_EXTRA_PIP_REQUIREMENTS=git+https://github.com/open-craft/xblock-poll.git

Then, the ``openedx`` docker image must be rebuilt::

    tutor images build openedx

.. _edx_platform_fork:

Running a fork of ``edx-platform``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to run your own flavor of edx-platform instead of the `official version <https://github.com/openedx/edx-platform/>`_. To do so, you will have to re-build the openedx image with the proper environment variables pointing to your repository and version::

    tutor images build openedx \
        --build-arg EDX_PLATFORM_REPOSITORY=https://mygitrepo/edx-platform.git \
        --build-arg EDX_PLATFORM_VERSION=my-tag-or-branch

Note that your edx-platform version must be a fork of the latest release **tag** (and not branch) in order to work. This latest tag can be obtained by running::

    tutor config printvalue OPENEDX_COMMON_VERSION

If you don't create your fork from this tag, you *will* have important compatibility issues with other services. In particular:

- Do not try to run a fork from an older (pre-Sumac) version of edx-platform: this will simply not work.
- Do not try to run a fork from the edx-platform master branch: there is a 99% probability that it will fail.
- Do not try to run a fork from the open-release/sumac.master branch: Tutor will attempt to apply security and bug fix patches that might already be included in the release/sumac but which were not yet applied to the latest release tag. Patch application will thus fail if you base your fork from the release/sumac branch.

.. _i18n:

Getting and customizing Translations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tutor builds images with the latest translations using the ``atlas pull`` `command <https://github.com/openedx/openedx-atlas>`_.

By default the translations are pulled from the `openedx-translations repository <https://github.com/openedx/openedx-translations>`_
from the ``ATLAS_REVISION`` branch. You can use custom translations on your fork of the openedx-translations repository by setting the following configuration parameters:

- ``ATLAS_REVISION`` (default: ``"main"`` on nightly and ``"{{ OPENEDX_COMMON_VERSION }}"`` if a named release is used)
- ``ATLAS_REPOSITORY`` (default: ``"openedx/openedx-translations"``). There's a feature request to `support GitLab and other providers <https://github.com/openedx/openedx-atlas/issues/20>`_.
- ``ATLAS_OPTIONS`` (default: ``""``) Pass additional arguments to ``atlas pull``. Refer to the `atlas documentations <https://github.com/openedx/openedx-atlas>`_ for more information.

If you are not running Open edX in English (``LANGUAGE_CODE`` default: ``"en"``), chances are that some strings will not be properly translated. In most cases, this is because not enough contributors have helped translate Open edX into your language. It happens!

With ``atlas``, it's possible to add custom translations by either `contributing to the Translations project in Transifex <https://docs.openedx.org/en/latest/translators/index.html>`_ or forking the `openedx-translations repository <https://github.com/openedx/openedx-translations>`_
and making custom changes as explained in `the repository docs <https://github.com/openedx/openedx-translations#readme>`_.

Running a different ``openedx`` Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Tutor runs the `overhangio/openedx <https://hub.docker.com/r/overhangio/openedx/>`_ docker image from Docker Hub. If you have an account on `hub.docker.com <https://hub.docker.com>`_ or you have a private image registry, you can build your image and push it to your registry with::

    tutor config save --set DOCKER_IMAGE_OPENEDX=docker.io/myusername/openedx:mytag
    tutor images build openedx
    tutor images push openedx

(See the relevant :ref:`configuration parameters <docker_images>`.)

The customised Docker image tag value will then be used by Tutor to run the platform, for instance when running ``tutor local launch``.


Passing custom docker build options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can set a limited set of Docker build options via ``tutor images build`` command. In some situations it might be necessary to tweak the docker build command, ex- setting up build caching using buildkit.
In these situations, you can set ``--docker-arg`` flag in the ``tutor images build`` command. You can set any `supported options <https://docs.docker.com/engine/reference/commandline/build/#options>`_ in the docker build command, For example::

    tutor images build openedx \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --docker-arg="--cache-from" \
        --docker-arg="docker.io/myusername/openedx:mytag"

This will result in passing the ``--cache-from`` option with the value ``docker.io/myusername/openedx:mytag`` to the docker build command.
