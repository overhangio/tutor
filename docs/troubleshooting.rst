.. _troubleshooting:

Troubleshooting
===============

What should you do if you have a problem?

.. warning::
    **Do not** create a GitHub issue!

1. Read the error logs that appear in the console. When running a single server platform as daemon, you can view the logs with the ``tutor local logs`` command. (see :ref:`logging` below)
2. Check if your problem already has a solution right here in the :ref:`troubleshooting` section.
3. Search for your problem in the `open and closed GitHub issues <https://github.com/overhangio/tutor/issues?utf8=%E2%9C%93&q=is%3Aissue>`_.
4. Search for your problem in the (now legacy) `Tutor community forums <https://discuss.overhang.io>`__.
5. Search for your problem in the `Open edX community forum <https://discuss.openedx.org/>`__.
6. If despite all your efforts, you can't solve the problem by yourself, you should discuss it in the `Open edX community forum <https://discuss.openedx.org>`__. Please give as many details about your problem as possible! As a rule of thumb, **people will not dedicate more time to solving your problem than you took to write your question**. You should tag your topic with "tutor" or the corresponding Tutor plugin name ("tutor-discovery", etc.) in order to notify the maintainers.
7. If you are *absolutely* positive that you are facing a technical issue with Tutor, and not with Open edX, not with your server, not your custom configuration, then, and only then, should you open an issue on `GitHub <https://github.com/overhangio/tutor/issues/>`__. You *must* follow the instructions from the issue template!!! If you do not follow this procedure, your GitHub issues will be mercilessly closed 🤯.

Do you need professional assistance with your Open edX platform? `Edly <https://edly.io>`__ provides online support as part of its `Open edX installation service <https://edly.io/services/open-edx-installation/>`__.

.. _logging:

Logging
-------

.. note::
    Logs are of paramount importance for debugging Tutor. When asking for help on the `Open edX forum <https://discuss.openedx.org>`__, **always include the unedited logs of your app**. Logs are obtained with::

         tutor local logs --tail=100 -f

To view the logs from all containers use the ``tutor local logs`` command, which was modeled on the standard `docker-compose logs <https://docs.docker.com/compose/reference/logs/>`_ command::

    tutor local logs --follow

To view the logs from just one container, for instance, the webserver::

    tutor local logs --follow caddy

The last commands produce the logs since the creation of the containers, which may be a lot. Similar to a ``tail -f``, past logs can be removed with::

    tutor local logs --tail=0 --follow

User who are more comfortable with a graphical user interface for viewing logs are encouraged to try out :ref:`Portainer <portainer>`.

.. _webserver:

"Cannot start service caddy: driver failed programming external connectivity"
-----------------------------------------------------------------------------

The containerized Caddy needs to listen to ports 80 and 443 on the host. If there is already a webserver, such as Apache, Caddy, or Nginx, running on the host, the caddy container will not be able to start. To solve this issue, check the section on :ref:`how to setup a web proxy <web_proxy>`.

"Couldn't connect to docker daemon"
-----------------------------------

This is not an error with Tutor, but with your Docker installation. This is frequently caused by a permission issue. Before running Tutor, you should be able to run::

    docker run --rm hello-world

If the above command does not work, you should fix your Docker installation. Some people will suggest running Docker as root, or with ``sudo``; **do not do this**. Instead, what you should probably do is add your user to the "docker" group. For more information, check out the `official Docker installation instructions <https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user>`__.

.. _migrations_killed:

"Running migrations... Killed!" / "Command failed with status 137: docker-compose"
----------------------------------------------------------------------------------

Open edX requires at least 4 GB RAM, in particular, to run the SQL migrations. If the ``tutor local launch`` command dies after displaying "Running migrations", you most probably need to buy more memory or add swap to your machine.

On macOS, by default, Docker allocates at most 2 GB of RAM to containers. ``launch`` tries to check the current allocation and outputs a warning if it can't find a value of at least 4 GB. Follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`__ to allocate at least 4-5 GB to the Docker daemon.

