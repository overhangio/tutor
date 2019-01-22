.. _customise:

Open edX platform customisation
===============================

There are different ways you can customise your Open edX platform. For instance, optional features can be activated during configuration. But if you want to add unique features to your Open edX platform, you are going to have to modify and re-build the ``openedx`` docker image. This is the image that contains the ``edx-platform`` repository: it is in charge of running the web application for the Open edX "core". Both the LMS and the CMS run from the ``openedx`` docker image. 

On a vanilla platform deployed by Tutor, the image that is run is downloaded from the `regis/openedx repository on Docker Hub <https://hub.docker.com/r/regis/openedx/>`_. This is also the image that is downloaded whenever we run ``tutor local pullimages``. But you can decide to build the image locally instead of downloading it. To do so, generate the image-building environment::

    tutor images env

Then, build and tag the ``openedx`` image::

    tutor images build openedx

The following sections describe how to modify various aspects of the docker image. Every time, you will have to re-build your own image with this command. Re-building should take ~20 minutes on a server with good bandwidth. After that, your custom image will be used for all commands. For instance:

1. you can start a local platform with ``tutor local start``
2. restart the services that use the ``openedx`` image with ``tutor local restart openedx``

Adding custom themes
--------------------

Comprehensive theming is enabled by default, but only the default theme is compiled. To compile your own theme, add it to the ``env/build/openedx/themes/`` folder::

    git clone https://github.com/me/myopenedxtheme.git env/build/openedx/themes/

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
-----------------------------------------

Would you like to include custom xblocks, or extra requirements to your Open edX platform? Additional requirements can be added to the ``env/build/openedx/requirements/private.txt`` file. For instance, to include the `polling xblock from Opencraft <https://github.com/open-craft/xblock-poll/>`_::

    echo "git+https://github.com/open-craft/xblock-poll.git" >> env/build/openedx/requirements/private.txt

Then, the ``openedx`` docker image must be rebuilt::

    tutor images build openedx

To install xblocks from a private repository that requires authentication, you must first clone the repository inside the ``openedx/requirements`` folder on the host::

    git clone git@github.com:me/myprivaterepo.git ./openedx/requirements/myprivaterepo

Then, declare your extra requirements with the ``-e`` flag in ``openedx/requirements/private.txt``::

    echo "-e ./myprivaterepo" >> env/build/openedx/requirements/private.txt

.. _edx_platform_fork:

Running a fork of ``edx-platform``
----------------------------------

You may want to run your own flavor of edx-platform instead of the `official version <https://github.com/edx/edx-platform/>`_. To do so, you will have to re-build the openedx image with the proper environment variables pointing to your repository and version::

    tutor images build openedx \
        --build-arg EDX_PLATFORM_REPOSITORY=https://mygitrepo/edx-platform.git \
        --build-arg EDX_PLATFORM_VERSION=my-tag-or-branch

Note that your release must be a fork of Hawthorn in order to work. Otherwise, you may have important compatibility issues with other services. In particular, **don't try to run Tutor with older versions of Open edX**.

Running a different ``openedx`` Docker image
--------------------------------------------

By default, Tutor runs the `regis/openedx <https://hub.docker.com/r/regis/openedx/>`_ docker image from Docker Hub. If you have an account on `hub.docker.com <https://hub.docker.com>`_ or you have a private image registry, you can build your image and push it to your registry::

    tutor images build openedx --namespace=myusername --version=mytag
    tutor images push openedx --namespace=myusername --version=mytag

Then add the following value to your ``config.yml``::

    OPENEDX_DOCKER_IMAGE: myusername/openedx:mytag

This value will then be used by Tutor when generating your environment. For instance, this is how you would use your image in a local deployment::

    tutor local env
    tutor local quickstart
