.. _options:

Optional features
=================

Some optional features may be activated or deactivated during the interactive configuration step. These features change configuration files (during the ``configure`` step) as well as make targets.

SSL/TLS certificates for HTTPS access
-------------------------------------

By activating this feature, a free SSL/TLS certificate from the `Let's Encrypt <https://letsencrypt.org/>`_ certificate authority will be created for your platform. With this feature, **your platform will no longer be accessible in HTTP**. Calls to http urls will be redirected to https url.

The following DNS records must exist and point to your server::

    LMS_HOST (e.g: myopenedx.com)
    preview.LMS_HOST (e.g: preview.myopenedx.com)
    CMS_HOST (e.g: studio.myopenedx.com)

Thus, **this feature will (probably) not work in development** because the DNS records will (probably) not point to your development machine.

To download the certificate manually, run::

    make https-certificate

To renew the certificate, run this command once per month::

    make https-certificate-renew

Student notes
-------------

With `notes <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/exercises_tools/notes.html?highlight=notes>`_, students can annotate portions of the courseware. 

.. image:: https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-hawthorn.master/_images/SFD_SN_bodyexample.png
    :alt: Notes in action

You should beware that the ``notes.<LMS_HOST>`` domain name should be activated and point to your server. For instance, if your LMS is hosted at http://myopenedx.com, the notes service should be found at http://notes.myopenedx.com.

Xqueue
------

`Xqueue <https://github.com/edx/xqueue>`_ is for grading problems with external services. If you don't know what it is, you probably don't need it.

Docker container web UI with `Portainer <https://portainer.io/>`_
-----------------------------------------------------------------

Portainer is a web UI for managing docker containers. It lets you view your entire Open edX platform at a glace. Try it! It's really cool.

.. image:: https://portainer.io/images/screenshots/portainer.gif
    :alt: Portainer demo

After launching your platfom, the web UI will be available at `http://portainer.localhost <http://portainer.localhost>`_ and http://portainer.YOUR_LMS_HOST. You will be asked to define a password for the admin user. Then, select a "Local environment" to work on and hit "Connect". You're done! Select the "local" group to view all running containers. Amon many other things, you'll be able to view the logs for each container, which is really useful.

Android app (beta)
------------------

The Android app for your platform can be easily built in just one command::

    make android

If all goes well, the debuggable APK for your platform should then be available in ./data/android. To obtain a release APK, you will need to obtain credentials from the app store and add them to ``config/android/gradle.properties``. Then run::

    make android-release

Building the Android app for an Open edX platform is currently labeled as a **beta feature** because it was not fully tested yet. In particular, there is no easy mechanism for overriding the edX assets in the mobile app. This is still a work-in-progress.

Stats
-----

By default, the install script will collect some information about your install and send it to a private server. The only transmitted information are the LMS domain name and the ID of the install. To disable stats collection, define the following environment variable::

    export DISABLE_STATS=1

If you decide to disable stats, please send me a message to tell me about your platform! 
