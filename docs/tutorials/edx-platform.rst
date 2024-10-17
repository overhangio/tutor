.. _edx_platform:

Working on edx-platform as a developer
======================================

Tutor supports running in development with ``tutor dev`` commands. Developers frequently need to work on a fork of some repository. The question then becomes: how to make their changes available within the "openedx" Docker container? 

For instance, when troubleshooting an issue in `edx-platform <https://github.com/openedx/edx-platform>`__, we would like to make some changes to a local fork of that repository, and then apply these changes immediately in the "lms" and the "cms" containers (but also "lms-worker", "cms-worker", etc.)

Similarly, when developing a custom XBlock, we would like to hot-reload any change we make to the XBlock source code within the containers.

Tutor provides a simple solution to these questions. In both cases, the solution takes the form of a ``tutor mounts add ...`` command.

Working on the "edx-platform" repository
----------------------------------------

Download the code from the upstream repository::

    cd /my/workspace/edx-plaform
    git clone https://github.com/openedx/edx-platform .

Check out the right version of the upstream repository. If you are working on the `current "zebulon" release <https://docs.openedx.org/en/latest/community/release_notes/index.html>`__ of Open edX, then you should checkout the corresponding branch::

    # "zebulon" is an example. You should put the actual release name here.
    # I.e: aspen, birch, cypress, etc.
    git checkout open-release/zebulon.master

On the other hand, if you are working on the Tutor :ref:`"nightly" <nightly>` branch then you should checkout the master branch::

    git checkout master

Then, mount the edx-platform repository with Tutor::

    tutor mounts add /my/workspace/edx-plaform

This command does a few "magical" things 🧙 behind the scenes:

1. Mount the edx-platform repository in the image at build-time. This means that when you run ``tutor images build openedx``, your custom repository will be used instead of the upstream. In particular, any change you've made to the installed requirements, static assets, etc. will be taken into account.
2. Mount the edx-platform repository at run time. Thus, when you run ``tutor dev start``, any change you make to the edx-platform repository will be hot-reloaded.

You can get a glimpse of how these auto-mounts work by running ``tutor mounts list``. It should output something similar to the following::

    $ tutor mounts list
    - name: /home/data/regis/projets/overhang/repos/edx/edx-platform
    build_mounts:
    - image: openedx
        context: edx-platform
    - image: openedx-dev
        context: edx-platform
    compose_mounts:
    - service: lms
        container_path: /openedx/edx-platform
    - service: cms
        container_path: /openedx/edx-platform
    - service: lms-worker
        container_path: /openedx/edx-platform
    - service: cms-worker
        container_path: /openedx/edx-platform
    - service: lms-job
        container_path: /openedx/edx-platform
    - service: cms-job
        container_path: /openedx/edx-platform

Working on edx-platform Python dependencies
-------------------------------------------

Quite often, developers don't want to work on edx-platform directly, but on a dependency of edx-platform. For instance: an XBlock. This works the same way as above. Let's take the example of the `"edx-ora2" <https://github.com/openedx/edx-ora2>`__ package, for open response assessments. First, clone the Python package::

    cd /my/workspace/edx-ora2
    git clone https://github.com/openedx/edx-ora2 .

Then, check out the right version of the package. This is the version that is indicated in the `edx-platform/requirements/edx/base.txt <https://github.com/openedx/edx-platform/blob/release/sumac/requirements/edx/base.txt>`__. Be careful that the version that is currently in use in your version of edx-platform is **not necessarily the head of the master branch**::

    git checkout <my-version-tag-or-branch>

Then, mount this repository::

    tutor mounts add /my/workspace/edx-ora2

Verify that your repository is properly bind-mounted by running ``tutor mounts list``::

    $ tutor mounts list
    - name: /my/workspace/edx-ora2
    build_mounts:
    - image: openedx
        context: mnt-edx-ora2
    - image: openedx-dev
        context: mnt-edx-ora2
    compose_mounts:
    - service: lms
        container_path: /mnt/edx-ora2
    - service: cms
        container_path: /mnt/edx-ora2
    - service: lms-worker
        container_path: /mnt/edx-ora2
    - service: cms-worker
        container_path: /mnt/edx-ora2
    - service: lms-job
        container_path: /mnt/edx-ora2
    - service: cms-job
        container_path: /mnt/edx-ora2

(If the ``_mounts`` entries are empty, it didn't work automatically - see below.)

You should then re-build the "openedx" Docker image to pick up your changes::

    tutor images build openedx-dev

Then, whenever you run ``tutor dev start``, the "lms" and "cms" containers should automatically hot-reload your changes.

To push your changes in production, you should do the same with ``tutor local`` and the "openedx" image::

    tutor images build openedx
    tutor local start -d

What if my edx-platform package is not automatically bind-mounted?
------------------------------------------------------------------

It is quite possible that your package is not automatically recognized and bind-mounted by Tutor. Out of the box, Tutor defines a set of regular expressions: if your package name matches this regular expression, it will be automatically bind-mounted. But if it does not, you have to tell Tutor about it.

To do so, you will need to create a :ref:`Tutor plugin <plugin_development_tutorial>` that implements the :py:data:`tutor.hooks.Filters.MOUNTED_DIRECTORIES` filter::

    from tutor import hooks
    hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "my-package"))

After you implement and enable that plugin, ``tutor mounts list`` should display your directory among the bind-mounted directories.

Debugging with breakpoints
--------------------------

To debug a local edx-platform repository, first, start development in detached mode (with ``-d``), add a `python breakpoint <https://docs.python.org/3/library/functions.html#breakpoint>`__ with ``breakpoint()`` anywhere in the code. Then, attach to the applicable service's container by running ``start`` (without ``-d``) followed by the service's name::

  # Start in detached mode:
  tutor dev start -d

  # Debugging LMS:
  tutor dev start lms

  # Or, debugging CMS:
  tutor dev start cms

Running edx-platform unit tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's possible to run the full set of unit tests that ship with `edx-platform <https://github.com/openedx/edx-platform/>`__. To do so, run a shell in the LMS development container::

    tutor dev run lms bash

Then, run unit tests with ``pytest`` commands::

    # Run tests on common apps
    unset DJANGO_SETTINGS_MODULE
    unset SERVICE_VARIANT
    pytest common
    pytest openedx
    pytest xmodule

    # Run tests on LMS
    export DJANGO_SETTINGS_MODULE=lms.envs.tutor.test
    pytest lms

    # Run tests on CMS
    export DJANGO_SETTINGS_MODULE=cms.envs.tutor.test
    pytest cms

.. note::
    Getting all edx-platform unit tests to pass on Tutor is currently a work-in-progress. Some unit tests are still failing. If you manage to fix some of these, please report your findings in the `Open edX forum <https://discuss.openedx.org/tag/tutor>`__.

Do I have to re-build the "openedx" Docker image after every change?
--------------------------------------------------------------------

No, you don't. Re-building the "openedx" Docker image may take a while, and you don't want to run this command every time you make a change to your local repositories. Because your host directory is bind-mounted in the containers at runtime, your changes will be automatically applied to the container. If you run ``tutor dev`` commands, then your changes will be automatically picked up.

If you run ``tutor local`` commands (for instance: when debugging a production instance) then your changes will *not* be automatically picked up. In such a case you should manually restart the containers::

    tutor local restart lms cms lms-worker cms-worker

Re-building the "openedx" image should only be necessary when you want to push your changes to a Docker registry, then pull them on a remote server.
