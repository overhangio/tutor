.. _plugin_development_tutorial:

=======================
Creating a Tutor plugin
=======================

Tutor plugins are the officially recommended way of customizing the behaviour of Tutor. If Tutor does not do things the way you want, then your first reaction should *not* be to fork Tutor, but instead to figure out whether you can create a plugin that will allow you to achieve what you want.

You may be thinking that creating a plugin might be overkill for your use case. It's almost certainly not! The stable plugin API guarantees that your changes will keep working even after you upgrade from one major release to the next, with little to no extra work. Also, it allows you to distribute your changes to other users.

A plugin can be created either as a simple, single Python module (a ``*.py`` file) or as a full-blown Python package. Single Python modules are easier to write, while Python packages can be distributed more easily with ``pip install ...``. We'll start by writing our plugin as a single Python module.

Plugins work by making extensive use of the Tutor hooks API. The list of available hooks is available from the :ref:`hooks catalog <hooks_catalog>`. Developers who want to understand how hooks work should check the :ref:`hooks API <hooks_api>`.

Writing a plugin as a single Python module
==========================================

Getting started
---------------

In the following, we'll create a new plugin called "myplugin". We start by creating the plugins root folder::

    $ mkdir -p "$(tutor plugins printroot)"

Then, create an empty "myplugin.py" file in this folder::

    $ touch "$(tutor plugins printroot)/myplugin.py"

We can verify that the plugin is correctly detected by running::

    $ tutor plugins list
    ...
    myplugin    (disabled)    /home/yourusername/.local/share/tutor-plugins/myplugin.py
    ...

Our plugin is disabled, for now. To enable it, we run::

    $ tutor plugins enable myplugin
    Plugin myplugin enabled
    Configuration saved to /home/yourusername/.local/share/tutor/config.yml
    Environment generated in /home/yourusername/.local/share/tutor/env

At this point your environment was updated, but there would not be any change there... because the plugin does not do anything. So let's get started and make some changes.

Modifying existing files with patches
-------------------------------------

We'll start by modifying some of our Open edX settings files. It's a frequent requirement to modify the ``FEATURES`` setting from the LMS or the CMS in edx-platform. In the legacy native installation, this was done by modifying the ``lms.env.yml`` and ``cms.env.yml`` files. Here we'll modify the Python setting files that define the edx-platform configuration. To achieve that we'll make use of two concepts from the Tutor API: :ref:`patches` and :ref:`filters`.

If you have not already read :ref:`how_does_tutor_work` now would be a good time ☺️ Tutor uses templates to generate various files, such as settings, Dockerfiles, etc. These templates include ``{{ patch("patch-name") }}`` statements that allow plugins to insert arbitrary content in there. These patches are located at strategic locations. See :ref:`patches` for more information.

