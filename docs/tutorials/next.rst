.. _next:

Running Open edX on the master branch (Tutor "Next")
====================================================

Tutor was designed to make it easy for everyone to run the latest release of Open edX. But sometimes, you want to run the latest, bleeding-edge version of Open edX. This is what we call "running master", as opposed to running the release branch. Running the master branch in production is strongly **not** recommended unless you are an Open edX expert and you really know what you are doing. But Open edX developers frequently need to run the master branch locally to implement and test new features for the next Open edX release. Thus, Tutor makes it easy to run Open edX on the master branch: this is called "Tutor Next".

Installing Tutor Next
---------------------

Running Tutor Next requires more than setting a few configuration variables: because there are so many Open edX settings, version numbers, etc. which may change between the latest release and the current master branch, Tutor Next is actually maintained as a separate branch of the Tutor repository. To install Tutor Next, you should install Tutor from the "next" branch of the source repository. To do so, run::

    git clone --branch=next https://github.com/overhangio/tutor.git
    pip install -e "./tutor[full]"

As usual, it is strongly recommended to run the command above in a `Python virtual environment <https://docs.python.org/3/tutorial/venv.html>`__.

In addition to installing Tutor Next itself, this will install automatically the "Next" versions of all official Tutor plugins (which are enumerated in `plugins.txt <https://github.com/overhangio/tutor/tree/next/requirements/plugins.txt>`_). Alternatively, if you wish to hack on an official plugin or install a custom plugin, you can clone that plugin's repository and install it. For instance::

    git clone --branch=next https://github.com/myorganization/tutor-contrib-myplugin.git
    pip install -e ./tutor-contrib-myplugin

Once Tutor Next is installed, you can run the usual ``tutor`` commands::

    tutor dev launch
    tutor dev run lms bash
    # ... and so on

Upgrading to the latest version of Open edX
-------------------------------------------

To pull the latest upstream changes, you should first upgrade Tutor Next::

    cd ./tutor
    git pull

Then, you will have to generate a more recent version of the "Next" Docker images. Images for running Tutor Next are published daily to docker.io (see `here <https://hub.docker.com/r/overhangio/openedx/tags?page=1&ordering=last_updated&name=next>`__). You can fetch the latest images with::

    tutor images pull all

Alternatively, you may want to build the images yourself. As usual, this is done with::

        tutor images build all

However, these images include the application master branch at the point in time when the image was built. The Docker layer caching mechanism might cause the ``git clone`` step from the build to be skipped. In such cases, you will have to bypass the caching mechanism with::

    tutor images build --no-cache all

Running Tutor Next alongside the latest release
-----------------------------------------------

When running Tutor Next, you usually do not want to override your existing Tutor installation. That's why a Tutor Next installation has the following differences from a regular release installation:

- The default Tutor project root is different in Tutor Next. By default it is set to ``~/.local/share/tutor-next`` on Linux (instead of ``~/.local/share/tutor``). To modify this location check the :ref:`corresponding documentation <tutor_root>`.
- The plugins root is set to ``~/.local/share/tutor-next-plugins`` on Linux (instead of ``~/.local/share/tutor-plugins``). This location may be modified by setting the ``TUTOR_PLUGINS_ROOT`` environment variable.
- The default docker-compose project name is set to ``tutor_next_local`` (instead of ``tutor_local``). This value may be modified by manually setting the ``LOCAL_PROJECT_NAME``.

Making changes to Tutor Next
----------------------------

In general pull requests should be open on the "master" branch of Tutor: the "master" branch is automatically merged on the "next" branch at every commit, such that changes made to Tutor releases find their way to Tutor Next as soon as they are merged. However, sometimes you want to make changes to Tutor Next exclusively, and not to the Tutor releases. This might be the case for instance when upgrading the running version of a third-party service (for instance: Elasticsearch, MySQL), or when the master branch requires specific changes. In that case, you should follow the instructions from the :ref:`contributing` section of the docs, with the following differences:

- Open your pull request on top of the "next" branch instead of "master".
- Add a description of your changes by creating a changelog entry with `make changelog-entry`, as in the master branch.
