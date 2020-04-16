.. _configuration_customisation:

Configuration and customisation
===============================

Tutor offers plenty of possibilities for platform customisation out of the box. There are two main ways in which the base Open edX installation can be customized:

a. Modifying the Tutor :ref:`configuration parameters <configuration>`.
b. Modifying the :ref:`Open edX docker image <customise>` that runs the Open edX platform.

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

- ``ACTIVATE_LMS`` (default: ``true``)
- ``ACTIVATE_CMS`` (default: ``true``)
- ``ACTIVATE_FORUM`` (default: ``true``)
- ``ACTIVATE_ELASTICSEARCH`` (default: ``true``)
- ``ACTIVATE_MEMCACHED`` (default: ``true``)
- ``ACTIVATE_MONGODB`` (default: ``true``)
- ``ACTIVATE_MYSQL`` (default: ``true``)
- ``ACTIVATE_RABBITMQ`` (default: ``true``)
- ``ACTIVATE_SMTP`` (default: ``true``)
- ``ACTIVATE_HTTPS`` (default: ``false``)

Every single Open edX service may be (de)activated at will by these configuration parameters. This is useful if you want, for instance, to distribute the various Open edX services on different servers.

Docker
~~~~~~

.. _docker_images:

Custom images
*************

- ``DOCKER_IMAGE_OPENEDX`` (default: ``"overhangio/openedx:{{ TUTOR_VERSION }}"``)
- ``DOCKER_IMAGE_ANDROID`` (default: ``"overhangio/openedx-android:{{ TUTOR_VERSION }}"``)
- ``DOCKER_IMAGE_FORUM`` (default: ``"overhangio/openedx-forum:{{ TUTOR_VERSION }}"``)

These configuration parameters define which image to run for each service. By default, the docker image tag matches the Tutor version it was built with.

Custom registry
***************

- ``DOCKER_REGISTRY`` (default: ``"docker.io/"``)

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

Open edX customisation
~~~~~~~~~~~~~~~~~~~~~~

- ``OPENEDX_CMS_GUNICORN_WORKERS`` (default: ``2``)
- ``OPENEDX_LMS_GUNICORN_WORKERS`` (default: ``2``)

By default there are 2 `gunicorn worker processes <https://docs.gunicorn.org/en/stable/settings.html#worker-processes>`__ to serve requests for the LMS and the CMS. However, each workers requires upwards of 500 Mb of RAM. You should reduce this value to 1 if your computer/server does not have enough memory.

Vendor services
~~~~~~~~~~~~~~~

Nginx
*****

- ``NGINX_HTTP_PORT`` (default: ``80``)
- ``NGINX_HTTPS_PORT`` (default: ``443``)
- ``WEB_PROXY`` (default: ``true``)

Nginx is used to route web traffic to the various applications and to serve static assets. In case there is another web server in front of the Nginx container (for instance, a web server running on the host or an Ingress controller on Kubernetes), the container exposed ports can be modified. If ``WEB_PROXY`` is set to ``true`` then we assume that SSL termination does not occur in the Nginx container.

MySQL
*****

- ``ACTIVATE_MYSQL`` (default: ``true``)
- ``MYSQL_HOST`` (default: ``"mysql"``)
- ``MYSQL_PORT`` (default: ``3306``)
- ``MYSQL_ROOT_PASSWORD`` (default: randomly generated) Note that you are responsible for creating the root user if you are using a managed database.

By default, a running Open edX platform deployed with Tutor includes all necessary 3rd-party services, such as MySQL, MongoDb, etc. But it's also possible to store data on a separate database, such as `Amazon RDS <https://aws.amazon.com/rds/>`_. For instance, to store data on an external MySQL database, set the following configuration::

    ACTIVATE_MYSQL: false
    MYSQL_HOST: yourhost
    MYSQL_ROOT_PASSWORD: <root user password>

Elasticsearch
*************

- ``ELASTICSEARCH_SCHEME`` (default: ``"http"``)
- ``ELASTICSEARCH_HOST`` (default: ``"elasticsearch"``)
- ``ELASTICSEARCH_PORT`` (default: ``9200``)
- ``ELASTICSEARCH_HEAP_SIZE`` (default: ``"1g"``)

Memcached
*********

- ``MEMCACHED_HOST`` (default: ``"memcached"``)
- ``MEMCACHED_PORT`` (default: ``11211``)

Mongodb
*******

- ``ACTIVATE_MONGODB`` (default: ``true``)
- ``MONGODB_HOST`` (default: ``"mongodb"``)
- ``MONGODB_DATABASE`` (default: ``"openedx"``)
- ``MONGODB_PORT`` (default: ``27017``)
- ``MONGODB_USERNAME`` (default: ``""``)
- ``MONGODB_PASSWORD`` (default: ``""``)

Rabbitmq
********

- ``ACTIVATE_RABBITMQ`` (default: ``true``)
- ``RABBITMQ_HOST`` (default: ``"rabbitmq"``)
- ``RABBITMQ_USERNAME`` (default: ``""``)
- ``RABBITMQ_PASSWORD`` (default: ``""``)

SMTP
****

- ``ACTIVATE_SMTP`` (default: ``true``)
- ``SMTP_HOST`` (default: ``"smtp"``)
- ``SMTP_PORT`` (default: ``25``)
- ``SMTP_USERNAME`` (default: ``""``)
- ``SMTP_PASSWORD`` (default: ``""``)
- ``SMTP_USE_TLS`` (default: ``false``)
- ``SMTP_USE_SSL`` (default: ``false``)

