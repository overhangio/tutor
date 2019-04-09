.. _configuration:

Configuration
=============

With Tutor, all Open edX deployment parameters are stored in a single ``config.yml`` file. This is the file that is generated when you run ``tutor local quickstart`` or ``tutor config save``. To view the content of this file, run::

    cat "$(tutor config printroot)/config.yml"

By default, this file contains only the required configuration parameters for running the platform. Optional configuration parameters may also be specified to modify the default behaviour. To do so, you can edit the ``config.yml`` file manually::

    vim "$(tutor config printroot)/config.yml"

Alternatively, you can set each parameter from the command line::

    tutor config save -y --set PARAM1=VALUE1 --set PARAM2=VALUE2

Or from the system environment::

    export TUTOR_PARAM1=VALUE1

Once the base configuration is created or updated, the environment is automatically re-generated. The environment is the set of all files required to manage an Open edX platform: Dockerfile, ``lms.env.json``, settings files, etc. You can view the environment files in the ``env`` folder::

    ls "$(tutor config printroot)/env"

With an up-to-date environment, Tutor is ready to launch an Open edX platform and perform usual operations. Below, we document some of the configuration parameters.

Docker
------

.. _docker_images:

Custom images
-------------

- ``DOCKER_IMAGE_OPENEDX`` (default: ``"regis/openedx:ironwood"``)
- ``DOCKER_IMAGE_ANDROID`` (default: ``"regis/openedx-android:ironwood"``)
- ``DOCKER_IMAGE_FORUM`` (default: ``"regis/openedx-forum:ironwood"``)
- ``DOCKER_IMAGE_NOTES`` (default: ``"regis/openedx-notes:ironwood"``)
- ``DOCKER_IMAGE_XQUEUE`` (default: ``"regis/openedx-xqueue:ironwood"``)

These configuration parameters define which image to run for each service.

Custom registry
---------------

- ``DOCKER_REGISTRY`` (default: ``""``)

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

Vendor services
---------------

MySQL
~~~~~

- ``ACTIVATE_MYSQL`` (default: ``true``)
- ``MYSQL_HOST`` (default: ``"mysql"``)
- ``MYSQL_PORT`` (default: ``3306``)
- ``MYSQL_ROOT_PASSWORD`` (default: randomly generated) Note that you are responsible for creating the root user if you are using a managed database.

By default, a running Open edX platform deployed with Tutor includes all necessary 3rd-party services, such as MySQL, MongoDb, etc. But it's also possible to store data on a separate database, such as `Amazon RDS <https://aws.amazon.com/rds/>`_. For instance, to store data on an external MySQL database, set the following configuration::

    ACTIVATE_MYSQL: false
    MYSQL_HOST: yourhost
    MYSQL_ROOT_PASSWORD: <root user password>

Elasticsearch
~~~~~~~~~~~~~

- ``ELASTICSEARCH_HOST`` (default: ``"elasticsearch"``)
- ``ELASTICSEARCH_PORT`` (default: ``9200``)

Memcached
~~~~~~~~~

- ``MEMCACHED_HOST`` (default: ``"memcached"``)
- ``MEMCACHED_PORT`` (default: ``11211``)

Mongodb
~~~~~~~

- ``ACTIVATE_MONGODB`` (default: ``true``)
- ``MONGODB_HOST`` (default: ``"mongodb"``)
- ``MONGODB_DATABASE`` (default: ``"openedx"``)
- ``MONGODB_PORT`` (default: ``27017``)
- ``MONGODB_USERNAME`` (default: ``""``)
- ``MONGODB_PASSWORD`` (default: ``""``)

Rabbitmq
~~~~~~~~

- ``ACTIVATE_RABBITMQ`` (default: ``true``)
- ``RABBITMQ_HOST`` (default: ``"rabbitmq"``)
- ``RABBITMQ_USERNAME`` (default: ``""``)
- ``RABBITMQ_PASSWORD`` (default: ``""``)

SMTP
~~~~

- ``ACTIVATE_SMTP`` (default: ``true``)
- ``SMTP_HOST`` (default: ``"smtp"``)
- ``SMTP_PORT`` (default: ``25``)
- ``SMTP_USERNAME`` (default: ``""``)
- ``SMTP_PASSWORD`` (default: ``""``)

Optional features
-----------------

Some optional features may be activated or deactivated during the interactive configuration step (``tutor config save``).

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

    tutor local https renew

Student notes
~~~~~~~~~~~~~

- ``ACTIVATE_NOTES`` (default: ``false``)

With `notes <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-ironwood.master/exercises_tools/notes.html?highlight=notes>`_, students can annotate portions of the courseware. 

.. image:: https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-ironwood.master/_images/SFD_SN_bodyexample.png
    :alt: Notes in action

You should beware that the ``notes.<LMS_HOST>`` domain name should be activated and point to your server. For instance, if your LMS is hosted at http://myopenedx.com, the notes service should be found at http://notes.myopenedx.com.

Xqueue
~~~~~~

- ``ACTIVATE_XQUEUE`` (default: ``false``)

`Xqueue <https://github.com/edx/xqueue>`_ is for grading problems with external services. If you don't know what it is, you probably don't need it.