If migrations were killed halfway, there is a good chance that the MySQL database is in a state that is hard to recover from. The easiest way to recover is to delete all the MySQL data and restart the launch process. After more memory has been allocated to the Docker daemon, run::

    tutor local stop
    sudo rm -rf "$(tutor config printroot)/data/mysql"
    tutor local launch

.. warning::
    THIS WILL ERASE ALL YOUR DATA! Do not run this on a production instance. This solution is only viable for new Open edX installations.

"Can't connect to MySQL server on 'mysql:3306' (111)"
-----------------------------------------------------

The most common reason this happens is that two different instances of Tutor are running simultaneously, causing a port conflict between MySQL containers. Tutor will try to prevent this situation from happening (for example, it will stop ``local`` containers when running ``tutor dev`` commands, and vice versa), but it cannot prevent all edge cases. So, as a first step, stop all possible Tutor platform variants::

    tutor dev stop
    tutor local stop
    tutor k8s stop

And then run the command(s) again, ensuring the correct Tutor variant is consistently used (``tutor dev``, ``tutor local``, or ``tutor k8s``).

If that does not work, then check if there are any other Docker containers running that may be using port 3306::

    docker ps -a

For example, if you have ever used :ref:`Tutor Main <main>`, check whether there are still ``tutor_main_`` containers running. Conversely, if trying to run Tutor Main now, check whether there are non-Main ``tutor_`` containers running. If so, switch to that other version of Tutor, run ``tutor (dev|local|k8s) stop``, and then switch back to the preferred version of Tutor.

Alternatively, if there are any other non-Tutor containers using port 3306, then stop and remove them::

    docker stop <container_name>
    docker rm <container_name>

Finally, if no container or other programs are making use of port 3306, check the logs of the MySQL container itself::

    tutor (dev|local|k8s) logs mysql

Check whether the MySQL container is crashing upon startup, and if so, what is causing it to crash.


Help! The Docker containers are eating all my RAM/CPU/CHEESE
------------------------------------------------------------

Containers that are consuming most resources are identified by running::

    docker stats

In idle mode, the "mysql" container should use ~200MB memory; ~200-300MB for the the "lms" and "cms" containers.

On some operating systems, such as RedHat, Arch Linux or Fedora, a very high limit of the number of open files (``nofile``) per container may cause the "mysql", "lms" and "cms" containers to use a lot of memory: up to 8-16GB. To check whether a platforms is impacted, run::

    cat /proc/$(pgrep dockerd)/limits | grep "Max open files"

If the output is 1073741816 or higher, then it is likely that the OS is affected by `this MySQL issue <https://github.com/docker-library/mysql/issues/579>`__. To learn more about the root cause, read `this containerd issue comment <https://github.com/containerd/containerd/pull/7566#issuecomment-1285417325>`__. Basically, the OS is hard-coding a very high limit for the allowed number of open files, and this is causing some containers to fail. To resolve the problem, configure the Docker daemon to enforce a lower value, as described `here <https://github.com/docker-library/mysql/issues/579#issuecomment-1432576518>`__. Edit ``/etc/docker/daemon.json`` and add the following contents::

    {
        "default-ulimits": {
            "nofile": {
                "Name": "nofile",
                "Hard": 1048576,
                "Soft": 1048576
            }
        }
    }

Check the configuration is valid with::

    dockerd --validate

Then restart the Docker service::

    sudo systemctl restart docker.service

Launch the Open edX platform again with ``tutor local launch``. We should observe normal memory usage.

"Build failed running pavelib.servers.lms: Subprocess return code: 1"
-----------------------------------------------------------------------