Let's say that we would like to limit access to our brand new Open edX platform. It is not ready for prime-time yet, so we want to prevent users from registering new accounts. There is a feature flag for that in the LMS: `FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] <https://edx.readthedocs.io/projects/edx-platform-technical/en/latest/featuretoggles.html#featuretoggle-FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION']>`__. By default this flag is set to a true value, enabling anyone to create an account. In the following we'll set it to false.

Add the following content to the ``myplugin.py`` file that you created earlier::

    from tutor import hooks

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False"
        )
    )

Let's go over these changes one by one::

    from tutor import hooks

This imports the ``hooks`` module from Tutor, which grants us access to ``hooks.Actions`` and ``hooks.Filters`` (among other things).

::

    hooks.Filters.ENV_PATCHES.add_item(
        (
            <name>,
            <content>
        )
    )

This means "add ``<content>`` to the ``{{ patch("<name>") }}`` statement, thanks to the :py:data:`tutor.hooks.Filters.ENV_PATCHES` filter". In our case, we want to modify the LMS settings, both in production and development. The right patch for that is :patch:`openedx-lms-common-settings`. We add one item, which is a single Python-formatted line of code::

    "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False"

.. note:: Notice how "False" starts with a capital "F"? That's how booleans are created in Python.

Now, re-render your environment with::

    $ tutor config save

You can check that the feature was added to your environment::

    $ grep -r ALLOW_PUBLIC_ACCOUNT_CREATION "$(tutor config printroot)/env"
    /home/yourusername/.local/share/tutor/env/apps/openedx/settings/lms/production.py:FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False
    /home/yourusername/.local/share/tutor/env/apps/openedx/settings/lms/development.py:FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False

Your new settings will be taken into account by restarting your platform::

    $ tutor local restart

Congratulations! You've created your first working plugin. As you can guess, you can add changes to other files by adding other similar patch statements to your plugin.

Modifying configuration
-----------------------

In the previous section you've learned how to add custom content to the Tutor templates. Now we'll see how to modify the Tutor configuration. Configuration settings can be specified in three ways:

1. "unique" settings that need to be generated or user-specified, and then preserved in config.yml: such settings do not have reasonable defaults for all users. Examples of such settings include passwords and secret keys, which should be different for every user.
2. "default" settings have static fallback values. They are only stored in config.yml when they are modified by users. Most settings belong in this category.
3. "override" settings modify configuration from Tutor core or from other plugins. These will be removed and restored to their default values when the plugin is disabled.

It is very strongly recommended to prefix unique and default settings with the plugin name, in all-caps, such that different plugins with the same configuration do not conflict with one another.

As an example, we'll make it possible to configure public account creation on the LMS via a Tutor setting. In the previous section we achieved that by creating a patch. Let's modify this patch::

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = {% if MYPLUGIN_PLATFORM_IS_PUBLIC %}True{% else %}False{% endif %}",
        )
    )

This new patch makes use of the ``MYPLUGIN_PLATFORM_IS_PUBLIC`` configuration setting, which we need to create. Since this setting is specific to our plugin and should be stored in config.yml only when it's modified, we create it as a "default" setting. We do that with the :py:data:`tutor.hooks.Filters.CONFIG_DEFAULTS` filter::

    hooks.Filters.CONFIG_DEFAULTS.add_item(
        ("MYPLUGIN_PLATFORM_IS_PUBLIC", False)
    )

You can check that the new configuration setting was properly defined::

    $ tutor config printvalue MYPLUGIN_PLATFORM_IS_PUBLIC
    False

Now you can quickly toggle the public account creation feature by modifying the new setting::

    $ tutor config save --set MYPLUGIN_PLATFORM_IS_PUBLIC=True
    $ tutor local restart


Adding new templates
--------------------

If you are adding an extra application to your Open edX platform, there is a good chance that you will create a new Docker image with a custom Dockerfile. This new application will have its own settings and build assets, for instance. This means that you need to add new templates to the Tutor environment. To do that, we will create a new subfolder in our plugins folder::

    $ mkdir -p "$(tutor plugins printroot)/templates/myplugin"

Then we tell Tutor about this new template root thanks to the :py:data:`tutor.hooks.Filters.ENV_TEMPLATE_ROOTS` filter::

    import os

    template_folder = os.path.join(os.path.dirname(__file__), "templates")
    hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(template_folder)

We create a "build" subfolder which will contain all assets to build our "myservice" image::

    $ mkdir -p "$(tutor plugins printroot)/templates/myplugin/build/myservice"

Create the following Dockerfile in ``$(tutor plugins printroot)/templates/myplugin/build/myservice/Dockerfile``::

    FROM docker.io/debian:bullseye-slim
    CMD echo "what an awesome plugin!"

Tell Tutor that the "build" folder should be recursively rendered to ``env/plugins/myplugin/build`` with the :py:data:`tutor.hooks.Filters.ENV_TEMPLATE_TARGETS`::

    hooks.Filters.ENV_TEMPLATE_TARGETS.add_item(
        ("myplugin/build", "plugins")
    )

At this point you can verify that the Dockerfile template was properly rendered::

    $ cat "$(tutor config printroot)/env/plugins/myplugin/build/myservice/Dockerfile"
    FROM docker.io/debian:bullseye-slim
    CMD echo "what an awesome plugin!"

We would like to build this image by running ``tutor images build myservice``. For that, we use the :py:data:`tutor.hooks.Filters.IMAGES_BUILD` filter::

    hooks.Filters.IMAGES_BUILD.add_item(
        (
            "myservice", # same name that will be passed to the `build` command
            ("plugins", "myplugin", "build", "myservice"), # path to the Dockerfile folder
            "myservice:latest", # Docker image tag
            (), # custom build arguments that will be passed to the `docker build` command
        )
    )

You can now build your image::

    $ tutor images build myservice
    Building image myservice:latest
    docker build -t myservice:latest /home/yourusername/.local/share/tutor/env/plugins/myplugin/build/myservice
    ...
    Successfully tagged myservice:latest

Similarly, to push/pull your image to/from a Docker registry, implement the :py:data:`tutor.hooks.Filters.IMAGES_PUSH` and :py:data:`tutor.hooks.Filters.IMAGES_PULL` filters::

    hooks.Filters.IMAGES_PUSH.add_item(("myservice", "myservice:latest"))
    hooks.Filters.IMAGES_PULL.add_item(("myservice", "myservice:latest"))

You can now run::

    $ tutor images push myservice
    $ tutor images pull myservice

The "myservice" container can be automatically run in local installations by implementing the :patch:`local-docker-compose-services` patch::

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-services",
            """
    myservice:
        image: myservice:latest
    """
        )
    )

You can now run the "myservice" container which will execute the ``CMD`` statement we wrote in the Dockerfile::

    $ tutor config save && tutor local run myservice
    ...
    Creating tutor_local_myservice_run ... done
    what an awesome plugin!

Declaring initialisation tasks
------------------------------

Services often need to run specific tasks before they can be started. For instance, the LMS and the CMS need to apply database migrations. These commands are written in shell scripts that are executed whenever we run ``launch``. We call these scripts "init tasks". To add a new local initialisation task, we must first add the corresponding service to the ``docker-compose-jobs.yml`` file by implementing the :patch:`local-docker-compose-jobs-services` patch::

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-jobs-services",
            """
    myservice-job:
        image: myservice:latest
    """,
        )
    )

The patch above defined the "myservice-job" container which will run our initialisation task. Make sure that it is applied by updating your environment::

    $ tutor config save

Next, we create an initialisation task by adding an item to the :py:data:`tutor.hooks.Filters.CLI_DO_INIT_TASKS` filter::


    hooks.Filters.CLI_DO_INIT_TASKS.add_item(
        (
            "myservice",
            """
    echo "++++++ initialising my plugin..."
    echo "++++++ done!"
    """
        )
    )

Run this initialisation task with::

    $ tutor local do init --limit=myplugin
    ...
    Running init task: myplugin/tasks/init.sh
    ...
    Creating tutor_local_myservice-job_run ... done
    ++++++ initialising my plugin...
    ++++++ done!
    All services initialised.

Tailoring services for development
----------------------------------

When you add services via :patch:`local-docker-compose-services`, those services will be available both in local production mode (``tutor local start``) and local development mode (``tutor dev start``). Sometimes, you may wish to further customize a service in ways that would not be suitable for production, but could be helpful for developers. To add in such customizations, implement the :patch:`local-docker-compose-dev-services` patch. For example, we can enable breakpoint debugging on the "myservice" development container by enabling the ``stdin_open`` and ``tty`` options::

    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-dev-services",
            """
    myservice:
        stdin_open: true
        tty: true
    """,
        )
    )

Final result
------------

Eventually, our plugin is composed of the following files, all stored within the folder indicated by ``tutor plugins printroot`` (on Linux: ``~/.local/share/tutor-plugins``).

``myplugin.py``
~~~~~~~~~~~~~~~

::

    import os
    from tutor import hooks

    # Define extra folder to look for templates and render the content of the "build" folder
    template_folder = os.path.join(os.path.dirname(__file__), "templates")
    hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(template_folder)
    hooks.Filters.ENV_TEMPLATE_TARGETS.add_item(
        ("myplugin/build", "plugins")
    )

    # Define patches
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = False"
        )
    )
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "openedx-lms-common-settings",
            "FEATURES['ALLOW_PUBLIC_ACCOUNT_CREATION'] = {% if MYPLUGIN_PLATFORM_IS_PUBLIC %}True{% else %}False{% endif %}",
        )
    )
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-services",
            """
    myservice:
        image: myservice:latest
    """
        )
    )
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-jobs-services",
            """
    myservice-job:
        image: myservice:latest
    """,
        )
    )
    hooks.Filters.ENV_PATCHES.add_item(
        (
            "local-docker-compose-dev-services",
            """
    myservice:
        stdin_open: true
        tty: true
    """,
        )
    )

    # Modify configuration
    hooks.Filters.CONFIG_DEFAULTS.add_item(
        ("MYPLUGIN_PLATFORM_IS_PUBLIC", False)
    )

    # Define tasks
    hooks.Filters.IMAGES_BUILD.add_item(
        (
            "myservice",
            ("plugins", "myplugin", "build", "myservice"),
            "myservice:latest",
            (),
        )
    )
    hooks.Filters.IMAGES_PUSH.add_item(("myservice", "myservice:latest"))
    hooks.Filters.IMAGES_PULL.add_item(("myservice", "myservice:latest"))
    hooks.Filters.CLI_DO_INIT_TASKS.add_item(
        (
            "myservice",
            """
    echo "++++++ initialising my plugin..."
    echo "++++++ done!"
    """
        )
    )

``templates/myplugin/build/myservice/Dockerfile``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    FROM docker.io/debian:bullseye-slim
    CMD echo "what an awesome plugin!"

``templates/myplugin/tasks/init.sh``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    echo "initialising my plugin..."
    echo "done!"

Distributing a plugin as a Python package
=========================================

Storing plugins as simple Python modules has the merit of simplicity, but it makes it more difficult to distribute them, either to other users or to remote servers. When your plugin grows more complex, it is recommended to migrate it to a Python package. You should create a package using the `plugin cookiecutter <https://github.com/overhangio/cookiecutter-tutor-plugin>`__. Packages are automatically detected as plugins thanks to the "tutor.plugin.v1" `entry point <https://setuptools.pypa.io/en/latest/userguide/entry_point.html#advertising-behavior>`__. The modules indicated by this entry point will be automatically imported when the plugins are enabled. See the cookiecutter project `README <https://github.com/overhangio/cookiecutter-tutor-plugin/blob/master/README.rst>`__ for more information.
