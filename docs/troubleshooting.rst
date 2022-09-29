.. _troubleshooting:

Troubleshooting
===============

What should you do if you have a problem?

.. warning::
    **Do not** create a Github issue!

1. Read the error logs that appear in the console. When running a single server platform as daemon, you can view the logs with the ``tutor local logs`` command. (see :ref:`logging` below)
2. Check if your problem already has a solution right here in the :ref:`troubleshooting` section.
3. Search for your problem in the `open and closed Github issues <https://github.com/overhangio/tutor/issues?utf8=%E2%9C%93&q=is%3Aissue>`_.
4. Search for your problem in the (now legacy) `Tutor community forums <https://discuss.overhang.io>`__.
5. Search for your problem in the `Open edX community forum <https://discuss.openedx.org/>`__.
6. If despite all your efforts, you can't solve the problem by yourself, you should discuss it in the `Open edX community forum <https://discuss.openedx.org>`__. Please give as many details about your problem as possible! As a rule of thumb, **people will not dedicate more time to solving your problem than you took to write your question**. You should tag your topic with "tutor" or the corresponding Tutor plugin name ("tutor-discovery", etc.) in order to notify the maintainers.
7. If you are *absolutely* positive that you are facing a technical issue with Tutor, and not with Open edX, not with your server, not your custom configuration, then, and only then, should you open an issue on `Github <https://github.com/overhangio/tutor/issues/>`__. You *must* follow the instructions from the issue template!!! If you do not follow this procedure, your Github issues will be mercilessly closed 🤯.

Do you need professional assistance with your tutor-managed Open edX platform? Overhang.IO offers online support as part of its `Long Term Support (LTS) offering <https://overhang.io/tutor/pricing>`__.

.. _logging:

Logging
-------

.. note::
    Logs are of paramount importance for debugging Tutor. When asking for help on the `Open edX forum <https://discuss.openedx.org>`__, **you should always include the unedited logs of your app**. You can get those with::

         tutor local logs --tail=100 -f

To view the logs from all containers use the ``tutor local logs`` command, which was modeled on the standard `docker-compose logs <https://docs.docker.com/compose/reference/logs/>`_ command::

    tutor local logs --follow

To view the logs from just one container, for instance, the webserver::

    tutor local logs --follow caddy

The last commands produce the logs since the creation of the containers, which can be a lot. Similar to a ``tail -f``, you can run::

    tutor local logs --tail=0 -f

If you'd rather use a graphical user interface for viewing logs, you are encouraged to try out :ref:`Portainer <portainer>`.

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

On macOS, by default, Docker allocates at most 2 GB of RAM to containers. ``launch`` tries to check your current allocation and outputs a warning if it can't find a value of at least 4 GB. You should follow `these instructions from the official Docker documentation <https://docs.docker.com/docker-for-mac/#advanced>`__ to allocate at least 4-5 GB to the Docker daemon.

If migrations were killed halfway, there is a good chance that the MySQL database is in a state that is hard to recover from. The easiest way to recover is simply to delete all the MySQL data and restart the launch process. After you have allocated more memory to the Docker daemon, run::

    tutor local stop
    sudo rm -rf "$(tutor config printroot)/data/mysql"
    tutor local launch

.. warning::
    THIS WILL ERASE ALL YOUR DATA! Do not run this on a production instance. This solution is only viable for new Open edX installations.

"Can't connect to MySQL server on 'mysql:3306' (111)"
-----------------------------------------------------

The most common reason this happens is that you are running two different instances of Tutor simultaneously, causing a port conflict between MySQL containers. Tutor will try to prevent you from doing that (for example, it will stop ``local`` containers if you start ``dev`` ones, and vice versa), but it cannot prevent all edge cases. So, as a first step, stop all possible Tutor platform variants::

    tutor dev stop
    tutor local stop
    tutor k8s stop
    
And then run your command(s) again, ensuring you're consistently using the correct Tutor variant (``tutor dev``, ``tutor local``, or ``tutor k8s``).

If that doesn't work, then check if you have any other Docker containers running that may using port 3306::

    docker ps -a
   
For example, if you have ever used `Tutor Nightly <https://docs.tutor.overhang.io/tutorials/nightly.html>`_, check whether you still have ``tutor_nightly_`` containers running. Conversely, if you're trying to run Tutor Nightly now, check whether you have non-Nightly ``tutor_`` containers running. If so, switch to that other version of Tutor, run ``tutor (dev|local|k8s) stop``, and then switch back to your preferred version of Tutor.

Alternatively, if there are any other non-Tutor containers using port 3306, then stop and remove them::

    docker stop <container_name>
    docker rm <container_name>

Finally, if you've ensured that containers or other programs are making use of port 3306, check the logs of the MySQL container itself::

    tutor (dev|local|k8s) logs mysql
  
Check whether the MySQL container is crashing upon startup, and if so, what is causing it to crash.


Help! The Docker containers are eating all my RAM/CPU/CHEESE
------------------------------------------------------------

You can identify which containers are consuming most resources by running::

    docker stats

"Build failed running pavelib.servers.lms: Subprocess return code: 1"
-----------------------------------------------------------------------

::

    python manage.py lms print_setting STATIC_ROOT 2>/dev/null
    ...
    Build failed running pavelib.servers.lms: Subprocess return code: 1`"

This might occur when you run a ``paver`` command. ``/dev/null`` eats the actual error, so you will have to run the command manually. Run ``tutor dev shell lms`` (or ``tutor dev shell cms``) to open a bash session and then::

    python manage.py lms print_setting STATIC_ROOT

The error produced should help you better understand what is happening.

The chosen default language does not display properly
-----------------------------------------------------

By default, Open edX comes with a `limited set <https://github.com/openedx/edx-platform/blob/master/conf/locale/config.yaml>` of translation/localization files. To complement these languages, we add locales from the `openedx-i18n project <https://github.com/openedx/openedx-i18n/blob/master/edx-platform/locale/config-extra.yaml>`_. But not all supported locales are downloaded. In some cases, the chosen default language will not display properly because it was not packaged in either edx-platform or openedx-i18n. If you feel like your language should be packaged, please `open an issue on the openedx-i18n project <https://github.com/openedx/openedx-i18n/issues>`_.

When I make changes to a course in the CMS, they are not taken into account by the LMS
--------------------------------------------------------------------------------------

This issue should only happen in development mode. Long story short, it can be solved by creating a Waffle switch with the following command::

    tutor dev run lms ./manage.py lms waffle_switch block_structure.invalidate_cache_on_publish on --create

If you'd like to learn more, please take a look at `this Github issue <https://github.com/overhangio/tutor/issues/302>`__.