::

    python manage.py lms print_setting STATIC_ROOT 2>/dev/null
    ...
    Build failed running pavelib.servers.lms: Subprocess return code: 1`"

This might occur when running a ``paver`` command. ``/dev/null`` eats the actual error, so we have to run the command manually to figure out the actual error. Run ``tutor dev shell lms`` (or ``tutor dev shell cms``) to open a bash session and then::

    python manage.py lms print_setting STATIC_ROOT

The error produced should help better understand what is happening.

The chosen default language does not display properly
-----------------------------------------------------

By default, Open edX comes with a `limited set <https://github.com/openedx/openedx-translations/tree/main/translations/edx-platform/conf/locale>` of translation/localization files.

Refer to the :ref:`i18n` section for more information about using your own translations.

When I make changes to a course in the CMS, they are not taken into account by the LMS
--------------------------------------------------------------------------------------

This issue should only happen in development mode. Long story short, it is solved by creating a Waffle switch with the following command::

    tutor dev run lms ./manage.py lms waffle_switch block_structure.invalidate_cache_on_publish on --create

To learn more, check out `this GitHub issue <https://github.com/overhangio/tutor/issues/302>`__.

.. _high_resource_consumption:

High resource consumption by Docker on ``tutor images build``
-------------------------------------------------------------

Some Docker images include many independent layers which are built in parallel by BuildKit. As a consequence, building these images will use up a lot of resources, sometimes even crashing the Docker daemon. To bypass this issue, we should explicitly limit the `maximum parallelism of BuildKit <https://docs.docker.com/build/buildkit/configure/#max-parallelism>`__. Create a ``buildkit.toml`` configuration file with the following contents::

    [worker.oci]
    max-parallelism = 2

This configuration file limits the number of layers built concurrently to 2, but we should select a value that is appropriate for our machine.

Then, create a builder named "max2cpu" that uses this configuration, and start using it right away::

    # don't forget to specify the correct path to the buildkit.toml configuration file
    docker buildx create --use --name=max2cpu --driver=docker-container --config=/path/to/buildkit.toml

Now build again::

    tutor images build all

All build commands should now make use of the newly configured builder. To later revert to the default builder, run ``docker buildx use default``.

.. note::
	Setting a too low value for maximum parallelism will result in longer build times.

fatal: the remote end hung up unexpectedly / fatal: early EOF / fatal: index-pack failed when running ``tutor images build ...``
--------------------------------------------------------------------------------------------------------------------------------

This issue can occur due to problems with the network connection while cloning edx-platform which is a fairly large repository.

First, try to run the same command once again to see if it works, as the network connection can sometimes drop during the build process.

If that does not work, follow the tutorial above for :ref:`High resource consumption <high_resource_consumption>` to limit the number of concurrent build steps so that the network connection is not being shared between multiple layers at once.

Can't override styles using Indigo Theme for MFEs
-------------------------------------------------

The solution can be found in `tutor-indigo <https://github.com/overhangio/tutor-indigo?tab=readme-ov-file#cant-override-styles-using-indigo-theme-for-mfes>`__ documentation.


NPM Dependency Conflict When overriding ``@edx/frontend-component-header`` or ``@edx/frontend-component-footer``
----------------------------------------------------------------------------------------------------------------

The detailed steps are mentioned in `tutor-mfe <https://github.com/overhangio/tutor-mfe?tab=readme-ov-file#npm-dependency-conflict-when-overriding-edxfrontend-component-header-or-edxfrontend-component-footer>`__ documentation.

"Plugin 'mysql_native_password' is not loaded"
----------------------------------------------

This issue can occur when Tutor is upgraded from v15 (Olive) or earlier to v18 (Redwood) or later because the users created in Tutor v15 and earlier utilize the mysql_native_password authentication plugin by default. This plugin has been deprecated as of MySQL v8.4.0 which is the default MySQL server used in Tutor v18 and onwards.

The handy :ref:`update-mysql-authentication-plugin <update_mysql_authentication_plugin>` do command in tutor can be used to fix this issue. To update the database users for a vanilla tutor installation::

    tutor local do update-mysql-authentication-plugin $(tutor config printvalue OPENEDX_MYSQL_USERNAME)
    tutor local do update-mysql-authentication-plugin $(tutor config printvalue MYSQL_ROOT_USERNAME)
