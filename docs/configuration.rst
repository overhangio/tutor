.. _configuration:

Configuration
=============

With Tutor, all Open edX deployment parameters are stored in a single ``config.yml`` file. This is the file that is generated when you run ``tutor local quickstart`` or ``tutor config save``. To view the content of this file, run::

    cat $(tutor config printroot)/config.yml

By default, this file contains only the required configuration parameters for running the platform. Optional configuration parameters may also be specified to modify the default behaviour. To do so, you can edit the ``config.yml`` file manually::

    vim $(tutor config printroot)/config.yml

Alternatively, you can set each parameter from the command line::

    tutor config save --silent --set PARAM1=VALUE1 --set PARAM2=VALUE2

Or from the system environment::

    export TUTOR_PARAM1=VALUE1

Once the base configuration is created or updated, the environment is automatically re-generated. The environment is the set of all files required to manage an Open edX platform: Dockerfile, ``lms.env.json``, settings files, etc. You can view the environment files in the ``env`` folder::

    ls $(tutor config printroot)/env

With an up-to-date environment, Tutor is ready to launch an Open edX platform and perform usual operations. Below, we document some of the configuration parameters.

.. _docker_images:

``DOCKER_IMAGE_*`` Custom Docker images
---------------------------------------

These configuration parameters define which image to run for each service.

- ``DOCKER_IMAGE_OPENEDX`` (default: ``regis/openedx:hawthorn``)
- ``DOCKER_IMAGE_ANDROID`` (default: ``regis/openedx-android:hawthorn``)
- ``DOCKER_IMAGE_FORUM`` (default: ``regis/openedx-forum:hawthorn``)
- ``DOCKER_IMAGE_NOTES`` (default: ``regis/openedx-notes:hawthorn``)
- ``DOCKER_IMAGE_XQUEUE`` (default: ``regis/openedx-xqueue:hawthorn``)

``DOCKER_REGISTRY`` Custom Docker registry
------------------------------------------

You may want to pull/push images from/to a custom docker registry. For instance, for a registry running on ``localhost:5000``, define::

    DOCKER_REGISTRY: localhost:5000/

(the trailing ``/`` is important)

``ACTIVATE_*`` Optional features
--------------------------------

Some optional features may be activated or deactivated during the interactive configuration step. These features change configuration files (during the ``configure`` step) as well as make targets.

``ACTIVATE_HTTPS`` SSL/TLS certificates for HTTPS access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

``ACTIVATE_NOTES`` Student notes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With `notes <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/exercises_tools/notes.html?highlight=notes>`_, students can annotate portions of the courseware. 

.. image:: https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/_images/SFD_SN_bodyexample.png
    :alt: Notes in action

You should beware that the ``notes.<LMS_HOST>`` domain name should be activated and point to your server. For instance, if your LMS is hosted at http://myopenedx.com, the notes service should be found at http://notes.myopenedx.com.

``ACTIVATE_XQUEUE`` Xqueue
~~~~~~~~~~~~~~~~~~~~~~~~~~

`Xqueue <https://github.com/edx/xqueue>`_ is for grading problems with external services. If you don't know what it is, you probably don't need it.
