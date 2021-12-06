.. _configuration_customisation:

Configuration and customisation
===============================

Tutor offers plenty of possibilities for platform customisation out of the box. There are two main ways in which the base Open edX installation can be customized:

a. Modifying the Tutor :ref:`configuration parameters <configuration>`.
b. Modifying the :ref:`Open edX docker image <customise>` that runs the Open edX platform.

This section does not cover :ref:`plugin development <plugins>`. For simple changes, such as modifying the ``*.env.json`` files or the edx-platform settings, *you should not fork edx-platform or tutor*! Instead, you should create a simple :ref:`plugin for Tutor <plugins_yaml>`.

.. _configuration:

Configuration
-------------

With Tutor, all Open edX deployment parameters are stored in a single ``config.yml`` file. This is the file that is generated when you run ``tutor local quickstart`` or ``tutor config save``. To view the content of this file, run::

    cat "$(tutor config printroot)/config.yml"

By default, this file contains only the required configuration parameters for running the platform. Optional configuration parameters may also be specified to modify the default behaviour. To do so, you can edit the ``config.yml`` file manually::

    vim "$(tutor config printroot)/config.yml"

Alternatively, you can set each parameter from the command line::

    tutor config save --set PARAM1=VALUE1 --set PARAM2=VALUE2

Or from the system environment::

    export TUTOR_PARAM1=VALUE1

Once the base configuration is created or updated, the environment is automatically re-generated. The environment is the set of all files required to manage an Open edX platform: Dockerfile, ``lms.env.json``, settings files, etc. You can view the environment files in the ``env`` folder::

    ls "$(tutor config printroot)/env"

With an up-to-date environment, Tutor is ready to launch an Open edX platform and perform usual operations. Below, we document some of the configuration parameters.

Individual service activation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``RUN_LMS`` (default: ``true``)
- ``RUN_CMS`` (default: ``true``)
- ``RUN_FORUM`` (default: ``true``)
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
- ``DOCKER_IMAGE_FORUM`` (default: ``"{{ DOCKER_REGISTRY }}overhangio/openedx-forum:{{ TUTOR_VERSION }}"``)

These configuration parameters define which image to run for each service. By default, the docker image tag matches the Tutor version it was built with.

Custom registry
***************

- ``DOCKER_REGISTRY`` (default: ``"docker.io/"``)

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

Open edX customisation
~~~~~~~~~~~~~~~~~~~~~~

- ``OPENEDX_COMMON_VERSION`` (default: ``"open-release/lilac.2"``)

This defines the default version that will be pulled from all Open edX git repositories.

- ``OPENEDX_CMS_UWSGI_WORKERS`` (default: ``2``)
- ``OPENEDX_LMS_UWSGI_WORKERS`` (default: ``2``)

By default there are 2 `uwsgi worker processes <https://uwsgi-docs.readthedocs.io/en/latest/Options.html#processes>`__ to serve requests for the LMS and the CMS. However, each workers requires upwards of 500 Mb of RAM. You should reduce this value to 1 if your computer/server does not have enough memory.

- ``OPENEDX_CELERY_REDIS_DB`` (default: ``0``)
- ``OPENEDX_CACHE_REDIS_DB`` (default: ``1``)

These two configuration parameters define which redis database to use for Open edX cache and celery task.

.. _openedx_extra_pip_requirements:

- ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` (default: ``openedx-scorm-xblock<13.0.0,>=12.0.0``)

This defines extra pip packages that are going to be installed for Open edX.

Vendor services
~~~~~~~~~~~~~~~

Caddy
*****

- ``RUN_CADDY`` (default: ``true``)

`Caddy <https://caddyserver.com>`__ is a web server used in Tutor as a web proxy for the generation of SSL/TLS certificates at runtime. If ``RUN_CADDY`` is set to ``false`` then we assume that SSL termination does not occur in the Caddy container, and thus the ``caddy`` container is not started.

Nginx
*****

- ``NGINX_HTTP_PORT`` (default: ``80``)

Nginx is used to route web traffic to the various applications and to serve static assets. When ``RUN_CADDY`` is false, the ``NGINX_HTTP_PORT`` is exposed on the host.

MySQL
*****

