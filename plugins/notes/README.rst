Students notes plugin for `Tutor <https://docs.tutor.overhang.io>`_
===================================================================

This is a plugin for `Tutor <https://docs.tutor.overhang.io>`_ to easily add the `Open edX note-taking app <https://github.com/edx/edx-notes-api>`_ to an Open edX platform. This app allows students to annotate portions of the courseware (see `the official documentation <https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-ironwood.master/exercises_tools/notes.html?highlight=notes>`_).

.. image:: https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/open-release-ironwood.master/_images/SFD_SN_bodyexample.png
    :alt: Notes in action

Installation
------------

The plugin is currently bundled with the `binary releases of Tutor <https://github.com/overhangio/tutor/releases>`_. If you have installed Tutor from source, you will have to install this plugin from source, too::
  
    pip install tutor-notes

Then, to enable this plugin, run::
  
    tutor plugins enable notes

		
You should beware that the ``notes.<LMS_HOST>`` domain name should exist and point to your server. For instance, if your LMS is hosted at http://myopenedx.com, the notes service should be found at http://notes.myopenedx.com.

If you would like to host the notes service at a different domain name, you can set the ``NOTES_HOST`` configuration variable (see below). In particular, in development you should set this configuration variable to ``notes.localhost`` in order to be able to access the notes service from the LMS. Otherwise you will get a "Sorry, we could not search the store for annotations" error.


Configuration
-------------

- ``NOTES_MYSQL_PASSWORD`` (default: ``"{{ 8|random_string }}"``)
- ``NOTES_SECRET_KEY`` (default: ``"{{ 24|random_string }}"``)
- ``NOTES_OAUTH2_SECRET`` (default: ``"{{ 24|random_string }}"``)
- ``NOTES_DOCKER_IMAGE`` (default: ``"overhangio/openedx-notes:{{ TUTOR_VERSION }}"``)
- ``NOTES_HOST`` (default: ``"notes.{{ LMS_HOST }}"``)
- ``NOTES_MYSQL_DATABASE`` (default: ``"notes"``)
- ``NOTES_MYSQL_USERNAME`` (default: ``"notes"``)

These values can be modified with ``tutor config save --set PARAM_NAME=VALUE`` commands.
