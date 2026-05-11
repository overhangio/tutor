.. _run:

Running Open edX
================

You have gone through the :ref:`installation <install>`: at this point, you should have a running Open edX platform. If you don't, please follow the instructions from the :ref:`Troubleshooting <troubleshooting>` section.

Logging-in as administrator
---------------------------

Out of the box, Tutor does not create any user for you. You will want to create a user yourself with staff and administrator privileges to access the studio. There is a :ref:`simple command for that <createuser>`.

Importing a demo course
-----------------------

To get a glimpse of the possibilities of Open edX, we recommend you import the `official demo test course <https://github.com/openedx/edx-demo-course>`__. Tutor provides a :ref:`simple command for that <democourse>`.

Verifying your platform with smoke tests
-----------------------------------------

Once your platform is running, you can verify it with the built-in smoke test suite::

    tutor local do tests smoke

To run authenticated tests (user API, enrollment, course creation), supply credentials::

    tutor local do tests smoke \
        --admin-password=yourpassword \
        --oauth-client-secret=yoursecret

For full documentation on CLI options, writing plugin tests, and the ``--limit`` flag, see the :ref:`smoke tests guide <smoketests>`.