- ``RUN_MYSQL`` (default: ``true``)
- ``MYSQL_HOST`` (default: ``"mysql"``)
- ``MYSQL_PORT`` (default: ``3306``)
- ``MYSQL_ROOT_USERNAME`` (default: ``"root"``)
- ``MYSQL_ROOT_PASSWORD`` (default: randomly generated) Note that you are responsible for creating the root user if you are using a managed database.

By default, a running Open edX platform deployed with Tutor includes all necessary 3rd-party services, such as MySQL, MongoDb, etc. But it's also possible to store data on a separate database, such as `Amazon RDS <https://aws.amazon.com/rds/>`_. For instance, to store data on an external MySQL database, set the following configuration::

    RUN_MYSQL: false
    MYSQL_HOST: yourhost
    MYSQL_ROOT_USERNAME: <root user name>
    MYSQL_ROOT_PASSWORD: <root user password>

.. note::
    When configuring an external MySQL database, please make sure it is using version 5.7.

Elasticsearch
*************

- ``ELASTICSEARCH_SCHEME`` (default: ``"http"``)
- ``ELASTICSEARCH_HOST`` (default: ``"elasticsearch"``)
- ``ELASTICSEARCH_PORT`` (default: ``9200``)
- ``ELASTICSEARCH_HEAP_SIZE`` (default: ``"1g"``)

Mongodb
*******

- ``RUN_MONGODB`` (default: ``true``)
- ``MONGODB_HOST`` (default: ``"mongodb"``)
- ``MONGODB_DATABASE`` (default: ``"openedx"``)
- ``MONGODB_PORT`` (default: ``27017``)
- ``MONGODB_USERNAME`` (default: ``""``)
- ``MONGODB_PASSWORD`` (default: ``""``)

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
- ``SMTP_PORT`` (default: ``25``)
- ``SMTP_USERNAME`` (default: ``""``)
- ``SMTP_PASSWORD`` (default: ``""``)
- ``SMTP_USE_TLS`` (default: ``false``)
- ``SMTP_USE_SSL`` (default: ``false``)

Note that the SMTP server shipped with Tutor by default does not implement TLS. With external servers, only one of SSL or TLS should be enabled, at most.

Forum
*****

- ``RUN_FORUM`` (default: ``true``)
- ``FORUM_HOST`` (default: ``"forum"``)
- ``FORUM_MONGODB_DATABASE`` (default: ``"cs_comments_service"``)

SSL/TLS certificates for HTTPS access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``ENABLE_HTTPS`` (default: ``false``)

When ``ENABLE_HTTPS`` is ``true``, the whole Open edX platform will be reconfigured to work with "https" URIs. Calls to "http" URIs will be redirected to "https". By default, SSL/TLS certificates will automatically be generated by Tutor (thanks to `Caddy <https://caddyserver.com/>`__) from the `Let's Encrypt <https://letsencrypt.org/>`_ certificate authority.

