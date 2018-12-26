.. _customise:

Customising the ``openedx`` docker image
========================================

The LMS and the CMS all run from the ``openedx`` docker image. The base image is downloaded from `Docker Hub <https://hub.docker.com/r/regis/openedx/>`_ when we run ``make update`` (or ``make all``). But you can also customise and build the image yourself. All image-building commands must be run inside the ``build`` folder::

    cd build

Build the base image with::

    make build-openedx

The following sections describe how to modify various aspects of the docker image. After you have built your own image, you can run it as usual::

    make run

Custom themes
-------------

Comprehensive theming is enabled by default, but only the default theme is compiled. To compile your own theme, add it to the ``build/openedx/themes/`` folder::

    git clone https://github.com/me/myopenedxtheme.git build/openedx/themes/

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

    make build-openedx

Make sure the assets can be served by the web server::

    make assets

Finally, follow the `Open edX documentation to enable your themes <https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/changing_appearance/theming/enable_themes.html#apply-a-theme-to-a-site>`_.

Extra xblocks and requirements
------------------------------

Would you like to include custom xblocks, or extra requirements to your Open edX platform? Additional requirements can be added to the ``openedx/requirements/private.txt`` file. For instance, to include the `polling xblock from Opencraft <https://github.com/open-craft/xblock-poll/>`_::

    echo "git+https://github.com/open-craft/xblock-poll.git" >> openedx/requirements/private.txt

Then, the ``openedx`` docker image must be rebuilt::

    make build-openedx

To install xblocks from a private repository that requires authentication, you must first clone the repository inside the ``openedx/requirements`` folder on the host::

    git clone git@github.com:me/myprivaterepo.git ./openedx/requirements/myprivaterepo

Then, declare your extra requirements with the ``-e`` flag in ``openedx/requirements/private.txt``::

    echo "-e ./myprivaterepo" >> openedx/requirements/private.txt

Forked version of edx-platform
------------------------------

You may want to run your own flavor of edx-platform instead of the `official version <https://github.com/edx/edx-platform/>`_. To do so, you will have to re-build the openedx image with the proper environment variables pointing to your repository and version::

    export EDX_PLATFORM_REPOSITORY=https://mygitrepo/edx-platform.git EDX_PLATFORM_VERSION=my-tag-or-branch
    make build-openedx

You can then restart the services which will now be running your forked version of edx-platform::

    make restart-openedx

Note that your release must be a fork of Hawthorn in order to work. Otherwise, you may have important compatibility issues with other services. In particular, **don't try to run Tutor with older versions of Open edX**.

Running a different ``openedx`` Docker image
--------------------------------------------

By default, Tutor runs the `regis/openedx <https://hub.docker.com/r/regis/openedx/>`_ docker image from Docker Hub. If you have an account on `hub.docker.com <https://hub.docker.com>`_ or you have a private image registry, you can build your image and push it to your registry. Then add the following content to the ``deploy/local/.env`` file::

    OPENEDX_DOCKER_IMAGE=myusername/myimage:mytag

Your own image will be used next time you run ``make run``.

Note that the ``make build`` and ``make push`` commands (from the ``build/`` folder) will no longer work as you expect and that you are responsible for building and pushing the image yourself.