Note that the SMTP server shipped with Tutor by default does not implement TLS. With external servers, only one of SSL or TLS should be enabled, at most.

SSL/TLS certificates for HTTPS access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``ACTIVATE_HTTPS`` (default: ``false``)

By activating this feature, a free SSL/TLS certificate from the `Let's Encrypt <https://letsencrypt.org/>`_ certificate authority will be created for your platform. With this feature, **your platform will no longer be accessible in HTTP**. Calls to http urls will be redirected to https url.

The following DNS records must exist and point to your server::

    LMS_HOST (e.g: myopenedx.com)
    preview.LMS_HOST (e.g: preview.myopenedx.com)
    CMS_HOST (e.g: studio.myopenedx.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

To create the certificate manually, run::

    tutor local https create

To renew the certificate, run this command once per month::

    tutor local stop nginx
    tutor local https renew
    tutor local start -d

.. _customise:

Custom Open edX docker image
----------------------------

There are different ways you can customise your Open edX platform. For instance, optional features can be activated during configuration. But if you want to add unique features to your Open edX platform, you are going to have to modify and re-build the ``openedx`` docker image. This is the image that contains the ``edx-platform`` repository: it is in charge of running the web application for the Open edX "core". Both the LMS and the CMS run from the ``openedx`` docker image. 

On a vanilla platform deployed by Tutor, the image that is run is downloaded from the `overhangio/openedx repository on Docker Hub <https://hub.docker.com/r/overhangio/openedx/>`_. This is also the image that is downloaded whenever we run ``tutor local pullimages``. But you can decide to build the image locally instead of downloading it. To do so, build and tag the ``openedx`` image::

    tutor images build openedx

The following sections describe how to modify various aspects of the docker image. Every time, you will have to re-build your own image with this command. Re-building should take ~20 minutes on a server with good bandwidth. After building a custom image, you should stop the old running containers::

    tutor local stop openedx

The custom image will be used the next time you run ``tutor local quickstart`` or ``tutor local start``. Do not attempt to run ``tutor local restart``! Restarting will not pick up the new image and will continue to use the old image.

openedx Docker Image build arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When building the "openedx" Docker image, it is possible to specify a few `arguments <https://docs.docker.com/engine/reference/builder/#arg>`__:

- ``EDX_PLATFORM_REPOSITORY`` (default: ``"https://github.com/edx/edx-platform.git"``)
- ``EDX_PLATFORM_VERSION`` (default: ``"open-release/ironwood.master"``)
- ``EDX_PLATFORM_VERSION_DATE`` (default: ``"20200227"``)
- ``NPM_REGISTRY`` (default: ``"https://registry.npmjs.org/"``)

These arguments can be specified from the command line, `very much like Docker <https://docs.docker.com/engine/reference/commandline/build/#set-build-time-variables---build-arg>`__. For instance::
    
    tutor images build -a EDX_PLATFORM_VERSION=customsha1 openedx

Adding custom themes
~~~~~~~~~~~~~~~~~~~~

Comprehensive theming is enabled by default, but only the default theme is compiled. To compile your own theme, add it to the ``env/build/openedx/themes/`` folder::

    git clone https://github.com/me/myopenedxtheme.git "$(tutor config printroot)/env/build/openedx/themes/"

The ``themes`` folder should have the following structure::

    openedx/themes/
        mycustomtheme1/
            cms/
                ...
            lms/
                ...
        mycustomtheme2/
            ...

Then you must rebuild the openedx Docker image::

    tutor images build openedx

Finally, follow the `Open edX documentation to apply your themes <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/changing_appearance/theming/enable_themes.html#apply-a-theme-to-a-site>`_. You will not have to modify the ``lms.env.json``/``cms.env.json`` files; just follow the instructions to add a site theme in http://localhost/admin (starting from step 3).

Installing extra xblocks and requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Would you like to include custom xblocks, or extra requirements to your Open edX platform? Additional requirements can be added to the ``env/build/openedx/requirements/private.txt`` file. For instance, to include the `polling xblock from Opencraft <https://github.com/open-craft/xblock-poll/>`_::

    echo "git+https://github.com/open-craft/xblock-poll.git" >> "$(tutor config printroot)/env/build/openedx/requirements/private.txt"

Then, the ``openedx`` docker image must be rebuilt::

    tutor images build openedx

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

Note that your release must be a fork of Ironwood in order to work. Otherwise, you may have important compatibility issues with other services. In particular, **don't try to run Tutor with older versions of Open edX**.

Running a different ``openedx`` Docker image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, Tutor runs the `overhangio/openedx <https://hub.docker.com/r/overhangio/openedx/>`_ docker image from Docker Hub. If you have an account on `hub.docker.com <https://hub.docker.com>`_ or you have a private image registry, you can build your image and push it to your registry with::

    tutor config save --set DOCKER_IMAGE_OPENEDX=myusername/openedx:mytag
    tutor images build openedx
    tutor images push openedx

(See the relevant :ref:`configuration parameters <docker_images>`.)

The customised Docker image tag value will then be used by Tutor to run the platform, for instance when running ``tutor local quickstart``.