The following DNS records must exist and point to your server::

    LMS_HOST (e.g: myopenedx.com)
    PREVIEW_LMS_HOST (e.g: preview.myopenedx.com)
    CMS_HOST (e.g: studio.myopenedx.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

If you would like to perform SSL/TLS termination with your own custom certificates, you will have to keep ``ENABLE_HTTPS=true`` and turn off the Caddy server with ``RUN_CADDY=false``. See the corresponding :ref:`tutorial <web_proxy>` for more information.

.. _customise:

.. _custom_openedx_docker_image:

Custom Open edX docker image
----------------------------

There are different ways you can customise your Open edX platform. For instance, optional features can be activated during configuration. But if you want to add unique features to your Open edX platform, you are going to have to modify and re-build the ``openedx`` docker image. This is the image that contains the ``edx-platform`` repository: it is in charge of running the web application for the Open edX "core". Both the LMS and the CMS run from the ``openedx`` docker image.

On a vanilla platform deployed by Tutor, the image that is run is downloaded from the `overhangio/openedx repository on Docker Hub <https://hub.docker.com/r/overhangio/openedx/>`_. This is also the image that is downloaded whenever we run ``tutor images pull openedx``. But you can decide to build the image locally instead of downloading it. To do so, build and tag the ``openedx`` image::

    tutor images build openedx

The following sections describe how to modify various aspects of the docker image. Every time, you will have to re-build your own image with this command. Re-building should take ~20 minutes on a server with good bandwidth. After building a custom image, you should stop the old running containers::

    tutor local stop

The custom image will be used the next time you run ``tutor local quickstart`` or ``tutor local start``. Do not attempt to run ``tutor local restart``! Restarting will not pick up the new image and will continue to use the old image.

openedx Docker Image build arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When building the "openedx" Docker image, it is possible to specify a few `arguments <https://docs.docker.com/engine/reference/builder/#arg>`__:

- ``EDX_PLATFORM_REPOSITORY`` (default: ``"https://github.com/edx/edx-platform.git"``)
- ``EDX_PLATFORM_VERSION`` (default: ``"{{ OPENEDX_COMMON_VERSION }}"``)
- ``NPM_REGISTRY`` (default: ``"https://registry.npmjs.org/"``)

These arguments can be specified from the command line, `very much like Docker <https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg>`__. For instance::

    tutor images build -a EDX_PLATFORM_VERSION=customsha1 openedx

Adding custom themes
~~~~~~~~~~~~~~~~~~~~

See :ref:`the corresponding tutorial <theming>`.

.. _custom_extra_xblocks:

Installing extra xblocks and requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Would you like to include custom xblocks, or extra requirements to your Open edX platform? Additional requirements can be added to the ``OPENEDX_EXTRA_PIP_REQUIREMENTS`` parameter in the :ref:`config file <configuration>` or to the ``env/build/openedx/requirements/private.txt`` file. The difference between them, is that ``private.txt`` file, even though it could be used for both, :ref:`should be used for installing extra xblocks or requirements from private repositories <extra_private_xblocks>`. For instance, to include the `polling xblock from Opencraft <https://github.com/open-craft/xblock-poll/>`_:

- add the following to the ``config.yml``::

    OPENEDX_EXTRA_PIP_REQUIREMENTS:
    - "git+https://github.com/open-craft/xblock-poll.git"

.. warning::
   Specifying extra requirements through ``config.yml`` overwrites :ref:`the default extra requirements<openedx_extra_pip_requirements>`. You might need to add them to the list, if your configuration depends on them.

- or add the dependency to ``private.txt``::

    echo "git+https://github.com/open-craft/xblock-poll.git" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"


Then, the ``openedx`` docker image must be rebuilt::

    tutor images build openedx

.. _extra_private_xblocks:

Installing extra requirements from private repositories
*******************************************************

When installing extra xblock or requirements from private repositories, ``private.txt`` file should be used, because it allows to install dependencies without adding git credentials to the Docker image. By adding your git credentials to the Docker image, you're risking leaking your git credentials, if you were to publish (intentionally or unintentionally) the Docker image in a public place.

To install xblocks from a private repository that requires authentication, you must first clone the repository inside the ``openedx/requirements`` folder on the host::

    git clone git@github.com:me/myprivaterepo.git "$(tutor config printroot)/env/build/openedx/requirements/myprivaterepo"

Then, declare your extra requirements with the ``-e`` flag in ``openedx/requirements/private.txt``::

    echo "-e ./myprivaterepo" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"

.. _edx_platform_fork:

Running a fork of ``edx-platform``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You may want to run your own flavor of edx-platform instead of the `official version <https://github.com/edx/edx-platform/>`_. To do so, you will have to re-build the openedx image with the proper environment variables pointing to your repository and version::

    tutor images build openedx \
        --build-arg EDX_PLATFORM_REPOSITORY=https://mygitrepo/edx-platform.git \
        --build-arg EDX_PLATFORM_VERSION=my-tag-or-branch

Note that your edx-platform version must be a fork of the latest release **tag** (and not branch) in order to work. This latest tag can be obtained by running::

    tutor config printvalue OPENEDX_COMMON_VERSION

If you don't create your fork from this tag, you *will* have important compatibility issues with other services. In particular:

- Do not try to run a fork from an older (pre-Lilac) version of edx-platform: this will simply not work.
- Do not try to run a fork from the edx-platform master branch: there is a 99% probability that it will fail.
- Do not try to run a fork from the open-release/lilac.master branch: Tutor will attempt to apply security and bug fix patches that might already be included in the open-release/lilac.master but which were not yet applied to the latest release tag. Patch application will thus fail if you base your fork from the open-release/lilac.master branch.

.. _i18n:

Adding custom translations
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are not running Open edX in English, chances are that some strings will not be properly translated. In most cases, this is because not enough contributors have helped translate Open edX in your language. It happens! With Tutor, available translated languages include those that come bundled with `edx-platform <https://github.com/edx/edx-platform/tree/open-release/lilac.master/conf/locale>`__ as well as those from `openedx-i18n <https://github.com/openedx/openedx-i18n/tree/master/edx-platform/locale>`__.

Tutor offers a relatively simple mechanism to add custom translations to the openedx Docker image. You should create a folder that corresponds to your language code in the "build/openedx/locale" folder of the Tutor environment. This folder should contain a "LC_MESSAGES" folder. For instance::

    mkdir -p "$(tutor config printroot)/env/build/openedx/locale/fr/LC_MESSAGES"

The language code should be similar to those used in edx-platform or openedx-i18n (see links above).

Then, add a "django.po" file there that will contain your custom translations::

    msgid ""
    msgstr ""
    "Content-Type: text/plain; charset=UTF-8"

    msgid "String to translate"
    msgstr "你翻译的东西 la traduction de votre bidule"


.. warning::
    Don't forget to specify the file ``Content-Type`` when adding message strings with non-ASCII characters; otherwise a ``UnicodeDecodeError`` will be raised during compilation.

The "String to translate" part should match *exactly* the string that you would like to translate. You cannot make it up! The best way to find this string is to copy-paste it from the `upstream django.po file for the English language <https://github.com/edx/edx-platform/blob/open-release/lilac.master/conf/locale/en/LC_MESSAGES/django.po>`__.

If you cannot find the string to translate in this file, then it means that you are trying to translate a string that is used in some piece of javascript code. Those strings are stored in a different file named "djangojs.po". You can check it out `in the edx-platform repo as well <https://github.com/edx/edx-platform/blob/open-release/lilac.master/conf/locale/en/LC_MESSAGES/djangojs.po>`__. Your custom javascript strings should also be stored in a "djangojs.po" file that should be placed in the same directory.

To recap, here is an example. To translate a few strings in French, both from django.po and djangojs.po, we would have the following file hierarchy::

    $(tutor config printroot)/env/build/openedx/locale/
        fr/
            LC_MESSAGES/
                django.po
                djangojs.po

With django.po containing::

    msgid ""
    msgstr ""
    "Content-Type: text/plain; charset=UTF-8"

    msgid "It works! Powered by Open edX{registered_trademark}"
    msgstr "Ça marche ! Propulsé by Open edX{registered_trademark}"

And djangojs.po::

    msgid ""
    msgstr ""
    "Content-Type: text/plain; charset=UTF-8"

    msgid "%(num_points)s point possible (graded, results hidden)"
    msgid_plural "%(num_points)s points possible (graded, results hidden)"
    msgstr[0] "%(num_points)s point possible (noté, résultats cachés)"
    msgstr[1] "%(num_points)s points possibles (notés, résultats cachés)"

Then you will have to re-build the openedx Docker image::

    tutor images build openedx openedx-dev

Beware that this will take a long time! Unfortunately it's difficult to accelerate this process, as translation files need to be compiled prior to collecting the assets. In development it's possible to accelerate the iteration loop -- but that exercise is left to the reader.


Running a different ``openedx`` Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Tutor runs the `overhangio/openedx <https://hub.docker.com/r/overhangio/openedx/>`_ docker image from Docker Hub. If you have an account on `hub.docker.com <https://hub.docker.com>`_ or you have a private image registry, you can build your image and push it to your registry with::

    tutor config save --set DOCKER_IMAGE_OPENEDX=docker.io/myusername/openedx:mytag
    tutor images build openedx
    tutor images push openedx

(See the relevant :ref:`configuration parameters <docker_images>`.)

The customised Docker image tag value will then be used by Tutor to run the platform, for instance when running ``tutor local quickstart``.


Passing custom docker build options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can set a limited set of Docker build options via ``tutor images build`` command. In some situations it might be necessary to tweak the docker build command, ex- setting up build caching using buildkit.
In these situations, you can set ``--docker-arg`` flag in the ``tutor images build`` command. You can set any `supported options <https://docs.docker.com/engine/reference/commandline/build/#options>`_ in the docker build command, For example::

    tutor images build openedx \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --docker-arg="--cache-from" \
        --docker-arg="docker.io/myusername/openedx:mytag"

This will result in passing the ``--cache-from`` option with the value ``docker.io/myusername/openedx:mytag`` to the docker build command.
